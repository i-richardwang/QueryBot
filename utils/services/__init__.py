"""
Services business service module.

Provides high-level business services, including:
- LLM service: Language model initialization and call chain management
"""

from .llm import init_language_model, LanguageModelChain, create_llm_chain
from .milvus_service import (
    create_milvus_collection,
    insert_to_milvus,
    update_milvus_records,
    search_in_milvus,
    asearch_in_milvus,
    get_collection_stats
)

__all__ = [
    # LLM service
    "init_language_model",
    "LanguageModelChain",
    "create_llm_chain",

    # Milvus vector database service
    "create_milvus_collection",
    "insert_to_milvus",
    "update_milvus_records",
    "search_in_milvus",
    "asearch_in_milvus",
    "get_collection_stats",
]