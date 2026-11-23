"""
Application Configuration using pydantic-settings.
All secrets and environment variables are strictly loaded from environment or .env.
"""

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment & Deployment
    ENVIRONMENT: str = "development"

    # Core Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./cat2026.db"

    # Security & Encryption
    MASTER_ENCRYPTION_KEY: str = "dGVzdF9tYXN0ZXJfa2V5XzMyX2J5dGVzX2xvbmdfMTIzNDU="  # 32 bytes base64 for dev
    JWT_SECRET_KEY: str = "cat2026_default_jwt_secret_must_be_changed_in_prod_32char"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SESSION_EXPIRE_MINUTES: int = 120

    # Uploads
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Google Gemini AI Provider
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Optional Supabase integration
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""


settings = Settings()
