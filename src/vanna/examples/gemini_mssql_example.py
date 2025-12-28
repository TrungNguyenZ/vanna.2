"""
Gemini AI example using SQL Server database.

This example demonstrates using the RunSqlTool with MSSQLRunner and Google Gemini AI
to intelligently query and analyze a SQL Server database.

Requirements:
- GOOGLE_API_KEY or GEMINI_API_KEY environment variable or .env file
- SQL Server database with ODBC connection string
- google-genai package: pip install 'vanna[gemini]'
- pyodbc and sqlalchemy packages: pip install pyodbc sqlalchemy

Usage:
  PYTHONPATH=. python -m vanna.examples.gemini_mssql_example
  Server: python -m vanna.servers --example gemini_mssql --port 8000
"""

import asyncio
import importlib.util
import os
import sys
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from vanna import Agent


def ensure_env() -> None:
    """Ensure required environment variables are set."""
    if importlib.util.find_spec("dotenv") is not None:
        from dotenv import load_dotenv

        # Load from local .env without overriding existing env
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"), override=False)
    else:
        print(
            "[warn] python-dotenv not installed; skipping .env load. Install with: pip install python-dotenv"
        )

    # Check for Google API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(
            "[error] GOOGLE_API_KEY or GEMINI_API_KEY is not set. Add it to your environment or .env file."
        )
        sys.exit(1)

    # Check for SQL Server connection string
    if not os.getenv("MSSQL_CONNECTION_STRING"):
        print(
            "[warn] MSSQL_CONNECTION_STRING is not set. Using example connection string."
        )
        print(
            "[info] Set MSSQL_CONNECTION_STRING in your environment or .env file."
        )
        print(
            "[info] Example: DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=YourDB;UID=username;PWD=password"
        )


async def main() -> None:
    """Run the Gemini SQL Server example."""
    ensure_env()

    try:
        from vanna.integrations.google import GeminiLlmService
    except ImportError:
        print(
            "[error] google-genai package is required. Install with: pip install 'vanna[gemini]'"
        )
        raise

    from vanna import AgentConfig, Agent, User
    from vanna.core.registry import ToolRegistry
    from vanna.core.user.resolver import UserResolver
    from vanna.core.user.request_context import RequestContext
    from vanna.core.recovery import ErrorRecoveryStrategy, RecoveryAction, RecoveryActionType
    from vanna.core.tool.models import ToolContext
    from vanna.integrations.mssql import MSSQLRunner
    from vanna.integrations.local.agent_memory import DemoAgentMemory
    from vanna.tools import RunSqlTool, VisualizeDataTool, LocalFileSystem

    # Get SQL Server connection string from environment
    # Example: DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=YourDB;UID=username;PWD=password
    odbc_conn_str = os.getenv(
        "MSSQL_CONNECTION_STRING",
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=master;UID=sa;PWD=YourPassword"
    )

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
    print(f"Using Gemini model: {model}")
    print(f"Connecting to SQL Server...")

    # Initialize Gemini LLM service
    llm = GeminiLlmService(
        model=model,
        api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
        temperature=0.7,
    )

    # Create shared FileSystem for tools
    file_system = LocalFileSystem(working_directory="./gemini_mssql_data")

    # Create tool registry and register the SQL tool with MSSQL runner
    tool_registry = ToolRegistry()
    try:
        mssql_runner = MSSQLRunner(odbc_conn_str=odbc_conn_str)
        sql_tool = RunSqlTool(sql_runner=mssql_runner, file_system=file_system)
        tool_registry.register(sql_tool)
        print("SQL Server connection established successfully!")
        
        # Register visualization tool
        try:
            viz_tool = VisualizeDataTool(file_system=file_system)
            tool_registry.register(viz_tool)
            print("Visualization tool registered successfully!")
        except ImportError:
            print("[warn] Visualization tool not available (plotly may not be installed)")
        except Exception as e:
            print(f"[warn] Failed to register visualization tool: {e}")
    except Exception as e:
        print(f"[error] Failed to connect to SQL Server: {e}")
        print(
            "[info] Please check your MSSQL_CONNECTION_STRING and ensure SQL Server is accessible."
        )
        sys.exit(1)

    class SimpleUserResolver(UserResolver):
        """Simple user resolver for demo purposes."""
        async def resolve_user(self, request_context: RequestContext) -> User:
            user_email = request_context.get_cookie("vanna_email", "demo@example.com")
            return User(
                id=user_email,
                email=user_email,
                group_memberships=["user"],
            )

    user_resolver = SimpleUserResolver()
    agent_memory = DemoAgentMemory(max_items=1000)

    agent = Agent(
        llm_service=llm,
        config=AgentConfig(
            stream_responses=False,  # Set to True for streaming in server mode
            include_thinking_indicators=True,
        ),
        tool_registry=tool_registry,
        user_resolver=user_resolver,
        agent_memory=agent_memory,
    )

    # Simulate a logged-in demo user via cookie-based resolver
    request_context = RequestContext(
        cookies={"vanna_email": "demo-user@example.com"},
        metadata={"demo": True},
        remote_addr="127.0.0.1",
    )
    conversation_id = "gemini-mssql-demo"

    # Sample queries to demonstrate different capabilities
    sample_questions = [
        "What tables are in this database?",
        "Show me the first 5 rows from the first table",
        "What's the schema of the database?",
    ]

    print("\n" + "=" * 60)
    print("Gemini SQL Server Database Assistant Demo")
    print("=" * 60)
    print("This demo shows Gemini querying a SQL Server database.")
    print("Gemini will intelligently construct SQL queries to answer questions.")
    print()

    for i, question in enumerate(sample_questions, 1):
        print(f"\n--- Question {i}: {question} ---")

        try:
            async for component in agent.send_message(
                request_context=request_context,
                message=question,
                conversation_id=conversation_id,
            ):
                # Handle different component types
                if hasattr(component, "simple_component") and component.simple_component:
                    if hasattr(component.simple_component, "text"):
                        print("Assistant:", component.simple_component.text)
                elif hasattr(component, "rich_component") and component.rich_component:
                    if (
                        hasattr(component.rich_component, "content")
                        and component.rich_component.content
                    ):
                        print("Assistant:", component.rich_component.content)
                elif hasattr(component, "content") and component.content:
                    print("Assistant:", component.content)
        except Exception as e:
            print(f"[error] Error processing question: {e}")

        print()  # Add spacing between questions

    print("\n" + "=" * 60)
    print("Demo complete! Gemini successfully queried the database.")
    print("=" * 60)


