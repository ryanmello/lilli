from pydantic import BaseModel, Field
from agents.base_agent import BaseAgent
from tools.execute_query import execute_query

class SQLAgentOutput(BaseModel):
    query: str = Field(description="The generated SQL query")
    explanation: str = Field(description="Explanation of what the query does")

class SQLAgent(BaseAgent):
    name = "sql_agent"
    description = "Generates SQL queries from natural language."
    instructions = "Use this agent when the user asks about database queries, data retrieval, or anything requiring SQL."
    system_prompt = """
    You are an expert SQL query generator. 
    Your task is to generate SQL queries based on user requests.

    Available tables:
    - customers (id, name, email, created_at)
    - orders (id, customer_id, total, status, created_at)

    Rules:
    - Generate valid PostgreSQL syntax
    - Use appropriate JOINs when needed
    - Be precise and efficient with your queries"""
    output_schema = SQLAgentOutput
    tools = [execute_query]

sql_agent = SQLAgent()
