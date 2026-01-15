from langchain_core.tools import tool

@tool
def execute_query(query: str) -> str:
    """Execute a SQL query and return the results."""
    return ""
