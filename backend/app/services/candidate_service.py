from uuid import uuid4

from app.analysis.candidate_detector import DetectedCandidate, PythonCandidateDetector
from app.schemas.api import Candidate, CandidateListResponse, SubmitCodeRequest, SubmitCodeResponse
from app.storage.memory import app_state


class CandidateService:
    def __init__(self, detector: PythonCandidateDetector | None = None) -> None:
        self.detector = detector or PythonCandidateDetector()

    def submit_code(self, payload: SubmitCodeRequest) -> SubmitCodeResponse:
        submission_id = f"sub-{uuid4().hex[:8]}"
        filename = self._normalize_filename(payload)
        normalized_code = self._normalize_code(payload.code)
        detected_candidates = self.detector.detect(normalized_code)
        app_state.submissions[submission_id] = {
            "source": payload.source,
            "code": normalized_code,
            "filename": filename,
            "candidates": [],
            "detected_candidates": [candidate.model_dump() for candidate in detected_candidates],
            "language": "python",
        }
        return SubmitCodeResponse(
            submission_id=submission_id,
            candidate_count=len(detected_candidates),
            status="accepted",
        )

    def list_candidates(self, submission_id: str) -> CandidateListResponse:
        submission = app_state.submissions.get(submission_id)
        if not submission:
            return CandidateListResponse(submission_id=submission_id, candidates=[])

        public_candidates = [
            Candidate.model_validate(candidate)
            for candidate in submission.get("detected_candidates", [])
        ]
        submission["candidates"] = [candidate.model_dump() for candidate in public_candidates]

        return CandidateListResponse(
            submission_id=submission_id,
            candidates=public_candidates,
        )

    @staticmethod
    def _normalize_filename(payload: SubmitCodeRequest) -> str:
        filename = (payload.filename or "").strip()

        if payload.source == "upload" and not filename:
            raise ValueError("filename is required for upload submissions.")

        if filename:
            if "/" in filename or "\\" in filename:
                raise ValueError("submit-code accepts exactly one Python file, not a file path.")
            if not filename.lower().endswith(".py"):
                raise ValueError("Only single Python files are supported.")
            return filename

        return "snippet.py"

    @staticmethod
    def _normalize_code(code: str) -> str:
        normalized = code.replace("\r\n", "\n").replace("\r", "\n")
        normalized = normalized.lstrip("\ufeff")
        if normalized and not normalized.endswith("\n"):
            normalized += "\n"
        return normalized
