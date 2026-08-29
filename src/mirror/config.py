from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    CONFIG_PATH: Path = PROJECT_ROOT / "config.yaml"

    GITHUB_TOKEN: str = "abc"

    S3_URL: str = "http://192.168.1.100:9000"
    KEY_S3: str | None = None
    TOKEN_S3: str | None = None
    VERSION_S3: str = "s3v4"
    BUCKET_NAME: str = "pomoyka"
    LOG_LEVEL: str = "INFO"
    ATTEMPTS: int = 3
    USERNAME_API: str | None = None
    PASSWORD_API: str | None = None
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


settings = Settings()
