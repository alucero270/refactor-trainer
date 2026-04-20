from fastapi import APIRouter, HTTPException, Query

from app.guidance.local import LocalGuidanceRetriever
from app.schemas.api import (
    AttemptFeedbackResponse,
    CandidateListResponse,
    ExerciseResponse,
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
from app.services.provider_service import ProviderService
from app.storage.memory import app_state

router = APIRouter()

provider_service = ProviderService()
candidate_service = CandidateService()
exercise_service = ExerciseService(LocalGuidanceRetriever())


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
    return exercise_service.submit_attempt(exercise_id, payload)


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


@router.get("/github/connect")
def github_connect() -> dict:
    return {"status": "stub", "message": "GitHub OAuth flow is not implemented in this scaffold."}


@router.get("/github/repos", response_model=GitHubReposResponse)
def github_repos() -> GitHubReposResponse:
    return GitHubReposResponse(
        repos=[
            {"id": "demo-repo", "name": "demo-repo", "owner": "placeholder"},
        ]
    )


@router.get("/github/repo/{repo_id}/tree", response_model=GitHubRepoTreeResponse)
def github_repo_tree(repo_id: str) -> GitHubRepoTreeResponse:
    return GitHubRepoTreeResponse(
        repo_id=repo_id,
        tree=[
            {"path": "src/example.py", "type": "blob"},
            {"path": "README.md", "type": "blob"},
        ],
    )


@router.post("/github/import-file", response_model=GitHubImportResponse)
def github_import_file(payload: GitHubImportRequest) -> GitHubImportResponse:
    if not payload.path.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only single-file Python imports are scaffolded.")

    return GitHubImportResponse(
        repo_id=payload.repo_id,
        path=payload.path,
        content="# placeholder imported Python file\n",
        status="stub",
    )
