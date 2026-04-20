import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.api import ProviderConfig
from app.storage.memory import app_state


@pytest.fixture(autouse=True)
def reset_app_state() -> None:
    app_state.provider_config = ProviderConfig()
    app_state.submissions.clear()
    app_state.exercises.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
