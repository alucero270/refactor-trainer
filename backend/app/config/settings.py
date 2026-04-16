from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Refactor Trainer"
    environment: str = "development"
    default_provider: str = "ollama"


@lru_cache
def get_settings() -> Settings:
    return Settings()

