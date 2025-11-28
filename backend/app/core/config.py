"""
Core configuration for FastAPI backend
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    app_name: str = "News Spectrum API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Supabase
    supabase_url: str
    supabase_service_role_key: str
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://newsspectrum.vercel.app",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 추가 환경변수 무시


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
