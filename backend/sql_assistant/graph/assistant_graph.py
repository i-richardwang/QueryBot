"""
QueryBot graph construction module.
Builds and configures the complete processing flow graph for QueryBot.
"""

import uuid
import logging
import os
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler

from backend.sql_assistant.states.assistant_state import SQLAssistantState
from backend.sql_assistant.nodes.intent_analysis_node import intent_analysis_node
from backend.sql_assistant.nodes.keyword_extraction_node import keyword_extraction_node
from backend.sql_assistant.nodes.term_mapping_node import domain_term_mapping_node
from backend.sql_assistant.nodes.query_rewrite_node import query_rewrite_node
from backend.sql_assistant.nodes.data_source_node import data_source_identification_node
from backend.sql_assistant.nodes.table_structure_node import (
    table_structure_analysis_node,
)
from backend.sql_assistant.nodes.query_example_node import query_example_node
from backend.sql_assistant.nodes.sql_generation_node import sql_generation_node
from backend.sql_assistant.nodes.permission_control_node import permission_control_node
from backend.sql_assistant.nodes.sql_execution_node import sql_execution_node
from backend.sql_assistant.nodes.error_analysis_node import error_analysis_node
from backend.sql_assistant.nodes.result_generation_node import result_generation_node
from backend.sql_assistant.nodes.feasibility_check_node import feasibility_check_node
from backend.sql_assistant.routes.node_routes import (
    route_after_intent,
    route_after_execution,
    route_after_error_analysis,
    route_after_feasibility_check,
    route_after_permission_check,
    route_after_data_source,
)

logger = logging.getLogger(__name__)


def initialize_langfuse():
    """
    Initialize Langfuse client (only when enabled).
    In Langfuse 3.x, the client needs to be initialized at application startup.
    """
    from utils.core.config import settings
    if settings.monitoring.langfuse_enabled:
        try:
            Langfuse(
                public_key=settings.monitoring.langfuse_public_key,
                secret_key=settings.monitoring.langfuse_secret_key,
                host=settings.monitoring.langfuse_host
            )
            logger.info("Langfuse client initialized successfully")
        except Exception as e:
            logger.warning(f"Langfuse client initialization failed: {e}")


def create_langfuse_handler() -> CallbackHandler:
    """
    Create Langfuse callback handler.

    In Langfuse 3.x, CallbackHandler no longer accepts constructor parameters,
    trace attributes are set through span context.

    Returns:
        CallbackHandler: Langfuse callback handler instance
    """
    return CallbackHandler()


def build_query_bot_graph() -> StateGraph:
    """Build the complete processing graph for QueryBot

    Create and configure all nodes and edges, set up routing logic.
    Includes intent analysis, keyword extraction, business term standardization, and the complete workflow.

    Returns:
        StateGraph: Configured state graph instance
    """
    # Create graph builder
    graph_builder = StateGraph(SQLAssistantState)

    # Add all nodes
    graph_builder.add_node("intent_analysis", intent_analysis_node)
    graph_builder.add_node("keyword_extraction", keyword_extraction_node)
    graph_builder.add_node("domain_term_mapping", domain_term_mapping_node)
    graph_builder.add_node("query_rewrite", query_rewrite_node)
    graph_builder.add_node(
        "data_source_identification", data_source_identification_node
    )
    graph_builder.add_node("table_structure_analysis", table_structure_analysis_node)
    graph_builder.add_node("feasibility_checking", feasibility_check_node)
    graph_builder.add_node("query_example_retrieval", query_example_node)
    graph_builder.add_node("sql_generation", sql_generation_node)
    graph_builder.add_node("permission_control", permission_control_node)
    graph_builder.add_node("sql_execution", sql_execution_node)
    graph_builder.add_node("error_analysis", error_analysis_node)
    graph_builder.add_node("result_generation", result_generation_node)

    # Set conditional edges
    graph_builder.add_conditional_edges(
        "intent_analysis",
        route_after_intent,
        {"keyword_extraction": "keyword_extraction", END: END},
    )

    graph_builder.add_conditional_edges(
        "feasibility_checking",
        route_after_feasibility_check,
        {"query_example_retrieval": "query_example_retrieval", END: END},
    )

    graph_builder.add_conditional_edges(
            "permission_control",
            route_after_permission_check,
            {
                "sql_execution": "sql_execution",
                "error_analysis": "error_analysis"
            }
        )

    graph_builder.add_conditional_edges(
        "sql_execution",
        route_after_execution,
        {"result_generation": "result_generation", "error_analysis": "error_analysis"},
    )

    graph_builder.add_conditional_edges(
        "error_analysis",
        route_after_error_analysis,
        {"sql_execution": "sql_execution", END: END},
    )

    # Add conditional edges after data source identification
    graph_builder.add_conditional_edges(
        "data_source_identification",
        route_after_data_source,
        {
            "table_structure_analysis": "table_structure_analysis",
            END: END
        }
    )

    # Modify basic flow edges, add permission control node
    graph_builder.add_edge("keyword_extraction", "domain_term_mapping")
    graph_builder.add_edge("domain_term_mapping", "query_rewrite")
    graph_builder.add_edge("query_rewrite", "data_source_identification")
    graph_builder.add_edge("table_structure_analysis", "feasibility_checking")
    graph_builder.add_edge("query_example_retrieval", "sql_generation")
    graph_builder.add_edge("sql_generation", "permission_control")
    graph_builder.add_edge("result_generation", END)

    # Set entry point
    graph_builder.add_edge(START, "intent_analysis")

    return graph_builder


