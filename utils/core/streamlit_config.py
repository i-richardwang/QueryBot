"""
Streamlit Cloud configuration adapter module
Supports dual configuration: local .env files and Streamlit Cloud secrets.toml
"""

import os
import streamlit as st
from typing import Optional, Dict, Any
from collections.abc import Mapping
from functools import lru_cache

from .config import Settings, get_env_file_path


def _get_first_present(d: Any, keys: list, default: Any = None) -> Any:
    """Return the first non-None value for any key in keys from mapping-like or attribute-like object d."""
    for k in keys:
        val = None
        try:
            if isinstance(d, Mapping):
                if k in d:
                    # Prefer mapping access
                    val = d.get(k) if hasattr(d, 'get') else d[k]
            else:
                # Fallback to attribute access
                if hasattr(d, k):
                    val = getattr(d, k)
        except Exception:
            val = None
        if val is not None:
            return val
    return default


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
            # Application basic configuration (support both lower and UPPER keys)
            if ('app' in st.secrets) or hasattr(st.secrets, 'app'):
                app_cfg = st.secrets["app"] if isinstance(st.secrets, Mapping) else st.secrets.app
                secrets.update({
                    'BASE_HOST': _get_first_present(app_cfg, ['base_host', 'BASE_HOST'], 'localhost'),
                    'USER_AUTH_ENABLED': _get_first_present(app_cfg, ['user_auth_enabled', 'USER_AUTH_ENABLED'], False),
                    'DEBUG': _get_first_present(app_cfg, ['debug', 'DEBUG'], False),
                    'FRONTEND_DIRECT_CALL': _get_first_present(app_cfg, ['frontend_direct_call', 'FRONTEND_DIRECT_CALL'], True),
                })
            
            # Database configuration (support lower keys and pre-namespaced UPPER keys)
            if ('database' in st.secrets) or hasattr(st.secrets, 'database'):
                db_cfg = st.secrets["database"] if isinstance(st.secrets, Mapping) else st.secrets.database
                secrets.update({
                    'SQLBOT_DB_URL': _get_first_present(db_cfg, ['url', 'SQLBOT_DB_URL']),
                    'SQLBOT_DB_TYPE': _get_first_present(db_cfg, ['type', 'SQLBOT_DB_TYPE'], 'mysql'),
                    'SQLBOT_DB_HOST': _get_first_present(db_cfg, ['host', 'SQLBOT_DB_HOST'], 'localhost'),
                    'SQLBOT_DB_PORT': _get_first_present(db_cfg, ['port', 'SQLBOT_DB_PORT'], 3306),
                    'SQLBOT_DB_USER': _get_first_present(db_cfg, ['user', 'SQLBOT_DB_USER'], 'root'),
                    'SQLBOT_DB_PASSWORD': _get_first_present(db_cfg, ['password', 'SQLBOT_DB_PASSWORD'], ''),
                    'SQLBOT_DB_NAME': _get_first_present(db_cfg, ['name', 'SQLBOT_DB_NAME'], 'sql_assistant'),
                })
            
            # Vector database configuration (support lower and UPPER keys)
            if ('vector_db' in st.secrets) or hasattr(st.secrets, 'vector_db'):
                v_cfg = st.secrets["vector_db"] if isinstance(st.secrets, Mapping) else st.secrets.vector_db
                secrets.update({
                    'VECTOR_DB_URI': _get_first_present(v_cfg, ['uri', 'VECTOR_DB_URI']),
                    'VECTOR_DB_TOKEN': _get_first_present(v_cfg, ['token', 'VECTOR_DB_TOKEN']),
                    'VECTOR_DB_HOST': _get_first_present(v_cfg, ['host', 'VECTOR_DB_HOST'], 'localhost'),
                    'VECTOR_DB_PORT': _get_first_present(v_cfg, ['port', 'VECTOR_DB_PORT'], 19530),
                    'VECTOR_DB_USERNAME': _get_first_present(v_cfg, ['username', 'VECTOR_DB_USERNAME']),
                    'VECTOR_DB_PASSWORD': _get_first_present(v_cfg, ['password', 'VECTOR_DB_PASSWORD']),
                    'VECTOR_DB_DATABASE': _get_first_present(v_cfg, ['database', 'VECTOR_DB_DATABASE'], 'default'),
                })
            
            # LLM configuration (support lower and UPPER keys within [llm])
            if ('llm' in st.secrets) or hasattr(st.secrets, 'llm'):
                llm_cfg = st.secrets["llm"] if isinstance(st.secrets, Mapping) else st.secrets.llm
                secrets.update({
                    'LLM_MODEL': _get_first_present(llm_cfg, ['model', 'LLM_MODEL'], 'Qwen/Qwen2.5-72B-Instruct'),
                    'LLM_API_KEY': _get_first_present(llm_cfg, ['api_key', 'LLM_API_KEY']),
                    'LLM_API_BASE': _get_first_present(llm_cfg, ['api_base', 'LLM_API_BASE'], 'https://api.siliconflow.cn/v1'),
                })
            
            # Embedding model configuration (support lower and UPPER keys)
            if ('embedding' in st.secrets) or hasattr(st.secrets, 'embedding'):
                e_cfg = st.secrets["embedding"] if isinstance(st.secrets, Mapping) else st.secrets.embedding
                secrets.update({
                    'EMBEDDING_API_KEY': _get_first_present(e_cfg, ['api_key', 'EMBEDDING_API_KEY']),
                    'EMBEDDING_API_BASE': _get_first_present(e_cfg, ['api_base', 'EMBEDDING_API_BASE'], 'https://api.siliconflow.cn/v1'),
                    'EMBEDDING_MODEL': _get_first_present(e_cfg, ['model', 'EMBEDDING_MODEL'], 'bge-large-zh'),
                })
            
            # Monitoring configuration (support lower and UPPER keys)
            if ('monitoring' in st.secrets) or hasattr(st.secrets, 'monitoring'):
                m_cfg = st.secrets["monitoring"] if isinstance(st.secrets, Mapping) else st.secrets.monitoring
                secrets.update({
                    'LANGFUSE_ENABLED': _get_first_present(m_cfg, ['langfuse_enabled', 'LANGFUSE_ENABLED'], False),
                    'LANGFUSE_PUBLIC_KEY': _get_first_present(m_cfg, ['langfuse_public_key', 'LANGFUSE_PUBLIC_KEY']),
                    'LANGFUSE_SECRET_KEY': _get_first_present(m_cfg, ['langfuse_secret_key', 'LANGFUSE_SECRET_KEY']),
                    'LANGFUSE_HOST': _get_first_present(m_cfg, ['langfuse_host', 'LANGFUSE_HOST'], 'https://cloud.langfuse.com'),
                    'PHOENIX_ENABLED': _get_first_present(m_cfg, ['phoenix_enabled', 'PHOENIX_ENABLED'], False),
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