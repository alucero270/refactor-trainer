from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    scaffold: bool


class SubmitCodeRequest(BaseModel):
    source: Literal["upload", "paste", "github"] = "paste"
    filename: str | None = None
    code: str = Field(..., min_length=0)


class Candidate(BaseModel):
    id: str
    title: str
    smell: str
    summary: str
    severity: str


class SubmitCodeResponse(BaseModel):
    submission_id: str
    candidate_count: int
    status: str


class CandidateListResponse(BaseModel):
    submission_id: str
    candidates: list[Candidate]


class CandidateResponse(BaseModel):
    exercise_id: str
    candidate_id: str
    instructions: str
    guidance_summary: str
    status: str


class HintResponse(BaseModel):
    exercise_id: str
    hints: list[str]
    guidance_summary: str
    status: str


class SubmitAttemptRequest(BaseModel):
    attempt_code: str


class AttemptFeedbackResponse(BaseModel):
    exercise_id: str
    accepted: bool
    feedback: str
    status: str


class ProviderSummary(BaseModel):
    name: str
    kind: str
    supports_local: bool


class ProviderListResponse(BaseModel):
    providers: list[ProviderSummary]


class ProviderConfig(BaseModel):
    default_provider: str = "ollama"
    configured_providers: list[str] = ["ollama"]


class ProviderConfigPayload(BaseModel):
    config: ProviderConfig


class ProviderConfigResponse(BaseModel):
    config: ProviderConfig


class ProviderHealthItem(BaseModel):
    provider: str
    status: str
    message: str


class ProviderHealthResponse(BaseModel):
    providers: list[ProviderHealthItem]


class GitHubRepo(BaseModel):
    id: str
    name: str
    owner: str


class GitHubReposResponse(BaseModel):
    repos: list[GitHubRepo]


class GitHubTreeItem(BaseModel):
    path: str
    type: str


class GitHubRepoTreeResponse(BaseModel):
    repo_id: str
    tree: list[GitHubTreeItem]


class GitHubImportRequest(BaseModel):
    repo_id: str
    path: str
    ref: str = "HEAD"


class GitHubImportResponse(BaseModel):
    repo_id: str
    path: str
    content: str
    status: str

