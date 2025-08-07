"""
Intent analysis node module.
Responsible for analyzing the clarity of user query intent and determining if further clarification is needed.
"""

from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage
import logging

from backend.sql_assistant.states.assistant_state import SQLAssistantState
from backend.sql_assistant.utils.format_utils import format_conversation_history
# Service function imports
from utils.services.llm import init_language_model, LanguageModelChain

logger = logging.getLogger(__name__)


class QueryIntentAnalysis(BaseModel):
    """Query intent analysis result model"""
    is_intent_clear: bool = Field(
        ...,
        description="Whether the query intent is clear. True means intent is clear and can proceed; False means clarification needed"
    )
    clarification_question: Optional[str] = Field(
        None,
        description="Clarification question to ask the user when intent is unclear"
    )


INTENT_CLARITY_ANALYSIS_PROMPT = """
You are a professional data query assistant responsible for determining the executability of user data query requests. Please analyze the user's query intent with an open and pragmatic attitude.

Judgment criteria:
1. Clear query objective: Clearly understand what data the user wants to query
2. Complete query conditions: If filtering is needed, are the conditions clear (not mandatory)
3. Clear time range: If the query involves time, is the time range clear (not mandatory)
4. Allow the existence of unknown proprietary terms and domain terminology, which will be explained in subsequent steps
5. Be tolerant of vague but inferable queries

Output requirements:
1. If it's not a data query request, set is_intent_clear to false and generate a reply explaining that you can only handle data query related questions
2. If intent is clear, set is_intent_clear to true
3. If intent is unclear, set is_intent_clear to false and generate a specific question to obtain missing information
4. Questions should specifically point out missing information points for user understanding and response
"""

INTENT_ANALYSIS_USER_PROMPT = """Please analyze the following user's data query request:

User query:
{query}

Please output the analysis results in the specified JSON format according to the system instructions."""


def create_intent_clarity_analyzer(temperature: float = 0.0) -> LanguageModelChain:
    """Create intent clarity analyzer

    Build LLM chain for evaluating query intent clarity

    Args:
        temperature: Model temperature parameter controlling output randomness

    Returns:
        LanguageModelChain: Configured intent clarity analysis chain
    """
    llm = init_language_model(temperature=temperature)
    return LanguageModelChain(
        model_cls=QueryIntentAnalysis,
        sys_msg=INTENT_CLARITY_ANALYSIS_PROMPT,
        user_msg=INTENT_ANALYSIS_USER_PROMPT,
        model=llm,
    )()


def intent_analysis_node(state: SQLAssistantState) -> dict:
    """Node function for analyzing user query intent

    Analyze user's query request to determine if it contains sufficient information to execute the query.
    If intent is unclear, will generate clarification questions.

    Args:
        state: Current state object

    Returns:
        dict: State update containing intent analysis results
    """
    # Get all conversation history
    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No message history found in state")

    # Format conversation history
    dialogue_history = format_conversation_history(messages)

    # Add user query log
    logger.info(f"User query: {dialogue_history}")

    # Create analysis chain
    analysis_chain = create_intent_clarity_analyzer()

    # Execute analysis
    result = analysis_chain.invoke({"query": dialogue_history})
    logger.info(f"Intent analysis result: Intent clarity={result['is_intent_clear']}, Clarification question={result.get('clarification_question')}")

    # If intent is unclear, add an assistant message asking for clarification
    response = {}
    if not result["is_intent_clear"] and result.get("clarification_question"):
        response["messages"] = [
            AIMessage(content=result["clarification_question"])]

    # Update state
    response.update({
        "query_intent": {
            "is_clear": result["is_intent_clear"],
            "clarification_needed": not result["is_intent_clear"],
            "clarification_question": result["clarification_question"] if not result["is_intent_clear"] else None
        },
        "is_intent_clear": result["is_intent_clear"]
    })

    return response
