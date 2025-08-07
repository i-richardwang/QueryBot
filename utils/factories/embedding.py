"""
Embedding factory module.

Provides unified Embedding model creation and management functionality.
"""

from typing import Optional
from langchain_openai import OpenAIEmbeddings

from utils.core.logging_config import get_logger
from utils.core.error_handler import (
    ValidationError,
    ProcessingError,
    error_handler,
    ErrorLevel
)
from utils.core.config import settings

logger = get_logger(__name__)


class EmbeddingFactory:
    """Text embedding model factory class.

    Simplified factory class that directly uses LangChain's official OpenAIEmbeddings.
    """

    @classmethod
    @error_handler("Create Embedding model", ProcessingError, ErrorLevel.ERROR)
    def create_embeddings(cls,
                         api_key: Optional[str] = None,
                         api_base: Optional[str] = None,
                         model: Optional[str] = None) -> OpenAIEmbeddings:
        """Create text embedding model instance.

        Args:
            api_key: API key, defaults to system configuration
            api_base: API base URL, defaults to system configuration
            model: Model name, defaults to system configuration

        Returns:
            OpenAIEmbeddings: Configured text embedding model instance

        Raises:
            ValidationError: Raised when model configuration is incomplete
            ProcessingError: Raised when model creation fails
        """
        # Get configuration information
        embedding_config = settings.embedding

        # Determine target parameters
        target_api_key = api_key or embedding_config.api_key
        target_api_base = api_base or embedding_config.api_base
        target_model = model or embedding_config.model

        # Parameter validation
        if not target_api_key or not target_api_base or not target_model:
            raise ValidationError("Text embedding model configuration incomplete")

        # Create OpenAIEmbeddings instance
        embeddings = OpenAIEmbeddings(
            openai_api_key=target_api_key,
            openai_api_base=target_api_base,
            model=target_model
        )

        logger.info(f"Text embedding model creation completed: {target_model}")
        return embeddings

    @classmethod
    def get_default_embeddings(cls) -> OpenAIEmbeddings:
        """Get default configured text embedding model.

        Creates text embedding model instance using default parameters from system configuration.

        Returns:
            OpenAIEmbeddings: Configured text embedding model instance
        """
        return cls.create_embeddings()

