import json

import pytest

from app.providers import mcp as mcp_module
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
from app.providers.mcp import McpProvider
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


@pytest.fixture
def mcp_provider() -> ModelProvider:
    app_state.provider_config = ProviderConfig(
        default_provider="mcp",
        configured_providers=["ollama", "mcp"],
        providers={"mcp": {"server_url": "http://localhost:8001/mcp"}},
    )
    return McpProvider()


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


def install_contract_fake_server(monkeypatch) -> None:
    required_tools = McpProvider._required_tools()
    outputs = {
        McpProvider.classify_tool: {
            "label": "LongMethod",
            "rationale": "The candidate has too much responsibility.",
        },
        McpProvider.exercise_tool: {
            "title": "Extract a cohesive helper",
            "description": "Refactor one responsibility boundary without changing behavior.",
            "difficulty": "Medium",
        },
        McpProvider.hint_tool: {
            "hint": "Look for the smallest responsibility boundary before editing.",
        },
    }

    def fake_urlopen(request, timeout):
        body = json.loads(request.data.decode("utf-8"))
        method = body["method"]
        if method == "tools/list":
            result = {"tools": [{"name": tool} for tool in sorted(required_tools)]}
        else:
            result = {"structuredContent": outputs[body["params"]["name"]]}

        return FakeResponse({"jsonrpc": "2.0", "id": body["id"], "result": result})

    monkeypatch.setattr(mcp_module.urllib_request, "urlopen", fake_urlopen)


def test_mcp_provider_satisfies_health_contract(mcp_provider, monkeypatch):
    install_contract_fake_server(monkeypatch)

    health = mcp_provider.healthCheck()

    assert isinstance(health, ProviderHealth)
    assert health.provider == "mcp"
    assert health.status == "ready"
    assert health.available is True
    assert health.failure is None


def test_mcp_provider_satisfies_generation_contracts(mcp_provider, monkeypatch):
    install_contract_fake_server(monkeypatch)

    classification = mcp_provider.classifyCandidate(make_classification_input())
    exercise = mcp_provider.generateExercise(make_exercise_input())
    hint = mcp_provider.generateHints(make_hint_input())

    assert isinstance(classification, CandidateClassificationResult)
    assert classification.label == "LongMethod"
    assert classification.rationale
    assert isinstance(exercise, ExerciseGenerationResult)
    assert exercise.title == "Extract a cohesive helper"
    assert exercise.difficulty == "Medium"
    assert isinstance(hint, HintGenerationResult)
    assert "responsibility boundary" in hint.hint
