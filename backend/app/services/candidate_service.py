from uuid import uuid4

from app.schemas.api import Candidate, CandidateListResponse, SubmitCodeRequest, SubmitCodeResponse
from app.storage.memory import app_state


class CandidateService:
    def submit_code(self, payload: SubmitCodeRequest) -> SubmitCodeResponse:
        submission_id = f"sub-{uuid4().hex[:8]}"
        candidates = self._detect_candidates(payload.code)
        app_state.submissions[submission_id] = {
            "source": payload.source,
            "code": payload.code,
            "filename": payload.filename,
            "candidates": candidates,
        }
        return SubmitCodeResponse(
            submission_id=submission_id,
            candidate_count=len(candidates),
            status="accepted",
        )

    def list_candidates(self, submission_id: str) -> CandidateListResponse:
        submission = app_state.submissions.get(submission_id)
        if not submission:
            return CandidateListResponse(submission_id=submission_id, candidates=[])

        return CandidateListResponse(
            submission_id=submission_id,
            candidates=submission["candidates"],
        )

    def _detect_candidates(self, code: str) -> list[Candidate]:
        if not code.strip():
            return []

        return [
            Candidate(
                id=f"cand-{uuid4().hex[:8]}",
                title="Extract focused helper",
                smell="long_function",
                summary="Deterministic scaffold candidate produced for non-empty input.",
                severity="medium",
            )
        ]

