import json

import pytest

from app.schemas.api import ProviderConfig
from app.storage.provider_config import (
    ProviderConfigStorageError,
    load_provider_config,
    save_provider_config,
)


def test_provider_config_storage_returns_default_when_file_is_missing(tmp_path):
    config = load_provider_config(tmp_path / "missing-provider-config.json")

    assert config == ProviderConfig()


def test_provider_config_storage_round_trips_byok_without_response_leakage(tmp_path):
    path = tmp_path / "nested" / "provider-config.json"
    config = ProviderConfig(
        default_provider="openai",
        configured_providers=["ollama", "openai", "anthropic"],
        providers={
            "openai": {
                "api_key": "stored-openai-key",
                "model": "gpt-test",
            },
            "anthropic": {
                "api_key": "stored-anthropic-key",
                "model": "claude-test",
            },
        },
    )

    save_provider_config(config, path)
    loaded = load_provider_config(path)

    assert loaded.providers.openai.api_key is not None
    assert loaded.providers.openai.api_key.get_secret_value() == "stored-openai-key"
    assert loaded.providers.anthropic.api_key is not None
    assert loaded.providers.anthropic.api_key.get_secret_value() == "stored-anthropic-key"
    assert "stored-openai-key" not in loaded.model_dump_json()
    assert "stored-anthropic-key" not in loaded.model_dump_json()


def test_provider_config_storage_writes_local_json_with_secret_fields(tmp_path):
    path = tmp_path / "provider-config.json"
    config = ProviderConfig(
        default_provider="openai",
        configured_providers=["ollama", "openai"],
        providers={"openai": {"api_key": "local-openai-key"}},
    )

    save_provider_config(config, path)

    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["default_provider"] == "openai"
    assert stored["providers"]["openai"]["api_key"] == "local-openai-key"


def test_provider_config_storage_rejects_invalid_json_without_payload_leakage(tmp_path):
    path = tmp_path / "provider-config.json"
    path.write_text("{not valid json with local-openai-key", encoding="utf-8")

    with pytest.raises(ProviderConfigStorageError) as exc_info:
        load_provider_config(path)

    assert str(exc_info.value) == "Stored provider configuration could not be read."
    assert "local-openai-key" not in str(exc_info.value)


def test_provider_config_storage_rejects_invalid_config_without_secret_leakage(tmp_path):
    path = tmp_path / "provider-config.json"
    path.write_text(
        json.dumps(
            {
                "default_provider": "openai",
                "configured_providers": ["ollama", "openai"],
                "providers": {"openai": {"api_key": ""}},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ProviderConfigStorageError) as exc_info:
        load_provider_config(path)

    assert str(exc_info.value) == "Stored provider configuration is invalid."
    assert "openai" not in str(exc_info.value)
