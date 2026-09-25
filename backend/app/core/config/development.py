
from pydantic_settings import SettingsConfigDict

from app.core.config.base import BASE_DIR, BaseAppSettings


class DevelopmentSettings(BaseAppSettings):
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR/".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )