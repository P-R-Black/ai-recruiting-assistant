from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    database_url: str

    icloud_username: str
    icloud_password: str

    outlook_username: str
    outlook_password: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR /".env",
        extra="ignore"
        )



settings = Settings()
