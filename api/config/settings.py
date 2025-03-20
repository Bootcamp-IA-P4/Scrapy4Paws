from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic_settings import BaseSettings
from pydantic import validator, SecretStr
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr  # Используем SecretStr для безопасного хранения пароля
    
    @validator('DB_PORT')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('DB_HOST')
    def validate_host(cls, v):
        if not v:
            raise ValueError('Host cannot be empty')
        return v
    
    @validator('DB_NAME')
    def validate_db_name(cls, v):
        if not v:
            raise ValueError('Database name cannot be empty')
        return v
    
    @validator('DB_USER')
    def validate_user(cls, v):
        if not v:
            raise ValueError('Database user cannot be empty')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Database settings
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD.get_secret_value()}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 