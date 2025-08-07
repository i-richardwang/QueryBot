"""
Formatting utility functions module.
Provides common functions for various data formatting.
"""

from typing import List, Dict
from langchain_core.messages import HumanMessage, BaseMessage
from tabulate import tabulate


def format_conversation_history(messages: List[BaseMessage]) -> str:
    """Format conversation history into prompt format

    Convert message list to structured conversation history text for LLM input

    Args:
        messages: Message history list

    Returns:
        str: Formatted conversation history
    """
    formatted = []
    for msg in messages:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        formatted.append(f"{role}: {msg.content}")
    return "\n".join(formatted)


def format_term_descriptions(term_mappings: Dict[str, Dict[str, str]]) -> List[Dict[str, str]]:
    """Format business term mapping information

    Args:
        term_mappings: Business term mapping information dictionary

    Returns:
        List[Dict[str, str]]: Formatted term mapping information list
    """
    if not term_mappings:
        return []

    formatted_mappings = []
    for mapping in term_mappings.values():
        formatted_mappings.append({
            "original_term": mapping["original_term"],
            "standard_name": mapping["standard_name"],
            "additional_info": mapping["additional_info"]
        })
    
    return formatted_mappings


def format_table_structures(table_structures: List[Dict]) -> str:
    """Format table structure information

    Args:
        table_structures: Table structure information list

    Returns:
        str: Formatted table structure description text
    """
    if not table_structures:
        return "No available table structure information"

    formatted = []
    for table in table_structures:
        formatted.append(
            f"Table name: {table['table_name']}\n"
            f"Description: {table.get('description', 'No description')}\n"
            f"Column information:\n{table['columns']}\n"
            f"Additional info: {table.get('additional_info', 'No additional info')}\n"
        )

    return "\n".join(formatted)


def format_results_preview(execution_result: Dict) -> str:
    """Format query results preview

    Format query results into readable table format.
    When results exceed 20 rows, return prompt information instead of displaying specific data.

    Args:
        execution_result: SQL execution result dictionary

    Returns:
        str: Formatted result preview text
    """
    if not execution_result.get('results'):
        return "No data"

    results = execution_result['results']
    columns = execution_result['columns']

    # If result set is too large, return prompt information
    if len(results) > 20:
        return f"Result set too large, not displaying specific data"

    # Build table format preview
    lines = []
    # Header
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("|" + "|".join(["-" * len(col) for col in columns]) + "|")
    # Data rows
    for row in results:
        lines.append("| " + " | ".join(str(row[col])
                                       for col in columns) + " |")

    return "\n".join(lines)


def format_full_results(execution_result: Dict) -> str:
    """Format complete query results

    Format query results into complete table format using tabulate to generate beautiful tables.

    Args:
        execution_result: SQL execution result dictionary

    Returns:
        str: Formatted complete result text
    """
    if not execution_result.get('results'):
        return "No data"

    results = execution_result['results']
    columns = execution_result['columns']

    # Convert results to row data list
    rows = []
    for row in results:
        rows.append([str(row[col]) for col in columns])

    # Generate table using tabulate
    # Use 'pipe' style for best display in notebooks
    table = tabulate(
        rows,
        headers=columns,
        tablefmt='pipe',  # Use pipe format for markdown table display in notebooks
        showindex=False,
        numalign='left',
        stralign='left'
    )
    
    return table
