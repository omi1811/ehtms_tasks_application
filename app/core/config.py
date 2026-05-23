from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """Application settings - loaded from .env or environment variables."""

    # Application
    PROJECT_NAME: str = "EHTMS"
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS - Pydantic auto-parses JSON strings from env vars for List[str]
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Database - REQUIRED (no default = must be set in .env or env vars)
    DATABASE_URL: str
    
    # Security - REQUIRED
    SECRET_KEY: str
    
    # Optional with safe defaults
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 5
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",              # Load .env file
        env_file_encoding="utf-8",    # Encoding
        case_sensitive=False,         # Env vars are case-insensitive
        extra="ignore"                # Ignore unknown env vars (safe for deployment)
    )

# Create singleton instance
settings = Settings()