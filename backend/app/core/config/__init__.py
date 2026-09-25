import os

from app.core.config.development import DevelopmentSettings
from app.core.config.production import ProductionSettings

environment = os.getenv("APP_ENV", "development").lower()

if environment == "production":
    settings = ProductionSettings()
elif environment == "development":
    settings = DevelopmentSettings()
else:
    raise ValueError(
        f"Unknown APP_ENV: {environment!r}. "
        "Expected 'development' or 'production'."
    )
    
