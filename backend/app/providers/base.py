from abc import ABC, abstractmethod

from app.providers.contracts import (
    CandidateClassificationInput,
    CandidateClassificationResult,
    ExerciseGenerationInput,
    ExerciseGenerationResult,
    HintGenerationInput,
    HintGenerationResult,
    ProviderHealth,
)


class ModelProvider(ABC):
    kind: str = "unknown"
    supports_local: bool = False

    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""

    @abstractmethod
    def healthCheck(self) -> ProviderHealth:
        """Return provider readiness information."""

    @abstractmethod
    def classifyCandidate(
        self, payload: CandidateClassificationInput
    ) -> CandidateClassificationResult:
        """Classify a refactor candidate."""

    @abstractmethod
    def generateExercise(
        self, payload: ExerciseGenerationInput
    ) -> ExerciseGenerationResult:
        """Generate a refactoring exercise."""

    @abstractmethod
    def generateHints(self, payload: HintGenerationInput) -> HintGenerationResult:
        """Generate one progressive hint."""
