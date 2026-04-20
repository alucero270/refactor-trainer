import re
from uuid import uuid4

from app.analysis.candidate_detector import PythonCandidateDetector
from app.guidance.base import GuidanceRequest, GuidanceRetriever, GuidanceSnippet
from app.providers.contracts import (
    CandidateClassificationInput,
    ExerciseGenerationInput,
    HintGenerationInput,
)
from app.schemas.api import AttemptFeedbackResponse, ExerciseResponse, HintResponse, SubmitAttemptRequest
from app.services.provider_service import ProviderService
from app.storage.memory import app_state


class ExerciseService:
    def __init__(
        self,
        guidance_retriever: GuidanceRetriever,
        provider_service: ProviderService | None = None,
    ) -> None:
        self.guidance_retriever = guidance_retriever
        self.provider_service = provider_service or ProviderService()
        self.detector = PythonCandidateDetector()

    def create_exercise(self, candidate_id: str) -> ExerciseResponse:
        candidate = self._find_candidate(candidate_id)
        provider = self.provider_service.resolve_default_provider()
        classification_guidance = self._classification_guidance(candidate["smell"])
        classification = provider.classifyCandidate(
            CandidateClassificationInput(
                language="python",
                candidate_code=candidate["candidate_code"],
                candidate_region=candidate["candidate_region"],
                detection_summary=candidate["detection_summary"],
                heuristic_label=candidate["smell"],
                guidance_snippets=classification_guidance,
            )
        )
        exercise_guidance = self._exercise_guidance(
            issue_label=classification.label,
            difficulty="Medium",
        )
        generated_exercise = provider.generateExercise(
            ExerciseGenerationInput(
                language="python",
                candidate_code=candidate["candidate_code"],
                candidate_region=candidate["candidate_region"],
                issue_label=classification.label,
                classification_rationale=classification.rationale,
                guidance_snippets=exercise_guidance,
            )
        )
        exercise_id = f"ex-{uuid4().hex[:8]}"
        app_state.exercises[exercise_id] = {
            "candidate_id": candidate_id,
            "candidate_code": candidate["candidate_code"],
            "candidate_region": candidate["candidate_region"],
            "issue_label": classification.label,
            "classification_rationale": classification.rationale,
            "title": generated_exercise.title,
            "description": generated_exercise.description,
            "difficulty": generated_exercise.difficulty,
            "revealed_hints": [],
        }
        return ExerciseResponse(
            exercise_id=exercise_id,
            candidate_id=candidate_id,
            title=generated_exercise.title,
            description=generated_exercise.description,
            difficulty=generated_exercise.difficulty,
            status="generated",
        )

    def generate_hints(self, exercise_id: str) -> HintResponse:
        exercise = self._find_exercise(exercise_id)
        guidance = self._guidance_with_fallback(
            GuidanceRequest(
                language="python",
                query="hint_policy",
                maxSnippets=1,
            )
        )
        guidance_summary = self._guidance_summary(guidance)
        revealed_hints = list(exercise.get("revealed_hints", []))

        if len(revealed_hints) < 2:
            provider = self.provider_service.resolve_default_provider()
            next_level = len(revealed_hints) + 1
            hint_guidance = self._hint_guidance(exercise["issue_label"])
            generated_hint = provider.generateHints(
                HintGenerationInput(
                    language="python",
                    exercise_title=exercise["title"],
                    exercise_description=exercise["description"],
                    hint_level=next_level,
                    candidate_code=exercise["candidate_code"],
                    issue_label=exercise["issue_label"],
                    guidance_snippets=hint_guidance,
                )
            )
            sanitized_hint = self._validate_hint(generated_hint.hint, exercise["candidate_code"])
            revealed_hints.append(sanitized_hint)
            exercise["revealed_hints"] = revealed_hints

        return HintResponse(
            exercise_id=exercise_id,
            hints=revealed_hints,
            guidance_summary=guidance_summary,
            status="generated",
        )

    def submit_attempt(
        self, exercise_id: str, payload: SubmitAttemptRequest
    ) -> AttemptFeedbackResponse:
        exercise = self._find_exercise(exercise_id)

        try:
            original_metrics = self.detector.inspect_candidate_code(exercise["candidate_code"])
            attempt_metrics = self.detector.inspect_candidate_code(payload.attempt_code)
        except ValueError:
            return AttemptFeedbackResponse(
                exercise_id=exercise_id,
                accepted=False,
                feedback="The submitted attempt does not parse as valid Python yet.",
                status="evaluated",
            )

        if self._normalize_code(payload.attempt_code) == self._normalize_code(exercise["candidate_code"]):
            return AttemptFeedbackResponse(
                exercise_id=exercise_id,
                accepted=False,
                feedback="The submitted attempt is unchanged from the original candidate region.",
                status="evaluated",
            )

        accepted = self._issue_improved(
            issue_label=exercise["issue_label"],
            original_metrics=original_metrics,
            attempt_metrics=attempt_metrics,
        )
        feedback = self._attempt_feedback(exercise["issue_label"], accepted)
        return AttemptFeedbackResponse(
            exercise_id=exercise_id,
            accepted=accepted,
            feedback=feedback,
            status="evaluated",
        )

    @staticmethod
    def _guidance_summary(guidance: list[GuidanceSnippet]) -> str:
        return guidance[0].summary

    @staticmethod
    def _find_candidate(candidate_id: str) -> dict:
        for submission in app_state.submissions.values():
            for candidate in submission.get("detected_candidates", []):
                if candidate["id"] == candidate_id:
                    return candidate
        raise LookupError(f"Candidate '{candidate_id}' was not found.")

    @staticmethod
    def _find_exercise(exercise_id: str) -> dict:
        exercise = app_state.exercises.get(exercise_id)
        if exercise is None:
            raise LookupError(f"Exercise '{exercise_id}' was not found.")
        return exercise

    @staticmethod
    def _validate_hint(hint: str, candidate_code: str) -> str:
        cleaned_hint = hint.strip()
        if not cleaned_hint:
            raise RuntimeError("Generated hint violated leakage guardrails.")

        if "```" in cleaned_hint:
            raise RuntimeError("Generated hint violated leakage guardrails.")

        if re.search(r"\b(step\s*\d+|\d+\.)", cleaned_hint, flags=re.IGNORECASE):
            raise RuntimeError("Generated hint violated leakage guardrails.")

        candidate_lines = [line.strip() for line in candidate_code.splitlines() if line.strip()]
        if any(len(line) > 20 and line in cleaned_hint for line in candidate_lines):
            raise RuntimeError("Generated hint violated leakage guardrails.")

        code_like_lines = [
            line
            for line in cleaned_hint.splitlines()
            if line.strip().startswith(("def ", "class ", "if ", "for ", "while ", "return "))
        ]
        if code_like_lines:
            raise RuntimeError("Generated hint violated leakage guardrails.")

        return cleaned_hint

    @staticmethod
    def _normalize_code(code: str) -> str:
        normalized = code.replace("\r\n", "\n").replace("\r", "\n").strip()
        return normalized

    @staticmethod
    def _issue_improved(*, issue_label: str, original_metrics, attempt_metrics) -> bool:
        if issue_label == "PoorNaming":
            return len(attempt_metrics.poor_names) < len(original_metrics.poor_names)
        if issue_label == "LongMethod":
            return (
                attempt_metrics.line_span < original_metrics.line_span
                or attempt_metrics.statement_count < original_metrics.statement_count
            )
        if issue_label == "DeepNesting":
            return attempt_metrics.max_nesting < original_metrics.max_nesting
        if issue_label == "DuplicatedCode":
            return (
                attempt_metrics.duplicate_statement_count
                < original_metrics.duplicate_statement_count
            )
        return False

    @staticmethod
    def _attempt_feedback(issue_label: str, accepted: bool) -> str:
        if accepted:
            return f"The targeted {issue_label} signal was reduced and the code still parses."
        return f"The submitted attempt parses, but the targeted {issue_label} signal did not improve yet."

    def _classification_guidance(self, issue_label: str) -> list[str]:
        return self._collect_guidance(
            GuidanceRequest(
                language="python",
                query="code_smell_taxonomy",
                issueType=issue_label,
                maxSnippets=2,
            )
        )

    def _exercise_guidance(self, *, issue_label: str, difficulty: str) -> list[str]:
        return self._collect_guidance(
            GuidanceRequest(
                language="python",
                query="refactoring_principles",
                maxSnippets=1,
            ),
            GuidanceRequest(
                language="python",
                query="exercise_authoring_rules",
                issueType=issue_label,
                difficulty=difficulty,
                maxSnippets=3,
            ),
        )

    def _hint_guidance(self, issue_label: str) -> list[str]:
        return self._collect_guidance(
            GuidanceRequest(
                language="python",
                query="hint_policy",
                issueType=issue_label,
                maxSnippets=2,
            )
        )

    def _collect_guidance(self, *requests: GuidanceRequest) -> list[str]:
        snippets: list[GuidanceSnippet] = []
        seen_topics: set[str] = set()

        for request in requests:
            for snippet in self._guidance_with_fallback(request):
                if snippet.topic in seen_topics:
                    continue
                seen_topics.add(snippet.topic)
                snippets.append(snippet)

        return [self._format_guidance_snippet(snippet) for snippet in snippets]

    def _guidance_with_fallback(self, request: GuidanceRequest) -> list[GuidanceSnippet]:
        guidance = self.guidance_retriever.getGuidance(request)
        if guidance:
            return guidance
        return self.guidance_retriever.getGuidance(
            GuidanceRequest(language=request.language, query="missing-topic", maxSnippets=1)
        )

    @staticmethod
    def _format_guidance_snippet(snippet: GuidanceSnippet) -> str:
        meaningful_lines = [
            line.strip()
            for line in snippet.content.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        excerpt = " ".join(meaningful_lines[:2]) if meaningful_lines else snippet.summary
        return f"{snippet.topic}: {excerpt}"
