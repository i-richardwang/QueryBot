"""
Permission control node module.
Responsible for SQL permission verification and permission condition injection.
"""

import logging
from typing import Dict, List, Optional, Tuple, NamedTuple
from sqlalchemy import text
import os
import sqlparse
from sqlparse.sql import TokenList, Identifier
from pydantic import BaseModel, Field
import re

from backend.sql_assistant.states.assistant_state import SQLAssistantState

# Factory class imports
from utils.factories.database import DatabaseFactory

# Core infrastructure imports
from utils.core.streamlit_config import settings

logger = logging.getLogger(__name__)


class TablePermissionConfig(BaseModel):
    """Table permission configuration model"""

    table_name: str = Field(..., description="Table name")
    need_dept_control: bool = Field(..., description="Whether department permission control is needed")
    dept_path_field: Optional[str] = Field(None, description="Department path field name")


class TableInfo(NamedTuple):
    """Table information including table name and alias"""

    name: str
    alias: Optional[str]


class PermissionValidator:
    """Permission validator"""

    def __init__(self):
        """Initialize database connection"""
        self.engine = DatabaseFactory.get_default_engine()

    def get_all_table_names(self) -> List[str]:
        """Get all configured table names from database"""
        query = text(
            """
            SELECT table_name
            FROM table_permission_config
            WHERE status = 1
        """
        )

        with self.engine.connect() as conn:
            result = conn.execute(query)
            return [row[0] for row in result]

    def _extract_table_info(self, statement: TokenList) -> List[TableInfo]:
        """Extract table information from SQL statement

        Use sqlparse to parse SQL and extract table names and alias information.

        Args:
            statement: TokenList object of SQL statement

        Returns:
            List[TableInfo]: List of table information
        """
        tables = []
        all_table_names = set(self.get_all_table_names())

        def _process_identifier(identifier: Identifier) -> Optional[TableInfo]:
            """Process single identifier"""
            # Get actual table name
            tokens = list(identifier.flatten())

            # Find first token matching known table names
            table_name = None
            for token in tokens:
                if token.value.lower() in {t.lower() for t in all_table_names}:
                    table_name = token.value
                    break

            if not table_name:
                return None

            # Check if there's an alias
            alias = None
            if len(tokens) > 1:
                # Last token might be alias
                last_token = tokens[-1]
                if (
                    last_token.value.lower() != table_name.lower()
                    and last_token.value.lower()
                    not in {"as", "from", "join", "where", "on", "and", "or"}
                ):
                    alias = last_token.value

            return TableInfo(table_name, alias)

        def _process_token(token):
            """Recursively process token"""
            if isinstance(token, Identifier):
                table_info = _process_identifier(token)
                if table_info:
                    tables.append(table_info)
            elif isinstance(token, TokenList):
                for sub_token in token.tokens:
                    _process_token(sub_token)

        # Process all tokens
        for token in statement.tokens:
            _process_token(token)

        return tables

    def extract_table_names(self, sql: str) -> List[TableInfo]:
        """Extract table information from SQL statement

        Args:
            sql: SQL statement

        Returns:
            List[TableInfo]: List of table information
        """
        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                raise ValueError("SQL parsing failed")

            statement = parsed[0]
            return self._extract_table_info(statement)

        except Exception as e:
            logger.error(f"Error extracting table information: {str(e)}")
            raise ValueError(f"Failed to extract table information: {str(e)}")

    def get_user_accessible_tables(self, user_id: int) -> List[str]:
        """Get all table names accessible to user"""
        query = text(
            """
            SELECT DISTINCT tpc.table_name
            FROM user_role ur
            JOIN role_table_permission rtp ON ur.role_id = rtp.role_id
            JOIN table_permission_config tpc ON rtp.table_permission_id = tpc.table_permission_id
            WHERE ur.user_id = :user_id
            AND tpc.status = 1
        """
        )

        with self.engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            return [row[0] for row in result]

    def get_user_dept_paths(self, user_id: int) -> List[str]:
        """Get user's department path list"""
        query = text(
            """
            SELECT dept_id
            FROM user_department
            WHERE user_id = :user_id
        """
        )

        with self.engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            return [row[0] for row in result]

    def get_table_permission_configs(
        self, table_names: List[str]
    ) -> Dict[str, TablePermissionConfig]:
        """Get permission configuration information for tables"""
        if not table_names:
            return {}

        query = text(
            """
            SELECT table_name, need_dept_control, dept_path_field
            FROM table_permission_config
            WHERE table_name IN :table_names
            AND status = 1
        """
        )

        configs = {}
        with self.engine.connect() as conn:
            result = conn.execute(query, {"table_names": tuple(table_names)})
            for row in result:
                configs[row[0]] = TablePermissionConfig(
                    table_name=row[0],
                    need_dept_control=bool(row[1]),
                    dept_path_field=row[2],
                )
        return configs

    def _build_auth_subquery(
            self,
            table_info: TableInfo,
            dept_path_field: str,
            dept_paths: List[str]
    ) -> str:
        """Build permission verification subquery

        Args:
            table_info: Table information (table name and alias)
            dept_path_field: Department path field
            dept_paths: User's department path list

        Returns:
            str: Built subquery SQL
        """
        # Build REGEXP pattern
        patterns = [f"(^|>){dept_id}(>|$)" for dept_id in dept_paths]
        regexp_pattern = "|".join(patterns)

        # Build subquery
        subquery = f"(SELECT * FROM {table_info.name} WHERE {dept_path_field} REGEXP '{regexp_pattern}')"

        # Always add alias, if original SQL doesn't specify alias, use original table name as alias
        alias = table_info.alias or table_info.name
        subquery = f"{subquery} AS {alias}"

        return subquery

    def verify_and_inject_permissions(
        self, user_id: int, sql: str
    ) -> Tuple[bool, Optional[str], Optional[List[str]]]:
        """Verify permissions and inject permission conditions"""
        try:
            # Extract all table information from SQL
            table_infos = self.extract_table_names(sql)
            logger.info(f"Table information extracted from SQL: {table_infos}")

            # Get all table names
            query_tables = [info.name for info in table_infos]

            # Get user accessible tables
            accessible_tables = self.get_user_accessible_tables(user_id)

            # Verify table permissions
            unauthorized_tables = [
                table for table in query_tables if table not in accessible_tables
            ]
            if unauthorized_tables:
                return False, None, unauthorized_tables

            # Get table permission configuration information
            table_configs = self.get_table_permission_configs(query_tables)

            # Get tables requiring department permission control
            dept_control_tables = [
                info
                for info in table_infos
                if table_configs.get(info.name)
                and table_configs[info.name].need_dept_control
            ]

            if not dept_control_tables:
                return True, sql, None

            # Get user's department paths
            dept_paths = self.get_user_dept_paths(user_id)
            if not dept_paths:
                return True, sql, None

            # Process each table requiring permission control
            modified_sql = sql
            for table_info in dept_control_tables:
                field = table_configs[table_info.name].dept_path_field
                if not field:
                    continue

                # Build subquery with permission control
                auth_subquery = self._build_auth_subquery(table_info, field, dept_paths)

                # Replace original table reference in SQL
                # Build different replacement patterns based on whether there's an alias
                if table_info.alias:
                    pattern = rf"{table_info.name}\s+(?:AS\s+)?{table_info.alias}\b"
                else:
                    pattern = rf"\b{table_info.name}\b"

                # Ignore case when replacing
                modified_sql = re.sub(
                    pattern, auth_subquery, modified_sql, flags=re.IGNORECASE
                )

            # Log modified SQL for debugging
            logger.info(f"SQL after permission injection: {modified_sql}")
            return True, modified_sql, None

        except Exception as e:
            logger.error(f"Permission verification process error: {str(e)}")
            return False, None, None


