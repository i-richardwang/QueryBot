"""
Utils Module - Clean Layered Architecture

Layered Architecture:
- utils.core.*        : Core infrastructure (configuration, constants, error handling, logging)
- utils.factories.*   : Connection factories (database, vector database, embedding models)
- utils.services.*    : Business services (LLM services, vector services)

Usage Guidelines:
- Import only the most core configuration and factory classes from utils root directory
- Import detailed functionality from specific layers to maintain code clarity and maintainability

Examples:
    # Core configuration and factory classes
    from utils import settings, DatabaseFactory, EmbeddingFactory, MilvusFactory

    # Detailed functionality
    from utils.core.logging_config import get_logger
    from utils.services.llm import init_language_model
    from utils.core.error_handler import ProcessingError
"""

# Only expose the most core APIs - configuration and factory classes
from .core.config import settings
from .factories.database import DatabaseFactory
from .factories.embedding import EmbeddingFactory
from .factories.milvus import MilvusFactory

# Version information
__version__ = "3.0.0"

# Public core APIs
__all__ = [
    "settings",
    "DatabaseFactory", 
    "EmbeddingFactory",
    "MilvusFactory",
]