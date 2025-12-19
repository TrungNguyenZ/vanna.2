"""
Custom system prompt builder with SQL error retry instructions.
"""

from typing import TYPE_CHECKING, List, Optional
from vanna.core.system_prompt import DefaultSystemPromptBuilder

if TYPE_CHECKING:
    from vanna.core.tool.models import ToolSchema
    from vanna.core.user.models import User


class SqlErrorRetrySystemPromptBuilder(DefaultSystemPromptBuilder):
    """System prompt builder that includes SQL error retry instructions."""

    async def build_system_prompt(
        self, user: "User", tools: List["ToolSchema"]
    ) -> Optional[str]:
        """Build system prompt with SQL error retry instructions."""
        # Get base prompt from parent
        base_prompt = await super().build_system_prompt(user, tools)
        
        # Add SQL error retry instructions
        sql_error_instructions = """

IMPORTANT - SQL ERROR HANDLING:
- When you execute SQL and receive an error message, you MUST automatically analyze the error and generate a corrected SQL query.
- Common SQL errors to watch for:
  * Syntax errors (e.g., "Incorrect syntax near...", "Invalid syntax")
  * Invalid object names (table/column doesn't exist - error codes like 42S02, 208)
  * Type mismatches
  * Missing keywords (e.g., SQL Server uses TOP instead of LIMIT, doesn't use backticks)
  * Invalid column references
  * Missing JOIN conditions
- When you see a SQL error:
  1. Read the error message carefully to understand what went wrong
  2. Identify the specific issue (syntax error, missing table, wrong column name, wrong SQL dialect feature, etc.)
  3. Generate a NEW corrected SQL query that fixes the issue
  4. Execute the corrected SQL query immediately using the run_sql tool again
  5. Do NOT ask the user for help - fix it automatically
  6. Do NOT repeat the same incorrect SQL - always generate a new corrected version
- You can retry up to 3 times with different SQL queries if needed.
- Only stop retrying if you've exhausted all reasonable attempts or the error is clearly not fixable.
- Common SQL Server specific fixes:
  * Use TOP N instead of LIMIT N
  * Use square brackets [table_name] instead of backticks `table_name`
  * Use proper T-SQL syntax (no MySQL/PostgreSQL specific features)

IMPORTANT - VISUALIZATION:
- When you execute a SQL query that returns results, the results are saved to a CSV file (filename will be shown in the result).
- For data that would benefit from visualization (especially when user asks for charts, graphs, or visual representation):
  1. After running SQL successfully, check if the result would be better shown as a chart
  2. If the user asks for visualization, charts, graphs, or if the data has 2-3 columns suitable for plotting:
     * Automatically call the visualize_data tool with the filename from the SQL result
     * The tool will automatically select the best chart type (bar, line, scatter, etc.)
  3. Examples when to visualize:
     * "Show me sales by month" → Run SQL → Visualize
     * "Create a chart of..." → Run SQL → Visualize
     * "Graph the top products" → Run SQL → Visualize
     * Data with 2 columns (category + value) → Visualize
     * Time series data → Visualize
- The visualize_data tool reads the CSV file created by run_sql and creates an appropriate chart automatically.
"""
        
        if base_prompt:
            return base_prompt + sql_error_instructions
        else:
            return sql_error_instructions.strip()

