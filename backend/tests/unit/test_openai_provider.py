import json
from urllib import error as urllib_error

import pytest

from app.providers import openai_provider as openai_module
from app.providers.contracts import (
    CandidateClassificationInput,
    ExerciseGenerationInput,
    HintGenerationInput,
)
from app.providers.openai_provider import OpenAIProvider
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


def configure_openai() -> None:
    app_state.provider_config = ProviderConfig(
        default_provider="openai",
        configured_providers=["ollama", "openai"],
        providers={
            "openai": {
                "api_key": "test-openai-key",
                "model": "gpt-test",
                "base_url": "https://openai.test/v1",
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


def test_openai_health_reports_ready_with_byok_config(monkeypatch):
    configure_openai()
    provider = OpenAIProvider()

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://openai.test/v1/models/gpt-test"
        assert request.headers["Authorization"] == "Bearer test-openai-key"
        return FakeResponse({"id": "gpt-test"})

    monkeypatch.setattr(openai_module.urllib_request, "urlopen", fake_urlopen)

    health = provider.healthCheck()

    assert health.status == "ready"
    assert health.available is True
    assert health.failure is None
    assert "gpt-test" in health.message


def test_openai_health_reports_missing_api_key_without_secret_leakage():
    provider = OpenAIProvider()

    health = provider.healthCheck()

    assert health.status == "unavailable"
    assert health.available is False
    assert health.failure is not None
    assert health.failure.code == "missing_api_key"
    assert "test-openai-key" not in health.model_dump_json()


def test_openai_generation_uses_schema_bound_responses(monkeypatch):
    configure_openai()
    provider = OpenAIProvider()
    generate_responses = iter(
        [
            {
                "output": [
                    {
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "label": "ExtractMethod",
                                        "rationale": "The code mixes concerns.",
                                    }
                                ),
                            }
                        ]
                    }
                ]
            },
            {
                "output_text": json.dumps(
                    {
                        "title": "Split the responsibilities",
                        "description": "Extract one cohesive helper without changing behavior.",
                        "difficulty": "Medium",
                    }
                )
            },
            {
                "output_text": json.dumps(
                    {
                        "hint": "Start by isolating the branch that handles one distinct responsibility.",
                    }
                )
            },
        ]
    )
    schema_names: list[str] = []

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://openai.test/v1/responses"
        body = json.loads(request.data.decode("utf-8"))
        schema_format = body["text"]["format"]
        schema_names.append(schema_format["name"])
        assert body["model"] == "gpt-test"
        assert body["store"] is False
        assert schema_format["type"] == "json_schema"
        assert schema_format["strict"] is True
        assert schema_format["schema"]["additionalProperties"] is False
        return FakeResponse(next(generate_responses))

    monkeypatch.setattr(openai_module.urllib_request, "urlopen", fake_urlopen)

    classification = provider.classifyCandidate(make_classification_input())
    exercise = provider.generateExercise(make_exercise_input())
    hint = provider.generateHints(make_hint_input())

    assert classification.label == "ExtractMethod"
    assert classification.rationale == "The code mixes concerns."
    assert exercise.title == "Split the responsibilities"
    assert exercise.difficulty == "Medium"
    assert "distinct responsibility" in hint.hint
    assert schema_names == [
        "candidate_classification",
        "exercise_generation",
        "hint_generation",
    ]


def test_openai_generation_rejects_invalid_json(monkeypatch):
    configure_openai()
    provider = OpenAIProvider()

    def fake_urlopen(request, timeout):
        return FakeResponse({"output_text": "not-json"})

    monkeypatch.setattr(openai_module.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(openai_module.OpenAIProviderError, match="valid JSON"):
        provider.generateHints(make_hint_input())


def test_openai_http_errors_do_not_include_api_key(monkeypatch):
    configure_openai()
    provider = OpenAIProvider()

    def fake_urlopen(request, timeout):
        raise urllib_error.HTTPError(
            request.full_url,
            401,
            "Unauthorized",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(openai_module.urllib_request, "urlopen", fake_urlopen)

    health = provider.healthCheck()

    assert health.status == "unavailable"
    assert health.failure is not None
    assert health.failure.code == "authentication_failed"
    assert "test-openai-key" not in health.model_dump_json()
