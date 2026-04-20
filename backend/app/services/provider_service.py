from collections.abc import Sequence

from app.providers.base import ModelProvider
from app.providers.registry import build_provider_registry
from app.schemas.api import ProviderHealthResponse, ProviderListResponse
from app.storage.memory import app_state


class ProviderService:
    def __init__(self, providers: Sequence[ModelProvider] | None = None) -> None:
        self.providers = list(providers) if providers is not None else build_provider_registry()

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
            providers=[provider.healthCheck().model_dump() for provider in self.providers]
        )

    def resolve_default_provider(self) -> ModelProvider:
        if len(self.providers) == 1:
            return self.providers[0]

        default_provider = app_state.provider_config.default_provider
        for provider in self.providers:
            if provider.name() == default_provider:
                return provider

        raise RuntimeError(f"Configured provider '{default_provider}' is not available.")
