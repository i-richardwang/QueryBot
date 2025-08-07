"""
Streamlit Cloud configuration adapter module
Supports dual configuration: local .env files and Streamlit Cloud secrets.toml
"""

import os
import streamlit as st
from typing import Optional, Dict, Any
from functools import lru_cache

from .config import Settings, get_env_file_path


def load_streamlit_secrets() -> Dict[str, Any]:
    """
    Load Streamlit secrets with support for nested configuration structure
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    secrets = {}
    
    # Try to get configuration from st.secrets
    if hasattr(st, 'secrets'):
        try:
            # Application basic configuration
            if 'app' in st.secrets:
                secrets.update({
                    'BASE_HOST': st.secrets.app.get('base_host', 'localhost'),
                    'USER_AUTH_ENABLED': st.secrets.app.get('user_auth_enabled', False),
                    'DEBUG': st.secrets.app.get('debug', False),
                    'FRONTEND_DIRECT_CALL': st.secrets.app.get('frontend_direct_call', True),  # Cloud default direct call
                })
            
            # Database configuration
            if 'database' in st.secrets:
                db_config = st.secrets.database
                secrets.update({
                    'SQLBOT_DB_URL': db_config.get('url'),
                    'SQLBOT_DB_TYPE': db_config.get('type', 'mysql'),
                    'SQLBOT_DB_HOST': db_config.get('host', 'localhost'),
                    'SQLBOT_DB_PORT': db_config.get('port', 3306),
                    'SQLBOT_DB_USER': db_config.get('user', 'root'),
                    'SQLBOT_DB_PASSWORD': db_config.get('password', ''),
                    'SQLBOT_DB_NAME': db_config.get('name', 'sql_assistant'),
                })
            
            # Vector database configuration
            if 'vector_db' in st.secrets:
                vector_config = st.secrets.vector_db
                secrets.update({
                    'VECTOR_DB_URI': vector_config.get('uri'),
                    'VECTOR_DB_TOKEN': vector_config.get('token'),
                    'VECTOR_DB_HOST': vector_config.get('host', 'localhost'),
                    'VECTOR_DB_PORT': vector_config.get('port', 19530),
                    'VECTOR_DB_USERNAME': vector_config.get('username'),
                    'VECTOR_DB_PASSWORD': vector_config.get('password'),
                    'VECTOR_DB_DATABASE': vector_config.get('database', 'default'),
                })
            
            # LLM configuration
            if 'llm' in st.secrets:
                llm_config = st.secrets.llm
                secrets.update({
                    'LLM_MODEL': llm_config.get('model', 'Qwen/Qwen2.5-72B-Instruct'),
                    'LLM_API_KEY': llm_config.get('api_key'),
                    'LLM_API_BASE': llm_config.get('api_base', 'https://api.siliconflow.cn/v1'),
                })
            
            # Embedding model configuration
            if 'embedding' in st.secrets:
                embedding_config = st.secrets.embedding
                secrets.update({
                    'EMBEDDING_API_KEY': embedding_config.get('api_key'),
                    'EMBEDDING_API_BASE': embedding_config.get('api_base', 'https://api.siliconflow.cn/v1'),
                    'EMBEDDING_MODEL': embedding_config.get('model', 'bge-large-zh'),
                })
            
            # Monitoring configuration
            if 'monitoring' in st.secrets:
                monitoring_config = st.secrets.monitoring
                secrets.update({
                    'LANGFUSE_ENABLED': monitoring_config.get('langfuse_enabled', False),
                    'LANGFUSE_PUBLIC_KEY': monitoring_config.get('langfuse_public_key'),
                    'LANGFUSE_SECRET_KEY': monitoring_config.get('langfuse_secret_key'),
                    'LANGFUSE_HOST': monitoring_config.get('langfuse_host', 'https://cloud.langfuse.com'),
                    'PHOENIX_ENABLED': monitoring_config.get('phoenix_enabled', False),
                })
                
        except Exception as e:
            # Use default configuration when Streamlit secrets loading fails
            print(f"Warning: Failed to load Streamlit secrets: {e}")
    
    return secrets


def setup_environment_for_streamlit():
    """
    Setup environment variables for Streamlit Cloud
    Priority: Streamlit Secrets > Environment Variables > Default Values
    """
    # First try to load Streamlit secrets
    streamlit_secrets = load_streamlit_secrets()
    
    # Set secrets to environment variables
    for key, value in streamlit_secrets.items():
        if value is not None:  # Only set non-empty values
            os.environ[key] = str(value)
    
    print(f"Loaded {len(streamlit_secrets)} configuration items from Streamlit secrets")


@lru_cache()
def get_streamlit_settings() -> Settings:
    """
    Get configuration instance adapted for Streamlit Cloud
    
    Returns:
        Settings: Configuration instance
    """
    # Setup Streamlit Cloud environment variables
    setup_environment_for_streamlit()
    
    # Create configuration instance (will use updated environment variables)
    return Settings()


def is_streamlit_cloud() -> bool:
    """
    Detect if running in Streamlit Cloud environment
    
    Returns:
        bool: Whether running in Streamlit Cloud environment
    """
    # Streamlit Cloud specific environment variables
    streamlit_cloud_indicators = [
        'STREAMLIT_SHARING_MODE',
        'STREAMLIT_SERVER_HEADLESS',
        '_STREAMLIT_INTERNAL_APP_CONFIG_OPTION_BROWSER.GATHER_USAGE_STATS'
    ]
    
    # Check if Streamlit Cloud environment indicators exist
    return any(os.getenv(indicator) for indicator in streamlit_cloud_indicators) or hasattr(st, 'secrets')


def get_demo_settings() -> Settings:
    """
    Get demo-friendly configuration
    Automatically detect runtime environment and apply appropriate configuration
    
    Returns:
        Settings: Configuration instance suitable for current environment
    """
    if is_streamlit_cloud():
        # Running on Streamlit Cloud
        print("Running on Streamlit Cloud - using secrets configuration")
        return get_streamlit_settings()
    else:
        # Local development environment
        print("Running locally - using .env configuration")
        from .config import settings
        return settings


# Convenient global configuration instance (automatically adapts to environment)
settings = get_demo_settings()