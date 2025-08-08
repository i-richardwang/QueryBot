"""
QueryBot API entry module.
Provides HTTP interfaces for external access to QueryBot services.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

from backend.sql_assistant.async_executor import (
    run_query_bot_async,
    request_tracker,
)
from langgraph.checkpoint.memory import MemorySaver
from backend.sql_assistant.utils.user_mapper import UserMapper
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from utils.core.streamlit_config import settings

# Setup logger
logger = logging.getLogger(__name__)

# Setup LLM cache
set_llm_cache(SQLiteCache(database_path="./data/llm_cache/langchain.db"))

if settings.monitoring.phoenix_enabled:
    from phoenix.otel import register
    from openinference.instrumentation.langchain import LangChainInstrumentor

    tracer_provider = register(
        project_name="query_bot",
        endpoint="http://localhost:6006/v1/traces",
    )
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

# FastAPI application
app = FastAPI(title="QueryBot API")


# Configuration
class Config:
    # User permission control (optional feature, set to False to skip user permission verification)
    USER_AUTH_ENABLED = settings.app.user_auth_enabled


class ChatResponse(BaseModel):
    text: str
    session_id: Optional[str] = None


# Global variables
checkpoint_saver = MemorySaver()
# User mapper (only used when user permission control is enabled)
user_mapper = UserMapper()


@app.post("/api/query-bot", response_model=ChatResponse)
async def process_query(request: Dict[str, Any] = Body(...)) -> ChatResponse:
    """Process SQL query requests"""
    # Generate request ID
    request_id = f"{request.get('username', 'anonymous')}_{hash(request.get('text', ''))}"

    try:
        text = request.get("text", "")
        username = request.get("username", "anonymous")
        session_id = request.get("session_id", None)

        # Check if the same request is being processed
        if await request_tracker.is_processing(request_id):
            return ChatResponse(
                text="Your previous query is being processed, please wait...", session_id=session_id
            )

        # Mark request as being processed
        await request_tracker.add_request(request_id)

        # Decide whether to perform user permission control based on environment variables
        user_id = None
        if Config.USER_AUTH_ENABLED:
            user_id = user_mapper.get_user_id(username)
            if user_id is None and username != "anonymous":
                raise HTTPException(
                    status_code=404,
                    detail="Sorry, you currently do not have access permissions. Please contact the data team to grant you relevant permissions.",
                )

        # Run QueryBot asynchronously
        result = await run_query_bot_async(
            query=text,
            thread_id=session_id,
            checkpoint_saver=checkpoint_saver,
            user_id=user_id,
        )

        # Get the last assistant message
        messages = result.get("messages", [])
        if not messages:
            raise ValueError("No assistant reply received")

        last_message = messages[-1].content

        return ChatResponse(
            text=last_message,
            session_id=result.get("thread_id", ""),
        )

    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Sorry, the system encountered a problem while processing your request. Please try again later. If the problem persists, please contact the data team for help.",
        )
    finally:
        # Remove request tracking
        await request_tracker.remove_request(request_id)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
