"""
Result generation node module.
Responsible for converting SQL query results into user-friendly descriptions.
"""

import logging
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage

from backend.sql_assistant.states.assistant_state import SQLAssistantState
from backend.sql_assistant.utils.format_utils import (
    format_results_preview,
    format_term_descriptions,
    format_full_results,
    format_table_structures
)
# Service function imports
from utils.services.llm import init_language_model, LanguageModelChain

logger = logging.getLogger(__name__)


class ResultGenerationOutput(BaseModel):
    """Query result generation output model"""
    result_description: str = Field(
        ...,
        description="User-facing query result description"
    )


# System prompt for result generation
RESULT_GENERATION_SYSTEM_PROMPT = """You are a professional data analyst responsible for converting SQL query results into clear, understandable natural language descriptions.

## Core Principles

1. Accuracy: Faithfully present data, avoid over-interpretation
2. Clarity: Use concise and clear language to ensure non-technical users can understand
3. Relevance: Always focus on answering the user's original query intent
4. Professionalism: Correctly use business terminology, maintain professional narrative standards

## Response Structure

- Answer user queries in a clear and direct manner
- Use precise numbers and standardized business terminology

## Special Case Handling

### A. Large Datasets (rows > 30)

Response structure:
1. Explain the situation
   - Inform user that query returned large amount of data (for detail queries, can provide specific row count; for statistical queries, should not provide specific row count)
   - Explain that specific content cannot be displayed due to large data volume

2. Provide optimization suggestions
   - Suggest optimizing queries through:
     * Adding time range restrictions
     * Adding specific filtering conditions (provide relevant filtering dimensions based on user's original query)
     * Suggest grouping statistics by appropriate dimensions

### B. Empty Result Set (rows = 0)

#### 1. Expectation-type queries (querying quantities, statistical values, specific values)

Response structure:
- Confirm no results found
- List filtering conditions used
- Provide possible reasons:
  * No data matching conditions actually exists
  * Terminology expression differences
  * Time range issues
  * Data missing
- Recommend broader query approaches

Example:
"No data found matching [specific conditions]. This may be due to [reason]. Suggest you try [alternative approach]."

#### 2. Verification-type queries (whether exists, whether meets conditions)

Response structure:
- Give direct negative response
- Restate conditions checked
- No additional suggestions needed

Example:
"After querying, no [objects] matching [specific conditions] found in [data source]."

## Result Interpretation Guide

1. Pay attention to distinguish whether SQL query results are statistical data or detailed data, avoid misinterpretation
2. Use business language for description, do not expose database table names and field names
3. Always ensure your answer directly addresses the user's original query intent while maintaining professionalism and accuracy.
"""

RESULT_GENERATION_USER_PROMPT = """Please generate query result description based on the following information:

1. User's query:
{rewritten_query}

2. Query results:
Total rows: {row_count}
Truncated: {truncated}
Query data source: {data_source}
Query statement: ```{sql_query}```
Data preview:
{results_preview}

3. Table structures used in query:
{table_structures}

4. Business term explanations:
{term_descriptions}

5. Current date:
{current_date}

Please generate a clear, professional description to explain the query results to the user."""


def create_result_generation_chain(temperature: float = 0.0) -> LanguageModelChain:
    """Create result generation task chain

    Args:
        temperature: Model temperature parameter controlling output randomness

    Returns:
        LanguageModelChain: Configured result generation task chain
    """
    llm = init_language_model(temperature=temperature)

    return LanguageModelChain(
        model_cls=ResultGenerationOutput,
        sys_msg=RESULT_GENERATION_SYSTEM_PROMPT,
        user_msg=RESULT_GENERATION_USER_PROMPT,
        model=llm,
    )()


def result_generation_node(state: SQLAssistantState) -> dict:
    """Result generation node function

    Convert SQL query results into user-friendly natural language descriptions.
    Includes data overview, key metrics, and special case explanations.

    Args:
        state: Current state object

    Returns:
        dict: State update containing result description
    """
    # Get necessary information
    execution_result = state.get("execution_result", {})
    if not execution_result or not execution_result.get('success'):
        return {"error": "Successful execution result not found in state"}

    try:
        # Prepare input data
        generated_sql = state.get("generated_sql", {})
        input_data = {
            "rewritten_query": state["rewritten_query"],
            "row_count": execution_result["row_count"],
            "truncated": execution_result["truncated"],
            "results_preview": format_results_preview(execution_result),
            "table_structures": format_table_structures(state.get("table_structures", [])),
            "term_descriptions": format_term_descriptions(
                state.get("domain_term_mappings", {})
            ),
            "data_source": state.get("matched_tables", [{}])[0].get("table_name", "Unknown data source"),
            "sql_query": generated_sql.get("sql_query", "Unknown SQL query"),
            "current_date": datetime.now().strftime("%Y-%m-%d")
        }

        # Create and execute result generation chain
        generation_chain = create_result_generation_chain()
        result = generation_chain.invoke(input_data)

        logger.info(f"Result generation completed: {result['result_description'][:100]}...")

        # Combine result description with complete table results
        formatted_table = format_full_results(execution_result)
        combined_message = (
            f"{result['result_description']}\n\n"
            f"Query result details:\n"
            f"{formatted_table}"
        )

        return {
            "result_description": result["result_description"],
            "messages": [AIMessage(content=result['result_description'])]
        }

    except Exception as e:
        error_msg = f"Result generation process error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
