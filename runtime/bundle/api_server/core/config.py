"""
UPID CLI API Server Configuration
Enterprise-grade configuration management with environment variable support
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="UPID_HOST")
    port: int = Field(default=8000, env="UPID_PORT")
    debug: bool = Field(default=True, env="UPID_DEBUG")
    workers: int = Field(default=4, env="UPID_WORKERS")
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./upid.db", 
        env="UPID_DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="UPID_DATABASE_ECHO")
    
    # Authentication Configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="UPID_SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(
        default=30, 
        env="UPID_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    algorithm: str = Field(default="HS256", env="UPID_ALGORITHM")
    
    # External API Configuration
    kubernetes_config_path: Optional[str] = Field(
        default=None,
        env="UPID_KUBERNETES_CONFIG_PATH"
    )
    
    # Cloud Provider Configuration
    aws_region: str = Field(default="us-west-2", env="AWS_REGION")
    gcp_project_id: Optional[str] = Field(default=None, env="GCP_PROJECT_ID")
    azure_subscription_id: Optional[str] = Field(default=None, env="AZURE_SUBSCRIPTION_ID")
    
    # ML Configuration
    models_path: str = Field(
        default="./models",
        env="UPID_MODELS_PATH"
    )
    ml_batch_size: int = Field(default=1000, env="UPID_ML_BATCH_SIZE")
    ml_prediction_threshold: float = Field(
        default=0.85,
        env="UPID_ML_PREDICTION_THRESHOLD"
    )
    
    # Monitoring Configuration  
    metrics_enabled: bool = Field(default=True, env="UPID_METRICS_ENABLED")
    log_level: str = Field(default="INFO", env="UPID_LOG_LEVEL")
    
    # Security Configuration
    cors_origins: List[str] = Field(
        default=["*"],
        env="UPID_CORS_ORIGINS"
    )
    rate_limit_per_minute: int = Field(
        default=100,
        env="UPID_RATE_LIMIT_PER_MINUTE"
    )
    
    # Feature Flags
    enable_ml_predictions: bool = Field(
        default=True,
        env="UPID_ENABLE_ML_PREDICTIONS"
    )
    enable_cost_optimization: bool = Field(
        default=True,
        env="UPID_ENABLE_COST_OPTIMIZATION"
    )
    enable_zero_pod_scaling: bool = Field(
        default=True,
        env="UPID_ENABLE_ZERO_POD_SCALING"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Environment-specific configurations
def get_production_settings() -> Settings:
    """Production environment settings"""
    settings = get_settings()
    settings.debug = False
    settings.database_echo = False
    settings.log_level = "WARNING"
    return settings


def get_development_settings() -> Settings:
    """Development environment settings"""  
    settings = get_settings()
    settings.debug = True
    settings.database_echo = True
    settings.log_level = "DEBUG"
    return settings


def get_test_settings() -> Settings:
    """Test environment settings"""
    settings = get_settings()
    settings.database_url = "sqlite:///./test.db"
    settings.debug = True
    settings.access_token_expire_minutes = 1
    return settings