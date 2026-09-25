
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[3]

class BaseAppSettings(BaseSettings):
    database_url: str

    icloud_username: str | None = None
    icloud_password: str | None = None

    outlook_username: str | None = None
    outlook_password: str | None = None

    application_id: str | None = None
    client_secret: str | None = None
    

