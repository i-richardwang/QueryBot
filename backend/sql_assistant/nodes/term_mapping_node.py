"""
Business term mapping node module.
Responsible for mapping user-input non-standard terms to standard domain terminology definitions.
"""

import os
import logging
from typing import Dict, List

from backend.sql_assistant.states.assistant_state import SQLAssistantState
# Factory class imports
from utils.factories.milvus import MilvusFactory
from utils.factories.embedding import EmbeddingFactory

# Service function imports
from utils.services.milvus_service import search_in_milvus

# Core infrastructure imports
from utils.core.config import settings

logger = logging.getLogger(__name__)


class DomainTermMapper:
    """Business domain term mapper

    Maps user-input non-standard terms to standard domain terminology definitions.
    Uses vector database for semantic similarity matching, supporting fuzzy matching and synonym handling.
    """

    def __init__(self):
        """Initialize term mapper"""
        # Create Milvus connection instance
        self.milvus_connection = MilvusFactory.create_connection(
            db_name=settings.vector_db.database,
            auto_connect=True
        )
        # Get term descriptions collection
        self.collection = self.milvus_connection.get_collection("term_descriptions")
        # Initialize embedding model
        self.embeddings = EmbeddingFactory.get_default_embeddings()

    def find_standard_terms(
        self, keywords: List[str], similarity_threshold: float = 0.9
    ) -> Dict[str, Dict[str, str]]:
        """Find standard terms and their information corresponding to keywords

        Args:
            keywords: List of keywords to be standardized
            similarity_threshold: Similarity matching threshold controlling matching strictness

        Returns:
            Dict[str, Dict[str, str]]: Mapping dictionary from keywords to standard term information
        """
        if not keywords:
            return {}

        term_mappings = {}

        for keyword in keywords:
            try:
                query_vector = self.embeddings.embed_query(keyword)

                results = search_in_milvus(
                    collection=self.collection,
                    query_vector=query_vector,
                    vector_field="original_term",
                    top_k=1,
                )

                if results and results[0]["distance"] > similarity_threshold:
                    term_mappings[keyword] = {
                        "original_term": results[0]["original_term"],
                        "standard_name": results[0]["standard_name"],
                        "additional_info": results[0]["additional_info"],
                    }

            except Exception as e:
                logger.error(f"Error processing keyword '{keyword}': {str(e)}")
                continue

        return term_mappings


def domain_term_mapping_node(state: SQLAssistantState) -> dict:
    """Domain term mapping node function

    Map extracted keywords to standard domain terms and obtain their canonical definitions.
    This step ensures subsequent processing uses unified business terminology.

    Args:
        state: Current state object

    Returns:
        dict: State update containing standardized terms and their explanations
    """
    # Get keywords list
    keywords = state.get("keywords", [])

    try:
        # Create standardizer instance
        standardizer = DomainTermMapper()

        # Execute term standardization
        term_mappings = standardizer.find_standard_terms(keywords)

        logger.info(f"Term mapping results: {term_mappings}")

        # Update state
        return {"domain_term_mappings": term_mappings}

    except Exception as e:
        error_msg = f"Business term standardization process error: {str(e)}"
        logger.error(error_msg)
        return {"domain_term_mappings": {}, "error": error_msg}
