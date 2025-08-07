"""
Query rewrite node module.
Responsible for rewriting user's original queries into standardized form.
"""

from pydantic import BaseModel, Field
import logging
from datetime import datetime

from backend.sql_assistant.states.assistant_state import SQLAssistantState
from backend.sql_assistant.utils.format_utils import (
    format_conversation_history,
    format_term_descriptions
)
# Service function imports
from utils.services.llm import init_language_model, LanguageModelChain

logger = logging.getLogger(__name__)


class QueryRewrite(BaseModel):
    """Query requirement rewrite result model"""
    rewritten_query: str = Field(
        ...,
        description="Rewritten query statement"
    )


# System prompt for query rewriting
QUERY_REWRITE_SYSTEM_PROMPT = """You are a professional data analyst responsible for rewriting user data query requirements into more standardized and clear forms.
Please follow these rules when rewriting queries:

Rewriting principles:
1. Maintain the core intent of the query unchanged, focus on user-expressed query requirements, do not include assistant's guiding questions in rewrite results
2. Use retrieved standard business terms to replace original non-standard terms (if they exist)
3. (If applicable) clearly specify the data scope of the query (time, region, etc.), but do not arbitrarily add scope restrictions not explicitly specified by the user
4. Clearly mark the attribution relationships of all query conditions
5. Standardize condition expressions
6. Remove irrelevant modifiers and tone words

Output requirements:
- Output a complete query sentence
- Use declarative sentence form
- Keep language concise and clear
- Ensure all necessary query conditions are included"""

QUERY_REWRITE_USER_PROMPT = """Please rewrite the user's query requirements based on the following information:

1. Conversation history:
{dialogue_history}

2. Business term information (if exists):
{term_descriptions}

3. Current date:
{current_date}

Please rewrite the query according to the rules in the system message and output results in the specified JSON format."""


def create_query_rewrite_chain(temperature: float = 0.0) -> LanguageModelChain:
    """Create query rewrite task chain

    Args:
        temperature: Model temperature parameter controlling output randomness

    Returns:
        LanguageModelChain: Configured query rewrite task chain
    """
    llm = init_language_model(temperature=temperature)

    return LanguageModelChain(
        model_cls=QueryRewrite,
        sys_msg=QUERY_REWRITE_SYSTEM_PROMPT,
        user_msg=QUERY_REWRITE_USER_PROMPT,
        model=llm,
    )()


def query_rewrite_node(state: SQLAssistantState) -> dict:
    """Query requirement rewrite node function

    Rewrite user's original query into standardized form,
    using standard business terms and clarifying query conditions and scope.

    Args:
        state: Current state object

    Returns:
        dict: State update containing rewritten query
    """
    # Get conversation history
    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No message history found in state")

    # Format conversation history
    dialogue_history = format_conversation_history(messages)

    # Format term descriptions
    term_descriptions = format_term_descriptions(
        state.get("domain_term_mappings", {})
    )

    # Create rewrite chain
    rewrite_chain = create_query_rewrite_chain()

    # Execute rewrite
    result = rewrite_chain.invoke({
        "dialogue_history": dialogue_history,
        "term_descriptions": term_descriptions,
        "current_date": datetime.now().strftime("%Y-%m-%d")
    })

    logger.info(f"Query rewrite completed, result: {result['rewritten_query']}")

    # Update state
    return {
        "rewritten_query": result["rewritten_query"]
    }
