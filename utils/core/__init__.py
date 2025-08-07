"""
Core infrastructure module.

Provides core infrastructure for the project, including:
- Configuration management: Unified configuration loading and management
- Constant definitions: Project-level constants
- Error handling: Standardized exception handling mechanisms
- Logging configuration: Unified logging configuration
"""

from .config import settings, get_settings
from .constants import (
    DatabaseConstants,
    ErrorMessages,
    SuccessMessages,
    BusinessConstants,
    HttpStatusCodes,
    PathConstants,
    TimeFormats,
    RegexPatterns
)
from .error_handler import (
    SQLAssistantError,
    DatabaseError,
    PermissionError,
    ValidationError,
    ProcessingError,
    ErrorLevel,
    error_handler,
    create_error_response
)
from .logging_config import get_logger, setup_logging, log_operation_result, log_database_operation, log_function_call

__all__ = [
    # Configuration
    "settings",
    "get_settings",

    # Constants
    "DatabaseConstants",
    "ErrorMessages",
    "SuccessMessages",
    "BusinessConstants",
    "HttpStatusCodes",
    "PathConstants",
    "TimeFormats",
    "RegexPatterns",

    # Error handling
    "SQLAssistantError",
    "DatabaseError",
    "PermissionError",
    "ValidationError",
    "ProcessingError",
    "ErrorLevel",
    "error_handler",
    "create_error_response",

    # Logging
    "get_logger",
    "setup_logging",
    "log_operation_result",
    "log_database_operation",
    "log_function_call",
]