from app.providers.base import ModelProvider
from app.providers.contracts import (
    CandidateClassificationInput,
    CandidateClassificationResult,
    ExerciseGenerationInput,
    ExerciseGenerationResult,
    HintGenerationInput,
    HintGenerationResult,
    ProviderFailure,
    ProviderHealth,
)


class OllamaProvider(ModelProvider):
    kind = "local"
    supports_local = True

    def name(self) -> str:
        return "ollama"

    def healthCheck(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name(),
            status="unavailable",
            available=False,
            message="Local Ollama path not yet wired.",
            failure=ProviderFailure(
                code="not_implemented",
                detail="Ollama health checks are not implemented in the scaffold.",
            ),
        )

    def classifyCandidate(
        self, payload: CandidateClassificationInput
    ) -> CandidateClassificationResult:
        return CandidateClassificationResult(
            label=payload.heuristic_label or "LongMethod",
            rationale="Stub classification for the Ollama provider contract.",
        )

    def generateExercise(
        self, payload: ExerciseGenerationInput
    ) -> ExerciseGenerationResult:
        return ExerciseGenerationResult(
            title=f"Refactor {payload.issue_label}",
            description="Stub exercise generated through the shared provider contract.",
            difficulty="Medium",
        )

    def generateHints(self, payload: HintGenerationInput) -> HintGenerationResult:
        return HintGenerationResult(
            hint=f"Stub hint level {payload.hint_level} from the Ollama provider contract."
        )
