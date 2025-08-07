"""
Unified logging configuration module.

Provides consistent log formatting and level settings.
"""

import os
import logging
import logging.config
from typing import Optional, Dict, Any


# Log format configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log level mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def get_log_level() -> int:
    """Get log level from environment."""
    level_name = os.environ.get('LOG_LEVEL', 'INFO').upper()
    return LOG_LEVELS.get(level_name, logging.INFO)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """Setup application logging configuration.

    Args:
        log_level: Log level
        log_file: Log file path
        enable_console: Whether to enable console output
    """
    level = LOG_LEVELS.get((log_level or 'INFO').upper(), logging.INFO)

    # Base configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': LOG_FORMAT,
                'datefmt': DATE_FORMAT
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                'datefmt': DATE_FORMAT
            }
        },
        'handlers': {},
        'root': {
            'level': level,
            'handlers': []
        },
        'loggers': {
            'backend.sql_assistant': {
                'level': level,
                'handlers': [],
                'propagate': True
            },
            'utils': {
                'level': level,
                'handlers': [],
                'propagate': True
            },
            'tools': {
                'level': level,
                'handlers': [],
                'propagate': True
            }
        }
    }

    # Console handler
    if enable_console:
        config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'level': level,
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        }
        config['root']['handlers'].append('console')

    # File handler
    if log_file:
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': level,
            'formatter': 'detailed',
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
        config['root']['handlers'].append('file')

    # Apply configuration
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance.

    Args:
        name: Logger name

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


def log_function_call(
    logger: logging.Logger,
    func_name: str,
    args: Optional[Dict[str, Any]] = None,
    level: int = logging.DEBUG
) -> None:
    """Log function call information.

    Args:
        logger: Logger instance
        func_name: Function name
        args: Function arguments
        level: Log level
    """
    if args:
        args_str = ", ".join([f"{k}={v}" for k, v in args.items()])
        message = f"Calling function {func_name}({args_str})"
    else:
        message = f"Calling function {func_name}()"

    logger.log(level, message)


def log_operation_result(
    logger: logging.Logger,
    operation: str,
    success: bool,
    details: Optional[str] = None,
    duration: Optional[float] = None
) -> None:
    """Log operation result.

    Args:
        logger: Logger instance
        operation: Operation description
        success: Whether operation was successful
        details: Additional details
        duration: Execution time in seconds
    """
    status = "succeeded" if success else "failed"
    message = f"{operation} {status}"

    if details:
        message += f": {details}"

    if duration is not None:
        message += f" (duration: {duration:.2f}s)"

    level = logging.INFO if success else logging.ERROR
    logger.log(level, message)


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table_name: Optional[str] = None,
    row_count: Optional[int] = None,
    success: bool = True,
    error: Optional[str] = None
) -> None:
    """Log database operation.

    Args:
        logger: Logger instance
        operation: Operation type (query, insert, update, etc.)
        table_name: Table name
        row_count: Number of affected rows
        success: Whether operation was successful
        error: Error message
    """
    message = f"Database {operation}"

    if table_name:
        message += f" - table: {table_name}"

    if success:
        if row_count is not None:
            message += f" - affected rows: {row_count}"
        logger.info(message)
    else:
        if error:
            message += f" - error: {error}"
        logger.error(message)


def init_default_logging():
    """Initialize default logging configuration."""
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    log_file = os.environ.get('LOG_FILE')

    setup_logging(
        log_level=log_level,
        log_file=log_file,
        enable_console=True
    )


# Auto-initialize
if not logging.getLogger().handlers:
    init_default_logging()