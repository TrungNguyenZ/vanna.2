"""
MongoDB-based chat history store.
"""

from typing import List, Optional
from datetime import datetime

try:
    from bson import ObjectId
    from bson.errors import InvalidId
except ImportError:
    # Fallback if bson is not available
    ObjectId = None
    InvalidId = Exception

from .database import MongoDBConnection
from .models import (
    ChatHistoryModel, 
    ChatMessage, 
    ConversationModel, 
    MessageModel,
    MessageType,
)


class MongoChatStore:
    """MongoDB-based chat history store."""
    
    def __init__(self, mongo_connection: MongoDBConnection):
        """Initialize MongoDB chat store.
        
        Args:
            mongo_connection: MongoDB connection instance
        """
        self.mongo = mongo_connection
        # Collections
        self.conversations_collection = mongo_connection.get_collection("conversations")
        self.messages_collection = mongo_connection.get_collection("messages")
        
        # Create indexes for collections
        # Note: conversations uses _id (ObjectId) as primary key, conversation_id_string for backward compatibility
        self.conversations_collection.create_index("conversation_id_string", unique=True, sparse=True)
        self.conversations_collection.create_index("user_id")
        self.conversations_collection.create_index("updated_at")
        
        # messages.conversation_id is ObjectId reference to conversations._id
        self.messages_collection.create_index("conversation_id")
        self.messages_collection.create_index([("conversation_id", 1), ("created_at", 1)])
        self.messages_collection.create_index("role")
    
    def _get_or_create_conversation_by_string_id(
        self, 
        conversation_id_string: str, 
        user_id: Optional[str] = None
    ) -> str:
        """Get or create conversation by string ID, return ObjectId as string.
        
        Args:
            conversation_id_string: String conversation ID (from frontend)
            user_id: Optional user ID
            
        Returns:
            ObjectId of conversation as string
        """
        # Don't create conversation if conversation_id_string is empty
        if not conversation_id_string or conversation_id_string.strip() == "":
            raise ValueError("Cannot create conversation with empty conversation_id_string")
        
        # Try to find existing conversation by conversation_id_string
        conv_doc = self.conversations_collection.find_one({"conversation_id_string": conversation_id_string})
        
        if conv_doc:
            return str(conv_doc["_id"])
        
        # Create new conversation
        conv_data = {
            "conversation_id_string": conversation_id_string,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = self.conversations_collection.insert_one(conv_data)
        return str(result.inserted_id)
    
    def _get_conversation_by_string_id(self, conversation_id_string: str) -> Optional[dict]:
        """Get conversation by string ID.
        
        Args:
            conversation_id_string: String conversation ID
            
        Returns:
            Conversation document or None
        """
        return self.conversations_collection.find_one({"conversation_id_string": conversation_id_string})
    
    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        user_id: Optional[str] = None,
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save a chat message to MongoDB.
        
        Args:
            conversation_id: String conversation ID (from frontend)
            role: Message role ('user' or 'assistant')
            content: Message content
            user_id: Optional user ID
            message_type: Type of message (text, sql, table, chart)
            metadata: Optional metadata (e.g., SQL query, chart config)
        """
        # Don't save if conversation_id is empty
        if not conversation_id or conversation_id.strip() == "":
            return
        
        # Get or create conversation and get its ObjectId
        conversation_object_id = self._get_or_create_conversation_by_string_id(
            conversation_id_string=conversation_id,
            user_id=user_id,
        )
        
        # Update conversation updated_at
        if ObjectId:
            try:
                self.conversations_collection.update_one(
                    {"_id": ObjectId(conversation_object_id)},
                    {"$set": {"updated_at": datetime.utcnow()}},
                )
            except (InvalidId, TypeError, AttributeError):
                # Fallback if ObjectId conversion fails
                self.conversations_collection.update_one(
                    {"conversation_id_string": conversation_id},
                    {"$set": {"updated_at": datetime.utcnow()}},
                )
        else:
            self.conversations_collection.update_one(
                {"conversation_id_string": conversation_id},
                {"$set": {"updated_at": datetime.utcnow()}},
            )
        
        # Save message to messages collection with ObjectId reference
        message_data = {
            "conversation_id": conversation_object_id,  # ObjectId as string
            "role": role,
            "message_type": message_type.value,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
        }
        self.messages_collection.insert_one(message_data)
    
    async def get_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[ChatHistoryModel]:
        """Get a conversation by string ID (returns legacy format for backward compatibility).
        
        Args:
            conversation_id: String conversation ID (from frontend)
            user_id: Optional user ID for filtering
            
        Returns:
            Chat history model or None if not found
        """
        # Get conversation by string ID
        conv_doc = self._get_conversation_by_string_id(conversation_id)
        if not conv_doc:
            return None
        
        # Check user_id if provided
        if user_id and conv_doc.get("user_id") != user_id:
            return None
        
        conversation_object_id = str(conv_doc["_id"])
        
        # Get messages from messages collection using ObjectId
        messages_cursor = self.messages_collection.find(
            {"conversation_id": conversation_object_id}
        ).sort("created_at", 1)
        
        messages = []
        for msg_doc in messages_cursor:
            msg_doc["_id"] = str(msg_doc["_id"])
            msg_model = MessageModel(**msg_doc)
            # Convert to legacy ChatMessage format
            messages.append(ChatMessage(
                role=msg_model.role,
                content=msg_model.content,
                timestamp=msg_model.created_at,
            ))
        
        # Return in legacy format
        conv_doc["_id"] = str(conv_doc["_id"])
        conv_model = ConversationModel(**conv_doc)
        
        return ChatHistoryModel(
            conversation_id=conversation_id,  # Use original string ID
            user_id=conv_model.user_id,
            messages=messages,
            created_at=conv_model.created_at,
            updated_at=conv_model.updated_at,
        )
    
    async def list_conversations(
        self,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ChatHistoryModel]:
        """List conversations (returns legacy format for backward compatibility).
        
        Args:
            user_id: Optional user ID for filtering
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            
        Returns:
            List of chat history models
        """
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        # Get conversations from new structure
        cursor = self.conversations_collection.find(query).sort("updated_at", -1).skip(offset).limit(limit)
        
        conversations = []
        for conv_doc in cursor:
            conv_doc["_id"] = str(conv_doc["_id"])
            conv_model = ConversationModel(**conv_doc)
            
            conversation_object_id = str(conv_doc["_id"])
            conversation_id_string = conv_model.conversation_id_string or conversation_object_id
            
            # Get messages for this conversation using ObjectId
            messages_cursor = self.messages_collection.find(
                {"conversation_id": conversation_object_id}
            ).sort("created_at", 1)
            
            messages = []
            for msg_doc in messages_cursor:
                msg_doc["_id"] = str(msg_doc["_id"])
                msg_model = MessageModel(**msg_doc)
                # Convert to legacy ChatMessage format
                messages.append(ChatMessage(
                    role=msg_model.role,
                    content=msg_model.content,
                    timestamp=msg_model.created_at,
                ))
            
            # Convert to legacy format
            conversations.append(ChatHistoryModel(
                conversation_id=conversation_id_string,  # Use string ID
                user_id=conv_model.user_id,
                messages=messages,
                created_at=conv_model.created_at,
                updated_at=conv_model.updated_at,
            ))
        
        return conversations
    
    async def create_empty_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """Create an empty conversation in MongoDB.
        
        Args:
            conversation_id: String conversation ID (from frontend)
            user_id: Optional user ID
            
        Returns:
            True if created, False if already exists
        """
        # Check if conversation already exists by string ID
        existing = self._get_conversation_by_string_id(conversation_id)
        if existing:
            return False
        
        # Create new empty conversation in new structure
        conv_data = {
            "conversation_id_string": conversation_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        self.conversations_collection.insert_one(conv_data)
        
        return True
    
    async def get_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[MessageModel]:
        """Get messages for a conversation with full details.
        
        Args:
            conversation_id: String conversation ID (from frontend)
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List of message models
        """
        # Get conversation ObjectId from string ID
        conv_doc = self._get_conversation_by_string_id(conversation_id)
        if not conv_doc:
            return []
        
        conversation_object_id = str(conv_doc["_id"])
        
        query = {"conversation_id": conversation_object_id}
        cursor = self.messages_collection.find(query).sort("created_at", 1)
        
        if offset > 0:
            cursor = cursor.skip(offset)
        if limit:
            cursor = cursor.limit(limit)
        
        messages = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            messages.append(MessageModel(**doc))
        
        return messages
    
    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """Delete a conversation and all its messages.
        
        Args:
            conversation_id: String conversation ID (from frontend)
            user_id: Optional user ID for filtering
            
        Returns:
            True if deleted, False if not found
        """
        # Get conversation by string ID
        conv_doc = self._get_conversation_by_string_id(conversation_id)
        if not conv_doc:
            return False
        
        # Check user_id if provided
        if user_id and conv_doc.get("user_id") != user_id:
            return False
        
        conversation_object_id = conv_doc["_id"]
        
        # Delete conversation from new structure
        conv_result = self.conversations_collection.delete_one({"_id": conversation_object_id})
        
        # Delete all messages for this conversation using ObjectId
        self.messages_collection.delete_many({"conversation_id": str(conversation_object_id)})
        
        return conv_result.deleted_count > 0

