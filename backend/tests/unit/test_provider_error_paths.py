"""Negative-path tests for remote providers.

These tests verify that malformed responses, HTTP errors, and missing fields
surface the correct typed error instead of leaking stack traces or returning
partial results. They complement the happy-path tests by exercising the
error branches the fake clients in the other test files do not reach.
"""
import json
from urllib import error as urllib_error

import pytest

from app.providers import anthropic as anthropic_module
from app.providers import openai_provider as openai_module
from app.providers.anthropic import AnthropicProvider, AnthropicProviderError
from app.providers.contracts import CandidateClassificationInput
from app.providers.openai_provider import OpenAIProvider, OpenAIProviderError
from app.schemas.api import ProviderConfig
from app.storage.memory import app_state


class _StreamResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> "_StreamResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return self.body


@pytest.fixture(autouse=True)
def restore_provider_config():
    original = app_state.provider_config.model_copy(deep=True)
    try:
        yield
    finally:
        app_state.provider_config = original


def _configure_openai() -> None:
    app_state.provider_config = ProviderConfig(
        default_provider="openai",
        configured_providers=["ollama", "openai"],
        providers={
            "openai": {"api_key": "k", "model": "gpt-test", "base_url": "https://openai.test/v1"}
        },
    )


def _configure_anthropic() -> None:
    app_state.provider_config = ProviderConfig(
        default_provider="anthropic",
        configured_providers=["ollama", "anthropic"],
        providers={
            "anthropic": {
                "api_key": "k",
                "model": "claude-test",
                "base_url": "https://anthropic.test/v1",
            }
        },
    )


def _classification_payload() -> CandidateClassificationInput:
    return CandidateClassificationInput(
        language="python",
        candidate_code="def f(): pass\n",
        candidate_region={"start_line": 1, "end_line": 1},
        detection_summary="stub",
        heuristic_label="PoorNaming",
        guidance_snippets=[],
    )


def test_openai_missing_api_key_raises_typed_error():
    app_state.provider_config = ProviderConfig()  # no openai configured

    with pytest.raises(OpenAIProviderError) as excinfo:
        OpenAIProvider().classifyCandidate(_classification_payload())

    assert excinfo.value.code == "missing_api_key"


def test_openai_surfaces_authentication_failure_from_401(monkeypatch):
    _configure_openai()

    def fake_urlopen(*args, **kwargs):
        raise urllib_error.HTTPError(
            url="https://openai.test/v1/responses",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(openai_module.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(OpenAIProviderError) as excinfo:
        OpenAIProvider().classifyCandidate(_classification_payload())

    assert excinfo.value.code == "authentication_failed"


def test_openai_reports_model_not_found_on_health_check_404(monkeypatch):
    _configure_openai()

    def fake_urlopen(*args, **kwargs):
        raise urllib_error.HTTPError(
            url="https://openai.test/v1/models/gpt-test",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(openai_module.urllib_request, "urlopen", fake_urlopen)

    health = OpenAIProvider().healthCheck()

    assert health.available is False
    assert health.failure is not None
    assert health.failure.code == "model_not_found"


def test_openai_rejects_malformed_output_without_text(monkeypatch):
    _configure_openai()

    def fake_urlopen(*args, **kwargs):
        return _StreamResponse(json.dumps({"output_text": "   ", "output": []}).encode("utf-8"))

    monkeypatch.setattr(openai_module.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(OpenAIProviderError) as excinfo:
        OpenAIProvider().classifyCandidate(_classification_payload())

    assert excinfo.value.code == "invalid_response"


def test_openai_rejects_non_json_text_output(monkeypatch):
    _configure_openai()

    def fake_urlopen(*args, **kwargs):
        return _StreamResponse(json.dumps({"output_text": "not-json"}).encode("utf-8"))

    monkeypatch.setattr(openai_module.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(OpenAIProviderError) as excinfo:
        OpenAIProvider().classifyCandidate(_classification_payload())

    assert excinfo.value.code == "invalid_response"


def test_anthropic_missing_api_key_raises_typed_error():
    app_state.provider_config = ProviderConfig()  # no anthropic configured

    with pytest.raises(AnthropicProviderError) as excinfo:
        AnthropicProvider().classifyCandidate(_classification_payload())

    assert excinfo.value.code == "missing_api_key"


def test_anthropic_rejects_tool_use_with_wrong_name(monkeypatch):
    _configure_anthropic()

    payload = {
        "content": [
            {
                "type": "tool_use",
                "name": "some_other_tool",
                "input": {"label": "PoorNaming", "rationale": "ok"},
            }
        ]
    }

    def fake_urlopen(*args, **kwargs):
        return _StreamResponse(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(anthropic_module.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(AnthropicProviderError) as excinfo:
        AnthropicProvider().classifyCandidate(_classification_payload())

    assert excinfo.value.code == "invalid_response"


def test_anthropic_rejects_response_without_content_blocks(monkeypatch):
    _configure_anthropic()

    def fake_urlopen(*args, **kwargs):
        return _StreamResponse(json.dumps({"content": None}).encode("utf-8"))

    monkeypatch.setattr(anthropic_module.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(AnthropicProviderError) as excinfo:
        AnthropicProvider().classifyCandidate(_classification_payload())

    assert excinfo.value.code == "invalid_response"


def test_anthropic_health_check_reports_connection_error(monkeypatch):
    _configure_anthropic()

    def fake_urlopen(*args, **kwargs):
        raise urllib_error.URLError("offline")

    monkeypatch.setattr(anthropic_module.urllib_request, "urlopen", fake_urlopen)

    health = AnthropicProvider().healthCheck()

    assert health.available is False
    assert health.failure is not None
    assert health.failure.code == "connection_error"
