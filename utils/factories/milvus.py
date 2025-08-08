"""
Milvus connection factory module.

Provides unified Milvus vector database connection creation and management functionality.
"""

from typing import Optional, Dict, Any
from pymilvus import (
    connections,
    Collection,
    utility
)

from utils.core.logging_config import get_logger
from utils.core.error_handler import (
    DatabaseError,
    error_handler,
    ErrorLevel
)
from utils.core.streamlit_config import settings

logger = get_logger(__name__)


class MilvusConnection:
    """Milvus connection instance class.

    Encapsulates the state and operations of a single Milvus connection. Each instance
    represents an independent database connection, providing connection management,
    collection operations and other core functionalities.
    """

    def __init__(self, alias: str, connection_params: Dict[str, Any]):
        """Initialize Milvus connection.

        Args:
            alias: Connection alias
            connection_params: Connection parameters
        """
        self.alias = alias
        self.connection_params = connection_params
        self._is_connected = False

    def connect(self) -> bool:
        """Establish connection."""
        try:
            # If already connected, disconnect first
            if connections.has_connection(self.alias):
                connections.disconnect(self.alias)
                self._is_connected = False

            # Establish connection
            connections.connect(alias=self.alias, **self.connection_params)

            # Verify connection
            if not connections.has_connection(self.alias):
                raise DatabaseError("Unable to establish connection to Milvus")

            self._is_connected = True

            # Log connection info based on connection type
            if 'uri' in self.connection_params:
                # Mask sensitive parts of URI for logging
                uri = self.connection_params['uri']
                masked_uri = uri.split('@')[0] + "@***" if '@' in uri else uri
                logger.info(f"Milvus connection established: {masked_uri}/{self.connection_params['db_name']}")
            else:
                logger.info(
                    f"Milvus connection established: {self.connection_params['host']}:"
                    f"{self.connection_params['port']}/{self.connection_params['db_name']}"
                )
            return True

        except Exception as e:
            self._is_connected = False
            raise DatabaseError(f"Milvus connection failed: {str(e)}")

    def is_connected(self) -> bool:
        """Check if connection is established."""
        return connections.has_connection(self.alias) and self._is_connected

    def disconnect(self):
        """Disconnect from Milvus."""
        if connections.has_connection(self.alias):
            connections.disconnect(self.alias)
        self._is_connected = False

    def get_collection(self, collection_name: str) -> Collection:
        """Get collection object."""
        if not self.is_connected():
            raise DatabaseError("Milvus not connected, please establish connection first")

        if not utility.has_collection(collection_name):
            raise DatabaseError(f"Collection {collection_name} does not exist")

        collection = Collection(collection_name, using=self.alias)

        # Ensure collection is loaded
        if not self.is_collection_loaded(collection_name):
            collection.load()
            logger.info(f"Collection {collection_name} loaded into memory")

        return collection

    def is_collection_loaded(self, collection_name: str) -> bool:
        """Check if collection is loaded."""
        try:
            load_state = utility.load_state(collection_name, using=self.alias)
            return str(load_state) == "LoadState.Loaded"
        except Exception as e:
            logger.warning(f"Failed to check load state of collection {collection_name}: {str(e)}")
            return False


