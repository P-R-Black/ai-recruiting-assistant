from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    database_url: str

    icloud_username: str | None = None
    icloud_password: str | None = None

    outlook_username: str | None = None
    outlook_password: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR /".env",
        extra="ignore"
        )



settings = Settings()
