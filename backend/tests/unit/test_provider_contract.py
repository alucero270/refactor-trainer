import pytest

from app.providers.anthropic import AnthropicProvider
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
from app.providers.mcp import McpProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai_provider import OpenAIProvider


def make_classification_input() -> CandidateClassificationInput:
    return CandidateClassificationInput(
        language="python",
        candidate_code="def example():\n    return 1\n",
        candidate_region="lines 1-2",
        heuristic_label="LongMethod",
        detection_summary="Function mixes responsibilities.",
        guidance_snippets=["Keep the contract provider-agnostic."],
    )


def make_exercise_input() -> ExerciseGenerationInput:
    return ExerciseGenerationInput(
        language="python",
        candidate_code="def example():\n    return 1\n",
        candidate_region="lines 1-2",
        issue_label="LongMethod",
        classification_rationale="The function mixes concerns.",
        guidance_snippets=["Describe the goal without giving the answer."],
    )


def make_hint_input() -> HintGenerationInput:
    return HintGenerationInput(
        language="python",
        exercise_title="Improve readability",
        exercise_description="Reduce responsibility overlap.",
        hint_level=1,
        candidate_code="def example():\n    return 1\n",
        issue_label="LongMethod",
        guidance_snippets=["Hints must stay progressive."],
    )


def test_model_provider_contract_is_abstract():
    assert ModelProvider.__abstractmethods__ == {
        "name",
        "healthCheck",
        "classifyCandidate",
        "generateExercise",
        "generateHints",
    }


@pytest.mark.parametrize(
    "provider_cls,expected_name",
    [
        (OllamaProvider, "ollama"),
        (OpenAIProvider, "openai"),
        (AnthropicProvider, "anthropic"),
        (McpProvider, "mcp"),
    ],
)
def test_provider_contract(provider_cls, expected_name):
    provider = provider_cls()

    assert provider.name() == expected_name
    assert provider.healthCheck() == ProviderHealth(
        provider=expected_name,
        status="unavailable",
        available=False,
        message=provider.healthCheck().message,
        failure=ProviderFailure(
            code="not_implemented",
            detail=provider.healthCheck().failure.detail,
        ),
    )

    classification = provider.classifyCandidate(make_classification_input())
    assert isinstance(classification, CandidateClassificationResult)
    assert classification.label == "LongMethod"
    assert classification.rationale

    exercise = provider.generateExercise(make_exercise_input())
    assert isinstance(exercise, ExerciseGenerationResult)
    assert exercise.title == "Refactor LongMethod"
    assert exercise.difficulty == "Medium"

    hint = provider.generateHints(make_hint_input())
    assert isinstance(hint, HintGenerationResult)
    assert "level 1" in hint.hint
