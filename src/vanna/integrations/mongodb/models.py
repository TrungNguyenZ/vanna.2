"""
MongoDB models for chat history and training data.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TrainingDataType(str, Enum):
    """Type of training data."""
    DEFAULT = "default"  # Data được thêm mặc định
    FROM_CHAT = "from_chat"  # Data được thêm từ đoạn chat


class MessageType(str, Enum):
    """Type of message content."""
    TEXT = "text"
    SQL = "sql"
    TABLE = "table"
    CHART = "chart"


class ChatMessage(BaseModel):
    """Chat message model (legacy - kept for backward compatibility)."""
    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MessageModel(BaseModel):
    """Message model for MongoDB (separate collection)."""
    id: Optional[str] = Field(default=None, alias="_id")
    conversation_id: str = Field(description="Conversation ID (ObjectId of conversations._id)")
    role: str = Field(description="Message role: 'user' or 'assistant'")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of message: text, sql, table, chart")
    content: str = Field(description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata (e.g., SQL query, chart config)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationModel(BaseModel):
    """Conversation model for MongoDB (separate collection).
    
    Note: Uses _id (ObjectId) as primary key. No conversation_id field.
    For backward compatibility, we maintain a mapping between string conversation_id
    (used by frontend) and ObjectId _id.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    # conversation_id removed - use _id instead
    user_id: Optional[str] = Field(default=None, description="User ID")
    title: Optional[str] = Field(default=None, description="Conversation title")
    # Store string conversation_id for backward compatibility (not used as primary key)
    conversation_id_string: Optional[str] = Field(default=None, description="String conversation ID for backward compatibility")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatHistoryModel(BaseModel):
    """Chat history model for MongoDB (legacy - kept for backward compatibility)."""
    id: Optional[str] = Field(default=None, alias="_id")
    conversation_id: str = Field(description="Conversation ID")
    user_id: Optional[str] = Field(default=None, description="User ID")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TrainingDataModel(BaseModel):
    """Training data model for MongoDB - chỉ lưu text."""
    id: Optional[str] = Field(default=None, alias="_id")
    text: str = Field(description="Training data text content")
    data_type: TrainingDataType = Field(
        default=TrainingDataType.DEFAULT,
        description="Type of training data"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation ID if created from chat"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