def create_demo_agent(config: Optional[Dict[str, Any]] = None) -> "Agent":
    """Create a demo agent with Gemini and SQL Server query tool.

    This function is called by the vanna server framework.

    Args:
        config: Optional configuration dict that may contain 'model' key

    Returns:
        Configured Agent with Gemini LLM and SQL Server tool
    """
    ensure_env()

    try:
        from vanna.integrations.google import GeminiLlmService
    except ImportError:
        print(
            "[error] google-genai package is required. Install with: pip install 'vanna[gemini]'"
        )
        raise

    from vanna import AgentConfig, Agent, User
    from vanna.core.registry import ToolRegistry
    from vanna.core.user.resolver import UserResolver
    from vanna.core.user.request_context import RequestContext
    from vanna.core.recovery import ErrorRecoveryStrategy, RecoveryAction, RecoveryActionType
    from vanna.core.tool.models import ToolContext
    from vanna.integrations.mssql import MSSQLRunner
    from vanna.integrations.local.agent_memory import DemoAgentMemory
    from vanna.tools import RunSqlTool, VisualizeDataTool, LocalFileSystem

    # Get SQL Server connection string from environment
    odbc_conn_str = os.getenv(
        "MSSQL_CONNECTION_STRING",
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=master;UID=sa;PWD=YourPassword"
    )

    # Get model from config (CLI parameter), environment variable, or default
    if config and "model" in config:
        model = config["model"]
    else:
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

    # Initialize Gemini LLM service
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required"
        )

    llm = GeminiLlmService(
        model=model,
        api_key=api_key,
        temperature=0.7,
    )

    # Create shared FileSystem for tools
    file_system = LocalFileSystem(working_directory="./gemini_mssql_data")

    # Create tool registry and register the SQL tool with MSSQL runner
    tool_registry = ToolRegistry()
    try:
        print(f"[info] Creating MSSQLRunner with connection string: {odbc_conn_str[:50]}...")
        mssql_runner = MSSQLRunner(odbc_conn_str=odbc_conn_str)
        print("[info] MSSQLRunner created successfully")
        
        sql_tool = RunSqlTool(sql_runner=mssql_runner, file_system=file_system)
        print(f"[info] RunSqlTool created with name: {sql_tool.name}")
        
        tool_registry.register(sql_tool)
        print(f"[info] [OK] SQL tool '{sql_tool.name}' registered successfully")
        
        # Register visualization tool
        try:
            viz_tool = VisualizeDataTool(file_system=file_system)
            tool_registry.register(viz_tool)
            print(f"[info] [OK] Visualization tool '{viz_tool.name}' registered successfully")
        except ImportError:
            print("[warn] Visualization tool not available (plotly may not be installed)")
        except Exception as e:
            print(f"[warn] Failed to register visualization tool: {e}")
        
        # Verify registration
        if sql_tool.name in tool_registry._tools:
            print(f"[info] [OK] Tool '{sql_tool.name}' confirmed in registry")
        else:
            print(f"[error] [FAIL] Tool '{sql_tool.name}' NOT found in registry!")
            
    except Exception as e:
        print(f"[error] Failed to create or register SQL tool: {e}")
        print(f"[error] Connection string: {odbc_conn_str[:50]}...")
        import traceback
        traceback.print_exc()
        raise

    class SimpleUserResolver(UserResolver):
        """Simple user resolver for demo purposes."""
        async def resolve_user(self, request_context: RequestContext) -> User:
            user_email = request_context.get_cookie("vanna_email", "demo@example.com")
            return User(
                id=user_email,
                email=user_email,
                group_memberships=["user"],
            )

    user_resolver = SimpleUserResolver()
    agent_memory = DemoAgentMemory(max_items=1000)

    # Create error recovery strategy for automatic retry
    class AutoRetryStrategy(ErrorRecoveryStrategy):
        """Automatically retry on errors, especially SQL column name errors."""
        
        async def handle_tool_error(
            self, error: Exception, context: ToolContext, attempt: int = 1
        ) -> RecoveryAction:
            """Retry tool errors automatically, especially for SQL errors."""
            error_msg = str(error).lower()
            
            # Retry on SQL errors (column name errors, syntax errors, etc.)
            if any(keyword in error_msg for keyword in ['column', 'invalid column', 'syntax', 'table', 'object']):
                if attempt < 3:  # Max 3 retries
                    return RecoveryAction(
                        action=RecoveryActionType.RETRY,
                        retry_delay_ms=500,  # Short delay for SQL errors
                        message=f"Retrying after SQL error (attempt {attempt}/3): {str(error)[:100]}"
                    )
            
            # For other errors, allow 2 retries
            if attempt < 2:
                return RecoveryAction(
                    action=RecoveryActionType.RETRY,
                    retry_delay_ms=1000,
                    message=f"Retrying after error (attempt {attempt}/2): {str(error)[:100]}"
                )
            
            # Max retries exceeded
            return RecoveryAction(
                action=RecoveryActionType.FAIL,
                message=f"Error after {attempt} attempts: {str(error)}"
            )
        
        async def handle_llm_error(
            self, error: Exception, request, attempt: int = 1
        ) -> RecoveryAction:
            """Retry LLM errors with backoff."""
            if attempt < 2:
                return RecoveryAction(
                    action=RecoveryActionType.RETRY,
                    retry_delay_ms=2000 * attempt,  # Exponential backoff
                    message=f"Retrying LLM call (attempt {attempt}/2)"
                )
            return RecoveryAction(
                action=RecoveryActionType.FAIL,
                message=f"LLM error after {attempt} attempts: {str(error)}"
            )

    error_recovery = AutoRetryStrategy()

    return Agent(
        llm_service=llm,
        config=AgentConfig(
            stream_responses=True,  # Enable streaming for web interface
            include_thinking_indicators=True,
            max_tool_iterations=15,  # Increase to allow more retries
        ),
        tool_registry=tool_registry,
        user_resolver=user_resolver,
        agent_memory=agent_memory,
        error_recovery_strategy=error_recovery,
    )


if __name__ == "__main__":
    asyncio.run(main())

