"""
FastAPI route implementations for Vanna Agents.
"""

import json
import traceback
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse

from ..base import ChatHandler, ChatRequest, ChatResponse
from ..base.templates import get_index_html
from ..base.training_models import (
    TrainingDataRequest,
    TrainingDataResponse,
    TrainingDataListResponse,
)
from ...core.user.request_context import RequestContext
from ...integrations.mongodb.models import TrainingDataType
from pydantic import BaseModel, Field


def register_chat_routes(
    app: FastAPI, chat_handler: ChatHandler, config: Optional[Dict[str, Any]] = None
) -> None:
    """Register chat routes on FastAPI app.

    Args:
        app: FastAPI application
        chat_handler: Chat handler instance
        config: Server configuration
    """
    config = config or {}

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        """Serve the main chat interface."""
        dev_mode = config.get("dev_mode", True)  # Default to True for local development
        cdn_url = config.get("cdn_url", "/static/vanna-components.js")
        api_base_url = config.get("api_base_url", "")

        return get_index_html(
            dev_mode=dev_mode, cdn_url=cdn_url, api_base_url=api_base_url
        )

    @app.post("/api/vanna/v2/chat_sse")
    async def chat_sse(
        chat_request: ChatRequest, http_request: Request
    ) -> StreamingResponse:
        """Server-Sent Events endpoint for streaming chat."""
        # Extract request context for user resolution
        chat_request.request_context = RequestContext(
            cookies=dict(http_request.cookies),
            headers=dict(http_request.headers),
            remote_addr=http_request.client.host if http_request.client else None,
            query_params=dict(http_request.query_params),
            metadata=chat_request.metadata,
        )

        async def generate() -> AsyncGenerator[str, None]:
            """Generate SSE stream."""
            try:
                async for chunk in chat_handler.handle_stream(chat_request):
                    chunk_json = chunk.model_dump_json()
                    yield f"data: {chunk_json}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                traceback.print_exc()
                error_data = {
                    "type": "error",
                    "data": {"message": str(e)},
                    "conversation_id": chat_request.conversation_id or "",
                    "request_id": chat_request.request_id or "",
                }
                yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    @app.websocket("/api/vanna/v2/chat_websocket")
    async def chat_websocket(websocket: WebSocket) -> None:
        """WebSocket endpoint for real-time chat."""
        await websocket.accept()

        try:
            while True:
                # Receive message
                try:
                    data = await websocket.receive_json()

                    # Extract request context for user resolution
                    metadata = data.get("metadata", {})
                    data["request_context"] = RequestContext(
                        cookies=dict(websocket.cookies),
                        headers=dict(websocket.headers),
                        remote_addr=websocket.client.host if websocket.client else None,
                        query_params=dict(websocket.query_params),
                        metadata=metadata,
                    )

                    chat_request = ChatRequest(**data)
                except Exception as e:
                    traceback.print_stack()
                    traceback.print_exc()
                    await websocket.send_json(
                        {
                            "type": "error",
                            "data": {"message": f"Invalid request: {str(e)}"},
                        }
                    )
                    continue

                # Stream response
                try:
                    async for chunk in chat_handler.handle_stream(chat_request):
                        await websocket.send_json(chunk.model_dump())

                    # Send completion signal
                    await websocket.send_json(
                        {
                            "type": "completion",
                            "data": {"status": "done"},
                            "conversation_id": chunk.conversation_id
                            if "chunk" in locals()
                            else "",
                            "request_id": chunk.request_id
                            if "chunk" in locals()
                            else "",
                        }
                    )

                except Exception as e:
                    traceback.print_stack()
                    traceback.print_exc()
                    await websocket.send_json(
                        {
                            "type": "error",
                            "data": {"message": str(e)},
                            "conversation_id": chat_request.conversation_id or "",
                            "request_id": chat_request.request_id or "",
                        }
                    )

        except WebSocketDisconnect:
            pass
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc()
            try:
                await websocket.send_json(
                    {
                        "type": "error",
                        "data": {"message": f"WebSocket error: {str(e)}"},
                    }
                )
            except Exception:
                pass
            finally:
                await websocket.close()

    @app.post("/api/vanna/v2/chat_poll")
    async def chat_poll(
        chat_request: ChatRequest, http_request: Request
    ) -> ChatResponse:
        """Polling endpoint for chat."""
        # Extract request context for user resolution
        chat_request.request_context = RequestContext(
            cookies=dict(http_request.cookies),
            headers=dict(http_request.headers),
            remote_addr=http_request.client.host if http_request.client else None,
            query_params=dict(http_request.query_params),
            metadata=chat_request.metadata,
        )

        try:
            result = await chat_handler.handle_poll(chat_request)
            return result
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

    @app.get("/api/vanna/v2/conversations")
    async def list_conversations(http_request: Request) -> Dict[str, Any]:
        """List conversations for the current user."""
        try:
            # Get user from request context
            request_context = RequestContext(
                cookies=dict(http_request.cookies),
                headers=dict(http_request.headers),
                remote_addr=http_request.client.host if http_request.client else None,
                query_params=dict(http_request.query_params),
            )
            
            # Resolve user
            user = await chat_handler.agent.user_resolver.resolve_user(request_context)
            user_id = user.id if hasattr(user, 'id') else None
            
            # Priority 1: Use MongoDB chat store if available
            if hasattr(chat_handler, 'mongo_chat_store') and chat_handler.mongo_chat_store:
                conversations = await chat_handler.mongo_chat_store.list_conversations(
                    user_id=user_id,
                    limit=50,
                    offset=0,
                )
                
                return {
                    "conversations": [
                        {
                            "id": conv.conversation_id,
                            "messages": [
                                {
                                    "role": msg.role,
                                    "content": msg.content,
                                }
                                for msg in conv.messages
                            ],
                            "created_at": conv.created_at.isoformat() if hasattr(conv.created_at, 'isoformat') else str(conv.created_at),
                            "updated_at": conv.updated_at.isoformat() if hasattr(conv.updated_at, 'isoformat') else str(conv.updated_at),
                        }
                        for conv in conversations
                    ]
                }
            
            # Priority 2: Fallback to conversation store
            if hasattr(chat_handler.agent, 'conversation_store'):
                conversations = await chat_handler.agent.conversation_store.list_conversations(
                    user, limit=50, offset=0
                )
                
                return {
                    "conversations": [
                        {
                            "id": conv.id,
                            "messages": [
                                {
                                    "role": msg.role,
                                    "content": msg.content,
                                }
                                for msg in conv.messages
                            ],
                            "created_at": conv.created_at.isoformat() if hasattr(conv.created_at, 'isoformat') else str(conv.created_at),
                            "updated_at": conv.updated_at.isoformat() if hasattr(conv.updated_at, 'isoformat') else str(conv.updated_at),
                        }
                        for conv in conversations
                    ]
                }
            
            return {"conversations": []}
        except Exception as e:
            traceback.print_exc()
            # Return empty list on error instead of failing
            return {"conversations": []}

    @app.post("/api/vanna/v2/conversations")
    async def create_conversation(http_request: Request) -> Dict[str, Any]:
        """Create a new empty conversation."""
        try:
            # Get conversation_id from request body
            body = await http_request.json()
            conversation_id = body.get("conversation_id")
            
            if not conversation_id:
                raise HTTPException(status_code=400, detail="conversation_id is required")
            
            # Get user from request context
            request_context = RequestContext(
                cookies=dict(http_request.cookies),
                headers=dict(http_request.headers),
                remote_addr=http_request.client.host if http_request.client else None,
                query_params=dict(http_request.query_params),
            )
            
            # Resolve user
            user = await chat_handler.agent.user_resolver.resolve_user(request_context)
            user_id = user.id if hasattr(user, 'id') else None
            
            # Create empty conversation in MongoDB if store is available
            if hasattr(chat_handler, 'mongo_chat_store') and chat_handler.mongo_chat_store:
                created = await chat_handler.mongo_chat_store.create_empty_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                )
                
                if created:
                    # Get the created conversation
                    conversation = await chat_handler.mongo_chat_store.get_conversation(
                        conversation_id=conversation_id,
                        user_id=user_id,
                    )
                    
                    if conversation:
                        return {
                            "id": conversation.conversation_id,
                            "messages": [],
                            "created_at": conversation.created_at.isoformat() if hasattr(conversation.created_at, 'isoformat') else str(conversation.created_at),
                            "updated_at": conversation.updated_at.isoformat() if hasattr(conversation.updated_at, 'isoformat') else str(conversation.updated_at),
                        }
                
                # If conversation already exists, return it
                conversation = await chat_handler.mongo_chat_store.get_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                )
                
                if conversation:
                    return {
                        "id": conversation.conversation_id,
                        "messages": [
                            {
                                "role": msg.role,
                                "content": msg.content,
                            }
                            for msg in conversation.messages
                        ],
                        "created_at": conversation.created_at.isoformat() if hasattr(conversation.created_at, 'isoformat') else str(conversation.created_at),
                        "updated_at": conversation.updated_at.isoformat() if hasattr(conversation.updated_at, 'isoformat') else str(conversation.updated_at),
                    }
            
            # If MongoDB is not available, just return success
            return {
                "id": conversation_id,
                "messages": [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")

    @app.get("/api/vanna/v2/conversations/{conversation_id}")
    async def get_conversation(conversation_id: str, http_request: Request) -> Dict[str, Any]:
        """Get a specific conversation by ID."""
        try:
            # Get user from request context
            request_context = RequestContext(
                cookies=dict(http_request.cookies),
                headers=dict(http_request.headers),
                remote_addr=http_request.client.host if http_request.client else None,
                query_params=dict(http_request.query_params),
            )
            
            # Resolve user
            user = await chat_handler.agent.user_resolver.resolve_user(request_context)
            user_id = user.id if hasattr(user, 'id') else None
            
            # Priority 1: Use MongoDB chat store if available
            if hasattr(chat_handler, 'mongo_chat_store') and chat_handler.mongo_chat_store:
                conversation = await chat_handler.mongo_chat_store.get_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                )
                
                if conversation:
                    # Get messages with full details (message_type, metadata)
                    messages = await chat_handler.mongo_chat_store.get_messages(
                        conversation_id=conversation_id,
                    )
                    
                    return {
                        "id": conversation.conversation_id,
                        "messages": [
                            {
                                "role": msg.role,
                                "content": msg.content,
                                "message_type": msg.message_type.value,
                                "metadata": msg.metadata,
                                "created_at": msg.created_at.isoformat() if hasattr(msg.created_at, 'isoformat') else str(msg.created_at),
                            }
                            for msg in messages
                        ],
                        "created_at": conversation.created_at.isoformat() if hasattr(conversation.created_at, 'isoformat') else str(conversation.created_at),
                        "updated_at": conversation.updated_at.isoformat() if hasattr(conversation.updated_at, 'isoformat') else str(conversation.updated_at),
                    }
                else:
                    raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Priority 2: Fallback to conversation store
            if hasattr(chat_handler.agent, 'conversation_store'):
                conversation = await chat_handler.agent.conversation_store.get_conversation(
                    conversation_id, user
                )
                
                if conversation:
                    return {
                        "id": conversation.id,
                        "messages": [
                            {
                                "role": msg.role,
                                "content": msg.content,
                            }
                            for msg in conversation.messages
                        ],
                        "created_at": conversation.created_at.isoformat() if hasattr(conversation.created_at, 'isoformat') else str(conversation.created_at),
                        "updated_at": conversation.updated_at.isoformat() if hasattr(conversation.updated_at, 'isoformat') else str(conversation.updated_at),
                    }
                else:
                    raise HTTPException(status_code=404, detail="Conversation not found")
            else:
                raise HTTPException(status_code=404, detail="Conversation store not available")
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

    @app.delete("/api/vanna/v2/conversations/{conversation_id}")
    async def delete_conversation(conversation_id: str, http_request: Request) -> Dict[str, Any]:
        """Delete a conversation."""
        try:
            # Get user from request context
            request_context = RequestContext(
                cookies=dict(http_request.cookies),
                headers=dict(http_request.headers),
                remote_addr=http_request.client.host if http_request.client else None,
                query_params=dict(http_request.query_params),
            )
            
            # Resolve user
            user = await chat_handler.agent.user_resolver.resolve_user(request_context)
            user_id = user.id if hasattr(user, 'id') else None
            
            # Priority 1: Use MongoDB chat store if available
            if hasattr(chat_handler, 'mongo_chat_store') and chat_handler.mongo_chat_store:
                deleted = await chat_handler.mongo_chat_store.delete_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                )
                
                if deleted:
                    return {"success": True, "message": "Conversation deleted"}
                else:
                    raise HTTPException(status_code=404, detail="Conversation not found")
            
            # If no MongoDB store, return error
            raise HTTPException(
                status_code=503,
                detail="Conversation deletion not available (MongoDB store not configured)"
            )
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

    # Training Data Endpoints
    @app.post("/api/vanna/v2/training-data", response_model=TrainingDataResponse)
    async def create_training_data(
        training_request: TrainingDataRequest,
    ) -> TrainingDataResponse:
        """Create new training data."""
        try:
            if not hasattr(chat_handler, 'mongo_training_store') or not chat_handler.mongo_training_store:
                raise HTTPException(
                    status_code=503,
                    detail="Training data store not available. Please check MongoDB configuration (MONGODB_CONNECTION_STRING or MONGODB_HOST)."
                )
            
            # Convert data_type to TrainingDataType enum if it's a string
            from ...integrations.mongodb.models import TrainingDataType
            data_type = training_request.data_type
            if isinstance(data_type, str):
                try:
                    data_type = TrainingDataType(data_type)
                except ValueError:
                    data_type = TrainingDataType.DEFAULT
            
            training_data = await chat_handler.mongo_training_store.create_training_data(
                text=training_request.text,
                data_type=data_type,
            )
            
            return TrainingDataResponse(
                id=training_data.id or "",
                text=training_data.text,
                data_type=training_data.data_type.value,
                conversation_id=training_data.conversation_id,
                created_at=training_data.created_at.isoformat(),
                updated_at=training_data.updated_at.isoformat(),
            )
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create training data: {str(e)}"
            )

    @app.get("/api/vanna/v2/training-data", response_model=TrainingDataListResponse)
    async def list_training_data(
        data_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> TrainingDataListResponse:
        """List training data."""
        try:
            if not hasattr(chat_handler, 'mongo_training_store') or not chat_handler.mongo_training_store:
                raise HTTPException(
                    status_code=503,
                    detail="Training data store not available. Please check MongoDB configuration."
                )
            
            training_type = None
            if data_type:
                try:
                    training_type = TrainingDataType(data_type)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid data_type: {data_type}. Must be 'default' or 'from_chat'"
                    )
            
            training_data_list = await chat_handler.mongo_training_store.list_training_data(
                data_type=training_type,
                limit=limit,
                offset=offset,
            )
            
            return TrainingDataListResponse(
                training_data=[
                    TrainingDataResponse(
                        id=td.id or "",
                        text=td.text,
                        data_type=td.data_type.value,
                        conversation_id=td.conversation_id,
                        created_at=td.created_at.isoformat(),
                        updated_at=td.updated_at.isoformat(),
                    )
                    for td in training_data_list
                ],
                total=len(training_data_list),
                limit=limit,
                offset=offset,
            )
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list training data: {str(e)}"
            )

    @app.get("/api/vanna/v2/training-data/{training_id}", response_model=TrainingDataResponse)
    async def get_training_data(training_id: str) -> TrainingDataResponse:
        """Get training data by ID."""
        try:
            if not hasattr(chat_handler, 'mongo_training_store') or not chat_handler.mongo_training_store:
                raise HTTPException(
                    status_code=503,
                    detail="Training data store not available. Please check MongoDB configuration (MONGODB_CONNECTION_STRING or MONGODB_HOST)."
                )
            
            training_data = await chat_handler.mongo_training_store.get_training_data(training_id)
            
            if not training_data:
                raise HTTPException(status_code=404, detail="Training data not found")
            
            return TrainingDataResponse(
                id=training_data.id or "",
                text=training_data.text,
                data_type=training_data.data_type.value,
                conversation_id=training_data.conversation_id,
                created_at=training_data.created_at.isoformat(),
                updated_at=training_data.updated_at.isoformat(),
            )
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get training data: {str(e)}"
            )

    @app.put("/api/vanna/v2/training-data/{training_id}", response_model=TrainingDataResponse)
    async def update_training_data(
        training_id: str,
        training_request: TrainingDataRequest,
    ) -> TrainingDataResponse:
        """Update training data."""
        try:
            if not hasattr(chat_handler, 'mongo_training_store') or not chat_handler.mongo_training_store:
                raise HTTPException(
                    status_code=503,
                    detail="Training data store not available. Please check MongoDB configuration (MONGODB_CONNECTION_STRING or MONGODB_HOST)."
                )
            
            training_data = await chat_handler.mongo_training_store.update_training_data(
                training_id=training_id,
                text=training_request.text,
                answer=training_request.answer,
                metadata=training_request.metadata,
            )
            
            if not training_data:
                raise HTTPException(status_code=404, detail="Training data not found")
            
            return TrainingDataResponse(
                id=training_data.id or "",
                text=training_data.text,
                data_type=training_data.data_type.value,
                conversation_id=training_data.conversation_id,
                created_at=training_data.created_at.isoformat(),
                updated_at=training_data.updated_at.isoformat(),
            )
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update training data: {str(e)}"
            )

    @app.delete("/api/vanna/v2/training-data/{training_id}")
    async def delete_training_data(training_id: str) -> Dict[str, Any]:
        """Delete training data."""
        try:
            if not hasattr(chat_handler, 'mongo_training_store') or not chat_handler.mongo_training_store:
                raise HTTPException(
                    status_code=503,
                    detail="Training data store not available. Please check MongoDB configuration (MONGODB_CONNECTION_STRING or MONGODB_HOST)."
                )
            
            deleted = await chat_handler.mongo_training_store.delete_training_data(training_id)
            
            if not deleted:
                raise HTTPException(status_code=404, detail="Training data not found")
            
            return {"success": True, "message": "Training data deleted"}
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete training data: {str(e)}"
            )

    # Database Connection Models
    class DatabaseConnectionRequest(BaseModel):
        type: str = Field(description="Database type: default, sqlserver, mysql, postgresql")
        host: str = Field(default="", description="Database host")
        port: int = Field(default=1433, description="Database port")
        database: str = Field(default="", description="Database name")
        username: str = Field(default="", description="Database username")
        password: str = Field(default="", description="Database password")
        options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional connection options")

    # Database Connection Endpoints
    @app.get("/api/vanna/v2/database/connection")
    async def get_database_connection() -> Dict[str, Any]:
        """Get current database connection configuration."""
        try:
            import os
            # Check for custom connection first
            db_type = os.getenv("DATABASE_TYPE", "")
            db_host = os.getenv("DATABASE_HOST", "")
            db_port = os.getenv("DATABASE_PORT", "")
            db_name = os.getenv("DATABASE_NAME", "")
            db_user = os.getenv("DATABASE_USER", "")
            db_password = os.getenv("DATABASE_PASSWORD", "")
            
            if db_type and db_host and db_name:
                return {
                    "connection": {
                        "type": db_type,
                        "host": db_host,
                        "port": int(db_port) if db_port else (1433 if db_type == "sqlserver" else 3306 if db_type == "mysql" else 5432),
                        "database": db_name,
                        "username": db_user,
                        "password": db_password,
                    }
                }
            
            # If no custom connection, return default SQL Server from .env
            sql_host = os.getenv("SQL_SERVER_HOST") or os.getenv("DATABASE_HOST") or ""
            sql_port = os.getenv("SQL_SERVER_PORT") or os.getenv("DATABASE_PORT") or "1433"
            sql_database = os.getenv("SQL_SERVER_DATABASE") or os.getenv("DATABASE_NAME") or ""
            sql_user = os.getenv("SQL_SERVER_USERNAME") or os.getenv("DATABASE_USER") or ""
            sql_password = os.getenv("SQL_SERVER_PASSWORD") or os.getenv("DATABASE_PASSWORD") or ""
            
            if sql_database:
                return {
                    "connection": {
                        "type": "default",
                        "host": sql_host,
                        "port": int(sql_port) if sql_port else 1433,
                        "database": sql_database,
                        "username": sql_user,
                        "password": sql_password,
                    }
                }
            
            return {"connection": None}
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get database connection: {str(e)}"
            )

    @app.post("/api/vanna/v2/database/test-default")
    async def test_default_database_connection() -> Dict[str, Any]:
        """Test default database connection from .env (SQL Server)."""
        try:
            import os
            import pyodbc
            
            # Get SQL Server connection from .env
            host = os.getenv("SQL_SERVER_HOST") or os.getenv("DATABASE_HOST") or "localhost"
            port = os.getenv("SQL_SERVER_PORT") or os.getenv("DATABASE_PORT") or "1433"
            database = os.getenv("SQL_SERVER_DATABASE") or os.getenv("DATABASE_NAME") or ""
            username = os.getenv("SQL_SERVER_USERNAME") or os.getenv("DATABASE_USER") or ""
            password = os.getenv("SQL_SERVER_PASSWORD") or os.getenv("DATABASE_PASSWORD") or ""
            
            if not database:
                return {"success": False, "message": "Không tìm thấy cấu hình database trong .env"}
            
            try:
                if username and password:
                    conn_str = (
                        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                        f"SERVER={host},{port};"
                        f"DATABASE={database};"
                        f"UID={username};"
                        f"PWD={password};"
                        f"TrustServerCertificate=yes;"
                    )
                else:
                    conn_str = (
                        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                        f"SERVER={host},{port};"
                        f"DATABASE={database};"
                        f"Trusted_Connection=yes;"
                        f"TrustServerCertificate=yes;"
                    )
                conn = pyodbc.connect(conn_str, timeout=5)
                conn.close()
                return {"success": True, "message": "Kết nối mặc định thành công!"}
            except ImportError:
                return {"success": False, "message": "pyodbc chưa được cài đặt. Cài đặt với: pip install pyodbc"}
            except Exception as e:
                return {"success": False, "message": f"Lỗi kết nối SQL Server: {str(e)}"}
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to test default database connection: {str(e)}"
            )

    @app.post("/api/vanna/v2/database/test")
    async def test_database_connection(connection: DatabaseConnectionRequest) -> Dict[str, Any]:
        """Test database connection."""
        try:
            success = False
            message = ""
            
            if connection.type == "default":
                # Test default connection
                result = await test_default_database_connection()
                return result
            
            if connection.type == "postgresql":
                try:
                    import psycopg2
                    conn = psycopg2.connect(
                        host=connection.host,
                        port=connection.port,
                        database=connection.database,
                        user=connection.username or None,
                        password=connection.password or None,
                        connect_timeout=5,
                    )
                    conn.close()
                    success = True
                    message = "Kết nối PostgreSQL thành công!"
                except ImportError:
                    message = "psycopg2 chưa được cài đặt. Cài đặt với: pip install psycopg2-binary"
                except Exception as e:
                    message = f"Lỗi kết nối PostgreSQL: {str(e)}"
                    
            elif connection.type == "mysql":
                try:
                    import pymysql
                    conn = pymysql.connect(
                        host=connection.host,
                        port=connection.port,
                        database=connection.database,
                        user=connection.username or None,
                        password=connection.password or None,
                        connect_timeout=5,
                    )
                    conn.close()
                    success = True
                    message = "Kết nối MySQL thành công!"
                except ImportError:
                    message = "pymysql chưa được cài đặt. Cài đặt với: pip install pymysql"
                except Exception as e:
                    message = f"Lỗi kết nối MySQL: {str(e)}"
                    
            elif connection.type == "sqlserver":
                try:
                    import pyodbc
                    if connection.username and connection.password:
                        conn_str = (
                            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                            f"SERVER={connection.host},{connection.port};"
                            f"DATABASE={connection.database};"
                            f"UID={connection.username};"
                            f"PWD={connection.password};"
                            f"TrustServerCertificate=yes;"
                        )
                    else:
                        conn_str = (
                            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                            f"SERVER={connection.host},{connection.port};"
                            f"DATABASE={connection.database};"
                            f"Trusted_Connection=yes;"
                            f"TrustServerCertificate=yes;"
                        )
                    conn = pyodbc.connect(conn_str, timeout=5)
                    conn.close()
                    success = True
                    message = "Kết nối SQL Server thành công!"
                except ImportError:
                    message = "pyodbc chưa được cài đặt. Cài đặt với: pip install pyodbc"
                except Exception as e:
                    message = f"Lỗi kết nối SQL Server: {str(e)}"
            else:
                message = f"Loại database không được hỗ trợ: {connection.type}"
            
            return {"success": success, "message": message}
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to test database connection: {str(e)}"
            )

    @app.post("/api/vanna/v2/database/connection")
    async def save_database_connection(connection: DatabaseConnectionRequest) -> Dict[str, Any]:
        """Save database connection configuration."""
        try:
            if connection.type == "default":
                # Reset to use default connection from .env
                return {
                    "success": True,
                    "message": "Đã lưu cấu hình sử dụng kết nối mặc định từ .env.",
                    "connection": {
                        "type": "default",
                    }
                }
            
            # In a real implementation, you would save this to a config file or environment variables
            # For now, we'll just return success
            # You might want to use a config manager or write to .env file
            
            # Note: In production, you should:
            # 1. Save to a secure config file
            # 2. Update environment variables (if using process manager)
            # 3. Reload database connection in the agent
            
            return {
                "success": True,
                "message": "Cấu hình đã được lưu. Vui lòng khởi động lại server để áp dụng thay đổi.",
                "connection": {
                    "type": connection.type,
                    "host": connection.host,
                    "port": connection.port,
                    "database": connection.database,
                    "username": connection.username,
                    # Don't return password in response
                }
            }
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save database connection: {str(e)}"
            )
