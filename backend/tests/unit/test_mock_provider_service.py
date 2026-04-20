from app.providers.mock import MockProvider
from app.services.provider_service import ProviderService


def test_provider_service_can_run_against_mock_provider():
    service = ProviderService(providers=[MockProvider()])

    provider_list = service.list_providers()
    health = service.health()

    assert provider_list.providers[0].name == "mock"
    assert provider_list.providers[0].kind == "mock"
    assert health.providers[0].provider == "mock"
    assert health.providers[0].available is True
