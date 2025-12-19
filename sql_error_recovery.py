"""
SQL Error Recovery Strategy for automatic SQL retry.

When SQL execution fails, this strategy allows the LLM to automatically
generate a new SQL query based on the error message.
"""

from typing import TYPE_CHECKING
from vanna.core.recovery import ErrorRecoveryStrategy, RecoveryAction, RecoveryActionType

if TYPE_CHECKING:
    from vanna.core.tool.models import ToolContext
    from vanna.core.llm import LlmRequest


class SqlErrorRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy that allows LLM to retry with new SQL when SQL errors occur.
    
    When a SQL execution fails, instead of immediately failing, this strategy
    allows the LLM to see the error and automatically generate a corrected SQL query.
    The LLM will receive the error message in the tool result and can retry.
    """

    def __init__(self, max_sql_retries: int = 3):
        """Initialize SQL error recovery strategy.
        
        Args:
            max_sql_retries: Maximum number of times to allow SQL retry attempts
        """
        self.max_sql_retries = max_sql_retries

    async def handle_tool_error(
        self, error: Exception, context: "ToolContext", attempt: int = 1
    ) -> RecoveryAction:
        """Handle SQL tool errors by allowing LLM to retry with new SQL.
        
        For SQL errors, we don't retry the same tool call. Instead, we let
        the error propagate to the LLM so it can generate a corrected SQL query.
        The LLM will see the error in the tool result and can call the tool again
        with a corrected SQL.
        
        Args:
            error: The exception that occurred
            context: Tool execution context
            attempt: Current attempt number (1-indexed)
            
        Returns:
            RecoveryAction indicating to fail (so LLM can see error and retry)
        """
        # For SQL errors, we want the LLM to see the error and generate new SQL
        # So we return FAIL to let the error propagate to LLM
        # The LLM will then automatically retry with corrected SQL
        return RecoveryAction(
            action=RecoveryActionType.FAIL,
            message=f"SQL execution failed. The LLM will analyze the error and generate a corrected SQL query. Error: {str(error)}"
        )

    async def handle_llm_error(
        self, error: Exception, request: "LlmRequest", attempt: int = 1
    ) -> RecoveryAction:
        """Handle LLM communication errors with retry.
        
        Args:
            error: The exception that occurred
            request: The LLM request that failed
            attempt: Current attempt number (1-indexed)
            
        Returns:
            RecoveryAction indicating how to proceed
        """
        # For LLM errors, we can retry with exponential backoff
        if attempt < 3:
            delay_ms = (2 ** (attempt - 1)) * 1000
            return RecoveryAction(
                action=RecoveryActionType.RETRY,
                retry_delay_ms=delay_ms,
                message=f"LLM communication error, retrying in {delay_ms}ms"
            )
        
        return RecoveryAction(
            action=RecoveryActionType.FAIL,
            message=f"LLM error after {attempt} attempts: {str(error)}"
        )

