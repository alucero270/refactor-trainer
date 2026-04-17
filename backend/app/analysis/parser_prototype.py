from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Literal


SegmentKind = Literal["function", "method"]


@dataclass(frozen=True)
class SyntaxFailure:
    message: str
    line: int | None
    column: int | None


@dataclass(frozen=True)
class CandidateSegment:
    qualified_name: str
    kind: SegmentKind
    start_line: int
    end_line: int


@dataclass(frozen=True)
class ParsePrototypeResult:
    syntax_valid: bool
    tree: ast.Module | None
    segments: tuple[CandidateSegment, ...]
    syntax_failure: SyntaxFailure | None


def parse_python_source(source: str, filename: str = "<submitted-code>") -> ParsePrototypeResult:
    """Parse one Python source string without executing it.

    Candidate scoring in MVP is segmented by the smallest function or method
    body available in the submitted file. This prototype records those units
    and returns syntax details instead of raising for invalid input.
    """

    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return ParsePrototypeResult(
            syntax_valid=False,
            tree=None,
            segments=(),
            syntax_failure=SyntaxFailure(
                message=exc.msg,
                line=exc.lineno,
                column=exc.offset,
            ),
        )

    collector = _SegmentCollector()
    collector.visit(tree)

    return ParsePrototypeResult(
        syntax_valid=True,
        tree=tree,
        segments=tuple(collector.segments),
        syntax_failure=None,
    )


class _SegmentCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self._scope_names: list[str] = []
        self._scope_kinds: list[Literal["class", "function"]] = []
        self.segments: list[CandidateSegment] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._scope_names.append(node.name)
        self._scope_kinds.append("class")
        self.generic_visit(node)
        self._scope_names.pop()
        self._scope_kinds.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_segment(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_segment(node)

    def _record_segment(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        parent_kind = self._scope_kinds[-1] if self._scope_kinds else None
        kind: SegmentKind = "method" if parent_kind == "class" else "function"
        qualified_name = ".".join([*self._scope_names, node.name])
        self.segments.append(
            CandidateSegment(
                qualified_name=qualified_name,
                kind=kind,
                start_line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
            )
        )
        self._scope_names.append(node.name)
        self._scope_kinds.append("function")
        self.generic_visit(node)
        self._scope_names.pop()
        self._scope_kinds.pop()
