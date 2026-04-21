import pytest

from app.providers.anthropic import AnthropicProvider
from app.providers.base import ModelProvider
from app.providers.contracts import (
    CandidateClassificationInput,
    ExerciseGenerationInput,
    HintGenerationInput,
    ProviderFailure,
    ProviderHealth,
)
from app.providers.mcp import McpProvider
from app.providers.mock import MockProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas.api import ProviderConfig
from app.storage.memory import app_state


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


@pytest.fixture(autouse=True)
def restore_provider_config():
    original = app_state.provider_config.model_copy(deep=True)
    try:
        yield
    finally:
        app_state.provider_config = original


def test_openai_provider_contract_requires_byok_configuration():
    provider = OpenAIProvider()

    assert provider.name() == "openai"
    assert provider.healthCheck() == ProviderHealth(
        provider="openai",
        status="unavailable",
        available=False,
        message="OpenAI is unavailable.",
        failure=ProviderFailure(
            code="missing_api_key",
            detail="OpenAI API key is required for BYOK provider access.",
        ),
    )


def test_anthropic_provider_contract_requires_byok_configuration():
    provider = AnthropicProvider()

    assert provider.name() == "anthropic"
    assert provider.healthCheck() == ProviderHealth(
        provider="anthropic",
        status="unavailable",
        available=False,
        message="Anthropic is unavailable.",
        failure=ProviderFailure(
            code="missing_api_key",
            detail="Anthropic API key is required for BYOK provider access.",
        ),
    )


def test_mcp_provider_contract_requires_server_url_configuration():
    provider = McpProvider()
    app_state.provider_config = ProviderConfig()

    assert provider.name() == "mcp"
    assert provider.healthCheck() == ProviderHealth(
        provider="mcp",
        status="unavailable",
        available=False,
        message="MCP provider is unavailable.",
        failure=ProviderFailure(
            code="missing_server_url",
            detail="MCP server_url is required for provider access.",
        ),
    )


def test_mock_provider_contract_is_deterministic():
    provider = MockProvider()
    classification_input = make_classification_input()
    exercise_input = make_exercise_input()
    hint_input = make_hint_input()

    assert provider.healthCheck() == ProviderHealth(
        provider="mock",
        status="ready",
        available=True,
        message="Mock provider is ready for deterministic development flows.",
    )

    first_classification = provider.classifyCandidate(classification_input)
    second_classification = provider.classifyCandidate(classification_input)
    assert first_classification == second_classification
    assert first_classification.label == "LongMethod"

    first_exercise = provider.generateExercise(exercise_input)
    second_exercise = provider.generateExercise(exercise_input)
    assert first_exercise == second_exercise
    assert first_exercise.title == "Practice improving LongMethod"

    first_hint = provider.generateHints(hint_input)
    second_hint = provider.generateHints(hint_input)
    assert first_hint == second_hint
    assert "LongMethod" in first_hint.hint
