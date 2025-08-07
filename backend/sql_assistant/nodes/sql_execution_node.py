"""
SQL execution node module.
Responsible for executing SQL queries and handling execution results.
"""

import os
from typing import Dict, Any
import pandas as pd
from sqlalchemy import text, Engine

from backend.sql_assistant.states.assistant_state import SQLAssistantState
# Factory class imports
from utils.factories.database import DatabaseFactory

# Core infrastructure imports
from utils.core.logging_config import get_logger, log_operation_result, log_database_operation
from utils.core.error_handler import ProcessingError, DatabaseError, error_handler, create_error_response, ErrorLevel
from utils.core.constants import DatabaseConstants, ErrorMessages, SuccessMessages, BusinessConstants

logger = get_logger(__name__)


class SQLExecutor:
    """SQL executor

    Responsible for executing SQL queries and handling results.
    Provides query retry mechanism, result pagination, error handling and other features.
    """

    def __init__(self):
        """Initialize SQL executor"""
        self.engine = DatabaseFactory.get_default_engine()

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute SQL query

        Args:
            sql_query: SQL query statement

        Returns:
            Dict: Dictionary containing execution results or error information.
                 On success contains results, columns, row_count and other info,
                 On failure contains error information.
        """
        try:
            # Use pandas to read SQL results
            df = pd.read_sql_query(text(sql_query), self.engine)

            # Convert results to dictionary list
            results = df.to_dict('records')

            # Get column information
            columns = list(df.columns)

            # Limit number of returned records
            max_rows = DatabaseConstants.MAX_RESULT_ROWS
            if len(results) > max_rows:
                results = results[:max_rows]
                truncated = True
            else:
                truncated = False

            # Log success
            log_database_operation(
                logger=logger,
                operation="query",
                row_count=len(df),
                success=True
            )

            return {
                'success': True,
                'results': results,
                'columns': columns,
                'row_count': len(df),
                'truncated': truncated,
                'error': None
            }

        except Exception as e:
            error_msg = f"{ErrorMessages.SQL_EXECUTION_FAILED}: {str(e)}"

            # Log failure
            log_database_operation(
                logger=logger,
                operation="query",
                success=False,
                error=str(e)
            )

            return create_error_response(
                error=error_msg,
                additional_data={
                    'results': None,
                    'columns': None,
                    'row_count': 0,
                    'truncated': False
                }
            )


def sql_execution_node(state: SQLAssistantState) -> dict:
    """SQL execution node function

    Execute generated SQL queries, handle execution results, support query retry.
    Use transactions to ensure data consistency, support result pagination.

    Args:
        state: Current state object

    Returns:
        dict: State update containing SQL execution results
    """
    # Get retry count
    retry_count = state.get("retry_count", 0)

    # Check if maximum retry count reached
    max_retries = BusinessConstants.MAX_SQL_RETRY
    if retry_count >= max_retries:
        error_response = create_error_response(
            error=ErrorMessages.MAX_RETRY_EXCEEDED,
            additional_data={"retry_count": retry_count}
        )
        return {"execution_result": error_response, "retry_count": retry_count}

    # Get SQL to execute
    # Prioritize using SQL fixed by error analysis node
    error_analysis = state.get("error_analysis_result", {})
    sql_source = "error_analysis" if error_analysis and error_analysis.get(
        "fixed_sql") else "generation"

    if sql_source == "error_analysis":
        sql_query = error_analysis["fixed_sql"]
    else:
        generated_sql = state.get("generated_sql", {})
        if not generated_sql:
            error_response = create_error_response(
                error=ErrorMessages.SQL_NOT_FOUND,
                additional_data={"retry_count": retry_count}
            )
            return {"execution_result": error_response, "retry_count": retry_count}

        # Use SQL with injected permissions
        sql_query = generated_sql.get('permission_controlled_sql')
        if not sql_query:
            error_response = create_error_response(
                error="Permission-controlled SQL query statement not found in state",
                additional_data={"retry_count": retry_count}
            )
            return {"execution_result": error_response, "retry_count": retry_count}

    try:
        # Create executor instance
        executor = SQLExecutor()

        # Execute SQL
        result = executor.execute_query(sql_query)

        # Log execution result
        log_operation_result(
            logger=logger,
            operation="SQL execution",
            success=result['success'],
            details=f"Returned {result.get('row_count', 0)} records" if result['success'] else result.get('error', 'Unknown error')
        )

        # Add additional information to execution result
        result.update({
            'sql_source': sql_source,
            'executed_sql': sql_query,
            'retry_number': retry_count
        })

        # Update state
        return {
            "execution_result": result,
            "retry_count": retry_count + 1  # Increment retry count
        }

    except Exception as e:
        error_msg = f"{ErrorMessages.PROCESSING_ERROR}: {str(e)}"
        logger.error(error_msg)

        error_response = create_error_response(
            error=error_msg,
            additional_data={
                'sql_source': sql_source,
                'executed_sql': sql_query,
                'retry_number': retry_count
            }
        )

        return {
            "execution_result": error_response,
            "retry_count": retry_count + 1  # Increment retry count even on failure
        }
