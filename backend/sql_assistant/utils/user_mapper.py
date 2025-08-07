"""
User mapping utility module.
Responsible for mapping queries between usernames and user IDs.
"""

import logging
from typing import Optional
from sqlalchemy import text

from utils.factories.database import DatabaseFactory

logger = logging.getLogger(__name__)

class UserMapper:
    """Username mapper

    Responsible for querying user IDs corresponding to usernames.
    """

    def __init__(self):
        """Initialize database connection"""
        self.engine = DatabaseFactory.get_default_engine()

    def get_user_id(self, username: str) -> Optional[int]:
        """Query user ID corresponding to username

        Args:
            username: Username

        Returns:
            Optional[int]: User ID, returns None if user does not exist
        """
        try:
            with self.engine.connect() as conn:
                query = text(
                    "SELECT user_id FROM user WHERE username = :username AND status = 1"
                )
                result = conn.execute(query, {"username": username}).fetchone()
                return result[0] if result else None

        except Exception as e:
            logger.error(f"Failed to query user ID: {str(e)}")
            return None