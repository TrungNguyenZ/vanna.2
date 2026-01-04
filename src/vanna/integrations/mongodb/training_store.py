"""
MongoDB-based training data store.
"""

from typing import List, Optional
from datetime import datetime

from .database import MongoDBConnection
from .models import TrainingDataModel, TrainingDataType


class MongoTrainingStore:
    """MongoDB-based training data store."""
    
    def __init__(self, mongo_connection: MongoDBConnection):
        """Initialize MongoDB training store.
        
        Args:
            mongo_connection: MongoDB connection instance
        """
        self.mongo = mongo_connection
        self.collection = mongo_connection.get_collection("training_data")
        
        # Create indexes
        try:
            self.collection.create_index("data_type")
            self.collection.create_index("conversation_id")
            self.collection.create_index("created_at")
        except Exception as e:
            print(f"Warning: Failed to create some indexes: {e}")
        
        # Text index for search - handle conflict with old index
        try:
            # Check if old text index exists and drop it
            existing_indexes = list(self.collection.list_indexes())
            for index in existing_indexes:
                index_name = index.get("name", "")
                # Check if it's the old text index (question_text_answer_text) or similar
                if "text" in index_name.lower() and ("question" in index_name.lower() or "answer" in index_name.lower()):
                    try:
                        self.collection.drop_index(index_name)
                        print(f"Dropped old text index: {index_name}")
                    except Exception as e:
                        print(f"Warning: Failed to drop old index {index_name}: {e}")
            
            # Create new text index
            self.collection.create_index([("text", "text")])
        except Exception as e:
            # If index already exists or conflict, try to use existing one
            error_msg = str(e)
            if "IndexOptionsConflict" in error_msg or "already exists" in error_msg.lower() or "code: 85" in error_msg:
                print(f"Warning: Text index conflict detected. Attempting to resolve...")
                # Try to drop old conflicting index and recreate
                try:
                    existing_indexes = list(self.collection.list_indexes())
                    for index in existing_indexes:
                        index_name = index.get("name", "")
                        # Find the conflicting text index
                        if "text" in index_name.lower() and not index_name == "text_text":
                            try:
                                self.collection.drop_index(index_name)
                                print(f"Dropped conflicting text index: {index_name}")
                                # Retry creating the new index
                                self.collection.create_index([("text", "text")])
                                print("Successfully created new text index")
                                break
                            except Exception as drop_error:
                                print(f"Warning: Failed to drop conflicting index {index_name}: {drop_error}")
                except Exception as resolve_error:
                    print(f"Warning: Could not resolve index conflict: {resolve_error}")
                    print("Using existing text index if available")
            else:
                print(f"Warning: Failed to create text index: {e}")
    
    async def create_training_data(
        self,
        text: str,
        data_type: TrainingDataType = TrainingDataType.DEFAULT,
        conversation_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> TrainingDataModel:
        """Create new training data.
        
        Args:
            text: Training data text content
            data_type: Type of training data
            conversation_id: Optional conversation ID if from chat
            metadata: Optional metadata dictionary
            
        Returns:
            Created training data model
        """
        try:
            # Convert data_type to enum if it's a string
            if isinstance(data_type, str):
                data_type = TrainingDataType(data_type)
            
            training_data = TrainingDataModel(
                text=text,
                data_type=data_type,
                conversation_id=conversation_id,
                metadata=metadata or {},
            )
            
            # Prepare document for MongoDB - exclude _id if it's None
            document = training_data.model_dump(by_alias=True)
            if document.get("_id") is None:
                document.pop("_id", None)
            
            result = self.collection.insert_one(document)
            training_data.id = str(result.inserted_id)
            
            return training_data
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
    
    async def get_training_data(self, training_id: str) -> Optional[TrainingDataModel]:
        """Get training data by ID.
        
        Args:
            training_id: Training data ID
            
        Returns:
            Training data model or None if not found
        """
        from bson import ObjectId
        
        try:
            doc = self.collection.find_one({"_id": ObjectId(training_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                
                # Handle old schema (question, sql, answer) -> convert to new schema (text)
                if "text" not in doc and ("question" in doc or "sql" in doc or "answer" in doc):
                    # Convert old schema to new schema
                    text_parts = []
                    if "question" in doc and doc["question"]:
                        text_parts.append(f"Q: {doc['question']}")
                    if "sql" in doc and doc["sql"]:
                        text_parts.append(f"SQL: {doc['sql']}")
                    if "answer" in doc and doc["answer"]:
                        text_parts.append(f"A: {doc['answer']}")
                    
                    doc["text"] = "\n".join(text_parts) if text_parts else "Migrated from old schema"
                    # Remove old fields
                    doc.pop("question", None)
                    doc.pop("sql", None)
                    doc.pop("answer", None)
                
                # Skip if still no text field
                if "text" not in doc or not doc["text"]:
                    return None
                
                return TrainingDataModel(**doc)
        except Exception:
            pass
        return None
    
    async def list_training_data(
        self,
        data_type: Optional[TrainingDataType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[TrainingDataModel]:
        """List training data.
        
        Args:
            data_type: Optional filter by data type (can be TrainingDataType enum or string)
            limit: Maximum number of items to return
            offset: Number of items to skip
            
        Returns:
            List of training data models
        """
        query = {}
        if data_type:
            if isinstance(data_type, str):
                query["data_type"] = data_type
            else:
                query["data_type"] = data_type.value
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        
        training_data_list = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            
            # Handle old schema (question, sql, answer) -> convert to new schema (text)
            if "text" not in doc and ("question" in doc or "sql" in doc or "answer" in doc):
                # Convert old schema to new schema
                text_parts = []
                if "question" in doc and doc["question"]:
                    text_parts.append(f"Q: {doc['question']}")
                if "sql" in doc and doc["sql"]:
                    text_parts.append(f"SQL: {doc['sql']}")
                if "answer" in doc and doc["answer"]:
                    text_parts.append(f"A: {doc['answer']}")
                
                doc["text"] = "\n".join(text_parts) if text_parts else "Migrated from old schema"
                # Remove old fields
                doc.pop("question", None)
                doc.pop("sql", None)
                doc.pop("answer", None)
            
            # Skip if still no text field
            if "text" not in doc or not doc["text"]:
                continue
            
            try:
                training_data_list.append(TrainingDataModel(**doc))
            except Exception:
                continue
        
        return training_data_list
    
    async def update_training_data(
        self,
        training_id: str,
        text: Optional[str] = None,
    ) -> Optional[TrainingDataModel]:
        """Update training data.
        
        Args:
            training_id: Training data ID
            text: Optional new text content
            
        Returns:
            Updated training data model or None if not found
        """
        from bson import ObjectId
        
        update_data = {"updated_at": datetime.utcnow()}
        if text is not None:
            update_data["text"] = text
        
        result = self.collection.update_one(
            {"_id": ObjectId(training_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_training_data(training_id)
        return None
    
    async def delete_training_data(self, training_id: str) -> bool:
        """Delete training data.
        
        Args:
            training_id: Training data ID
            
        Returns:
            True if deleted, False if not found
        """
        from bson import ObjectId
        
        try:
            result = self.collection.delete_one({"_id": ObjectId(training_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def search_training_data(
        self,
        query: str,
        data_type: Optional[TrainingDataType] = None,
        limit: int = 10,
    ) -> List[TrainingDataModel]:
        """Search training data by text.
        
        Args:
            query: Search query
            data_type: Optional filter by data type (can be TrainingDataType enum or string)
            limit: Maximum number of results
            
        Returns:
            List of matching training data models
        """
        search_query = {"$text": {"$search": query}}
        if data_type:
            if isinstance(data_type, str):
                search_query["data_type"] = data_type
            else:
                search_query["data_type"] = data_type.value
        
        cursor = self.collection.find(search_query).limit(limit)
        
        training_data_list = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            
            # Handle old schema (question, sql, answer) -> convert to new schema (text)
            if "text" not in doc and ("question" in doc or "sql" in doc or "answer" in doc):
                # Convert old schema to new schema
                text_parts = []
                if "question" in doc and doc["question"]:
                    text_parts.append(f"Q: {doc['question']}")
                if "sql" in doc and doc["sql"]:
                    text_parts.append(f"SQL: {doc['sql']}")
                if "answer" in doc and doc["answer"]:
                    text_parts.append(f"A: {doc['answer']}")
                
                doc["text"] = "\n".join(text_parts) if text_parts else "Migrated from old schema"
                # Remove old fields
                doc.pop("question", None)
                doc.pop("sql", None)
                doc.pop("answer", None)
            
            # Skip if still no text field
            if "text" not in doc or not doc["text"]:
                continue
            
            try:
                training_data_list.append(TrainingDataModel(**doc))
            except Exception:
                continue
        
        return training_data_list

