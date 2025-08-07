"""
Unified configuration management module.

Type-safe configuration management based on Pydantic Settings.
Streamlined configuration system optimized for demo projects.
"""

import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


def get_project_root() -> str:
    """Get project root directory path."""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Search upward for directory containing pyproject.toml
    while current_dir != os.path.dirname(current_dir):
        config_path = os.path.join(current_dir, 'pyproject.toml')
        if os.path.exists(config_path):
            return current_dir
        current_dir = os.path.dirname(current_dir)

    # If not found, return parent directory of utils as default
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_env_file_path() -> str:
    """Get .env file path."""
    project_root = get_project_root()
    env_file = os.path.join(project_root, '.env')
    return env_file



class DatabaseConfig(BaseSettings):
    """Database configuration."""

    # Option 1: Use complete database URL (recommended for cloud databases)
    url: Optional[str] = Field(default=None, description="Complete database URL (e.g., postgresql://user:pass@host:port/db)")

    # Option 2: Individual connection parameters (fallback for local databases)
    type: str = Field(default="mysql", description="Database type (mysql or postgresql)")
    host: str = Field(default="localhost", description="Database host address")
    port: int = Field(default=3306, description="Database port")
    user: str = Field(default="root", description="Database username")
    password: str = Field(default="", description="Database password")
    name: str = Field(default="sql_assistant", description="Database name")

    class Config:
        env_prefix = "SQLBOT_DB_"
        case_sensitive = False


class VectorDBConfig(BaseSettings):
    """Vector database configuration."""

    # Option 1: Complete URI (recommended for Zilliz Cloud)
    uri: Optional[str] = Field(default=None, description="Complete Milvus/Zilliz Cloud URI")
    token: Optional[str] = Field(default=None, description="Authentication token (for Zilliz Cloud)")

    # Option 2: Individual connection parameters (for local Milvus)
    host: str = Field(default="localhost", description="Milvus host address")
    port: int = Field(default=19530, description="Milvus port")
    username: Optional[str] = Field(default=None, description="Milvus username")
    password: Optional[str] = Field(default=None, description="Milvus password")
    database: str = Field(default="default", description="Milvus database name")

    class Config:
        env_prefix = "VECTOR_DB_"
        case_sensitive = False


class LLMConfig(BaseSettings):
    """LLM configuration."""

    model: str = Field(
        default="Qwen/Qwen2.5-72B-Instruct",
        description="LLM model name"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="LLM API key"
    )
    api_base: str = Field(
        default="https://api.siliconflow.cn/v1",
        description="LLM API base URL"
    )

    class Config:
        env_prefix = "LLM_"
        case_sensitive = False


class EmbeddingConfig(BaseSettings):
    """Embedding model configuration."""

    api_key: str = Field(..., description="Embedding model API key")
    api_base: str = Field(
        default="https://api.siliconflow.cn/v1/embeddings",
        description="Embedding model API base URL"
    )
    model: str = Field(default="bge-large-zh", description="Embedding model name")

    class Config:
        env_prefix = "EMBEDDING_"
        case_sensitive = False


class MonitoringConfig(BaseSettings):
    """Monitoring configuration."""

    langfuse_enabled: bool = Field(default=False, description="Whether to enable Langfuse")
    langfuse_public_key: Optional[str] = Field(default=None, description="Langfuse public key")
    langfuse_secret_key: Optional[str] = Field(default=None, description="Langfuse secret key")
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        description="Langfuse host address"
    )
    phoenix_enabled: bool = Field(default=False, description="Whether to enable Phoenix")

    class Config:
        env_prefix = ""
        case_sensitive = False

    @field_validator('langfuse_public_key')
    @classmethod
    def validate_langfuse_public_key(cls, v, info):
        if info.data.get('langfuse_enabled') and not v:
            raise ValueError('Public key must be provided when Langfuse is enabled')
        return v

    @field_validator('langfuse_secret_key')
    @classmethod
    def validate_langfuse_secret_key(cls, v, info):
        if info.data.get('langfuse_enabled') and not v:
            raise ValueError('Secret key must be provided when Langfuse is enabled')
        return v


class AppConfig(BaseSettings):
    """Application configuration."""

    base_host: str = Field(default="localhost", description="Base host address")
    user_auth_enabled: bool = Field(default=False, description="Whether to enable user authentication")
    debug: bool = Field(default=False, description="Whether to enable debug mode")
    frontend_direct_call: bool = Field(default=False, description="Enable frontend direct call to backend")

    class Config:
        env_prefix = ""
        case_sensitive = False


class Settings(BaseSettings):
    """Main configuration class."""

    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    class Config:
        env_file = get_env_file_path()
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def get_database_url(self) -> str:
        """Get database connection URL."""
        # Priority 1: Use complete URL if provided
        if self.database.url:
            # Convert generic postgresql:// to postgresql+psycopg2:// for SQLAlchemy
            url = self.database.url
            if url.startswith('postgresql://'):
                url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)
            elif url.startswith('mysql://'):
                url = url.replace('mysql://', 'mysql+pymysql://', 1)
            return url

        # Priority 2: Build URL from individual components
        db_type = self.database.type.lower()

        if db_type == 'postgresql':
            return (
                f"postgresql+psycopg2://"
                f"{self.database.user}:{self.database.password}@"
                f"{self.database.host}:{self.database.port}/"
                f"{self.database.name}"
            )
        elif db_type == 'mysql':
            return (
                f"mysql+pymysql://"
                f"{self.database.user}:{self.database.password}@"
                f"{self.database.host}:{self.database.port}/"
                f"{self.database.name}"
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def get_llm_api_key(self) -> str:
        """Get LLM API key."""
        return self.llm.api_key

    def get_llm_api_base(self) -> str:
        """Get LLM API base URL."""
        return self.llm.api_base


@lru_cache()
def get_settings() -> Settings:
    """Get global configuration instance."""
    env_file_path = get_env_file_path()

    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('\'"')
                    os.environ[key] = value

    return Settings()


# Global configuration instance
settings = get_settings()


