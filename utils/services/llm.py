"""
LLM service module.
Specialized in handling language model initialization, configuration, and call chain management.
"""

import os
import logging
from typing import Any, Optional, Type
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from utils.core.logging_config import get_logger

logger = get_logger(__name__)


def init_language_model(
    temperature: float = 0.0,
    model_name: Optional[str] = None,
    **kwargs: Any
) -> ChatOpenAI:
    """
    Initialize language model with simplified configuration.

    Args:
        temperature: Model output temperature, controls randomness. Default is 0.0.
        model_name: Model name, if not provided uses settings from configuration file
        **kwargs: Other optional parameters, will be passed to model initialization.

    Returns:
        Initialized language model instance.

    Raises:
        ValueError: Raised when provided parameters are invalid or necessary configuration is missing.
    """
    from utils.core.config import settings

    llm_config = settings.llm
    model_name = model_name or llm_config.model

    # Get API configuration
    openai_api_key = settings.get_llm_api_key()
    openai_api_base = settings.get_llm_api_base()

    if not openai_api_key or not openai_api_base:
        raise ValueError(
            "Unable to find LLM API key or base URL. Please check environment variables or configuration file settings."
        )

    model_params = {
        "model": model_name,
        "openai_api_key": openai_api_key,
        "openai_api_base": openai_api_base,
        "temperature": temperature,
        'max_tokens': 1024,
        **kwargs,
    }

    logger.info(f"Initializing LLM: model={model_name}")
    return ChatOpenAI(**model_params)


class LanguageModelChain:
    """
    Language model chain for processing input and generating output conforming to specified schema.

    Attributes:
        model_cls: Pydantic model class defining the output structure.
        parser: JSON output parser.
        prompt_template: Chat prompt template.
        chain: Complete processing chain.
    """

    def __init__(
        self,
        model_cls: Type[BaseModel],
        sys_msg: str,
        user_msg: str,
        model: Any
    ):
        """
        Initialize LanguageModelChain instance.

        Args:
            model_cls: Pydantic model class defining the output structure.
            sys_msg: System message.
            user_msg: User message.
            model: Language model instance.

        Raises:
            ValueError: Raised when provided parameters are invalid.
        """
        if not issubclass(model_cls, BaseModel):
            raise ValueError("model_cls must be a subclass of Pydantic BaseModel")
        if not isinstance(sys_msg, str) or not isinstance(user_msg, str):
            raise ValueError("sys_msg and user_msg must be string types")
        if not callable(model):
            raise ValueError("model must be a callable object")

        self.model_cls = model_cls
        self.parser = JsonOutputParser(pydantic_object=model_cls)

        format_instructions = """
Output your answer as a JSON object that conforms to the following schema:
```json
{schema}
```

Important instructions:
1. Ensure your JSON is valid and properly formatted.
2. Do not include the schema definition in your answer.
3. Only output the data instance that matches the schema.
4. Do not include any explanations or comments within the JSON output.
        """

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", sys_msg + format_instructions),
                ("human", user_msg),
            ]
        ).partial(schema=model_cls.model_json_schema())

        self.chain = self.prompt_template | model | self.parser

        logger.debug(f"Created LanguageModelChain: model_cls={model_cls.__name__}")

    def __call__(self) -> Any:
        """
        Invoke the processing chain.

        Returns:
            Output of the processing chain.
        """
        return self.chain


def create_llm_chain(
    model_cls: Type[BaseModel],
    sys_msg: str,
    user_msg: str,
    **llm_kwargs
) -> LanguageModelChain:
    """
    Convenience function: Create complete LLM processing chain.

    Args:
        model_cls: Pydantic model class
        sys_msg: System message
        user_msg: User message
        **llm_kwargs: Parameters passed to init_language_model

    Returns:
        LanguageModelChain: Configured processing chain
    """
    model = init_language_model(**llm_kwargs)
    return LanguageModelChain(model_cls, sys_msg, user_msg, model)