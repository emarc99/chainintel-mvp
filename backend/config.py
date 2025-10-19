"""
Configuration module for ChainIntel Backend
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # DIMO API Configuration
    dimo_client_id: Optional[str] = None
    dimo_domain: Optional[str] = None
    dimo_api_key: Optional[str] = None
    dimo_environment: str = "Production"

    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
