import threading
from dataclasses import dataclass, field

from app.schemas.api import ProviderConfig
from app.storage.provider_config import load_provider_config


@dataclass
class AppState:
    provider_config: ProviderConfig = field(default_factory=load_provider_config)
    submissions: dict = field(default_factory=dict)
    exercises: dict = field(default_factory=dict)
    lock: threading.RLock = field(default_factory=threading.RLock, repr=False, compare=False)


app_state = AppState()
