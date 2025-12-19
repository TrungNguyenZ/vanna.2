"""Script để chạy Vanna server với FastAPI."""

from pathlib import Path
from config import load_config
from vanna import Agent, ToolRegistry, AgentConfig
from vanna.core.user import UserResolver, RequestContext, User
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.servers.fastapi import VannaFastAPIServer


class SimpleUserResolver(UserResolver):
    """Simple user resolver for demo - always returns the same test user."""

    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(
            id="user123",
            username="testuser",
            email="test@example.com",
            group_memberships=["user"],
        )


def create_llm_service(config):
    """Create LLM service based on configuration."""
    llm_config = config.get_llm_config()
    
    if llm_config["provider"] == "anthropic":
        from vanna.integrations.anthropic import AnthropicLlmService
        if not llm_config["api_key"]:
            raise ValueError("ANTHROPIC_API_KEY is not set in .env file")
        return AnthropicLlmService(
            api_key=llm_config["api_key"],
            model=llm_config["model"]
        )
    elif llm_config["provider"] == "openai":
        from vanna.integrations.openai import OpenAILlmService
        if not llm_config["api_key"]:
            raise ValueError("OPENAI_API_KEY is not set in .env file")
        return OpenAILlmService(
            api_key=llm_config["api_key"],
            model=llm_config["model"]
        )
    elif llm_config["provider"] == "gemini":
        from vanna.integrations.google import GeminiLlmService
        if not llm_config["api_key"]:
            raise ValueError("GEMINI_API_KEY is not set in .env file")
        return GeminiLlmService(
            api_key=llm_config["api_key"],
            model=llm_config["model"]
        )
    else:
        raise ValueError(f"Unsupported AI provider: {llm_config['provider']}")


def create_sql_runner(config):
    """Create SQL runner based on database configuration."""
    db_config = config.get_database_config()
    
    if db_config["type"] == "sqlite":
        from vanna.integrations.sqlite import SqliteRunner
        db_path = Path(db_config["database_path"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return SqliteRunner(database_path=str(db_path))
    
    elif db_config["type"] == "postgresql":
        from vanna.integrations.postgres import PostgresRunner
        return PostgresRunner(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
            schema=db_config.get("schema", "public")
        )
    
    elif db_config["type"] == "mysql":
        from vanna.integrations.mysql import MySQLRunner
        return MySQLRunner(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"]
        )
    
    elif db_config["type"] == "mssql":
        from vanna.integrations.mssql import MSSQLRunner
        conn_str = config.get_connection_string()
        return MSSQLRunner(odbc_conn_str=conn_str)
    
    else:
        raise ValueError(f"Unsupported database type: {db_config['type']}")


def create_agent(config):
    """Create and configure the Vanna agent."""
    print(f"Đang khởi tạo AI provider: {config.ai_provider}")
    llm_service = create_llm_service(config)
    
    print(f"Đang kết nối database: {config.db_type}")
    sql_runner = create_sql_runner(config)
    
    tool_registry = ToolRegistry()
    user_resolver = SimpleUserResolver()
    agent_memory = DemoAgentMemory(max_items=1000)
    
    # Create shared FileSystem for SQL tool (to save CSV) and visualization tool (to read CSV)
    from vanna.tools import LocalFileSystem
    file_system = LocalFileSystem(working_directory="./data_storage")
    
    # Register SQL execution tool with FileSystem (so it can save CSV files)
    from vanna.tools import RunSqlTool
    sql_tool = RunSqlTool(sql_runner=sql_runner, file_system=file_system)
    tool_registry.register_local_tool(sql_tool, access_groups=[])
    
    # Register visualization tool to create charts from CSV files
    from vanna.tools import VisualizeDataTool
    viz_tool = VisualizeDataTool(file_system=file_system)
    tool_registry.register_local_tool(viz_tool, access_groups=[])
    print("✓ Visualization tool đã được đăng ký - Agent có thể tạo biểu đồ từ kết quả SQL")
    
    # Use FileSystemConversationStore to persist conversation history
    # This allows the agent to understand context from previous messages in the conversation
    from vanna.integrations.local import FileSystemConversationStore
    conversation_store = FileSystemConversationStore(base_dir="./conversations")
    
    # SQL Error Recovery Strategy: Allow automatic retry with new SQL when SQL errors occur
    from sql_error_recovery import SqlErrorRecoveryStrategy
    sql_error_recovery = SqlErrorRecoveryStrategy(max_sql_retries=3)
    
    # Custom system prompt builder with SQL error retry instructions
    from custom_system_prompt import SqlErrorRetrySystemPromptBuilder
    system_prompt_builder = SqlErrorRetrySystemPromptBuilder()
    
    return Agent(
        llm_service=llm_service,
        tool_registry=tool_registry,
        user_resolver=user_resolver,
        agent_memory=agent_memory,
        conversation_store=conversation_store,  # Enable conversation persistence
        error_recovery_strategy=sql_error_recovery,  # Enable SQL error recovery
        system_prompt_builder=system_prompt_builder,  # Custom system prompt with SQL error retry
        config=AgentConfig(
            stream_responses=True,
            include_thinking_indicators=True,
            auto_save_conversations=True,  # Automatically save conversation history
        ),
    )


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Đang khởi động Vanna AI Server...")
        print("=" * 60)
        
        # Load configuration
        config = load_config()
        
        print(f"\nCấu hình:")
        print(f"  - AI Provider: {config.ai_provider} ({config.get_llm_config()['model']})")
        print(f"  - Database: {config.db_type}")
        print(f"  - Server: http://{config.server_host}:{config.server_port}")
        
        # Create agent
        agent = create_agent(config)
        print("\n✓ Agent đã được khởi tạo thành công!")
        
        # Start server
        print("\n" + "=" * 60)
        print("Đang khởi động FastAPI server...")
        print(f"Server URL: http://localhost:{config.server_port}")
        print(f"API Docs: http://localhost:{config.server_port}/docs")
        print("\nNhấn Ctrl+C để dừng server")
        print("=" * 60 + "\n")
        
        server = VannaFastAPIServer(agent)
        server.run(host=config.server_host, port=config.server_port)
        
    except ValueError as e:
        print(f"\n❌ Lỗi cấu hình: {e}")
        print("\nVui lòng kiểm tra file .env và đảm bảo các biến môi trường cần thiết đã được thiết lập.")
        print("Tham khảo file .env.example để xem cấu hình mẫu.")
    except ImportError as e:
        print(f"\n❌ Lỗi import: {e}")
        print("\nVui lòng cài đặt các package cần thiết:")
        print("  - Anthropic: pip install 'vanna[anthropic]'")
        print("  - OpenAI: pip install 'vanna[openai]'")
        print("  - PostgreSQL: pip install 'vanna[postgres]'")
        print("  - MySQL: pip install 'vanna[mysql]'")
        print("  - SQL Server: pip install 'vanna[mssql]'")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
