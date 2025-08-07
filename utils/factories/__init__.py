"""
Factories connection factory module.

Provides connection factories for various external services, including:
- Database factory: MySQL connection management
- Vector database factory: Milvus connection management
- Embedding model factory: Embedding model management
"""

from .database import DatabaseFactory
from .embedding import EmbeddingFactory
from .milvus import MilvusFactory

__all__ = [
    # Database factory
    "DatabaseFactory",

    # Embedding model factory
    "EmbeddingFactory",

    # Vector database factory
    "MilvusFactory",
]