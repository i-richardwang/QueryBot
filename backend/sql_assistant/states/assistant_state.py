"""
QueryBot state definition module.
Defines the state data structures used by QueryBot during processing.
"""

from typing import Annotated, Dict, Optional, List, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

# Import message addition annotation
from langgraph.graph.message import add_messages


class SQLAssistantState(TypedDict):
    """QueryBot state type definition"""
    # User ID
    user_id: Optional[int]
    # Message history
    messages: Annotated[List[BaseMessage], add_messages]
    # Query intent analysis result
    query_intent: Optional[Dict]
    # Flag indicating whether intent is clear
    is_intent_clear: bool
    # Extracted keyword list
    keywords: List[str]
    # Business terms and their descriptions
    domain_term_mappings: Dict[str, str]
    # Rewritten query
    rewritten_query: Optional[str]
    # Matched table information
    matched_tables: List[Dict[str, Any]]
    # Table structure information
    table_structures: List[Dict[str, Any]]
    # Generated SQL information
    generated_sql: Optional[Dict[str, Any]]
    # SQL execution result
    execution_result: Optional[Dict[str, Any]]
    # SQL error analysis result
    error_analysis_result: Optional[Dict[str, Any]]
    # SQL execution retry count
    retry_count: int
    # Query result feedback
    result_feedback: Optional[str]
    # Feasibility check result
    feasibility_check: Optional[Dict]
    query_examples: Optional[List[Dict[str, str]]]
    has_relevant_tables: bool