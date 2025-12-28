"""
Flask route implementations for Vanna Agents.
"""

import asyncio
import json
import traceback
from typing import Any, AsyncGenerator, Dict, Generator, Optional, Union

from flask import Flask, Response, jsonify, request

from ..base import ChatHandler, ChatRequest
from ..base.templates import get_index_html
from ...core.user.request_context import RequestContext


def register_chat_routes(
    app: Flask, chat_handler: ChatHandler, config: Optional[Dict[str, Any]] = None
) -> None:
    """Register chat routes on Flask app.

    Args:
        app: Flask application
        chat_handler: Chat handler instance
        config: Server configuration
    """
    config = config or {}

    @app.route("/")
    def index() -> str:
        """Serve the main chat interface."""
        dev_mode = config.get("dev_mode", True)  # Default to True for local development
        cdn_url = config.get("cdn_url", "/static/vanna-components.js")
        api_base_url = config.get("api_base_url", "")

        return get_index_html(
            dev_mode=dev_mode, cdn_url=cdn_url, api_base_url=api_base_url
        )

    @app.route("/api/vanna/v2/chat_sse", methods=["POST"])
    def chat_sse() -> Union[Response, tuple[Response, int]]:
        """Server-Sent Events endpoint for streaming chat."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON body required"}), 400

            # Extract request context for user resolution
            data["request_context"] = RequestContext(
                cookies=dict(request.cookies),
                headers=dict(request.headers),
                remote_addr=request.remote_addr,
                query_params=dict(request.args),
            )

            chat_request = ChatRequest(**data)
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc()
            return jsonify({"error": f"Invalid request: {str(e)}"}), 400

        def generate() -> Generator[str, None, None]:
            """Generate SSE stream."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:

                async def async_generate() -> AsyncGenerator[str, None]:
                    async for chunk in chat_handler.handle_stream(chat_request):
                        chunk_json = chunk.model_dump_json()
                        yield f"data: {chunk_json}\n\n"

                gen = async_generate()
                try:
                    while True:
                        chunk = loop.run_until_complete(gen.__anext__())
                        yield chunk
                except StopAsyncIteration:
                    yield "data: [DONE]\n\n"
            finally:
                loop.close()

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    @app.route("/api/vanna/v2/chat_websocket")
    def chat_websocket() -> tuple[Response, int]:
        """WebSocket endpoint placeholder."""
        return jsonify(
            {
                "error": "WebSocket endpoint not implemented in basic Flask example",
                "suggestion": "Use Flask-SocketIO for WebSocket support",
            }
        ), 501

    @app.route("/api/vanna/v2/chat_poll", methods=["POST"])
    def chat_poll() -> Union[Response, tuple[Response, int]]:
        """Polling endpoint for chat."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON body required"}), 400

            # Extract request context for user resolution
            data["request_context"] = RequestContext(
                cookies=dict(request.cookies),
                headers=dict(request.headers),
                remote_addr=request.remote_addr,
                query_params=dict(request.args),
            )

            chat_request = ChatRequest(**data)
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc()
            return jsonify({"error": f"Invalid request: {str(e)}"}), 400

        # Run async handler in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(chat_handler.handle_poll(chat_request))
            return jsonify(result.model_dump())
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc()
            return jsonify({"error": f"Chat failed: {str(e)}"}), 500
        finally:
            loop.close()

    @app.route("/api/vanna/v2/conversations", methods=["GET"])
    def list_conversations() -> Union[Response, tuple[Response, int]]:
        """List conversations for the current user."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Get user from request context
            request_context = RequestContext(
                cookies=dict(request.cookies),
                headers=dict(request.headers),
                remote_addr=request.remote_addr,
                query_params=dict(request.args),
            )
            
            # Resolve user
            user = loop.run_until_complete(chat_handler.agent.user_resolver.resolve_user(request_context))
            
            # Get conversations from conversation store
            if hasattr(chat_handler.agent, 'conversation_store'):
                conversations = loop.run_until_complete(
                    chat_handler.agent.conversation_store.list_conversations(user, limit=50, offset=0)
                )
                
                return jsonify({
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
                })
            else:
                return jsonify({"conversations": []})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"conversations": []})
        finally:
            loop.close()

    @app.route("/api/vanna/v2/conversations/<conversation_id>", methods=["GET"])
    def get_conversation(conversation_id: str) -> Union[Response, tuple[Response, int]]:
        """Get a specific conversation by ID."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Get user from request context
            request_context = RequestContext(
                cookies=dict(request.cookies),
                headers=dict(request.headers),
                remote_addr=request.remote_addr,
                query_params=dict(request.args),
            )
            
            # Resolve user
            user = loop.run_until_complete(chat_handler.agent.user_resolver.resolve_user(request_context))
            
            # Get conversation from conversation store
            if hasattr(chat_handler.agent, 'conversation_store'):
                conversation = loop.run_until_complete(
                    chat_handler.agent.conversation_store.get_conversation(conversation_id, user)
                )
                
                if conversation:
                    return jsonify({
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
                    })
                else:
                    return jsonify({"error": "Conversation not found"}), 404
            else:
                return jsonify({"error": "Conversation store not available"}), 404
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": f"Failed to get conversation: {str(e)}"}), 500
        finally:
            loop.close()
