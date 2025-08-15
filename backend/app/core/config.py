"""
Configuration management using Pydantic BaseSettings
"""

from pydantic import BaseSettings, Field
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"], env="ALLOWED_ORIGINS")
    
    # Database Settings
    NEO4J_URI: str = Field(default="neo4j://localhost:7687", env="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="password", env="NEO4J_PASSWORD")
    
    # Vector Database Settings
    MILVUS_HOST: str = Field(default="localhost", env="MILVUS_HOST")
    MILVUS_PORT: int = Field(default=19530, env="MILVUS_PORT")
    MILVUS_COLLECTION_NAME: str = Field(default="educational_content", env="MILVUS_COLLECTION_NAME")
    
    # RAG Settings
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    LLM_MODEL: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL")
    MAX_CONTEXT_LENGTH: int = Field(default=4000, env="MAX_CONTEXT_LENGTH")
    TOP_K_RETRIEVAL: int = Field(default=5, env="TOP_K_RETRIEVAL")
    
    # Content Processing
    CHUNK_SIZE: int = Field(default=512, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=50, env="CHUNK_OVERLAP")
    
    # File Storage
    UPLOAD_DIR: Path = Field(default=Path("uploads"), env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(default=[".pdf", ".txt", ".docx", ".md"], env="ALLOWED_FILE_TYPES")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # Knowledge Graph Settings
    GRAPH_STORE_PATH: Path = Field(default=Path("data/graph_store.json"), env="GRAPH_STORE_PATH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.GRAPH_STORE_PATH.parent, exist_ok=True)