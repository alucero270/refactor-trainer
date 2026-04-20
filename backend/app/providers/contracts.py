from typing import Literal

from pydantic import BaseModel, Field, model_validator


DifficultyLabel = Literal["Easy", "Medium", "Hard"]
HintLevel = Literal[1, 2]
ProviderHealthStatus = Literal["ready", "unavailable"]


class ProviderFailure(BaseModel):
    code: str
    detail: str


class ProviderHealth(BaseModel):
    provider: str
    status: ProviderHealthStatus
    available: bool
    message: str
    failure: ProviderFailure | None = None

    @model_validator(mode="after")
    def validate_status_details(self) -> "ProviderHealth":
        if self.available:
            if self.status != "ready":
                raise ValueError("ready providers must report status='ready'")
            if self.failure is not None:
                raise ValueError("ready providers must not include failure details")
            return self

        if self.status != "unavailable":
            raise ValueError("unavailable providers must report status='unavailable'")
        if self.failure is None:
            raise ValueError("unavailable providers must include failure details")
        return self


class CandidateClassificationInput(BaseModel):
    language: str
    candidate_code: str
    candidate_region: str
    detection_summary: str
    guidance_snippets: list[str] = Field(default_factory=list)
    heuristic_label: str | None = None


class CandidateClassificationResult(BaseModel):
    label: str
    rationale: str


class ExerciseGenerationInput(BaseModel):
    language: str
    candidate_code: str
    candidate_region: str
    issue_label: str
    classification_rationale: str
    guidance_snippets: list[str] = Field(default_factory=list)


class ExerciseGenerationResult(BaseModel):
    title: str
    description: str
    difficulty: DifficultyLabel


class HintGenerationInput(BaseModel):
    language: str
    exercise_title: str
    exercise_description: str
    hint_level: HintLevel
    candidate_code: str
    issue_label: str
    guidance_snippets: list[str] = Field(default_factory=list)


class HintGenerationResult(BaseModel):
    hint: str
