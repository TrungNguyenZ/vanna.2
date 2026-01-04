"""
Training data context enhancer for LLM.
"""

from typing import TYPE_CHECKING, Optional
from .base import LlmContextEnhancer

if TYPE_CHECKING:
    from ..user.models import User
    from ..llm.models import LlmMessage
    from ...integrations.mongodb.training_store import MongoTrainingStore


class TrainingDataContextEnhancer(LlmContextEnhancer):
    """Enhancer that uses training data to add relevant context.
    
    This enhancer searches training data for relevant examples based on
    the user's message and adds them to the system prompt.
    """

    def __init__(self, training_store: Optional["MongoTrainingStore"] = None):
        """Initialize with optional training store.
        
        Args:
            training_store: Optional MongoTrainingStore instance.
                          If not provided, enhancement will be skipped.
        """
        self.training_store = training_store

    async def enhance_system_prompt(
        self, system_prompt: str, user_message: str, user: "User"
    ) -> str:
        """Enhance system prompt with relevant training data.
        
        Searches training data for relevant examples based on the
        user's message and adds them to the system prompt.
        
        Args:
            system_prompt: The original system prompt
            user_message: The initial user message
            user: The user making the request
            
        Returns:
            Enhanced system prompt with relevant training data examples
        """
        if not self.training_store:
            return system_prompt

        try:
            # Get all default training data (no limit)
            from ...integrations.mongodb.models import TrainingDataType
            default_training = await self.training_store.list_training_data(
                data_type=TrainingDataType.DEFAULT,
                limit=10000,  # Get all default training data (large limit to get everything)
            )
            
            # Try to search for relevant training data
            training_data_list = []
            try:
                training_data_list = await self.training_store.search_training_data(
                    query=user_message,
                    limit=5,
                )
            except Exception as search_error:
                # If text search fails (e.g., no text index), fallback to getting recent training data
                try:
                    all_training = await self.training_store.list_training_data(
                        data_type=TrainingDataType.FROM_CHAT,
                        limit=5,
                    )
                    # Simple keyword matching as fallback
                    user_keywords = user_message.lower().split()
                    for td in all_training:
                        if any(keyword in td.text.lower() for keyword in user_keywords if len(keyword) > 3):
                            training_data_list.append(td)
                            if len(training_data_list) >= 5:
                                break
                except Exception:
                    pass
            
            if not training_data_list and not default_training:
                return system_prompt

            # Format training data as context snippets
            examples_section = "\n\n## Training Data Examples\n\n"
            examples_section += "The following examples from training data may be relevant:\n\n"

            # Add default training data first
            for td in default_training:
                examples_section += f"**Example:**\n{td.text}\n\n"

            # Add relevant training data from search (avoid duplicates)
            seen_texts = {td.text for td in default_training}
            for td in training_data_list:
                if td.text not in seen_texts:
                    examples_section += f"**Example:**\n{td.text}\n\n"
                    seen_texts.add(td.text)

            # Append examples to system prompt
            enhanced_prompt = system_prompt + examples_section
            return enhanced_prompt

        except Exception as e:
            # If training data search fails, return original prompt
            import traceback
            traceback.print_exc()
            return system_prompt

