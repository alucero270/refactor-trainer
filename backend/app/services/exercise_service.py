import re
from uuid import uuid4

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

    def create_exercise(self, candidate_id: str) -> ExerciseResponse:
        candidate = self._find_candidate(candidate_id)
        provider = self.provider_service.resolve_default_provider()
        classification = provider.classifyCandidate(
            CandidateClassificationInput(
                language="python",
                candidate_code=candidate["candidate_code"],
                candidate_region=candidate["candidate_region"],
                detection_summary=candidate["detection_summary"],
                heuristic_label=candidate["smell"],
            )
        )
        generated_exercise = provider.generateExercise(
            ExerciseGenerationInput(
                language="python",
                candidate_code=candidate["candidate_code"],
                candidate_region=candidate["candidate_region"],
                issue_label=classification.label,
                classification_rationale=classification.rationale,
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
        guidance = self.guidance_retriever.getGuidance(
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
            generated_hint = provider.generateHints(
                HintGenerationInput(
                    language="python",
                    exercise_title=exercise["title"],
                    exercise_description=exercise["description"],
                    hint_level=next_level,
                    candidate_code=exercise["candidate_code"],
                    issue_label=exercise["issue_label"],
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
        return AttemptFeedbackResponse(
            exercise_id=exercise_id,
            accepted=False,
            feedback=(
                "Attempt evaluation is intentionally stubbed. "
                f"Received {len(payload.attempt_code)} characters for future analysis."
            ),
            status="stub",
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
