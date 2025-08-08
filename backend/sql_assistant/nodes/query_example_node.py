"""
Query example retrieval node module.
Responsible for retrieving the most similar SQL query examples based on user queries.
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
from utils.core.streamlit_config import settings

logger = logging.getLogger(__name__)

class QueryExampleRetriever:
    def __init__(self):
        # Create Milvus connection instance
        self.milvus_connection = MilvusFactory.create_connection(
            db_name=settings.vector_db.database,
            auto_connect=True
        )
        # Get query examples collection
        self.collection = self.milvus_connection.get_collection("query_examples")
        # Initialize embedding model
        self.embeddings = EmbeddingFactory.get_default_embeddings()

    def retrieve_examples(
        self, query: str, top_k: int = 2
    ) -> List[Dict[str, str]]:
        """
        Retrieve the most similar SQL query examples based on query

        Args:
            query: User query text
            top_k: Number of most similar examples to return

        Returns:
            List of most similar query examples
        """
        try:
            # Generate vector representation of query text
            query_vector = self.embeddings.embed_query(query)

            # Search for similar examples in vector database
            results = search_in_milvus(
                collection=self.collection,
                query_vector=query_vector,
                vector_field="query_text",
                top_k=top_k,
            )

            # Convert result format
            return [
                {
                    "query_text": result["query_text"],
                    "query_sql": result["query_sql"],
                }
                for result in results
            ]

        except Exception as e:
            logger.error(f"Query example retrieval failed: {str(e)}")
            return []

def query_example_node(state: SQLAssistantState) -> dict:
    """
    Query example retrieval node function

    Retrieve SQL query examples most similar to current query from vector database

    Args:
        state: Current state object

    Returns:
        dict: State update containing retrieved query examples
    """
    # Get rewritten query
    rewritten_query = state.get("rewritten_query")
    if not rewritten_query:
        return {"query_examples": []}

    try:
        # Create example retriever instance
        retriever = QueryExampleRetriever()

        # Retrieve similar examples
        query_examples = retriever.retrieve_examples(rewritten_query)

        logger.info(f"Retrieved {len(query_examples)} similar query examples")

        return {"query_examples": query_examples}

    except Exception as e:
        error_msg = f"Query example retrieval process error: {str(e)}"
        logger.error(error_msg)
        return {"query_examples": [], "error": error_msg}
