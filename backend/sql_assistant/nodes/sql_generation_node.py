"""
SQL generation node module.
Responsible for generating SQL query statements.
"""

from pydantic import BaseModel, Field
import logging
from datetime import datetime

from backend.sql_assistant.states.assistant_state import SQLAssistantState
from backend.sql_assistant.utils.format_utils import (
    format_table_structures,
    format_term_descriptions
)
# Service function imports
from utils.services.llm import init_language_model, LanguageModelChain

logger = logging.getLogger(__name__)


class SQLGenerationResult(BaseModel):
    """SQL generation result model"""
    sql_query: str = Field(
        ...,
        description="Generated SQL query statement"
    )


SQL_GENERATION_SYSTEM_PROMPT = """
You are a professional data analyst responsible for generating high-quality SQL query statements. Please think systematically and generate SQL following these steps:

### I. Query Intent Analysis

1. Understand core query objectives
   - Clarify what data the user wants to retrieve
   - Determine the business scope of the query
   - Identify time range requirements (may have no time range requirements)
   - Understand whether user needs detailed data or aggregated data

2. Implementation dependency analysis
   - Direct retrieval type: Can results be obtained through simple queries/aggregation
   - Statistics dependent type: Need to calculate certain statistical values as conditions first
   - Detail dependent type: Need to process detailed data before statistics
   - Multi-level dependent type: Need multiple levels of processing

### II. Query Structure Design

1. Data source selection
   - Single table priority principle: Fully consider whether requirements can be implemented through single table queries
   - Only consider multi-table joins when ALL following conditions are met:
     * All single table query possibilities have been exhausted
     * Clearly verified that single table cannot meet current requirements
     * Indeed need fields from other tables to complete the query

2. Query type determination
   - Direct query: Simple SELECT statements
   - Subquery: Need temporary result sets
   - Progressive query: Scenarios requiring multi-step processing

### III. SQL Writing Standards

1. Field selection
   - Unless user explicitly requests, limit to within 5 fields
   - For statistical queries, GROUP BY grouping conditions should not exceed 2 fields
   - Prohibit using SELECT *
   - Add meaningful aliases for calculated fields

2. Condition construction
   - Reasonably use WHERE conditions for filtering
   - Use LIKE '%%keyword%%' for fuzzy matching on potentially ambiguous fields
   - Properly handle NULL value situations
   - Use subqueries to optimize performance when necessary

3. Time handling
   - Uniformly use DATE/DATETIME functions to handle dates
   - Pay attention to string date conversions

### IV. Example Reference

1. If related query examples are provided, please refer to the SQL writing patterns in the examples
2. Do not directly copy example SQL, but understand the logic and structure within
3. Ensure the final generated SQL strictly matches current query requirements

### V. Important Notes

1. Use {database_type} syntax
2. Strictly check which table each field belongs to, ensure no incorrect use of one table's fields in another table during queries
3. When generating SQL, strictly refer to standard term names and additional information provided in business term explanations to ensure query condition accuracy
"""

SQL_GENERATION_USER_PROMPT = """Please generate SQL query statements based on the following information:

1. Query requirements:
{rewritten_query}

2. Available table structures:
{table_structures}

3. Business term explanations (if exist):
{term_descriptions}

4. Current date:
{current_date}

5. Query examples (user's actual requirements may differ from examples, please do not directly use query statements from examples, but regenerate query statements based on user requirements):
{query_examples}

Please generate standard SQL query statements and output results in the specified JSON format."""


def create_sql_generation_chain(temperature: float = 0.0) -> LanguageModelChain:
    """Create SQL generation task chain"""
    llm = init_language_model(temperature=temperature)

    return LanguageModelChain(
        model_cls=SQLGenerationResult,
        sys_msg=SQL_GENERATION_SYSTEM_PROMPT,
        user_msg=SQL_GENERATION_USER_PROMPT,
        model=llm,
    )()


def sql_generation_node(state: SQLAssistantState) -> dict:
    """SQL generation node function"""
    if not state.get("rewritten_query"):
        return {"error": "Rewritten query not found in state"}
    if not state.get("table_structures"):
        return {"error": "Table structure information not found in state"}

    try:
        # Get database type from configuration
        from utils.core.config import settings
        db_type = settings.database.type.upper()

        input_data = {
            "rewritten_query": state["rewritten_query"],
            "table_structures": format_table_structures(state["table_structures"]),
            "term_descriptions": format_term_descriptions(
                state.get("domain_term_mappings", {})
            ),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "database_type": db_type,
            "query_examples": "\n".join([
            f"Example query: [{example['query_text']}]\nExample SQL: [{example['query_sql']}]"
            for example in state.get("query_examples", [])
        ]) or "No related examples"
        }

        generation_chain = create_sql_generation_chain()
        result = generation_chain.invoke(input_data)

        logger.info(f"Generated SQL query: {result['sql_query']}")

        return {
            "generated_sql": {
                "sql_query": result["sql_query"]
            }
        }

    except Exception as e:
        error_msg = f"SQL generation process error: {str(e)}"
        return {"error": error_msg}
