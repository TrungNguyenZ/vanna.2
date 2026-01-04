"""
Request and response models for training data endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ...integrations.mongodb.models import TrainingDataType


class TrainingDataRequest(BaseModel):
    """Request model for creating/updating training data."""
    
    text: str = Field(description="Training data text content")
    data_type: TrainingDataType = Field(
        default=TrainingDataType.DEFAULT,
        description="Type of training data"
    )


class TrainingDataResponse(BaseModel):
    """Response model for training data."""
    
    id: str = Field(description="Training data ID")
    text: str = Field(description="Training data text content")
    data_type: str = Field(description="Type of training data")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Update timestamp")


class TrainingDataListResponse(BaseModel):
    """Response model for listing training data."""
    
    training_data: List[TrainingDataResponse] = Field(description="List of training data")
    total: int = Field(description="Total number of items")
    limit: int = Field(description="Limit used")
    offset: int = Field(description="Offset used")


