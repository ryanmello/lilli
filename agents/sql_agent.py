from pydantic import BaseModel, Field

class SQLAgentOutput(BaseModel):
    """Output schema for the SQL agent."""
    query: str = Field(description="The generated SQL query")
    explanation: str = Field(description="Explanation of what the query does")

async def sql_agent_handler(user_input: str) -> SQLAgentOutput:
    # TODO: Implement actual SQL generation logic
    return SQLAgentOutput(
        query=f"SELECT * FROM table WHERE condition",
        explanation=f"Generated query for: {user_input}"
    )
