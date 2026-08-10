from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    browserbase_api_key: str = ""
    testing_mode: bool = True

    @property
    def max_personas(self) -> int:
        return 2 if self.testing_mode else 22

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache()
def get_settings():
    return Settings()
