"""
Configuration Management for Brain-Inspired AI Framework
Centralized settings and environment management.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }
    """Application settings"""
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=4, description="Number of worker processes")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./brain_ai.db",
        description="Database connection URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # AI & LLM Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", description="OpenAI model name")
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
    )
    
    # Memory System Configuration
    MEMORY_RETENTION_DAYS: int = Field(default=365, description="Memory retention period in days")
    MEMORY_MAX_SIZE: int = Field(default=100000, description="Maximum memory items")
    MEMORY_SIMILARITY_THRESHOLD: float = Field(
        default=0.7,
        description="Similarity threshold for memory retrieval"
    )
    
    # Learning Configuration
    LEARNING_RATE: float = Field(default=0.01, description="Learning rate for memory updates")
    MIN_ACTIVATION_STRENGTH: float = Field(
        default=0.1,
        description="Minimum strength for memory activation"
    )
    FORGETTING_RATE: float = Field(default=0.001, description="Rate of memory forgetting")
    
    # Reasoning Configuration
    REASONING_TIMEOUT: int = Field(default=30, description="Reasoning timeout in seconds")
    MAX_REASONING_TOKENS: int = Field(default=2000, description="Maximum tokens for reasoning")
    
    # Vector Store Configuration
    VECTOR_COLLECTION_NAME: str = Field(
        default="brain_ai_memories",
        description="Vector collection name for ChromaDB"
    )
    VECTOR_DISTANCE_METRIC: str = Field(
        default="cosine",
        description="Distance metric for vector similarity"
    )
    
    # Monitoring Configuration
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    METRICS_PORT: int = Field(default=9090, description="Metrics port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = Field(
        default=100,
        description="Maximum concurrent API requests"
    )
    REQUEST_TIMEOUT: int = Field(default=60, description="Request timeout in seconds")
    BATCH_SIZE: int = Field(default=32, description="Batch processing size")
    
    # Security Configuration
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for security"
    )
    API_KEY_REQUIRED: bool = Field(default=False, description="Require API key for access")
    

# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings (useful for testing)"""
    global _settings
    _settings = None
    return get_settings()