from fastapi import APIRouter, Header, HTTPException, Query
from pathlib import PurePosixPath

from app.guidance.local import LocalGuidanceRetriever
from app.schemas.api import (
    AttemptFeedbackResponse,
    CandidateListResponse,
    ExerciseResponse,
    GitHubConnectResponse,
    GitHubImportRequest,
    GitHubImportResponse,
    GitHubRepoTreeResponse,
    GitHubReposResponse,
    HealthResponse,
    HintResponse,
    ProviderConfigPayload,
    ProviderConfigResponse,
    ProviderHealthResponse,
    ProviderListResponse,
    SubmitAttemptRequest,
    SubmitCodeRequest,
    SubmitCodeResponse,
)
from app.services.candidate_service import CandidateService
from app.services.exercise_service import ExerciseService
from app.services.github_service import (
    GitHubApiError,
    GitHubConnectionError,
    GitHubService,
    GitHubToken,
    extract_bearer_token,
    redact_secret,
)
from app.services.provider_service import ProviderService
from app.storage.memory import app_state

router = APIRouter()

provider_service = ProviderService()
candidate_service = CandidateService()
exercise_service = ExerciseService(LocalGuidanceRetriever())
github_service = GitHubService()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", app="refactor-trainer", scaffold=True)


@router.post("/submit-code", response_model=SubmitCodeResponse)
def submit_code(payload: SubmitCodeRequest) -> SubmitCodeResponse:
    try:
        return candidate_service.submit_code(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/candidates", response_model=CandidateListResponse)
def list_candidates(submission_id: str = Query(...)) -> CandidateListResponse:
    return candidate_service.list_candidates(submission_id)


@router.post("/exercise/{candidate_id}", response_model=ExerciseResponse)
def create_exercise(candidate_id: str) -> ExerciseResponse:
    try:
        return exercise_service.create_exercise(candidate_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/hints/{exercise_id}", response_model=HintResponse)
def get_hints(exercise_id: str) -> HintResponse:
    try:
        return exercise_service.generate_hints(exercise_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/submit-attempt/{exercise_id}", response_model=AttemptFeedbackResponse)
def submit_attempt(
    exercise_id: str, payload: SubmitAttemptRequest
) -> AttemptFeedbackResponse:
    try:
        return exercise_service.submit_attempt(exercise_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/providers", response_model=ProviderListResponse)
def list_providers() -> ProviderListResponse:
    return provider_service.list_providers()


@router.get("/provider/config", response_model=ProviderConfigResponse)
def get_provider_config() -> ProviderConfigResponse:
    return ProviderConfigResponse(config=app_state.provider_config)


@router.put("/provider/config", response_model=ProviderConfigResponse)
def update_provider_config(payload: ProviderConfigPayload) -> ProviderConfigResponse:
    app_state.provider_config = payload.config
    return ProviderConfigResponse(config=app_state.provider_config)


@router.get("/provider/health", response_model=ProviderHealthResponse)
def provider_health() -> ProviderHealthResponse:
    return provider_service.health()


@router.get("/github/connect", response_model=GitHubConnectResponse)
def github_connect(authorization: str | None = Header(default=None)) -> GitHubConnectResponse:
    token: GitHubToken | None = None
    try:
        token = extract_bearer_token(authorization)
        return github_service.connection_status(token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GitHubConnectionError as exc:
        raise HTTPException(status_code=401, detail=redact_secret(str(exc), token)) from exc


@router.get("/github/repos", response_model=GitHubReposResponse)
def github_repos(authorization: str | None = Header(default=None)) -> GitHubReposResponse:
    token: GitHubToken | None = None
    try:
        token = _require_github_token(authorization)
        return github_service.list_repositories(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except GitHubConnectionError as exc:
        raise HTTPException(status_code=401, detail=redact_secret(str(exc), token)) from exc
    except GitHubApiError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail=redact_secret(exc.detail, token)
        ) from exc


@router.get("/github/repo/{repo_id}/tree", response_model=GitHubRepoTreeResponse)
def github_repo_tree(
    repo_id: str,
    authorization: str | None = Header(default=None),
    path: str = Query(default=""),
    ref: str | None = Query(default=None),
) -> GitHubRepoTreeResponse:
    token: GitHubToken | None = None
    try:
        token = _require_github_token(authorization)
        return github_service.list_tree(token=token, repo_id=repo_id, path=path, ref=ref)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except GitHubConnectionError as exc:
        raise HTTPException(status_code=401, detail=redact_secret(str(exc), token)) from exc
    except GitHubApiError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail=redact_secret(exc.detail, token)
        ) from exc


@router.post("/github/import-file", response_model=GitHubImportResponse)
def github_import_file(
    payload: GitHubImportRequest, authorization: str | None = Header(default=None)
) -> GitHubImportResponse:
    if not payload.path.lower().endswith(".py"):
        raise HTTPException(status_code=400, detail="Only single Python files are supported.")

    filename = PurePosixPath(payload.path).name
    if not filename:
        raise HTTPException(status_code=400, detail="GitHub import requires one selected file.")

    token: GitHubToken | None = None
    try:
        token = _require_github_token(authorization)
        imported_file = github_service.fetch_file(
            token=token,
            repo_id=payload.repo_id,
            path=payload.path,
            ref=payload.ref,
        )
        submission = candidate_service.submit_code(
            SubmitCodeRequest(source="github", filename=filename, code=imported_file.content)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GitHubConnectionError as exc:
        raise HTTPException(status_code=401, detail=redact_secret(str(exc), token)) from exc
    except GitHubApiError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail=redact_secret(exc.detail, token)
        ) from exc

    return GitHubImportResponse(
        repo_id=payload.repo_id,
        path=imported_file.path,
        content=imported_file.content,
        submission_id=submission.submission_id,
        candidate_count=submission.candidate_count,
        status="imported",
    )


def _require_github_token(authorization: str | None) -> GitHubToken:
    token = extract_bearer_token(authorization)
    if token is None:
        raise ValueError("GitHub bearer token is required for targeted import browsing.")
    return token
