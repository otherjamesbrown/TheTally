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
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://thetally_user:password@localhost:5432/thetally_dev"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "thetally_dev"
    DATABASE_USER: str = "thetally_user"
    DATABASE_PASSWORD: str = "password"
    
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
    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 2FA
    OTP_ISSUER: str = "TheTally"
    OTP_SECRET_LENGTH: int = 32
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["csv", "ofx", "qif"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
