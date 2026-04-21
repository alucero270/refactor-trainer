import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.api import ProviderConfig
from app.storage.provider_config import PROVIDER_CONFIG_PATH_ENV
from app.storage.memory import app_state


@pytest.fixture
def provider_config_path(tmp_path, monkeypatch):
    path = tmp_path / "provider-config.json"
    monkeypatch.setenv(PROVIDER_CONFIG_PATH_ENV, str(path))
    return path


@pytest.fixture(autouse=True)
def reset_app_state(provider_config_path) -> None:
    app_state.provider_config = ProviderConfig()
    app_state.submissions.clear()
    app_state.exercises.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
