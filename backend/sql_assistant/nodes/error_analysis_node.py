"""
Error analysis node module.
Responsible for analyzing SQL execution error causes and providing repair solutions.
"""

import logging
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.messages import AIMessage

from backend.sql_assistant.states.assistant_state import SQLAssistantState
from backend.sql_assistant.utils.format_utils import (
    format_table_structures,
    format_term_descriptions,
)
# Service function imports
from utils.services.llm import init_language_model, LanguageModelChain

logger = logging.getLogger(__name__)


class ErrorAnalysisResult(BaseModel):
    """SQL error analysis result model"""

    error_analysis: str = Field(..., description="Error cause reasoning and analysis")
    is_sql_fixable: bool = Field(
        ..., description="Determine whether the error can be resolved by modifying SQL"
    )
    fixed_sql: Optional[str] = Field(
        None, description="Provide corrected SQL statement when error is fixable"
    )
    user_feedback: Optional[str] = Field(None, description="User-friendly error explanation")


ERROR_ANALYSIS_SYSTEM_PROMPT = """You are a professional data analyst responsible for analyzing SQL execution failure causes and providing solutions.
Please follow these rules for analysis:

1. Error type analysis:
   - Syntax errors: SQL statement syntax issues
   - Field errors: Table or field name errors, type mismatches
   - Data errors: Null value handling, data range, type conversion issues
   - Permission errors: Database access permission issues
   - Connection errors: Database connection, network issues
   - Other system errors: Database server issues, etc.

2. Determine repairability:
   - Repairable: Issues that can be resolved by modifying SQL statements (syntax errors, field errors, etc.)
   - Non-repairable: Issues requiring system-level solutions (permissions, connections, etc.)

3. Repair suggestions:
   - If it's a repairable error, provide specific corrected SQL statement
   - Ensure corrected SQL matches original query intent
   - Maintain SQL optimization principles
   - Ensure correct table and field names are used

4. User feedback requirements:
   - For permission issues:
     * Point out which tables the user lacks access permissions for
     * Use natural language to represent table names, don't expose database table names
     * Suggest user contact data team to apply for appropriate permissions
   - For other non-repairable issues:
     * Explain the problem in easy-to-understand language
     * Provide clear follow-up handling suggestions
     * Express appropriate apologies

5. Output requirements:
   - Clearly indicate whether it can be fixed by modifying SQL
   - Explain error causes in detail
   - For repairable errors, provide corrected SQL
   - For non-repairable errors, provide user-friendly feedback information"""

ERROR_ANALYSIS_USER_PROMPT = """Please analyze the causes of the following SQL execution failure and provide solutions:

1. Original query requirements:
{rewritten_query}

2. Available table structures:
{table_structures}

3. Business term explanations:
{term_descriptions}

4. Current date:
{current_date}

5. Failed SQL execution:
{failed_sql}

6. Error message:
{error_message}

Please analyze error causes, determine whether it can be fixed by modifying SQL, and output analysis results in the specified JSON format.
"""


def create_error_analysis_chain(temperature: float = 0.0) -> LanguageModelChain:
    """Create error analysis task chain"""
    llm = init_language_model(temperature=temperature)

    return LanguageModelChain(
        model_cls=ErrorAnalysisResult,
        sys_msg=ERROR_ANALYSIS_SYSTEM_PROMPT,
        user_msg=ERROR_ANALYSIS_USER_PROMPT,
        model=llm,
    )()


def error_analysis_node(state: SQLAssistantState) -> dict:
    """SQL error analysis node function

    Analyze SQL execution failure causes, determine if repairable,
    and provide repair solutions when possible.

    Args:
        state: Current state object

    Returns:
        dict: State update containing error analysis results
    """
    # Get execution result
    execution_result = state.get("execution_result", {})
    if not execution_result or execution_result.get("success", True):
        return {"error": "Failed execution result not found in state"}

    generated_sql = state.get("generated_sql", {})
    if not generated_sql or not generated_sql.get("sql_query"):
        return {"error": "Generated SQL not found in state"}

    try:
        # Prepare input data
        input_data = {
            "rewritten_query": state["rewritten_query"],
            "table_structures": format_table_structures(state["table_structures"]),
            "term_descriptions": format_term_descriptions(
                state.get("domain_term_mappings", {})
            ),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "failed_sql": generated_sql.get("permission_controlled_sql", ""),
            "error_message": execution_result["error"],
        }

        # Create and execute error analysis chain
        analysis_chain = create_error_analysis_chain()
        result = analysis_chain.invoke(input_data)

        logger.info(f"Error analysis result: Is fixable={result['is_sql_fixable']}")
        if result['is_sql_fixable'] and result['fixed_sql']:
            logger.info(f"Fixed SQL: {result['fixed_sql']}")

        # Construct return result
        response = {
            "error_analysis_result": {
                "is_sql_fixable": result["is_sql_fixable"],
                "error_analysis": result["error_analysis"],
                "fixed_sql": result["fixed_sql"] if result["is_sql_fixable"] else None,
                "user_feedback": result["user_feedback"]
            }
        }

        # Only add message when there's user feedback
        if result.get("user_feedback"):
            response["messages"] = [AIMessage(content=result["user_feedback"])]

        return response

    except Exception as e:
        error_msg = f"Error analysis process error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
