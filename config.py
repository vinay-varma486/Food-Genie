import os
import json
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")),
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "FoodGenie API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "foodgenie-super-secret-production-grade-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Database (PostgreSQL URL by default, falls back to SQLite for local development)
    DATABASE_URL: str = "sqlite:///./foodgenie.db"
    
    # AI / LLM Configuration
    LLM_PROVIDER: str = "auto"  # "auto" | "openrouter" | "gemini" | "openai" | "internal"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "nvidia/nemotron-3.5-super-vl:free"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Gnani AI Cloned Voice Configuration
    GNANI_API_KEY: str = ""
    GNANI_API_KEY_ID: str = ""
    GNANI_VOICE_EMBEDDING: str = ""

    # Email Delivery & OTP Verification Configuration
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_USE_TLS: bool = True
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = ""
    OTP_EXPIRE_MINUTES: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    OTP_MAX_ATTEMPTS: int = 5
    OTP_MAX_REQUESTS_PER_HOUR: int = 5

    # Multilingual & Voice
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: Union[str, List[str]] = ["en", "te", "hi", "ta", "kn"]

    @field_validator("SUPPORTED_LANGUAGES", mode="before")
    @classmethod
    def assemble_supported_languages(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

settings = Settings()
