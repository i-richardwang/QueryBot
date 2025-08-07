"""
Node routing module.
Defines the routing logic between nodes in the state graph.
"""

from langgraph.graph import END

from backend.sql_assistant.states.assistant_state import SQLAssistantState


def route_after_intent(state: SQLAssistantState):
    """Routing function after intent analysis

    Decide the next processing node based on intent analysis results.
    If intent is unclear, end conversation for clarification; otherwise continue processing.

    Args:
        state: Current state object

    Returns:
        str: Next node identifier
    """
    if not state["is_intent_clear"]:
        return END
    return "keyword_extraction"


def route_after_execution(state: SQLAssistantState):
    """Routing function after SQL execution

    Decide next operation based on SQL execution results.
    If execution succeeds, proceed to result feedback; if fails, proceed to error analysis.

    Args:
        state: Current state object

    Returns:
        str: Next node identifier
    """
    execution_result = state.get("execution_result", {})
    if execution_result.get("success", False):
        return "result_generation"  # Execution successful, generate result feedback
    return "error_analysis"  # Execution failed, proceed to error analysis


def route_after_error_analysis(state: SQLAssistantState):
    """Routing function after error analysis

    Decide next operation based on error analysis results.
    If error is fixable, re-execute with fixed SQL;
    otherwise end processing flow.

    Args:
        state: Current state object

    Returns:
        str: Next node identifier
    """
    error_analysis_result = state.get("error_analysis_result", {})
    if error_analysis_result.get("is_sql_fixable", False):
        state["generated_sql"] = {"sql_query": error_analysis_result["fixed_sql"]}
        return "sql_execution"
    return END


def route_after_feasibility_check(state: SQLAssistantState):
    """Routing function after feasibility check

    Decide next operation based on feasibility check results.
    If query is feasible, generate SQL; otherwise end processing.

    Args:
        state: Current state object

    Returns:
        str: Next node identifier
    """
    feasibility_check = state.get("feasibility_check", {})
    if not feasibility_check or not feasibility_check.get("is_feasible"):
        return END
    return "query_example_retrieval"


def route_after_permission_check(state: SQLAssistantState):
    """Routing function after permission check

    Decide next processing node based on execution results:
    - Verification passed: proceed to SQL execution node
    - Verification failed: directly proceed to error analysis node

    Args:
        state: Current state object

    Returns:
        str: Next node identifier
    """
    execution_result = state.get("execution_result", {})

    if execution_result.get("success", False):
        return "sql_execution"
    return "error_analysis"


def route_after_data_source(state: SQLAssistantState):
    """Routing function after data source identification

    Decide next operation based on whether relevant data tables are found.
    If no relevant tables found, end processing; otherwise continue with table structure analysis.

    Args:
        state: Current state object

    Returns:
        str: Next node identifier
    """
    if not state.get("has_relevant_tables", False):
        return END
    return "table_structure_analysis"