def run_query_bot(
    query: str,
    thread_id: Optional[str] = None,
    checkpoint_saver: Optional[Any] = None,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Run QueryBot

    Args:
        query: User's query text
        thread_id: Session ID
        checkpoint_saver: State saver instance
        user_id: User ID for permission control

    Returns:
        Dict[str, Any]: Processing result dictionary
    """
    # Initialize Langfuse client (if enabled)
    initialize_langfuse()

    # Create graph builder
    graph_builder = build_query_bot_graph()

    # Use default memory saver
    if checkpoint_saver is None:
        checkpoint_saver = MemorySaver()

    # Compile graph
    graph = graph_builder.compile(checkpointer=checkpoint_saver)

    # Generate session ID
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    # Configure runtime parameters
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # Construct input state
    state_input = {
        "messages": [HumanMessage(content=query)],
        "user_id": user_id,  # Add user ID to initial state
    }

    # Execute graph
    try:
        # Use span context only when Langfuse is enabled
        from utils.core.config import settings
        if settings.monitoring.langfuse_enabled:
            langfuse_client = get_client()
            with langfuse_client.start_as_current_span(name="query-bot-query") as span:
                # Set trace attributes
                span.update_trace(
                    user_id=str(user_id) if user_id else None,
                    session_id=thread_id,
                    tags=["query_bot"],
                    input={"query": query}
                )

                # Add callbacks
                config["callbacks"] = [create_langfuse_handler()]

                # Execute graph
                result = graph.invoke(state_input, config)

                # Set output
                span.update_trace(output=result)

                return result
        else:
            return graph.invoke(state_input, config)

    except Exception as e:
        error_msg = f"QueryBot execution error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}


def stream_query_bot(
    query: str,
    thread_id: Optional[str] = None,
    checkpoint_saver: Optional[Any] = None,
    user_id: Optional[int] = None,
):
    """Stream QueryBot execution with native LangGraph updates

    Args:
        query: User's query text
        thread_id: Session ID
        checkpoint_saver: State saver instance
        user_id: User ID for permission control

    Yields:
        Dict[str, Any]: Stream chunks from graph execution
    """
    # Initialize Langfuse client (if enabled)
    initialize_langfuse()

    # Create graph builder
    graph_builder = build_query_bot_graph()

    # Use default memory saver
    if checkpoint_saver is None:
        checkpoint_saver = MemorySaver()

    # Compile graph
    graph = graph_builder.compile(checkpointer=checkpoint_saver)

    # Generate session ID
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    # Configure runtime parameters
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # Construct input state
    state_input = {
        "messages": [HumanMessage(content=query)],
        "user_id": user_id,
    }

    # Stream execution with Langfuse monitoring
    try:
        from utils.core.config import settings
        if settings.monitoring.langfuse_enabled:
            langfuse_client = get_client()
            with langfuse_client.start_as_current_span(name="query-bot-stream") as span:
                # Set trace attributes
                span.update_trace(
                    user_id=str(user_id) if user_id else None,
                    session_id=thread_id,
                    tags=["query_bot", "stream"],
                    input={"query": query}
                )

                # Add callbacks for monitoring
                config["callbacks"] = [create_langfuse_handler()]

                # Stream with native LangGraph updates mode
                final_result = None
                for chunk in graph.stream(state_input, config, stream_mode="updates"):
                    # Capture final result
                    for node_name, node_output in chunk.items():
                        if isinstance(node_output, dict) and 'messages' in node_output:
                            final_result = node_output

                    yield chunk

                # Set final output for monitoring
                if final_result:
                    span.update_trace(output=final_result)
        else:
            # Stream without monitoring
            for chunk in graph.stream(state_input, config, stream_mode="updates"):
                yield chunk

    except Exception as e:
        error_msg = f"QueryBot streaming error: {str(e)}"
        logger.error(error_msg)
        yield {"error": {"error": error_msg}}
