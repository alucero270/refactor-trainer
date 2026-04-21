import json

import pytest

from app.providers import mcp as mcp_module
from app.providers.contracts import (
    CandidateClassificationInput,
    ExerciseGenerationInput,
    HintGenerationInput,
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


def configure_mcp() -> None:
    app_state.provider_config = ProviderConfig(
        default_provider="mcp",
        configured_providers=["ollama", "mcp"],
        providers={"mcp": {"server_url": "http://localhost:8001/mcp"}},
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


def json_rpc_response(request: dict, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request["id"], "result": result}


def test_mcp_health_reports_ready_when_required_tools_exist(monkeypatch):
    configure_mcp()
    provider = McpProvider()

    def fake_urlopen(request, timeout):
        assert request.full_url == "http://localhost:8001/mcp"
        assert request.headers["Mcp-method"] == "tools/list"
        body = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            json_rpc_response(
                body,
                {
                    "tools": [
                        {"name": provider.classify_tool},
                        {"name": provider.exercise_tool},
                        {"name": provider.hint_tool},
                    ]
                },
            )
        )

    monkeypatch.setattr(mcp_module.urllib_request, "urlopen", fake_urlopen)

    health = provider.healthCheck()

    assert health.status == "ready"
    assert health.available is True
    assert health.failure is None


def test_mcp_health_reports_missing_required_tools(monkeypatch):
    configure_mcp()
    provider = McpProvider()

    def fake_urlopen(request, timeout):
        body = json.loads(request.data.decode("utf-8"))
        return FakeResponse(json_rpc_response(body, {"tools": [{"name": provider.classify_tool}]}))

    monkeypatch.setattr(mcp_module.urllib_request, "urlopen", fake_urlopen)

    health = provider.healthCheck()

    assert health.status == "unavailable"
    assert health.available is False
    assert health.failure is not None
    assert health.failure.code == "missing_tools"
    assert provider.exercise_tool in health.failure.detail
    assert provider.hint_tool in health.failure.detail


def test_mcp_generation_uses_schema_bound_tool_calls(monkeypatch):
    configure_mcp()
    provider = McpProvider()
    tool_results = {
        provider.classify_tool: {
            "label": "ExtractMethod",
            "rationale": "The code mixes concerns.",
        },
        provider.exercise_tool: {
            "title": "Split the responsibilities",
            "description": "Extract one cohesive helper without changing behavior.",
            "difficulty": "Medium",
        },
        provider.hint_tool: {
            "hint": "Start by isolating the branch that handles one distinct responsibility.",
        },
    }
    called_tools: list[str] = []

    def fake_urlopen(request, timeout):
        assert request.headers["Mcp-method"] == "tools/call"
        body = json.loads(request.data.decode("utf-8"))
        tool_name = body["params"]["name"]
        called_tools.append(tool_name)
        assert request.headers["Mcp-name"] == tool_name
        arguments = body["params"]["arguments"]
        assert "input" in arguments
        assert arguments["output_schema"]["additionalProperties"] is False
        return FakeResponse(
            json_rpc_response(
                body,
                {
                    "structuredContent": tool_results[tool_name],
                    "content": [{"type": "text", "text": json.dumps(tool_results[tool_name])}],
                },
            )
        )

    monkeypatch.setattr(mcp_module.urllib_request, "urlopen", fake_urlopen)

    classification = provider.classifyCandidate(make_classification_input())
    exercise = provider.generateExercise(make_exercise_input())
    hint = provider.generateHints(make_hint_input())

    assert classification.label == "ExtractMethod"
    assert classification.rationale == "The code mixes concerns."
    assert exercise.title == "Split the responsibilities"
    assert exercise.difficulty == "Medium"
    assert "distinct responsibility" in hint.hint
    assert called_tools == [
        provider.classify_tool,
        provider.exercise_tool,
        provider.hint_tool,
    ]


def test_mcp_generation_accepts_text_json_tool_content(monkeypatch):
    configure_mcp()
    provider = McpProvider()

    def fake_urlopen(request, timeout):
        body = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            json_rpc_response(
                body,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"hint": "Look for one responsibility boundary."}),
                        }
                    ]
                },
            )
        )

    monkeypatch.setattr(mcp_module.urllib_request, "urlopen", fake_urlopen)

    hint = provider.generateHints(make_hint_input())

    assert hint.hint == "Look for one responsibility boundary."


def test_mcp_generation_rejects_invalid_text_json_tool_content(monkeypatch):
    configure_mcp()
    provider = McpProvider()

    def fake_urlopen(request, timeout):
        body = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            json_rpc_response(body, {"content": [{"type": "text", "text": "not-json"}]})
        )

    monkeypatch.setattr(mcp_module.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(mcp_module.McpProviderError, match="valid JSON"):
        provider.generateHints(make_hint_input())
