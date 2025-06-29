"""
Configuration settings for LysoData-Miner Backend
=================================================
Centralized configuration management using Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    APP_NAME: str = "LysoData-Miner"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Database settings (matching existing lysobacter database)
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5434, description="PostgreSQL port")
    POSTGRES_USER: str = Field(default="lysobacter_user", description="PostgreSQL user")
    POSTGRES_PASSWORD: str = Field(default="lysobacter_password", description="PostgreSQL password")
    POSTGRES_DB: str = Field(default="lysobacter_db", description="PostgreSQL database name")
    POSTGRES_SCHEMA: str = Field(default="lysobacter", description="PostgreSQL schema")
    
    # Connection settings
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout seconds")
    
    # CORS settings for frontend integration
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://89.169.171.236:3000,http://89.169.171.236:8000",
        description="Allowed CORS origins (comma-separated)"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # API settings
    API_RATE_LIMIT: int = Field(default=1000, description="API rate limit per minute")
    MAX_RESULTS_PER_PAGE: int = Field(default=100, description="Maximum results per page")
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="Default page size")
    
    # Search and identification settings
    DEFAULT_IDENTIFICATION_LIMIT: int = Field(default=50, description="Default number of identification results")
    MAX_IDENTIFICATION_LIMIT: int = Field(default=200, description="Maximum identification results")
    DEFAULT_TOLERANCE: int = Field(default=2, description="Default tolerance for strain identification")
    
    # Cache settings (for future Redis integration)
    CACHE_TTL: int = Field(default=300, description="Cache TTL in seconds")
    ENABLE_CACHING: bool = Field(default=False, description="Enable Redis caching")
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    RELOAD: bool = Field(default=True, description="Auto-reload on code changes")
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def async_database_url(self) -> str:
        """Construct async PostgreSQL connection URL"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    def get_database_url(self, async_driver: bool = True) -> str:
        """Get database URL with optional async driver"""
        return self.async_database_url if async_driver else self.database_url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Use localhost for development
    POSTGRES_HOST: str = "localhost"


class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Use docker service name for production
    POSTGRES_HOST: str = "postgres"
    
    # Production CORS origins
    ALLOWED_ORIGINS: str = "https://lysodata-miner.com,https://www.lysodata-miner.com"


class TestingSettings(Settings):
    """Testing environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Use test database
    POSTGRES_DB: str = "lysobacter_test_db"
    
    # Disable caching for tests
    ENABLE_CACHING: bool = False


def get_settings() -> Settings:
    """Get settings based on environment"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Export the configured settings
settings = get_settings() 