def permission_control_node(state: SQLAssistantState) -> dict:
    """Permission control node function"""
    # Get user ID and generated SQL
    user_id = state.get("user_id")
    generated_sql = state.get("generated_sql", {})

    if not generated_sql or not generated_sql.get("sql_query"):
        return {
            "execution_result": {"success": False, "error": "Generated SQL not found in state"}
        }

    # Check if permission control is enabled
    if not settings.app.user_auth_enabled:
        return {
            "execution_result": {
                "success": True,
                "sql_query": generated_sql["sql_query"],
            },
            "generated_sql": {
                "sql_query": generated_sql["sql_query"],
                "permission_controlled_sql": generated_sql["sql_query"]
            }
        }

    if not user_id:
        return {"execution_result": {"success": False, "error": "User ID information not found"}}

    try:
        # Create permission validator
        validator = PermissionValidator()

        # Execute permission verification and injection
        is_valid, modified_sql, unauthorized_tables = (
            validator.verify_and_inject_permissions(
                user_id=user_id, sql=generated_sql["sql_query"]
            )
        )

        if not is_valid:
            error_msg = f"Permission verification failed: No access to tables {', '.join(unauthorized_tables or ['unknown tables'])}"
            return {
                "execution_result": {
                    "success": False,
                    "error": error_msg,
                    "sql_source": "permission_control",
                }
            }

        # Verification passed, update SQL
        return {
            "generated_sql": {
                "sql_query": generated_sql["sql_query"],
                "permission_controlled_sql": modified_sql
            },
            "execution_result": {"success": True},
        }

    except Exception as e:
        error_msg = f"Permission control process error: {str(e)}"
        logger.error(error_msg)
        return {
            "execution_result": {
                "success": False,
                "error": error_msg,
                "sql_source": "permission_control",
            }
        }
