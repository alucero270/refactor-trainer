import json
import os
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.schemas.api import ProviderConfig


PROVIDER_CONFIG_PATH_ENV = "REFACTOR_TRAINER_PROVIDER_CONFIG_PATH"
DEFAULT_PROVIDER_CONFIG_PATH = Path.home() / ".refactor-trainer" / "provider-config.json"


class ProviderConfigStorageError(RuntimeError):
    pass


def provider_config_path() -> Path:
    configured_path = os.environ.get(PROVIDER_CONFIG_PATH_ENV)
    if configured_path and configured_path.strip():
        return Path(configured_path).expanduser()
    return DEFAULT_PROVIDER_CONFIG_PATH


def load_provider_config(path: Path | None = None) -> ProviderConfig:
    target_path = path or provider_config_path()
    if not target_path.exists():
        return ProviderConfig()

    try:
        payload = json.loads(target_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderConfigStorageError(
            "Stored provider configuration could not be read."
        ) from exc

    try:
        return ProviderConfig.model_validate(payload)
    except ValidationError as exc:
        raise ProviderConfigStorageError(
            "Stored provider configuration is invalid."
        ) from exc


def save_provider_config(config: ProviderConfig, path: Path | None = None) -> None:
    target_path = path or provider_config_path()
    payload = _serializable_config(config)
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    temp_path = target_path.with_suffix(f"{target_path.suffix}.tmp")

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_text(encoded, encoding="utf-8")
        _restrict_owner_access(temp_path)
        temp_path.replace(target_path)
    except OSError as exc:
        raise ProviderConfigStorageError(
            "Provider configuration could not be saved locally."
        ) from exc


def _serializable_config(config: ProviderConfig) -> dict[str, Any]:
    payload = config.model_dump(mode="json")
    providers = payload["providers"]
    providers["openai"]["api_key"] = _secret_value(config.providers.openai.api_key)
    providers["anthropic"]["api_key"] = _secret_value(config.providers.anthropic.api_key)
    return payload


def _secret_value(secret) -> str | None:
    if secret is None:
        return None
    return secret.get_secret_value()


def _restrict_owner_access(path: Path) -> None:
    try:
        path.chmod(0o600)
    except OSError:
        return
