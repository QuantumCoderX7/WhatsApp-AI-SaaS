import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate root .env path (4 levels up from backend/app/core/config.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "WhatsApp AI SaaS Platform"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    
    # Security & Tokens
    SECRET_KEY: str = "dev_secret_key_change_me_in_production_super_secure_32_bytes_min"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    ALGORITHM: str = "HS256"
    
    # Database (Default to SQLite fallback if Postgres is unavailable locally)
    DATABASE_URL: str = "sqlite+aiosqlite:///./whatsapp_saas.db"
    SYNC_DATABASE_URL: str = "sqlite:///./whatsapp_saas.db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_SSL: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Google Gemini AI Studio
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    
    # Meta WhatsApp API
    META_ACCESS_TOKEN: str = ""          # Reads temporary or permanent System User token from .env
    META_PHONE_NUMBER_ID: str = ""
    META_WABA_ID: str = ""
    META_VERIFY_TOKEN: str = "whatsapp_ai_verify_token_dev"
    META_APP_ID: str = ""
    META_APP_SECRET: str = "meta_app_secret"
    META_API_VERSION: str = "v23.0"
    META_BUSINESS_PHONE_NUMBER: Optional[str] = None
    
    # Supabase Storage
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_STORAGE_BUCKET: str = "knowledge-documents"

    # ngrok
    NGROK_AUTHTOKEN: Optional[str] = None
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "https://*.vercel.app"]

    model_config = SettingsConfigDict(
        env_file=ENV_PATH if os.path.exists(ENV_PATH) else ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
