from pydantic_settings import SettingsConfigDict

from .base import BaseAppSettings


class ProductionSettings(BaseAppSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
    )