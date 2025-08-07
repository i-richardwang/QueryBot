"""
Query feasibility check node module.
Responsible for evaluating whether existing data tables can meet user query requirements.
"""

from pydantic import BaseModel, Field
from typing import Optional
import logging

from backend.sql_assistant.states.assistant_state import SQLAssistantState
from backend.sql_assistant.utils.format_utils import (
    format_table_structures,
    format_term_descriptions,
)
# Service function imports
from utils.services.llm import init_language_model, LanguageModelChain
from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)


class FeasibilityCheckResult(BaseModel):
    """Data source matching assessment result

    Evaluates whether given data table structures contain necessary information to answer user queries
    """

    feasible_analysis: str = Field(
        ..., description="Detailed reasoning process of the assessment"
    )
    is_feasible: bool = Field(
        ..., description="Indicates whether existing data tables contain all necessary information to answer user queries"
    )
    user_feedback: Optional[str] = Field(
        None, description="User-friendly feedback when data tables cannot meet query requirements"
    )


FEASIBILITY_CHECK_SYSTEM_PROMPT = """You are a professional data analysis expert who needs to rigorously evaluate whether data tables can provide complete and accurate information to answer user queries.

Assessment steps:

1. Analyze basic attributes of data tables
   - Understand the main purpose of data tables (e.g., transaction records, training records, employee roster)
   - Determine update characteristics of data tables (e.g., snapshot, transaction log, master data)
   - Evaluate coverage scope of data tables (e.g., whether it includes all employees, or only specific groups)

2. Analyze data requirements of user queries
   - Identify core information needed for queries (e.g., headcount, amount, status)
   - Determine business scope of queries (e.g., all employees, specific departments, specific time periods)
   - Judge whether queries require accurate point-in-time data

3. Strict matching assessment
   Must satisfy ALL following conditions to be judged as matching (is_feasible = true):
   - Main purpose of data tables is directly related to query objectives
   - Data tables contain complete information required for queries
   - Coverage scope of data tables meets query requirements
   - Data tables can provide accurate results (not partial data or derived data)

4. Common non-matching situations
   Following situations must be judged as non-matching (is_feasible = false):
   - Statistical scope of data tables does not match query requirements
   - Data tables have related fields but cannot guarantee data completeness
   - Complex derivation is needed to obtain query results

5. Output requirements:
   a) feasible_analysis should include:
      - Identify core data requirements of user queries
      - Analyze key information of existing data tables
      - Explain main reasons for matching or non-matching
      - Keep concise reasoning process records

   b) When judged as non-matching, user_feedback should:
      - Distinguish between two situations:
        * No data tables related to user queries in the database
        * Related tables exist but lack necessary field information
      - Use natural language to describe table names, do not expose database table names
      - Inform users concisely and clearly, avoid over-explanation
"""


FEASIBILITY_CHECK_USER_PROMPT = """Please evaluate whether the following data tables contain sufficient information to answer user queries:

1. User query requirements:
{rewritten_query}

2. Existing data table structures:
{table_structures}

3. Related business term explanations (if exist):
{term_descriptions}

Please first understand the basic attributes and coverage scope of data tables, then rigorously evaluate whether accurate query results can be provided.
Even if data tables contain related fields, judge whether data completeness and accuracy meet query requirements."""


def create_feasibility_check_chain(temperature: float = 0.0) -> LanguageModelChain:
    """Create feasibility check task chain"""
    llm = init_language_model(temperature=temperature)

    return LanguageModelChain(
        model_cls=FeasibilityCheckResult,
        sys_msg=FEASIBILITY_CHECK_SYSTEM_PROMPT,
        user_msg=FEASIBILITY_CHECK_USER_PROMPT,
        model=llm,
    )()


def feasibility_check_node(state: SQLAssistantState) -> dict:
    """Query feasibility check node function"""
    if not state.get("rewritten_query"):
        return {"error": "Rewritten query not found in state"}
    if not state.get("table_structures"):
        return {"error": "Table structure information not found in state"}

    try:
        input_data = {
            "rewritten_query": state["rewritten_query"],
            "table_structures": format_table_structures(state["table_structures"]),
            "term_descriptions": format_term_descriptions(
                state.get("domain_term_mappings", {})
            ),
        }

        check_chain = create_feasibility_check_chain()
        result = check_chain.invoke(input_data)

        logger.info(f"Feasibility check result: {'Passed' if result['is_feasible'] else 'Failed'}" +
                   (f", Reason: {result['user_feedback']}" if not result['is_feasible'] else ""))

        response = {
            "feasibility_check": {
                "is_feasible": result["is_feasible"],
                "feasible_analysis": result["feasible_analysis"],
                "user_feedback": result["user_feedback"] if not result["is_feasible"] else None,
            }
        }

        if not result["is_feasible"] and result["user_feedback"]:
            response["messages"] = [AIMessage(content=result["user_feedback"])]

        return response

    except Exception as e:
        error_msg = f"Feasibility check process error: {str(e)}"
        return {"error": error_msg}
