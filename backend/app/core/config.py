"""
Application configuration
"""
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Project
    PROJECT_NAME: str = "Index Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/index_platform"
    BIGQUERY_PROJECT_ID: str = ""
    BIGQUERY_DATASET: str = "index_platform"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Alternative frontend
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Allowed Hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Redis (for caching and Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # External APIs
    ALPHA_VANTAGE_API_KEY: str = ""
    YAHOO_FINANCE_API_URL: str = "https://query1.finance.yahoo.com"
    
    # Data Processing
    MAX_WORKERS: int = 4
    BATCH_SIZE: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
