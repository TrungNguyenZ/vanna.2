"""
Configuration loader for Vanna AI Agent.
Loads settings from environment variables.
"""
import os
from typing import Optional, Dict, Any
from pathlib import Path


class Config:
    """Configuration class for loading environment variables."""
    
    def __init__(self):
        """Load configuration from environment variables."""
        # AI Provider Configuration
        self.ai_provider = os.getenv("AI_PROVIDER", "anthropic").lower()
        
        # Anthropic
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        
        # OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        # Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        # Database Configuration
        self.db_type = os.getenv("DB_TYPE", "sqlite").lower()
        
        # SQLite
        self.sqlite_database_path = os.getenv("SQLITE_DATABASE_PATH", "./data/database.db")
        
        # PostgreSQL
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_database = os.getenv("POSTGRES_DATABASE", "")
        self.postgres_user = os.getenv("POSTGRES_USER", "")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "")
        self.postgres_schema = os.getenv("POSTGRES_SCHEMA", "public")
        
        # MySQL
        self.mysql_host = os.getenv("MYSQL_HOST", "localhost")
        self.mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
        self.mysql_database = os.getenv("MYSQL_DATABASE", "")
        self.mysql_user = os.getenv("MYSQL_USER", "")
        self.mysql_password = os.getenv("MYSQL_PASSWORD", "")
        
        # MSSQL
        self.mssql_host = os.getenv("MSSQL_HOST", "localhost")
        self.mssql_port = int(os.getenv("MSSQL_PORT", "1433"))
        self.mssql_database = os.getenv("MSSQL_DATABASE", "")
        self.mssql_user = os.getenv("MSSQL_USER", "")
        self.mssql_password = os.getenv("MSSQL_PASSWORD", "")
        self.mssql_driver = os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")
        
        # Server Configuration
        self.server_host = os.getenv("SERVER_HOST", "0.0.0.0")
        self.server_port = int(os.getenv("SERVER_PORT", "8001"))
        
        # Memory Configuration
        self.memory_type = os.getenv("MEMORY_TYPE", "chromadb")
        self.chroma_persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_memory")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on provider."""
        if self.ai_provider == "anthropic":
            return {
                "provider": "anthropic",
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model
            }
        elif self.ai_provider == "openai":
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model
            }
        elif self.ai_provider == "gemini":
            return {
                "provider": "gemini",
                "api_key": self.gemini_api_key,
                "model": self.gemini_model
            }
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration based on type."""
        if self.db_type == "sqlite":
            return {
                "type": "sqlite",
                "database_path": self.sqlite_database_path
            }
        elif self.db_type == "postgresql":
            return {
                "type": "postgresql",
                "host": self.postgres_host,
                "port": self.postgres_port,
                "database": self.postgres_database,
                "user": self.postgres_user,
                "password": self.postgres_password,
                "schema": self.postgres_schema
            }
        elif self.db_type == "mysql":
            return {
                "type": "mysql",
                "host": self.mysql_host,
                "port": self.mysql_port,
                "database": self.mysql_database,
                "user": self.mysql_user,
                "password": self.mysql_password
            }
        elif self.db_type == "mssql":
            return {
                "type": "mssql",
                "host": self.mssql_host,
                "port": self.mssql_port,
                "database": self.mssql_database,
                "user": self.mssql_user,
                "password": self.mssql_password,
                "driver": self.mssql_driver
            }
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def get_connection_string(self) -> Optional[str]:
        """Get database connection string."""
        if self.db_type == "postgresql":
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        elif self.db_type == "mysql":
            return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        elif self.db_type == "mssql":
            # ODBC connection string for MSSQL
            # TrustServerCertificate=yes: Trust the server certificate (bypass SSL verification)
            # Encrypt=yes: Enable encryption for the connection
            return f"DRIVER={{{self.mssql_driver}}};SERVER={self.mssql_host},{self.mssql_port};DATABASE={self.mssql_database};UID={self.mssql_user};PWD={self.mssql_password};Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30"
        return None


def load_config() -> Config:
    """Load configuration from .env file and return Config object."""
    from dotenv import load_dotenv
    
    # Try to load from .env file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try current directory
        load_dotenv()
    
    return Config()
