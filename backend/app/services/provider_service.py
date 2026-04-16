from app.providers.registry import build_provider_registry
from app.schemas.api import ProviderHealthResponse, ProviderListResponse


class ProviderService:
    def __init__(self) -> None:
        self.providers = build_provider_registry()

    def list_providers(self) -> ProviderListResponse:
        return ProviderListResponse(
            providers=[
                {
                    "name": provider.name(),
                    "kind": provider.kind,
                    "supports_local": provider.supports_local,
                }
                for provider in self.providers
            ]
        )

    def health(self) -> ProviderHealthResponse:
        return ProviderHealthResponse(
            providers=[provider.healthCheck() for provider in self.providers]
        )

