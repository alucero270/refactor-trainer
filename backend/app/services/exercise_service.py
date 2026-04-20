from uuid import uuid4

from app.guidance.base import GuidanceRequest, GuidanceRetriever, GuidanceSnippet
from app.providers.contracts import CandidateClassificationInput, ExerciseGenerationInput
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
        guidance = self.guidance_retriever.getGuidance(
            GuidanceRequest(
                language="python",
                query="hint_policy",
                maxSnippets=1,
            )
        )
        guidance_summary = self._guidance_summary(guidance)
        hints = [
            "Start by identifying the smallest behavior-preserving extraction.",
            "Name the new unit around intent, not implementation detail.",
        ]
        return HintResponse(
            exercise_id=exercise_id,
            hints=hints,
            guidance_summary=guidance_summary,
            status="stub",
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
