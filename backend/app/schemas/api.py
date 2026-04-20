from typing import Literal

from pydantic import BaseModel, Field, SecretStr, model_validator


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


class ExerciseResponse(BaseModel):
    exercise_id: str
    candidate_id: str
    title: str
    description: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    status: Literal["generated"]


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


ProviderName = Literal["ollama", "openai", "anthropic", "mcp"]


class OllamaProviderConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str | None = None


class OpenAIProviderConfig(BaseModel):
    api_key: SecretStr | None = None
    model: str | None = None
    base_url: str | None = None


class AnthropicProviderConfig(BaseModel):
    api_key: SecretStr | None = None
    model: str | None = None
    base_url: str | None = None


class McpProviderConfig(BaseModel):
    server_url: str | None = None
    model: str | None = None


class ProviderSettings(BaseModel):
    ollama: OllamaProviderConfig = Field(default_factory=OllamaProviderConfig)
    openai: OpenAIProviderConfig = Field(default_factory=OpenAIProviderConfig)
    anthropic: AnthropicProviderConfig = Field(default_factory=AnthropicProviderConfig)
    mcp: McpProviderConfig = Field(default_factory=McpProviderConfig)


class ProviderConfig(BaseModel):
    default_provider: ProviderName = "ollama"
    configured_providers: list[ProviderName] = Field(default_factory=lambda: ["ollama"])
    providers: ProviderSettings = Field(default_factory=ProviderSettings)

    @model_validator(mode="after")
    def validate_provider_selection(self) -> "ProviderConfig":
        configured = list(dict.fromkeys(self.configured_providers))
        if len(configured) != len(self.configured_providers):
            raise ValueError("configured_providers must not contain duplicates")

        if self.default_provider not in configured:
            raise ValueError("default_provider must be included in configured_providers")

        if "openai" in configured and not self._has_secret(self.providers.openai.api_key):
            raise ValueError("openai.api_key is required when openai is configured")

        if "anthropic" in configured and not self._has_secret(self.providers.anthropic.api_key):
            raise ValueError("anthropic.api_key is required when anthropic is configured")

        if "mcp" in configured and not self._has_text(self.providers.mcp.server_url):
            raise ValueError("mcp.server_url is required when mcp is configured")

        return self

    @staticmethod
    def _has_secret(value: SecretStr | None) -> bool:
        return value is not None and bool(value.get_secret_value().strip())

    @staticmethod
    def _has_text(value: str | None) -> bool:
        return value is not None and bool(value.strip())


class ProviderConfigPayload(BaseModel):
    config: ProviderConfig


class ProviderConfigResponse(BaseModel):
    config: ProviderConfig


class ProviderHealthFailure(BaseModel):
    code: str
    detail: str


class ProviderHealthItem(BaseModel):
    provider: str
    status: Literal["ready", "unavailable"]
    available: bool
    message: str
    failure: ProviderHealthFailure | None = None


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
