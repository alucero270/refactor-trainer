import pytest
from pydantic import ValidationError

from app.schemas.api import ProviderConfig


def test_provider_config_defaults_to_local_first_ollama():
    config = ProviderConfig()

    assert config.default_provider == "ollama"
    assert config.configured_providers == ["ollama"]
    assert config.providers.ollama.base_url == "http://localhost:11434"


def test_provider_config_requires_default_provider_to_be_configured():
    with pytest.raises(ValidationError, match="default_provider must be included"):
        ProviderConfig(default_provider="openai", configured_providers=["ollama"])


def test_provider_config_rejects_duplicate_provider_entries():
    with pytest.raises(ValidationError, match="configured_providers must not contain duplicates"):
        ProviderConfig(configured_providers=["ollama", "ollama"])


def test_provider_config_requires_openai_key_when_configured():
    with pytest.raises(ValidationError, match="openai.api_key is required"):
        ProviderConfig(
            default_provider="openai",
            configured_providers=["ollama", "openai"],
        )


def test_provider_config_requires_anthropic_key_when_configured():
    with pytest.raises(ValidationError, match="anthropic.api_key is required"):
        ProviderConfig(
            default_provider="anthropic",
            configured_providers=["ollama", "anthropic"],
        )


def test_provider_config_requires_mcp_server_url_when_configured():
    with pytest.raises(ValidationError, match="mcp.server_url is required"):
        ProviderConfig(
            default_provider="mcp",
            configured_providers=["ollama", "mcp"],
        )


def test_provider_config_rejects_invalid_mcp_server_url_when_configured():
    with pytest.raises(ValidationError, match=r"mcp.server_url must be an absolute HTTP\(S\) URL"):
        ProviderConfig(
            default_provider="mcp",
            configured_providers=["ollama", "mcp"],
            providers={"mcp": {"server_url": "localhost:8001/mcp"}},
        )


def test_provider_config_normalizes_blank_mcp_server_url_to_missing():
    with pytest.raises(ValidationError, match="mcp.server_url is required"):
        ProviderConfig(
            default_provider="mcp",
            configured_providers=["ollama", "mcp"],
            providers={"mcp": {"server_url": "   "}},
        )


def test_provider_config_accepts_absolute_mcp_server_url():
    config = ProviderConfig(
        default_provider="mcp",
        configured_providers=["ollama", "mcp"],
        providers={"mcp": {"server_url": " https://localhost:8001/mcp "}},
    )

    assert config.providers.mcp.server_url == "https://localhost:8001/mcp"


def test_provider_config_accepts_byok_and_mcp_settings():
    config = ProviderConfig(
        default_provider="openai",
        configured_providers=["ollama", "openai", "anthropic", "mcp"],
        providers={
            "ollama": {"base_url": "http://localhost:11434"},
            "openai": {"api_key": "openai-test-key", "model": "gpt-test"},
            "anthropic": {"api_key": "anthropic-test-key"},
            "mcp": {"server_url": "http://localhost:8001/mcp"},
        },
    )

    assert config.providers.openai.api_key is not None
    assert config.providers.openai.api_key.get_secret_value() == "openai-test-key"
    assert config.providers.anthropic.api_key is not None
    assert config.providers.mcp.server_url == "http://localhost:8001/mcp"
