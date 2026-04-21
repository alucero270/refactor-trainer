import json
from urllib import error as urllib_error

import pytest

from app.providers import anthropic as anthropic_module
from app.providers.anthropic import AnthropicProvider
from app.providers.contracts import (
    CandidateClassificationInput,
    ExerciseGenerationInput,
    HintGenerationInput,
)
from app.schemas.api import ProviderConfig
from app.storage.memory import app_state


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


@pytest.fixture(autouse=True)
def restore_provider_config():
    original = app_state.provider_config.model_copy(deep=True)
    try:
        yield
    finally:
        app_state.provider_config = original


def configure_anthropic() -> None:
    app_state.provider_config = ProviderConfig(
        default_provider="anthropic",
        configured_providers=["ollama", "anthropic"],
        providers={
            "anthropic": {
                "api_key": "test-anthropic-key",
                "model": "claude-test",
                "base_url": "https://anthropic.test/v1",
            }
        },
    )


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


def tool_response(name: str, payload: dict) -> dict:
    return {
        "content": [
            {
                "type": "tool_use",
                "name": name,
                "input": payload,
            }
        ]
    }


def test_anthropic_health_reports_ready_with_byok_config(monkeypatch):
    configure_anthropic()
    provider = AnthropicProvider()

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://anthropic.test/v1/models"
        assert request.headers["X-api-key"] == "test-anthropic-key"
        assert request.headers["Anthropic-version"] == "2023-06-01"
        return FakeResponse({"data": [{"id": "claude-test"}]})

    monkeypatch.setattr(anthropic_module.urllib_request, "urlopen", fake_urlopen)

    health = provider.healthCheck()

    assert health.status == "ready"
    assert health.available is True
    assert health.failure is None
    assert "claude-test" in health.message


def test_anthropic_health_reports_missing_api_key_without_secret_leakage():
    provider = AnthropicProvider()

    health = provider.healthCheck()

    assert health.status == "unavailable"
    assert health.available is False
    assert health.failure is not None
    assert health.failure.code == "missing_api_key"
    assert "test-anthropic-key" not in health.model_dump_json()


def test_anthropic_generation_uses_schema_bound_tool_outputs(monkeypatch):
    configure_anthropic()
    provider = AnthropicProvider()
    generate_responses = iter(
        [
            tool_response(
                "candidate_classification",
                {
                    "label": "ExtractMethod",
                    "rationale": "The code mixes concerns.",
                },
            ),
            tool_response(
                "exercise_generation",
                {
                    "title": "Split the responsibilities",
                    "description": "Extract one cohesive helper without changing behavior.",
                    "difficulty": "Medium",
                },
            ),
            tool_response(
                "hint_generation",
                {
                    "hint": "Start by isolating the branch that handles one distinct responsibility.",
                },
            ),
        ]
    )
    tool_names: list[str] = []

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://anthropic.test/v1/messages"
        body = json.loads(request.data.decode("utf-8"))
        tool = body["tools"][0]
        tool_names.append(tool["name"])
        assert body["model"] == "claude-test"
        assert body["max_tokens"] == 1024
        assert body["tool_choice"] == {"type": "tool", "name": tool["name"]}
        assert tool["input_schema"]["additionalProperties"] is False
        return FakeResponse(next(generate_responses))

    monkeypatch.setattr(anthropic_module.urllib_request, "urlopen", fake_urlopen)

    classification = provider.classifyCandidate(make_classification_input())
    exercise = provider.generateExercise(make_exercise_input())
    hint = provider.generateHints(make_hint_input())

    assert classification.label == "ExtractMethod"
    assert classification.rationale == "The code mixes concerns."
    assert exercise.title == "Split the responsibilities"
    assert exercise.difficulty == "Medium"
    assert "distinct responsibility" in hint.hint
    assert tool_names == [
        "candidate_classification",
        "exercise_generation",
        "hint_generation",
    ]


def test_anthropic_generation_rejects_missing_tool_output(monkeypatch):
    configure_anthropic()
    provider = AnthropicProvider()

    def fake_urlopen(request, timeout):
        return FakeResponse({"content": [{"type": "text", "text": "{}"}]})

    monkeypatch.setattr(anthropic_module.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(anthropic_module.AnthropicProviderError, match="tool output"):
        provider.generateHints(make_hint_input())


def test_anthropic_http_errors_do_not_include_api_key(monkeypatch):
    configure_anthropic()
    provider = AnthropicProvider()

    def fake_urlopen(request, timeout):
        raise urllib_error.HTTPError(
            request.full_url,
            401,
            "Unauthorized",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(anthropic_module.urllib_request, "urlopen", fake_urlopen)

    health = provider.healthCheck()

    assert health.status == "unavailable"
    assert health.failure is not None
    assert health.failure.code == "authentication_failed"
    assert "test-anthropic-key" not in health.model_dump_json()
