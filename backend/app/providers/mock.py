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


class MockProvider(ModelProvider):
    kind = "mock"
    supports_local = True

    def name(self) -> str:
        return "mock"

    def healthCheck(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name(),
            status="ready",
            available=True,
            message="Mock provider is ready for deterministic development flows.",
        )

    def classifyCandidate(
        self, payload: CandidateClassificationInput
    ) -> CandidateClassificationResult:
        return CandidateClassificationResult(
            label=payload.heuristic_label or "LongMethod",
            rationale=(
                "Mock provider classification based on deterministic detection summary: "
                f"{payload.detection_summary}"
            ),
        )

    def generateExercise(
        self, payload: ExerciseGenerationInput
    ) -> ExerciseGenerationResult:
        return ExerciseGenerationResult(
            title=f"Practice improving {payload.issue_label}",
            description=(
                "Refactor the selected region to address the documented issue without "
                "changing behavior."
            ),
            difficulty="Medium",
        )

    def generateHints(self, payload: HintGenerationInput) -> HintGenerationResult:
        hints = {
            1: f"Start by isolating the part of the code that shows the {payload.issue_label} smell.",
            2: "Extract one cohesive responsibility first, then reassess whether the main flow reads more clearly.",
        }
        return HintGenerationResult(hint=hints[payload.hint_level])
