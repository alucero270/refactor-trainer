import pytest
from pydantic import ValidationError

from app.providers.contracts import ProviderFailure, ProviderHealth


def test_provider_health_accepts_ready_state_without_failure():
    health = ProviderHealth(
        provider="mock",
        status="ready",
        available=True,
        message="Mock provider is ready.",
    )

    assert health.failure is None


def test_provider_health_requires_failure_details_when_unavailable():
    with pytest.raises(ValidationError, match="unavailable providers must include failure details"):
        ProviderHealth(
            provider="ollama",
            status="unavailable",
            available=False,
            message="Unavailable",
        )


def test_provider_health_rejects_failure_details_for_ready_state():
    with pytest.raises(ValidationError, match="ready providers must not include failure details"):
        ProviderHealth(
            provider="mock",
            status="ready",
            available=True,
            message="Ready",
            failure=ProviderFailure(code="unexpected", detail="No failure expected."),
        )
