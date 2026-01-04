"""
Composite LLM context enhancer that combines multiple enhancers.
"""

from typing import TYPE_CHECKING, List, Optional

from .base import LlmContextEnhancer

if TYPE_CHECKING:
    from ..user.models import User
    from ..llm.models import LlmMessage


class CompositeLlmContextEnhancer(LlmContextEnhancer):
    """Composite enhancer that combines multiple enhancers.
    
    This enhancer applies multiple enhancers in sequence, allowing
    you to combine different enhancement strategies.
    
    Example:
        enhancer = CompositeLlmContextEnhancer([
            DefaultLlmContextEnhancer(agent_memory),
            TrainingDataContextEnhancer(training_store)
        ])
    """

    def __init__(self, enhancers: List[LlmContextEnhancer]):
        """Initialize with list of enhancers.
        
        Args:
            enhancers: List of LlmContextEnhancer instances to apply in sequence
        """
        self.enhancers = enhancers

    async def enhance_system_prompt(
        self, system_prompt: str, user_message: str, user: "User"
    ) -> str:
        """Enhance system prompt by applying all enhancers in sequence.
        
        Args:
            system_prompt: The original system prompt
            user_message: The initial user message
            user: The user making the request
            
        Returns:
            Enhanced system prompt after applying all enhancers
        """
        enhanced_prompt = system_prompt
        for enhancer in self.enhancers:
            enhanced_prompt = await enhancer.enhance_system_prompt(
                enhanced_prompt, user_message, user
            )
        return enhanced_prompt

    async def enhance_user_messages(
        self, messages: List["LlmMessage"], user: "User"
    ) -> List["LlmMessage"]:
        """Enhance user messages by applying all enhancers in sequence.
        
        Args:
            messages: List of LLM messages
            user: The user making the request
            
        Returns:
            Enhanced messages after applying all enhancers
        """
        enhanced_messages = messages
        for enhancer in self.enhancers:
            enhanced_messages = await enhancer.enhance_user_messages(
                enhanced_messages, user
            )
        return enhanced_messages

