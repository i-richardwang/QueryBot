"""
Project constants definition module.
Centrally manages constant values used throughout the project.
"""

from enum import Enum


# Database related constants
class DatabaseConstants:
    """Database related constants"""
    # MySQL defaults
    MYSQL_DEFAULT_USER = 'root'
    MYSQL_DEFAULT_PORT = 3306

    # PostgreSQL defaults
    POSTGRESQL_DEFAULT_USER = 'postgres'
    POSTGRESQL_DEFAULT_PORT = 5432

    # Common defaults
    DEFAULT_HOST = 'localhost'
    DEFAULT_MILVUS_PORT = '19530'

    # Connection pool configuration
    DEFAULT_POOL_SIZE = 5
    DEFAULT_MAX_OVERFLOW = 10
    DEFAULT_POOL_RECYCLE_TIME = 3600  # 1 hour

    # Query related
    MAX_RESULT_ROWS = 100
    DEFAULT_TIMEOUT = 30  # seconds


# Error message constants
class ErrorMessages:
    """Standard error messages"""

    # Database errors
    DB_NAME_NOT_CONFIGURED = "Database name not configured"
    DB_CONNECTION_FAILED = "Database connection failed"
    DB_QUERY_FAILED = "Database query failed"

    # Milvus errors
    MILVUS_CONNECTION_FAILED = "Milvus connection failed"
    MILVUS_NOT_CONNECTED = "Milvus not connected, please call connect() method first"
    COLLECTION_NOT_EXISTS = "Collection does not exist"
    COLLECTION_LOAD_FAILED = "Collection loading failed"

    # Embedding errors
    EMBEDDING_API_KEY_MISSING = "Embedding API key not configured"
    EMBEDDING_API_BASE_MISSING = "Embedding API base URL not configured"
    EMBEDDING_MODEL_MISSING = "Embedding model name not configured"
    EMBEDDING_CREATION_FAILED = "Embedding model creation failed"

    # Permission errors
    USER_NOT_FOUND = "User not found"
    PERMISSION_DENIED = "Permission verification failed"
    UNAUTHORIZED_TABLE_ACCESS = "Unauthorized table access"

    # SQL execution errors
    SQL_NOT_FOUND = "SQL query statement not found in state"
    SQL_EXECUTION_FAILED = "SQL execution failed"
    MAX_RETRY_EXCEEDED = "Maximum retry limit reached"

    # System errors
    SYSTEM_ERROR = "System processing error"
    PROCESSING_ERROR = "Processing error occurred"
    UNKNOWN_ERROR = "Unknown error"


# Success message constants
class SuccessMessages:
    """Standard success messages"""

    # Connection success
    DB_CONNECTED = "Database connected successfully"
    MILVUS_CONNECTED = "Milvus connected successfully"
    EMBEDDING_INITIALIZED = "Embedding model initialized"

    # Operation success
    COLLECTION_LOADED = "Collection loaded successfully"
    SQL_EXECUTED = "SQL executed successfully"
    QUERY_PROCESSED = "Query processed successfully"


# Configuration constants are managed through utils.config.settings
# Use the centralized configuration system for all settings


# Business logic constants
class BusinessConstants:
    """Business logic related constants"""

    # Retry related
    MAX_SQL_RETRY = 2
    DEFAULT_RETRY_COUNT = 0

    # User related
    ANONYMOUS_USER = "anonymous"

    # Session related
    DEFAULT_THREAD_PREFIX = "thread_"

    # Node names
    NODE_INTENT_ANALYSIS = "intent_analysis"
    NODE_KEYWORD_EXTRACTION = "keyword_extraction"
    NODE_DOMAIN_TERM_MAPPING = "domain_term_mapping"
    NODE_QUERY_REWRITE = "query_rewrite"
    NODE_DATA_SOURCE_IDENTIFICATION = "data_source_identification"
    NODE_TABLE_STRUCTURE_ANALYSIS = "table_structure_analysis"
    NODE_FEASIBILITY_CHECKING = "feasibility_checking"
    NODE_QUERY_EXAMPLE_RETRIEVAL = "query_example_retrieval"
    NODE_SQL_GENERATION = "sql_generation"
    NODE_PERMISSION_CONTROL = "permission_control"
    NODE_SQL_EXECUTION = "sql_execution"
    NODE_ERROR_ANALYSIS = "error_analysis"
    NODE_RESULT_GENERATION = "result_generation"


# HTTP status code related
class HttpStatusCodes:
    """HTTP status code constants"""
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


# File path constants
class PathConstants:
    """File path related constants"""
    DATA_DIR = "./data"
    CACHE_DIR = "./data/llm_cache"
    LOG_DIR = "./logs"
    CONFIG_DIR = "./config"

    # Cache files
    LANGCHAIN_CACHE_DB = "./data/llm_cache/langchain.db"


# Time format constants
class TimeFormats:
    """Time format constants"""
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"


# Regular expression constants
class RegexPatterns:
    """Regular expression pattern constants"""
    TABLE_ALIAS_PATTERN = r"{table_name}\s+(?:AS\s+)?{alias}\b"
    TABLE_NAME_PATTERN = r"\b{table_name}\b"
    DEPT_PATH_PATTERN = "(^|>){dept_id}(>|$)"