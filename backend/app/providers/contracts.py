from typing import Literal

from pydantic import BaseModel, Field


DifficultyLabel = Literal["Easy", "Medium", "Hard"]
HintLevel = Literal[1, 2]


class ProviderHealth(BaseModel):
    provider: str
    status: str
    message: str


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
