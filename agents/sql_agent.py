from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from agents.base_agent import BaseAgent
from tools.execute_query import execute_query

class SQLAgentOutput(BaseModel):
    message: str = Field(description="Natural language message summarizing the query results")
    data: Optional[List[Dict[str, Any]]] = Field(default=None, description="The raw data rows returned from the query")
    columns: Optional[List[str]] = Field(default=None, description="Column names for table rendering")
    row_count: int = Field(description="Number of rows returned or affected")
    query: str = Field(description="The SQL query that was executed (for transparency/debugging)")
    success: bool = Field(description="Whether the query executed successfully")
    error: Optional[str] = Field(default=None, description="Error message if the query failed")

class SQLAgent(BaseAgent):
    name = "sql_agent"
    description = "Answers data questions by querying the database."
    instructions = "Use this agent when the user asks questions about their data, wants to retrieve information from the database, or needs to create, update, or delete records."
    system_prompt = """
    You are a data analyst assistant that answers questions by querying a PostgreSQL database.

    Your workflow:
    1. Understand what data the user is asking for
    2. Generate an appropriate SQL query
    3. Execute the query using the execute_query tool
    4. Interpret the results and provide a clear, helpful answer

    Available tables:
    - customers (id, name, email, created_at)
    - orders (id, customer_id, total, status, created_at)

    Rules:
    - Generate valid PostgreSQL syntax
    - For large result sets, consider using LIMIT unless the user needs all rows
    - Provide context and insights about the data, not just raw numbers
    """
    output_schema = SQLAgentOutput
    tools = [execute_query]

sql_agent = SQLAgent()
