"""
MongoDB connection and database management.
"""

import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pymongo import MongoClient
    from pymongo.database import Database
    from pymongo.collection import Collection

try:
    from pymongo import MongoClient
    from pymongo.database import Database
    from pymongo.collection import Collection
    
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    # Define dummy types for type checking when pymongo is not available
    MongoClient = None  # type: ignore
    Database = None  # type: ignore
    Collection = None  # type: ignore


class MongoDBConnection:
    """MongoDB connection manager."""
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        database_name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB connection string (mongodb://...)
            database_name: Database name (default: "vanna" or from MONGODB_DATABASE_NAME env)
            host: MongoDB host (if not using connection_string)
            port: MongoDB port (default: 27017 or from MONGODB_PORT env)
            username: MongoDB username (if not using connection_string)
            password: MongoDB password (if not using connection_string)
        """
        if not MONGO_AVAILABLE:
            raise ImportError(
                "pymongo is required for MongoDB integration. "
                "Install with: pip install pymongo"
            )
        
        # Get values from environment variables if not provided
        if not connection_string:
            connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        
        if not database_name:
            database_name = os.getenv("MONGODB_DATABASE_NAME", "vanna")
        
        if not host:
            host = os.getenv("MONGODB_HOST")
        
        if port is None:
            port_str = os.getenv("MONGODB_PORT")
            port = int(port_str) if port_str else 27017
        
        if not username:
            username = os.getenv("MONGODB_USERNAME")
        
        if not password:
            password = os.getenv("MONGODB_PASSWORD")
        
        # Connect to MongoDB
        if connection_string:
            self.client = MongoClient(connection_string)
        elif host:
            # Nếu có username và password, sử dụng authentication
            if username and password:
                self.client = MongoClient(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                )
            else:
                # Không có authentication, kết nối trực tiếp
                self.client = MongoClient(host=host, port=port)
        else:
            # Default to localhost (không có authentication)
            self.client = MongoClient("mongodb://localhost:27017/")
        
        self.database: Database = self.client[database_name]
        
    def get_collection(self, collection_name: str):  # type: ignore
        """Get a MongoDB collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            MongoDB collection
        """
        return self.database[collection_name]
    
    def close(self):
        """Close MongoDB connection."""
        self.client.close()

