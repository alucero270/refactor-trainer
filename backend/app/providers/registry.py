from app.providers.anthropic import AnthropicProvider
from app.providers.mcp import McpProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai_provider import OpenAIProvider


def build_provider_registry():
    return [
        OllamaProvider(),
        OpenAIProvider(),
        AnthropicProvider(),
        McpProvider(),
    ]

