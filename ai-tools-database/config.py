import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List

# Load credentials from .env.local if it exists
env_local_path = Path.home() / ".env.local"
if env_local_path.exists():
    print("Loading credentials from .env.local...")
    with open(env_local_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://username:password@localhost:5432/ai_tools_db"

    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False

    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Logging
    log_level: str = "INFO"

    # Development Settings
    reload: bool = True
    workers: int = 1

    # Database Pool Settings
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    # CORS Settings
    allowed_origins: str = "*"

    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Cache Settings
    redis_url: Optional[str] = None
    cache_ttl: int = 3600

    # Monitoring
    sentry_dsn: Optional[str] = None
    metrics_enabled: bool = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse allowed origins from string to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()