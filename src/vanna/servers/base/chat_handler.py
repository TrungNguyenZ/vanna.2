"""
Framework-agnostic chat handling logic.
"""

import uuid
from typing import AsyncGenerator, List, Optional, TYPE_CHECKING

from ...core import Agent
from .models import ChatRequest, ChatResponse, ChatStreamChunk

if TYPE_CHECKING:
    from ...integrations.mongodb.chat_store import MongoChatStore
    from ...integrations.mongodb.training_store import MongoTrainingStore


class ChatHandler:
    """Core chat handling logic - framework agnostic."""

    def __init__(
        self,
        agent: Agent,
        mongo_chat_store: Optional["MongoChatStore"] = None,
        mongo_training_store: Optional["MongoTrainingStore"] = None,
    ):
        """Initialize chat handler.

        Args:
            agent: The agent to handle chat requests
            mongo_chat_store: Optional MongoDB chat store for saving history
            mongo_training_store: Optional MongoDB training store for saving training data
        """
        self.agent = agent
        self.mongo_chat_store = mongo_chat_store
        self.mongo_training_store = mongo_training_store

    async def handle_stream(
        self, request: ChatRequest
    ) -> AsyncGenerator[ChatStreamChunk, None]:
        """Stream chat responses.

        Args:
            request: Chat request

        Yields:
            Chat stream chunks
        """
        # Don't create conversation_id for starter UI requests
        # If conversation_id is empty and message is empty, it's likely a starter UI request
        is_starter_ui = (
            not request.conversation_id or request.conversation_id.strip() == ""
        ) and (
            not request.message or request.message.strip() == ""
        )
        
        if is_starter_ui:
            # Keep conversation_id empty for starter UI - don't create conversation
            conversation_id = ""
        else:
            # Create conversation_id if not provided and this is a real message
            conversation_id = request.conversation_id or self._generate_conversation_id()
        
        # Use request_id from client for tracking, or use the one generated internally
        request_id = request.request_id or str(uuid.uuid4())

        # Get user ID for MongoDB storage
        user_id = None
        try:
            user = await self.agent.user_resolver.resolve_user(request.request_context)
            user_id = user.id if hasattr(user, 'id') else None
        except Exception:
            pass

        # Save user message to MongoDB if store is available
        # Only save if message is not empty (skip starter UI requests)
        if self.mongo_chat_store and request.message and request.message.strip() and conversation_id:
            try:
                from ...integrations.mongodb.models import MessageType
                await self.mongo_chat_store.save_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=request.message,
                    user_id=user_id,
                    message_type=MessageType.TEXT,
                )
            except Exception as e:
                print(f"Warning: Failed to save user message to MongoDB: {e}")

        # Collect assistant response components for saving
        assistant_components = []
        
        async for component in self.agent.send_message(
            request_context=request.request_context,
            message=request.message,
            conversation_id=conversation_id,
        ):
            yield ChatStreamChunk.from_component(component, conversation_id, request_id)
            
            # Collect components for saving to MongoDB
            try:
                from ...integrations.mongodb.models import MessageType
                
                # Try to get serialized data
                rich_data = component.rich_component.serialize_for_frontend()
                if isinstance(rich_data, dict):
                    comp_type = rich_data.get('type', '')
                    comp_data = rich_data.get('data', {})
                    
                    # Determine message type from component type
                    message_type = MessageType.TEXT
                    metadata = {}
                    
                    if comp_type == 'code_block':
                        # Check if it's SQL
                        language = comp_data.get('language', '').lower()
                        if 'sql' in language:
                            message_type = MessageType.SQL
                            metadata = {'language': language, 'code': comp_data.get('code', '')}
                        else:
                            message_type = MessageType.TEXT
                            metadata = {'language': language, 'code': comp_data.get('code', '')}
                    elif comp_type == 'table' or comp_type == 'dataframe':
                        message_type = MessageType.TABLE
                        metadata = {'columns': comp_data.get('columns', []), 'data': comp_data.get('data', [])}
                    elif comp_type == 'chart':
                        message_type = MessageType.CHART
                        metadata = {'chart_type': comp_data.get('chart_type', ''), 'config': comp_data.get('config', {})}
                    elif comp_type in ['text', 'assistant-message']:
                        message_type = MessageType.TEXT
                    
                    # Get content
                    content = comp_data.get('content', '')
                    if not content and comp_type == 'code_block':
                        content = comp_data.get('code', '')
                    if not content and comp_type in ['table', 'dataframe']:
                        content = f"Table with {len(comp_data.get('data', []))} rows"
                    if not content and comp_type == 'chart':
                        content = f"Chart: {comp_data.get('chart_type', 'unknown')}"
                    
                    if content:
                        assistant_components.append({
                            'type': message_type,
                            'content': content,
                            'metadata': metadata,
                        })
            except Exception as e:
                # Fallback: try to get content directly
                try:
                    from ...integrations.mongodb.models import MessageType
                    if hasattr(component.rich_component, 'data'):
                        data = component.rich_component.data
                        if hasattr(data, 'content'):
                            assistant_components.append({
                                'type': MessageType.TEXT,
                                'content': str(data.content),
                                'metadata': {},
                            })
                except Exception:
                    pass

        # Save assistant response components to MongoDB if store is available
        # Only save if conversation_id is not empty (skip starter UI requests)
        if self.mongo_chat_store and assistant_components and conversation_id:
            try:
                from ...integrations.mongodb.models import MessageType
                for comp in assistant_components:
                    await self.mongo_chat_store.save_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=comp['content'],
                        user_id=user_id,
                        message_type=comp['type'],
                        metadata=comp['metadata'],
                    )
            except Exception as e:
                print(f"Warning: Failed to save assistant message to MongoDB: {e}")
        
        # Legacy: Also save combined text for backward compatibility
        # Only save if conversation_id is not empty (skip starter UI requests)
        if self.mongo_chat_store and assistant_components and conversation_id:
            try:
                # Combine all text content for legacy support
                text_parts = [c['content'] for c in assistant_components if c['type'] == MessageType.TEXT]
                if text_parts:
                    assistant_content = " ".join(text_parts)
                    # This will be saved as TEXT type, which is fine
                    pass  # Already saved above
            except Exception:
                pass

        # Save to training data if requested OR if SQL is present (auto-save SQL)
        # Only save if conversation_id is not empty (skip starter UI requests)
        if self.mongo_training_store and assistant_components and conversation_id:
            try:
                from ...integrations.mongodb.models import TrainingDataType, MessageType
                
                # Separate text and SQL components
                text_parts = [c['content'] for c in assistant_components if c['type'] == MessageType.TEXT]
                sql_parts = []
                
                # Collect SQL queries from multiple sources
                for comp in assistant_components:
                    if comp['type'] == MessageType.SQL:
                        # Try to get SQL code from metadata or content
                        sql_code = comp.get('metadata', {}).get('code', '') or comp.get('content', '')
                        if sql_code and sql_code.strip():
                            sql_parts.append(sql_code.strip())
                
                # Also check for SQL in code blocks that might not be detected as SQL type
                for comp in assistant_components:
                    if comp.get('type') == MessageType.TEXT:
                        metadata = comp.get('metadata', {})
                        language = metadata.get('language', '').lower()
                        code = metadata.get('code', '')
                        # If it's a code block with SQL-like language or contains SQL keywords
                        if ('sql' in language or 'mysql' in language or 'postgres' in language or 
                            'mssql' in language or 'tsql' in language) and code:
                            sql_parts.append(code.strip())
                        # Also check if content looks like SQL (contains SQL keywords)
                        elif code and any(keyword in code.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']):
                            sql_parts.append(code.strip())
                
                # Only save if there's SQL or if user explicitly requested
                has_sql = len(sql_parts) > 0
                should_save = request.save_to_training or has_sql
                
                if should_save:
                    # Build training text with question, answer, and SQL
                    training_parts = [f"Q: {request.message}"]
                    
                    if text_parts:
                        training_parts.append(f"A: {' '.join(text_parts)}")
                    
                    if sql_parts:
                        # Remove duplicates while preserving order
                        seen = set()
                        unique_sql = []
                        for sql in sql_parts:
                            sql_normalized = sql.strip().upper()
                            if sql_normalized not in seen:
                                seen.add(sql_normalized)
                                unique_sql.append(sql)
                        
                        for sql in unique_sql:
                            training_parts.append(f"SQL: {sql}")
                    
                    training_text = "\n".join(training_parts)
                    
                    if training_text.strip():
                        await self.mongo_training_store.create_training_data(
                            text=training_text,
                            data_type=TrainingDataType.FROM_CHAT,
                            conversation_id=conversation_id,
                        )
                        print(f"Saved training data: SQL queries={len(sql_parts)}, User requested={request.save_to_training}")
            except Exception as e:
                import traceback
                print(f"Warning: Failed to save to training data: {e}")
                traceback.print_exc()

    async def handle_poll(self, request: ChatRequest) -> ChatResponse:
        """Handle polling-based chat.

        Args:
            request: Chat request

        Returns:
            Complete chat response
        """
        chunks = []
        async for chunk in self.handle_stream(request):
            chunks.append(chunk)

        return ChatResponse.from_chunks(chunks)

    def _generate_conversation_id(self) -> str:
        """Generate new conversation ID."""
        return f"conv_{uuid.uuid4().hex[:8]}"
