from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings / Настройки базы данных
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # API settings / Настройки API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # Scrapy settings / Настройки Scrapy
    SCRAPY_LOG_LEVEL: str = "INFO"
    SCRAPY_FEED_EXPORT_ENCODING: str = "utf-8"

    class Config:
        env_file = ".env"

settings = Settings() 