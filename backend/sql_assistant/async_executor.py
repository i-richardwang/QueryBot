"""
QueryBot asynchronous execution module.
Provides functionality for asynchronous execution of QueryBot tasks.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional

from backend.sql_assistant.graph.assistant_graph import run_query_bot

logger = logging.getLogger(__name__)

# Create thread pool executor
thread_pool = ThreadPoolExecutor(max_workers=3)


async def run_query_bot_async(
    query: str,
    thread_id: Optional[str] = None,
    checkpoint_saver: Optional[Any] = None,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Run QueryBot asynchronously

    Execute synchronous processing logic in thread pool to avoid blocking the event loop
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        thread_pool, run_query_bot, query, thread_id, checkpoint_saver, user_id
    )


# For managing requests being processed
class RequestTracker:
    def __init__(self):
        self._processing_requests = set()
        self._lock = asyncio.Lock()

    async def is_processing(self, request_id: str) -> bool:
        """Check if request is being processed"""
        async with self._lock:
            return request_id in self._processing_requests

    async def add_request(self, request_id: str):
        """Add request being processed"""
        async with self._lock:
            self._processing_requests.add(request_id)

    async def remove_request(self, request_id: str):
        """Remove completed request"""
        async with self._lock:
            self._processing_requests.discard(request_id)


# Create global request tracker
request_tracker = RequestTracker()
