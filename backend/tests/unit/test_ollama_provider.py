import json

import pytest

from app.providers import ollama as ollama_module
from app.providers.contracts import (
    CandidateClassificationInput,
    ExerciseGenerationInput,
    HintGenerationInput,
)
from app.providers.ollama import OllamaProvider
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


def test_ollama_health_reports_ready_with_available_model(monkeypatch):
    provider = OllamaProvider()

    def fake_urlopen(request, timeout):
        assert request.full_url == "http://localhost:11434/api/tags"
        return FakeResponse({"models": [{"name": "llama3.2:latest"}]})

    monkeypatch.setattr(ollama_module.urllib_request, "urlopen", fake_urlopen)

    health = provider.healthCheck()

    assert health.status == "ready"
    assert health.available is True
    assert health.failure is None
    assert "llama3.2:latest" in health.message


def test_ollama_health_reports_missing_configured_model(monkeypatch):
    provider = OllamaProvider()
    app_state.provider_config = ProviderConfig(
        providers={"ollama": {"model": "codellama:7b"}},
    )

    def fake_urlopen(request, timeout):
        return FakeResponse({"models": [{"name": "llama3.2:latest"}]})

    monkeypatch.setattr(ollama_module.urllib_request, "urlopen", fake_urlopen)

    health = provider.healthCheck()

    assert health.status == "unavailable"
    assert health.available is False
    assert health.failure is not None
    assert health.failure.code == "model_not_found"


def test_ollama_generation_uses_shared_contract_shapes(monkeypatch):
    provider = OllamaProvider()
    app_state.provider_config = ProviderConfig(
        providers={"ollama": {"model": "llama3.2:latest"}},
    )
    generate_responses = iter(
        [
            {"response": json.dumps({"label": "ExtractMethod", "rationale": "The code mixes concerns."})},
            {
                "response": json.dumps(
                    {
                        "title": "Split the responsibilities",
                        "description": "Extract one cohesive helper without changing behavior.",
                        "difficulty": "Medium",
                    }
                )
            },
            {
                "response": json.dumps(
                    {
                        "hint": "Start by isolating the branch that handles one distinct responsibility.",
                    }
                )
            },
        ]
    )
    captured_models: list[str] = []

    def fake_urlopen(request, timeout):
        if request.full_url.endswith("/api/tags"):
            return FakeResponse({"models": [{"name": "llama3.2:latest"}]})

        body = json.loads(request.data.decode("utf-8"))
        captured_models.append(body["model"])
        assert body["stream"] is False
        assert body["format"] == "json"
        return FakeResponse(next(generate_responses))

    monkeypatch.setattr(ollama_module.urllib_request, "urlopen", fake_urlopen)

    classification = provider.classifyCandidate(make_classification_input())
    exercise = provider.generateExercise(make_exercise_input())
    hint = provider.generateHints(make_hint_input())

    assert classification.label == "ExtractMethod"
    assert classification.rationale == "The code mixes concerns."
    assert exercise.title == "Split the responsibilities"
    assert exercise.difficulty == "Medium"
    assert "distinct responsibility" in hint.hint
    assert captured_models == ["llama3.2:latest", "llama3.2:latest", "llama3.2:latest"]
