"""
Keyword extraction node module.
Responsible for extracting key business entities and terms from user queries.
"""

from pydantic import BaseModel, Field
from typing import List
import logging

from backend.sql_assistant.states.assistant_state import SQLAssistantState
from backend.sql_assistant.utils.format_utils import format_conversation_history
# Service function imports
from utils.services.llm import init_language_model, LanguageModelChain

logger = logging.getLogger(__name__)


class QueryKeywordExtraction(BaseModel):
    """Query keyword extraction result model"""
    keywords: List[str] = Field(
        default_factory=list,
        description="List of key entities extracted from the query"
    )


# System prompt for domain entity extraction
DOMAIN_ENTITY_EXTRACTION_PROMPT = """You are a professional data analyst responsible for extracting specific business entity names that require precise matching from user queries.

Extraction principles:
1. Only extract specific entity names that require exact matching in the database
2. These entities typically have uniqueness and specificity - replacing them with other names would lead to completely different query results

Do NOT extract:
1. Generic concept words (e.g., training, data, personnel, content)
2. Time-related expressions (e.g., 2023, last month)
3. Vague descriptive words (e.g., recent, all)
4. Common measurement units (e.g., quantity, amount, ratio)

Judgment criteria:
- Does this word need to be precisely matched against specific values in the database?
- Would replacing it with other words result in completely different query results?
- Does this word represent a unique business entity?

Output requirements:
1. Only output entity names that truly require exact matching
2. Return empty list if no entities requiring exact matching are found
3. Remove duplicates
4. Maintain original form of entity expressions"""

KEYWORD_EXTRACTION_USER_PROMPT = """Please extract specific business entity names that require exact matching from the following conversation:

Conversation history:
{dialogue_history}

Please extract key entities according to the rules in the system message and output results in the specified JSON format.
Note: Only extract entity names that need to be precisely matched against specific values in the database."""


def create_keyword_extraction_chain(temperature: float = 0.0) -> LanguageModelChain:
    """Create keyword extraction task chain

    Args:
        temperature: Model temperature parameter controlling output randomness

    Returns:
        LanguageModelChain: Configured keyword extraction task chain
    """
    llm = init_language_model(temperature=temperature)
    return LanguageModelChain(
        model_cls=QueryKeywordExtraction,
        sys_msg=DOMAIN_ENTITY_EXTRACTION_PROMPT,
        user_msg=KEYWORD_EXTRACTION_USER_PROMPT,
        model=llm,
    )()


def keyword_extraction_node(state: SQLAssistantState) -> dict:
    """Keyword extraction node function

    Extract key business entities and terms from user queries and conversation history.
    Includes business objects, metrics, and dimensions.

    Args:
        state: Current state object

    Returns:
        dict: State update containing extracted keywords
    """
    # Get conversation history
    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No message history found in state")

    # Format conversation history
    dialogue_history = format_conversation_history(messages)

    # Create extraction chain
    extraction_chain = create_keyword_extraction_chain()

    # Execute extraction
    result = extraction_chain.invoke({
        "dialogue_history": dialogue_history
    })

    logger.info(f"Extracted keywords: {result['keywords']}")

    # Update state
    return {
        "keywords": result["keywords"]
    }
