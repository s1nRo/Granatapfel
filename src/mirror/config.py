from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

filepath = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    GITHUB_TOKEN: str = "abc"

    model_config = SettingsConfigDict(env_file = filepath / ".env", extra="ignore")

settings = Settings()