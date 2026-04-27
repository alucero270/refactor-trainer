from fastapi import APIRouter, Header, HTTPException, Query

from app.diagnostics import log_event, metrics
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
    MetricsResponse,
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
    GitHubConnectionError,
    GitHubRequestError,
    GitHubService,
    extract_bearer_token,
    require_bearer_token,
)
from app.services.provider_service import ProviderService
from app.storage.memory import app_state
from app.storage.provider_config import ProviderConfigStorageError, save_provider_config

router = APIRouter()

provider_service = ProviderService()
candidate_service = CandidateService()
exercise_service = ExerciseService(LocalGuidanceRetriever())
github_service = GitHubService()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", app="refactor-trainer", scaffold=True)


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics() -> MetricsResponse:
    return MetricsResponse(counters=metrics.snapshot())


@router.post("/submit-code", response_model=SubmitCodeResponse)
def submit_code(payload: SubmitCodeRequest) -> SubmitCodeResponse:
    try:
        response = candidate_service.submit_code(payload)
        metrics.increment("submit_code.accepted")
        log_event(
            "submit_code.accepted",
            source=payload.source,
            filename=payload.filename,
            submission_id=response.submission_id,
            candidate_count=response.candidate_count,
        )
        return response
    except ValueError as exc:
        metrics.increment("submit_code.rejected")
        log_event("submit_code.rejected", source=payload.source, filename=payload.filename)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/candidates", response_model=CandidateListResponse)
def list_candidates(submission_id: str = Query(...)) -> CandidateListResponse:
    response = candidate_service.list_candidates(submission_id)
    metrics.increment("candidates.listed")
    log_event(
        "candidates.listed",
        submission_id=submission_id,
        candidate_count=len(response.candidates),
    )
    return response


@router.post("/exercise/{candidate_id}", response_model=ExerciseResponse)
def create_exercise(candidate_id: str) -> ExerciseResponse:
    try:
        response = exercise_service.create_exercise(candidate_id)
        metrics.increment("exercise.generated")
        log_event(
            "exercise.generated",
            candidate_id=candidate_id,
            exercise_id=response.exercise_id,
            difficulty=response.difficulty,
        )
        return response
    except LookupError as exc:
        metrics.increment("exercise.failed")
        log_event("exercise.failed", candidate_id=candidate_id, failure="not_found")
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        metrics.increment("exercise.failed")
        log_event("exercise.failed", candidate_id=candidate_id, failure="provider_error")
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/hints/{exercise_id}", response_model=HintResponse)
def get_hints(exercise_id: str) -> HintResponse:
    try:
        response = exercise_service.generate_hints(exercise_id)
        metrics.increment("hints.generated")
        log_event("hints.generated", exercise_id=exercise_id, hint_count=len(response.hints))
        return response
    except LookupError as exc:
        metrics.increment("hints.failed")
        log_event("hints.failed", exercise_id=exercise_id, failure="not_found")
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        metrics.increment("hints.failed")
        log_event("hints.failed", exercise_id=exercise_id, failure="provider_error")
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/submit-attempt/{exercise_id}", response_model=AttemptFeedbackResponse)
def submit_attempt(
    exercise_id: str, payload: SubmitAttemptRequest
) -> AttemptFeedbackResponse:
    try:
        response = exercise_service.submit_attempt(exercise_id, payload)
        metrics.increment("attempt.evaluated")
        log_event(
            "attempt.evaluated",
            exercise_id=exercise_id,
            accepted=response.accepted,
        )
        return response
    except LookupError as exc:
        metrics.increment("attempt.failed")
        log_event("attempt.failed", exercise_id=exercise_id, failure="not_found")
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/providers", response_model=ProviderListResponse)
def list_providers() -> ProviderListResponse:
    return provider_service.list_providers()


@router.get("/provider/config", response_model=ProviderConfigResponse)
def get_provider_config() -> ProviderConfigResponse:
    return ProviderConfigResponse(config=app_state.provider_config)


@router.put("/provider/config", response_model=ProviderConfigResponse)
def update_provider_config(payload: ProviderConfigPayload) -> ProviderConfigResponse:
    try:
        save_provider_config(payload.config)
    except ProviderConfigStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    app_state.provider_config = payload.config
    metrics.increment("provider_config.updated")
    log_event(
        "provider_config.updated",
        default_provider=payload.config.default_provider,
        configured_providers=payload.config.configured_providers,
    )
    return ProviderConfigResponse(config=app_state.provider_config)


@router.get("/provider/health", response_model=ProviderHealthResponse)
def provider_health() -> ProviderHealthResponse:
    return provider_service.health()


@router.get("/github/connect", response_model=GitHubConnectResponse)
def github_connect(authorization: str | None = Header(default=None)) -> GitHubConnectResponse:
    try:
        token = extract_bearer_token(authorization)
        response = github_service.connection_status(token)
        metrics.increment("github.connect.checked")
        log_event("github.connect.checked", status=response.status)
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GitHubConnectionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/github/repos", response_model=GitHubReposResponse)
def github_repos(authorization: str | None = Header(default=None)) -> GitHubReposResponse:
    try:
        token = require_bearer_token(authorization)
        repos = github_service.list_repos(token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GitHubConnectionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except GitHubRequestError as exc:
        raise HTTPException(status_code=exc.status or 502, detail=exc.detail) from exc
    metrics.increment("github.repos.listed")
    log_event("github.repos.listed", repo_count=len(repos))
    return GitHubReposResponse(repos=repos)


@router.get("/github/repo/tree", response_model=GitHubRepoTreeResponse)
def github_repo_tree(
    repo_id: str = Query(...),
    ref: str = Query(default="HEAD"),
    authorization: str | None = Header(default=None),
) -> GitHubRepoTreeResponse:
    try:
        token = require_bearer_token(authorization)
        tree = github_service.get_tree(token, repo_id, ref)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GitHubConnectionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except GitHubRequestError as exc:
        raise HTTPException(status_code=exc.status or 502, detail=exc.detail) from exc
    metrics.increment("github.tree.listed")
    log_event("github.tree.listed", repo_id=repo_id, entry_count=len(tree))
    return GitHubRepoTreeResponse(repo_id=repo_id, tree=tree)


@router.post("/github/import-file", response_model=GitHubImportResponse)
def github_import_file(
    payload: GitHubImportRequest,
    authorization: str | None = Header(default=None),
) -> GitHubImportResponse:
    try:
        token = require_bearer_token(authorization)
        response = github_service.import_file(token, payload.repo_id, payload.path, payload.ref)
    except ValueError as exc:
        metrics.increment("github.import.rejected")
        log_event("github.import.rejected", repo_id=payload.repo_id, path=payload.path)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GitHubConnectionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except GitHubRequestError as exc:
        raise HTTPException(status_code=exc.status or 502, detail=exc.detail) from exc
    metrics.increment("github.import.accepted")
    log_event("github.import.accepted", repo_id=payload.repo_id, path=payload.path)
    return response
