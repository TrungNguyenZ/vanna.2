"""
Flask server factory for Vanna Agents.
"""

import asyncio
from typing import Any, Dict, Optional

from flask import Flask
from flask_cors import CORS

from ...core import Agent
from ..base import ChatHandler
from .routes import register_chat_routes


class VannaFlaskServer:
    """Flask server factory for Vanna Agents."""

    def __init__(self, agent: Agent, config: Optional[Dict[str, Any]] = None):
        """Initialize Flask server.

        Args:
            agent: The agent to serve (must have user_resolver configured)
            config: Optional server configuration
        """
        self.agent = agent
        self.config = config or {}
        
        # Try to initialize MongoDB stores if MongoDB is configured
        mongo_chat_store = None
        mongo_training_store = None
        
        try:
            import os
            # Check if MongoDB connection string is available
            mongo_connection_string = os.getenv("MONGODB_CONNECTION_STRING")
            mongo_host = os.getenv("MONGODB_HOST")
            
            if mongo_connection_string or mongo_host:
                from ...integrations.mongodb import MongoDBConnection
                from ...integrations.mongodb.chat_store import MongoChatStore
                from ...integrations.mongodb.training_store import MongoTrainingStore
                
                # Create MongoDB connection
                mongo_connection = MongoDBConnection()
                
                # Create stores
                mongo_chat_store = MongoChatStore(mongo_connection)
                mongo_training_store = MongoTrainingStore(mongo_connection)
                
                # Integrate TrainingDataContextEnhancer into Agent
                # Create composite enhancer if agent already has an enhancer
                from ...core.enhancer import DefaultLlmContextEnhancer, CompositeLlmContextEnhancer
                from ...core.enhancer.training_data_enhancer import TrainingDataContextEnhancer
                
                training_enhancer = TrainingDataContextEnhancer(mongo_training_store)
                
                # If agent already has an enhancer, combine them
                if hasattr(agent, 'llm_context_enhancer') and agent.llm_context_enhancer:
                    existing_enhancer = agent.llm_context_enhancer
                    # Create composite enhancer
                    composite_enhancer = CompositeLlmContextEnhancer([
                        existing_enhancer,
                        training_enhancer,
                    ])
                    agent.llm_context_enhancer = composite_enhancer
                else:
                    # Use default enhancer + training enhancer
                    default_enhancer = DefaultLlmContextEnhancer(agent.agent_memory)
                    composite_enhancer = CompositeLlmContextEnhancer([
                        default_enhancer,
                        training_enhancer,
                    ])
                    agent.llm_context_enhancer = composite_enhancer
                
                print("MongoDB stores initialized successfully")
                print("TrainingDataContextEnhancer integrated into Agent")
        except ImportError:
            print("Warning: pymongo not installed. MongoDB features will be disabled.")
        except Exception as e:
            print(f"Warning: Failed to initialize MongoDB stores: {e}")
        
        self.chat_handler = ChatHandler(
            agent,
            mongo_chat_store=mongo_chat_store,
            mongo_training_store=mongo_training_store,
        )

    def create_app(self) -> Flask:
        """Create configured Flask app.

        Returns:
            Configured Flask application
        """
        # Check if dev mode is enabled - default to True for local development
        dev_mode = self.config.get("dev_mode", True)
        static_folder = self.config.get("static_folder", "frontends/webcomponent/dist")
        
        # Always try to serve static files if folder exists
        import os
        if os.path.exists(static_folder):
            app = Flask(__name__, static_folder=static_folder, static_url_path="/static")
        else:
            app = Flask(__name__)

        # Apply configuration
        app.config.update(self.config.get("flask", {}))

        # Enable CORS if configured
        cors_config = self.config.get("cors", {})
        if cors_config.get("enabled", True):
            CORS(app, **{k: v for k, v in cors_config.items() if k != "enabled"})

        # Register routes
        register_chat_routes(app, self.chat_handler, self.config)

        # Add health check
        @app.route("/health")
        def health_check() -> Dict[str, str]:
            return {"status": "healthy", "service": "vanna"}

        return app

    def run(self, **kwargs: Any) -> None:
        """Run the Flask server.

        This method automatically detects if running in an async environment
        (Jupyter, Colab, IPython, etc.) and:
        - Installs and applies nest_asyncio to handle existing event loops
        - Sets up port forwarding if in Google Colab
        - Displays the correct URL for accessing the app

        Args:
            **kwargs: Arguments passed to Flask.run()
        """
        import sys

        app = self.create_app()

        # Set defaults
        run_kwargs = {"host": "0.0.0.0", "port": 5000, "debug": False, **kwargs}

        # Get the port from run_kwargs
        port = run_kwargs.get("port", 5000)

        # Check if we're in an environment with a running event loop
        # (Jupyter, Colab, IPython, VS Code notebooks, etc.)
        in_async_env = False
        try:
            import asyncio

            try:
                asyncio.get_running_loop()
                in_async_env = True
            except RuntimeError:
                in_async_env = False
        except Exception:
            pass

        if in_async_env:
            # Apply nest_asyncio to allow nested event loops
            try:
                import nest_asyncio

                nest_asyncio.apply()
            except ImportError:
                print("Warning: nest_asyncio not installed. Installing...")
                import subprocess

                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "nest_asyncio"]
                )
                import nest_asyncio

                nest_asyncio.apply()

        # Check if we're specifically in Google Colab for port forwarding
        in_colab = "google.colab" in sys.modules

        if in_colab:
            try:
                from google.colab import output

                output.serve_kernel_port_as_window(port)
                from google.colab.output import eval_js

                print("Your app is running at:")
                print(eval_js(f"google.colab.kernel.proxyPort({port})"))
            except Exception as e:
                print(f"Warning: Could not set up Colab port forwarding: {e}")
                print(f"Your app is running at: http://localhost:{port}")
        else:
            print("Your app is running at:")
            print(f"http://localhost:{port}")

        app.run(**run_kwargs)