class MilvusFactory:
    """Milvus connection factory class.

    Designed with factory pattern, specifically responsible for creating and configuring
    Milvus connection instances. Supports connection parameter customization, intelligent
    caching and automatic connection management.
    """

    _connections_cache: Dict[str, MilvusConnection] = {}  # Cache for created connections

    @classmethod
    def _build_connection_params(cls,
                                db_name: Optional[str] = None,
                                host: Optional[str] = None,
                                port: Optional[int] = None,
                                username: Optional[str] = None,
                                password: Optional[str] = None,
                                uri: Optional[str] = None,
                                token: Optional[str] = None) -> Dict[str, Any]:
        """Build connection parameters.

        Args:
            db_name: Database name
            host: Host address
            port: Port number
            username: Username
            password: Password
            uri: Complete URI (for Zilliz Cloud)
            token: Authentication token (for Zilliz Cloud)

        Returns:
            Dict[str, Any]: Connection parameters dictionary
        """
        # Get default configuration
        vector_db_config = settings.vector_db

        # Priority 1: Use URI and token if provided (for Zilliz Cloud)
        if uri or (vector_db_config.uri and vector_db_config.token):
            connection_params = {
                "uri": uri or vector_db_config.uri,
                "db_name": db_name or vector_db_config.database
            }

            # Add token if provided
            auth_token = token or vector_db_config.token
            if auth_token:
                connection_params["token"] = auth_token

            return connection_params

        # Priority 2: Use traditional host/port parameters
        connection_params = {
            "host": host or vector_db_config.host,
            "port": port or vector_db_config.port,
            "db_name": db_name or vector_db_config.database
        }

        # Add authentication parameters
        auth_username = username or vector_db_config.username
        auth_password = password or vector_db_config.password

        if auth_username:
            connection_params["user"] = auth_username
        if auth_password:
            connection_params["password"] = auth_password

        return connection_params

    @classmethod
    @error_handler("Create Milvus connection", DatabaseError, ErrorLevel.ERROR)
    def create_connection(cls,
                         alias: Optional[str] = None,
                         db_name: Optional[str] = None,
                         host: Optional[str] = None,
                         port: Optional[int] = None,
                         username: Optional[str] = None,
                         password: Optional[str] = None,
                         uri: Optional[str] = None,
                         token: Optional[str] = None,
                         auto_connect: bool = True) -> MilvusConnection:
        """Create Milvus connection instance.

        Args:
            alias: Connection alias, uses default if None
            db_name: Database name
            host: Host address
            port: Port number
            username: Username
            password: Password
            uri: Complete URI (for Zilliz Cloud)
            token: Authentication token (for Zilliz Cloud)
            auto_connect: Whether to automatically establish connection

        Returns:
            MilvusConnection: Milvus connection instance

        Raises:
            DatabaseError: Raised when connection creation fails
        """
        # Determine connection alias
        connection_alias = alias or "default"

        # Generate cache key
        cache_key = f"{connection_alias}_{db_name or 'default'}_{host or 'default'}_{port or 'default'}"

        # Check if connection exists in cache
        if cache_key in cls._connections_cache:
            cached_connection = cls._connections_cache[cache_key]
            if auto_connect and not cached_connection.is_connected():
                cached_connection.connect()
            logger.debug(f"Reusing cached Milvus connection: {connection_alias}")
            return cached_connection

        # Build connection parameters
        connection_params = cls._build_connection_params(
            db_name=db_name,
            host=host,
            port=port,
            username=username,
            password=password,
            uri=uri,
            token=token
        )

        # Create connection instance
        milvus_connection = MilvusConnection(connection_alias, connection_params)

        # Establish connection if auto_connect is enabled
        if auto_connect:
            milvus_connection.connect()

        # Cache connection instance
        cls._connections_cache[cache_key] = milvus_connection

        logger.info(f"Milvus connection instance created: {connection_alias}")
        return milvus_connection

    @classmethod
    def create_default_connection(cls, auto_connect: bool = True) -> MilvusConnection:
        """Create default configured Milvus connection.

        Creates connection instance using default parameters from system configuration.

        Args:
            auto_connect: Whether to automatically establish connection, defaults to True

        Returns:
            MilvusConnection: Configured Milvus connection instance
        """
        return cls.create_connection(auto_connect=auto_connect)

    @classmethod
    def create_collection_accessor(cls,
                                  collection_name: str,
                                  db_name: Optional[str] = None,
                                  alias: Optional[str] = None) -> Collection:
        """Create collection accessor (convenience method).

        Args:
            collection_name: Collection name
            db_name: Database name
            alias: Connection alias

        Returns:
            Collection: Milvus collection object
        """
        # Create connection
        connection = cls.create_connection(
            alias=alias,
            db_name=db_name,
            auto_connect=True
        )

        # Get collection
        return connection.get_collection(collection_name)
