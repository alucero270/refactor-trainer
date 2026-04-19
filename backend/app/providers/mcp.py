from app.providers.base import ModelProvider
from app.providers.contracts import (
    CandidateClassificationInput,
    CandidateClassificationResult,
    ExerciseGenerationInput,
    ExerciseGenerationResult,
    HintGenerationInput,
    HintGenerationResult,
    ProviderHealth,
)


class McpProvider(ModelProvider):
    kind = "mcp"
    supports_local = False

    def name(self) -> str:
        return "mcp"

    def healthCheck(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name(),
            status="stub",
            message="MCP transport is intentionally not implemented yet.",
        )

    def classifyCandidate(
        self, payload: CandidateClassificationInput
    ) -> CandidateClassificationResult:
        return CandidateClassificationResult(
            label=payload.heuristic_label or "LongMethod",
            rationale="Stub classification for the MCP provider contract.",
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
            hint=f"Stub hint level {payload.hint_level} from the MCP provider contract."
        )
