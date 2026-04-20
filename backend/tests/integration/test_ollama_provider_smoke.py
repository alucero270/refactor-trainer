import json

import pytest

from app.providers import ollama as ollama_module
from app.providers.base import ModelProvider
from app.providers.contracts import ExerciseGenerationInput
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


def test_ollama_provider_smoke(monkeypatch):
    provider: ModelProvider = OllamaProvider()
    app_state.provider_config = ProviderConfig(
        providers={"ollama": {"model": "llama3.2:latest"}},
    )
    exercise_input = ExerciseGenerationInput(
        language="python",
        candidate_code="def render(items):\n    return [item.name for item in items]\n",
        candidate_region="lines 1-2",
        issue_label="LongMethod",
        classification_rationale="The function mixes formatting and traversal concerns.",
        guidance_snippets=["Do not reveal the final refactoring."],
    )
    request_paths: list[str] = []

    def fake_urlopen(request, timeout):
        request_paths.append(request.full_url)
        if request.full_url.endswith("/api/tags"):
            return FakeResponse({"models": [{"name": "llama3.2:latest"}]})

        return FakeResponse(
            {
                "response": json.dumps(
                    {
                        "title": "Separate traversal from presentation",
                        "description": "Extract the formatting responsibility into one helper without changing behavior.",
                        "difficulty": "Medium",
                    }
                )
            }
        )

    monkeypatch.setattr(ollama_module.urllib_request, "urlopen", fake_urlopen)

    health = provider.healthCheck()
    exercise = provider.generateExercise(exercise_input)

    assert health.status == "ready"
    assert health.available is True
    assert "llama3.2:latest" in health.message
    assert exercise.title == "Separate traversal from presentation"
    assert exercise.difficulty == "Medium"
    assert request_paths == [
        "http://localhost:11434/api/tags",
        "http://localhost:11434/api/tags",
        "http://localhost:11434/api/generate",
    ]
