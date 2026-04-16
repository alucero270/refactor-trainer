from dataclasses import dataclass, field

from app.schemas.api import ProviderConfig


@dataclass
class AppState:
    provider_config: ProviderConfig = field(default_factory=ProviderConfig)
    submissions: dict = field(default_factory=dict)
    exercises: dict = field(default_factory=dict)


app_state = AppState()

