"""
Application configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "TheTally"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")  # nosec B104
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://thetally_user:dev_password@localhost:5432/thetally_dev")  # nosec B105
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "thetally_dev")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "thetally_user")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "dev_password")  # nosec B105
    
    # GCP Database Configuration
    GCP_PROJECT_ID: str = ""
    GCP_REGION: str = "us-central1"
    GCP_DATABASE_INSTANCE: str = "thetally-postgres"
    GCP_DATABASE_VERSION: str = "POSTGRES_15"
    GCP_DATABASE_TIER: str = "db-f1-micro"
    GCP_DATABASE_SSL_MODE: str = "require"
    
    # Database Connection Pool
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")  # nosec B105
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")  # nosec B105
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 2FA
    OTP_ISSUER: str = "TheTally"
    OTP_SECRET_LENGTH: int = 32
    
    # Project
    PROJECT_NAME: str = "TheTally"
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["csv", "ofx", "qif"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
