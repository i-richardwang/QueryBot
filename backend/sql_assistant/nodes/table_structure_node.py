"""
Table structure analysis node module.
Responsible for parsing detailed structure information of data tables.
"""

import logging

from backend.sql_assistant.states.assistant_state import SQLAssistantState

logger = logging.getLogger(__name__)


def table_structure_analysis_node(state: SQLAssistantState) -> dict:
    """Table structure analysis node function

    Parse table structures from schema information obtained from vector database,
    providing necessary table structure information for subsequent SQL generation.

    Args:
        state: Current state object

    Returns:
        dict: State update containing table structure information
    """
    # Get matched table list
    matched_tables = state.get("matched_tables", [])
    if not matched_tables:
        return {
            "table_structures": [],
            "error": "No data tables found for analysis"
        }

    try:
        table_structures = []
        failed_tables = []

        # Process each matched table
        for table in matched_tables:
            try:
                # Get schema from table information
                schema_str = table.get("schema")
                if not schema_str:
                    raise ValueError("Table structure information not found")

                # Build table structure information
                structure = {
                    "table_name": table["table_name"],
                    "columns": schema_str,
                    "description": table.get("description", ""),
                    "additional_info": table.get("additional_info", "")
                }
                table_structures.append(structure)

            except Exception as table_error:
                failed_tables.append({
                    "table_name": table["table_name"],
                    "error": str(table_error)
                })
                logger.warning(f"Table {table['table_name']} structure parsing failed: {str(table_error)}")
                continue

        logger.info(f"Table structure analysis completed, successfully parsed {len(table_structures)} table structures, failed {len(failed_tables)} tables")

        return {
            "table_structures": table_structures,
            "failed_tables": failed_tables
        }

    except Exception as e:
        error_msg = f"Table structure analysis process error: {str(e)}"
        logger.error(error_msg)
        return {
            "table_structures": [],
            "failed_tables": [],
            "error": error_msg
        }
