import pytest

from app.providers.anthropic import AnthropicProvider
from app.providers.mcp import McpProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai_provider import OpenAIProvider


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
    assert provider.healthCheck()["provider"] == expected_name
    assert provider.classifyCandidate({"candidate": "x"})["result"] == "stub"
    assert provider.generateExercise({"candidate": "x"})["result"] == "stub"
    assert provider.generateHints({"exercise": "x"})["result"] == "stub"

