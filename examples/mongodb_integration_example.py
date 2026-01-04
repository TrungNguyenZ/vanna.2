"""
Example: MongoDB integration for chat history and training data.

This example shows how to:
1. Set up MongoDB connection
2. Configure chat handler with MongoDB stores
3. Use training data context enhancer
4. Save chat history and training data
"""

import asyncio
import os
from vanna.core import Agent
from vanna.integrations.mongodb import MongoDBConnection
from vanna.integrations.mongodb.chat_store import MongoChatStore
from vanna.integrations.mongodb.training_store import MongoTrainingStore
from vanna.core.enhancer.training_data_enhancer import TrainingDataContextEnhancer
from vanna.servers.base import ChatHandler
from vanna.servers.fastapi import VannaFastAPIServer

# Example: Set up MongoDB connection
# You can use connection string or individual parameters
mongo_connection = MongoDBConnection(
    connection_string=os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/"),
    database_name="vanna",
)

# Create stores
chat_store = MongoChatStore(mongo_connection)
training_store = MongoTrainingStore(mongo_connection)

# Create training data context enhancer
training_enhancer = TrainingDataContextEnhancer(training_store)

# Example: Create agent with training data enhancer
# (You'll need to configure your LLM service, tool registry, etc.)
# agent = Agent(
#     llm_service=...,
#     tool_registry=...,
#     user_resolver=...,
#     agent_memory=...,
#     llm_context_enhancer=training_enhancer,  # Use training data enhancer
# )

# Create chat handler with MongoDB stores
# chat_handler = ChatHandler(
#     agent=agent,
#     mongo_chat_store=chat_store,
#     mongo_training_store=training_store,
# )

# Create FastAPI server
# server = VannaFastAPIServer(agent=agent, config={})
# app = server.create_app()

# Example: Add training data manually
async def add_training_data_example():
    """Example of adding training data."""
    # Add default training data
    await training_store.create_training_data(
        question="What are the top 10 customers?",
        sql="SELECT TOP 10 * FROM customers ORDER BY revenue DESC",
        answer="The top 10 customers are listed by revenue.",
        data_type="default",
    )
    
    # Add training data from chat
    await training_store.create_training_data(
        question="How many orders were placed last month?",
        sql="SELECT COUNT(*) FROM orders WHERE order_date >= DATEADD(month, -1, GETDATE())",
        answer="There were 1,234 orders placed last month.",
        data_type="from_chat",
        conversation_id="conv_abc123",
    )

# Example: List training data
async def list_training_data_example():
    """Example of listing training data."""
    # List all training data
    all_data = await training_store.list_training_data(limit=10)
    
    # List only default training data
    default_data = await training_store.list_training_data(
        data_type="default",
        limit=10,
    )
    
    # List only from_chat training data
    chat_data = await training_store.list_training_data(
        data_type="from_chat",
        limit=10,
    )
    
    print(f"Total training data: {len(all_data)}")
    print(f"Default training data: {len(default_data)}")
    print(f"Chat training data: {len(chat_data)}")

# Example: Search training data
async def search_training_data_example():
    """Example of searching training data."""
    results = await training_store.search_training_data(
        query="top customers",
        limit=5,
    )
    
    for result in results:
        print(f"Question: {result.question}")
        print(f"Answer: {result.answer}")

if __name__ == "__main__":
    # Run examples
    asyncio.run(add_training_data_example())
    asyncio.run(list_training_data_example())
    asyncio.run(search_training_data_example())


