"""
Data source identification node module.
Responsible for identifying data tables most relevant to query requirements.
"""

import os
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from langchain_core.messages import AIMessage

from backend.sql_assistant.states.assistant_state import SQLAssistantState
# Factory class imports
from utils.factories.milvus import MilvusFactory
from utils.factories.embedding import EmbeddingFactory

# Service function imports
from utils.services.milvus_service import search_in_milvus
from utils.services.llm import init_language_model, LanguageModelChain

# Core infrastructure imports
from utils.core.config import settings

logger = logging.getLogger(__name__)


class TableSelectionResult(BaseModel):
    """Table selection result model"""

    selection_reasoning: str = Field(..., description="Brief explanation of the reasoning process for table selection")
    selected_table_names: List[str] = Field(
        ..., description="Most relevant table names selected from candidates (maximum 3 tables)"
    )


TABLE_SELECTION_SYSTEM_PROMPT = """You are a professional data analyst responsible for selecting the most suitable tables from candidate data tables to answer user queries.
Please follow these principles:

1. Understand query requirements:
   - Analyze the core information the user wants to query
   - Identify the main dimensions and metrics of the query
   - Determine if multi-table joins are needed

2. Evaluate table relevance:
   - Whether the table's main purpose is directly related to the query objective
   - Whether the table contains required key fields
   - Whether the table's data granularity is appropriate
   - Whether the table's data update characteristics meet the requirements

3. Selection principles:
   - Select the most relevant tables based on query requirements
   - Select at most three tables
   - Choose tables with the most appropriate data granularity
   - Avoid selecting redundant tables

4. Output requirements:
   - Briefly explain the reasoning process and selection rationale (within 20 words)
"""


TABLE_SELECTION_USER_PROMPT = """Please select the most suitable tables from the following candidate data tables to answer the user query:

1. User query requirements:
{query}

2. Candidate data table list:
{candidate_tables}

Please analyze the relevance of each table, select at most 2 most suitable tables, and explain the selection reasons in detail."""


class DataSourceMatcher:
    """Data source matcher"""

    def __init__(self):
        """Initialize data source matcher"""
        # Create Milvus connection instance
        self.milvus_connection = MilvusFactory.create_connection(
            db_name=settings.vector_db.database,
            auto_connect=True
        )
        # Get table descriptions collection
        self.collection = self.milvus_connection.get_collection("table_descriptions")
        # Initialize embedding model
        self.embeddings = EmbeddingFactory.get_default_embeddings()

    def find_candidate_tables(
        self, query: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Identify candidate data tables most relevant to the query

        Args:
            query: Standardized query text
            top_k: Number of most relevant tables to return

        Returns:
            List[Dict[str, Any]]: List of candidate table information, each table contains name, description and similarity score

        Raises:
            ValueError: Raised when vector search fails
        """
        try:
            # Generate vector representation of query text
            query_vector = self.embeddings.embed_query(query)

            # Search for similar tables in vector database
            results = search_in_milvus(
                collection=self.collection,
                query_vector=query_vector,
                vector_field="description",
                top_k=top_k,
            )

            # Convert result format
            return [
                {
                    "table_name": result["table_name"],
                    "description": result["description"],
                    "similarity_score": result["distance"],
                    "additional_info": result.get("additional_info", ""),
                    "schema": result.get("schema", ""),
                }
                for result in results
            ]

        except Exception as e:
            raise ValueError(f"Data table vector search failed: {str(e)}")


def create_table_selection_chain(temperature: float = 0.0) -> LanguageModelChain:
    """Create table selection task chain"""
    llm = init_language_model(temperature=temperature)

    return LanguageModelChain(
        model_cls=TableSelectionResult,
        sys_msg=TABLE_SELECTION_SYSTEM_PROMPT,
        user_msg=TABLE_SELECTION_USER_PROMPT,
        model=llm,
    )()


def format_candidate_tables(tables: List[Dict[str, Any]]) -> str:
    """Format candidate table information"""
    formatted = []
    for i, table in enumerate(tables, 1):
        formatted.append(
            f"{i}. Table name: {table['table_name']}\n"
            f"   Description: {table['description']}\n"
            f"   Additional info: {table['additional_info']}\n"
        )
    return "\n".join(formatted)


def data_source_identification_node(state: SQLAssistantState) -> dict:
    """Data source identification node function

    First match candidate tables based on vector similarity, then use LLM to select the most relevant tables.

    Args:
        state: Current state object

    Returns:
        dict: State update containing relevant data table information, maintaining format consistency with original version
    """
    # Get rewritten query
    rewritten_query = state.get("rewritten_query")
    if not rewritten_query:
        raise ValueError("Rewritten query not found in state")

    try:
        # Create matcher instance
        matcher = DataSourceMatcher()

        # 1. Get candidate tables
        candidate_tables = matcher.find_candidate_tables(rewritten_query)
        logger.info(f"Number of initially matched candidate tables: {len(candidate_tables)}")

        # 2. Create table selection chain
        selection_chain = create_table_selection_chain()

        # 3. Use LLM to select most relevant tables
        input_data = {
            "query": rewritten_query,
            "candidate_tables": format_candidate_tables(candidate_tables),
        }

        selection_result = selection_chain.invoke(input_data)
        selected_table_names = selection_result["selected_table_names"]
        has_relevant_tables = len(selected_table_names) > 0

        logger.info(
            f"LLM selection result: Selected tables {selected_table_names}\n"
            f"Selection reasoning: {selection_result['selection_reasoning']}"
        )

        # 4. Extract complete information of selected tables from candidates
        matched_tables = [
            table
            for table in candidate_tables
            if table["table_name"] in selected_table_names
        ]

        # 5. If no relevant tables found, add user-friendly prompt message
        response = {
            "matched_tables": matched_tables,
            "has_relevant_tables": has_relevant_tables
        }

        if not has_relevant_tables:
            response["messages"] = [
                AIMessage(content="Sorry, no data tables related to your query were found in the system.\n"
                                "Suggestions:\n"
                                "- Try using different keywords to describe your requirements\n"
                                "- Contact the data team to check if relevant data support is available")
            ]

        return response

    except Exception as e:
        error_msg = f"Data source identification process error: {str(e)}"
        logger.error(error_msg)
        return {"matched_tables": [], "error": error_msg}
