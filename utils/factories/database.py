"""
Database connection factory module.
Provides unified database connection creation and management functionality.
"""

from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import QueuePool

from utils.core.logging_config import get_logger
from utils.core.error_handler import (
    DatabaseError,
    ValidationError,
    error_handler,
    ErrorLevel
)
from utils.core.streamlit_config import settings

logger = get_logger(__name__)


class DatabaseFactory:
    """Database connection factory class

    Designed with factory pattern, specifically responsible for creating and configuring database engines and connections.
    Supports connection pool management, parameter customization, and intelligent caching mechanism.
    """

    _engines_cache: dict = {}  # Engine instance cache

    @classmethod
    @error_handler("Create database connection engine", DatabaseError, ErrorLevel.ERROR)
    def create_engine(cls,
                     database_name: Optional[str] = None,
                     pool_size: int = 5,
                     max_overflow: int = 10,
                     pool_recycle: int = 3600,
                     echo: bool = False) -> Engine:
        """Create database connection engine

        Args:
            database_name: Database name, if None uses default database from configuration
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            pool_recycle: Connection recycle time (seconds)
            echo: Whether to print SQL statements

        Returns:
            Engine: SQLAlchemy engine instance
            
        Raises:
            ValidationError: Raised when database configuration is incomplete
            DatabaseError: Raised when connection creation fails
        """
        # Get database configuration
        db_config = settings.database

        # Determine target database name
        target_db_name = database_name or db_config.name
        if not target_db_name:
            raise ValidationError("Database name not configured")

        # Generate cache key
        cache_key = f"{target_db_name}_{pool_size}_{max_overflow}_{pool_recycle}_{echo}"

        # Check if engine exists in cache
        if cache_key in cls._engines_cache:
            logger.debug(f"Reusing cached database engine: {target_db_name}")
            return cls._engines_cache[cache_key]

        # Build database connection URL
        # Priority 1: Use complete URL if provided
        if hasattr(db_config, 'url') and db_config.url:
            db_url = db_config.url
            # Convert generic postgresql:// to postgresql+psycopg2:// for SQLAlchemy
            if db_url.startswith('postgresql://'):
                db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
            elif db_url.startswith('mysql://'):
                db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)

            # If a specific database name is requested, we need to replace it in the URL
            if database_name and database_name != db_config.name:
                # This is a simplified approach - for complex URLs, consider using sqlalchemy.engine.url.make_url
                import re
                db_url = re.sub(r'/[^/?]+(\?|$)', f'/{database_name}\\1', db_url)
        else:
            # Priority 2: Build URL from individual components
            db_type = getattr(db_config, 'type', 'mysql').lower()

            if db_type == 'postgresql':
                db_url = (
                    f"postgresql+psycopg2://"
                    f"{db_config.user}:{db_config.password}@"
                    f"{db_config.host}:{db_config.port}/"
                    f"{target_db_name}"
                )
            elif db_type == 'mysql':
                db_url = (
                    f"mysql+pymysql://"
                    f"{db_config.user}:{db_config.password}@"
                    f"{db_config.host}:{db_config.port}/"
                    f"{target_db_name}"
                )
            else:
                raise ValidationError(f"Unsupported database type: {db_type}")

        # Create engine with connection pool configuration
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            pool_recycle=pool_recycle,
            echo=echo
        )

        # Cache engine
        cls._engines_cache[cache_key] = engine

        logger.info(
            f"Database engine created: {db_config.host}:{db_config.port}/{target_db_name}"
        )
        return engine
    
    @classmethod
    def create_connection(cls, engine: Optional[Engine] = None):
        """Create database connection

        Args:
            engine: Database engine, if None creates default engine

        Returns:
            Database connection object
        """
        if engine is None:
            engine = cls.create_engine()
        return engine.connect()

    @classmethod
    def get_default_engine(cls) -> Engine:
        """Get default configured database engine

        Creates database engine instance using default parameters from system configuration.

        Returns:
            Engine: Configured SQLAlchemy engine instance
        """
        return cls.create_engine()
