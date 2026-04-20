import ast
import re
from collections import Counter

from pydantic import BaseModel

from app.schemas.api import Candidate


class DetectedCandidate(Candidate):
    start_line: int
    end_line: int
    candidate_code: str
    candidate_region: str
    detection_summary: str


class CandidateCodeMetrics(BaseModel):
    line_span: int
    statement_count: int
    max_nesting: int
    duplicate_statement_count: int
    poor_names: list[str]


class PythonCandidateDetector:
    _priority = {
        "LongMethod": 0,
        "DeepNesting": 1,
        "DuplicatedCode": 2,
        "PoorNaming": 3,
    }
    _generic_names = {"data", "info", "item", "obj", "process", "run", "stuff", "temp", "thing", "value"}

    def detect(self, code: str) -> list[DetectedCandidate]:
        module = self._parse_module(code)

        lines = code.splitlines()
        candidates: list[DetectedCandidate] = []

        for node in ast.walk(module):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                candidates.extend(self._detect_for_function(node, lines))

        deduped = self._dedupe_candidates(candidates)
        ranked = sorted(
            deduped,
            key=lambda candidate: (
                self._priority.get(candidate.smell, 99),
                candidate.start_line,
                candidate.id,
            ),
        )
        return ranked[:3]

    def inspect_candidate_code(self, code: str) -> CandidateCodeMetrics:
        module = self._parse_module(code)
        function = next(
            (
                node
                for node in module.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ),
            None,
        )
        if function is None:
            return CandidateCodeMetrics(
                line_span=0,
                statement_count=0,
                max_nesting=0,
                duplicate_statement_count=0,
                poor_names=[],
            )
        return self._metrics_for_function(function)

    def _detect_for_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, lines: list[str]
    ) -> list[DetectedCandidate]:
        candidates: list[DetectedCandidate] = []
        metrics = self._metrics_for_function(node)
        line_span = metrics.line_span
        statement_count = metrics.statement_count
        max_depth = metrics.max_nesting
        duplicate_count = metrics.duplicate_statement_count
        poor_names = metrics.poor_names

        if line_span >= 12 or statement_count >= 8:
            candidates.append(
                self._build_candidate(
                    node=node,
                    lines=lines,
                    smell="LongMethod",
                    title=f"Break up long function '{node.name}'",
                    summary=(
                        f"Function '{node.name}' spans {line_span} lines across "
                        f"{statement_count} statements, which suggests multiple responsibilities."
                    ),
                    severity="high" if line_span >= 20 or statement_count >= 12 else "medium",
                )
            )

        if max_depth > 2:
            candidates.append(
                self._build_candidate(
                    node=node,
                    lines=lines,
                    smell="DeepNesting",
                    title=f"Flatten nested flow in '{node.name}'",
                    summary=(
                        f"Function '{node.name}' reaches {max_depth} nested control-flow levels, "
                        "which raises cognitive load."
                    ),
                    severity="high" if max_depth > 3 else "medium",
                )
            )

        if duplicate_count > 0:
            candidates.append(
                self._build_candidate(
                    node=node,
                    lines=lines,
                    smell="DuplicatedCode",
                    title=f"Extract repeated logic from '{node.name}'",
                    summary=(
                        f"Function '{node.name}' repeats {duplicate_count} non-trivial statement "
                        "shapes that could be extracted into shared logic."
                    ),
                    severity="medium",
                )
            )

        if poor_names:
            candidates.append(
                self._build_candidate(
                    node=node,
                    lines=lines,
                    smell="PoorNaming",
                    title=f"Clarify naming in '{node.name}'",
                    summary=(
                        f"Function '{node.name}' uses generic names ({', '.join(poor_names)}), "
                        "which slows comprehension."
                    ),
                    severity="low",
                )
            )

        return candidates

    def _metrics_for_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> CandidateCodeMetrics:
        return CandidateCodeMetrics(
            line_span=self._line_span(node),
            statement_count=self._statement_count(node),
            max_nesting=self._max_nesting(node),
            duplicate_statement_count=self._duplicate_statement_count(node),
            poor_names=self._poor_names(node),
        )

    def _build_candidate(
        self,
        *,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        lines: list[str],
        smell: str,
        title: str,
        summary: str,
        severity: str,
    ) -> DetectedCandidate:
        start_line = node.lineno
        end_line = node.end_lineno or node.lineno
        candidate_code = "\n".join(lines[start_line - 1 : end_line])
        slug = re.sub(r"[^a-z0-9]+", "-", f"{smell}-{node.name}".lower()).strip("-")

        return DetectedCandidate(
            id=f"cand-{slug}-{start_line}",
            title=title,
            smell=smell,
            summary=summary,
            severity=severity,
            start_line=start_line,
            end_line=end_line,
            candidate_code=candidate_code,
            candidate_region=f"lines {start_line}-{end_line}",
            detection_summary=summary,
        )

    @staticmethod
    def _line_span(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        end_line = node.end_lineno or node.lineno
        return (end_line - node.lineno) + 1

    @staticmethod
    def _statement_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        return sum(
            1
            for candidate in ast.walk(node)
            if isinstance(candidate, ast.stmt)
            and not isinstance(candidate, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        )

    def _max_nesting(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        return self._nesting_in_body(node.body, 0)

    def _nesting_in_body(self, body: list[ast.stmt], depth: int) -> int:
        max_depth = depth
        for statement in body:
            child_bodies = self._child_bodies(statement)
            if child_bodies:
                current_depth = depth + 1
                max_depth = max(max_depth, current_depth)
                for child_body in child_bodies:
                    max_depth = max(max_depth, self._nesting_in_body(child_body, current_depth))
        return max_depth

    @staticmethod
    def _child_bodies(statement: ast.stmt) -> list[list[ast.stmt]]:
        child_bodies: list[list[ast.stmt]] = []
        for attribute in ("body", "orelse", "finalbody"):
            value = getattr(statement, attribute, None)
            if isinstance(value, list) and value:
                child_bodies.append(value)
        handlers = getattr(statement, "handlers", None)
        if handlers:
            child_bodies.extend(handler.body for handler in handlers if handler.body)
        return child_bodies

    @staticmethod
    def _duplicate_statement_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        fingerprints = [
            ast.dump(statement, include_attributes=False)
            for statement in ast.walk(node)
            if isinstance(statement, (ast.Assign, ast.AugAssign, ast.Expr, ast.Return))
        ]
        counts = Counter(fingerprint for fingerprint in fingerprints if len(fingerprint) > 30)
        return sum(1 for count in counts.values() if count > 1)

    def _poor_names(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
        names: list[str] = []
        if node.name.lower() in self._generic_names:
            names.append(node.name)

        for candidate in ast.walk(node):
            if isinstance(candidate, ast.Name) and isinstance(candidate.ctx, ast.Store):
                normalized = candidate.id.lower()
                if normalized in {"i", "j", "k"}:
                    continue
                if len(candidate.id) <= 2 or normalized in self._generic_names:
                    names.append(candidate.id)

        deduped = list(dict.fromkeys(names))
        if len(deduped) >= 2 or (deduped and node.name.lower() in self._generic_names):
            return deduped
        return []

    @staticmethod
    def _dedupe_candidates(candidates: list[DetectedCandidate]) -> list[DetectedCandidate]:
        deduped: dict[tuple[str, int, int], DetectedCandidate] = {}
        for candidate in candidates:
            deduped[(candidate.smell, candidate.start_line, candidate.end_line)] = candidate
        return list(deduped.values())

    @staticmethod
    def _parse_module(code: str) -> ast.Module:
        try:
            return ast.parse(code)
        except SyntaxError as exc:
            detail = exc.msg
            if exc.lineno is not None:
                detail = f"{detail} at line {exc.lineno}"
            raise ValueError(f"Submitted code is not valid Python syntax: {detail}.") from exc
