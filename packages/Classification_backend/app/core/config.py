from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 30
    POOL_TIMEOUT: int = 30
    OCR_CLASSIFICATION_ENDPOINT: str = ""
    DEBUG: bool = False
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_LOCATION: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


    #  ADD INDEXES IN TABLES