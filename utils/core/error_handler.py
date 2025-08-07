"""
Unified error handling module.

Provides consistent exception handling patterns and error message formatting.
"""

import logging
import functools
from typing import Dict, Any, Optional, Type, Union
from enum import Enum


class ErrorLevel(Enum):
    """Error level enumeration."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SQLAssistantError(Exception):
    """Base exception class for QueryBot."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        level: ErrorLevel = ErrorLevel.ERROR
    ):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.level = level
        super().__init__(self.message)


class DatabaseError(SQLAssistantError):
    """Database-related errors."""
    pass


class PermissionError(SQLAssistantError):
    """Permission-related errors."""
    pass


class ValidationError(SQLAssistantError):
    """Validation-related errors."""
    pass


class ProcessingError(SQLAssistantError):
    """Processing errors."""
    pass


def standardize_error_message(
    operation: str,
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """Standardize error message format.

    Args:
        operation: Operation description
        error: Original exception
        context: Additional context information

    Returns:
        str: Standardized error message
    """
    base_msg = f"{operation} failed: {str(error)}"

    if context:
        context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
        base_msg += f" (context: {context_str})"

    return base_msg


def log_and_raise(
    logger: logging.Logger,
    error_class: Type[SQLAssistantError],
    operation: str,
    original_error: Exception,
    context: Optional[Dict[str, Any]] = None,
    level: ErrorLevel = ErrorLevel.ERROR
) -> None:
    """Log and raise standardized exception.

    Args:
        logger: Logger instance
        error_class: Exception class to raise
        operation: Operation description
        original_error: Original exception
        context: Additional context information
        level: Error level
    """
    error_msg = standardize_error_message(operation, original_error, context)

    # Log based on level
    if level == ErrorLevel.CRITICAL:
        logger.critical(error_msg)
    elif level == ErrorLevel.ERROR:
        logger.error(error_msg)
    elif level == ErrorLevel.WARNING:
        logger.warning(error_msg)
    else:
        logger.info(error_msg)

    # Raise standardized exception
    raise error_class(
        message=error_msg,
        context=context,
        level=level
    )


def error_handler(
    operation: str,
    error_class: Type[SQLAssistantError] = ProcessingError,
    level: ErrorLevel = ErrorLevel.ERROR,
    return_dict: bool = False
):
    """Unified error handling decorator.

    Args:
        operation: Operation description
        error_class: Exception type
        level: Error level
        return_dict: Whether to return error dict instead of raising exception
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)

            try:
                return func(*args, **kwargs)
            except SQLAssistantError:
                # If already a standard exception, re-raise directly
                raise
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }

                if return_dict:
                    error_msg = standardize_error_message(operation, e, context)
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "error_type": error_class.__name__
                    }
                else:
                    log_and_raise(
                        logger=logger,
                        error_class=error_class,
                        operation=operation,
                        original_error=e,
                        context=context,
                        level=level
                    )
        return wrapper
    return decorator


def create_error_response(
    error: Union[str, Exception, SQLAssistantError],
    success: bool = False,
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized error response dictionary.

    Args:
        error: Error information
        success: Whether operation was successful
        additional_data: Additional data

    Returns:
        Dict[str, Any]: Standardized error response
    """
    response = {
        "success": success,
        "error": str(error),
        "error_type": type(error).__name__ if isinstance(error, Exception) else "GeneralError"
    }

    if isinstance(error, SQLAssistantError):
        response.update({
            "error_code": error.error_code,
            "context": error.context,
            "level": error.level.value
        })

    if additional_data:
        response.update(additional_data)

    return response