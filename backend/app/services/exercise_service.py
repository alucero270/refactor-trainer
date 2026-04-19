from uuid import uuid4

from app.guidance.base import GuidanceRequest, GuidanceRetriever, GuidanceSnippet
from app.schemas.api import AttemptFeedbackResponse, CandidateResponse, HintResponse, SubmitAttemptRequest
from app.storage.memory import app_state


class ExerciseService:
    def __init__(self, guidance_retriever: GuidanceRetriever) -> None:
        self.guidance_retriever = guidance_retriever

    def create_exercise(self, candidate_id: str) -> CandidateResponse:
        exercise_id = f"ex-{uuid4().hex[:8]}"
        guidance = self.guidance_retriever.getGuidance(
            GuidanceRequest(
                language="python",
                query="exercise_authoring_rules",
                maxSnippets=1,
            )
        )
        guidance_summary = self._guidance_summary(guidance)
        app_state.exercises[exercise_id] = {
            "candidate_id": candidate_id,
            "guidance_excerpt": guidance_summary,
        }
        return CandidateResponse(
            exercise_id=exercise_id,
            candidate_id=candidate_id,
            instructions="Placeholder exercise for the selected candidate.",
            guidance_summary=guidance_summary,
            status="stub",
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
