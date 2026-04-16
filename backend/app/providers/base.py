from abc import ABC, abstractmethod


class ModelProvider(ABC):
    kind: str = "unknown"
    supports_local: bool = False

    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""

    @abstractmethod
    def healthCheck(self) -> dict:
        """Return a placeholder health payload."""

    @abstractmethod
    def classifyCandidate(self, payload: dict) -> dict:
        """Classify a refactor candidate."""

    @abstractmethod
    def generateExercise(self, payload: dict) -> dict:
        """Generate a placeholder exercise."""

    @abstractmethod
    def generateHints(self, payload: dict) -> dict:
        """Generate placeholder hints."""

