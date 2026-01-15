from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from utils.logger import get_logger
from services.database import engine
from sqlalchemy import text

logger = get_logger(__name__)

# Example Outputs
# SELECT
# {
#   "success": true,
#   "query_type": "SELECT",
#   "data": [
#     {"id": 1, "name": "Ryan Mello", "email": "ryanmello897@gmail.com"},
#     {"id": 2, "name": "Fernando Mendoza", "email": "fmendoza@iu.edu"}
#   ],
#   "columns": ["id", "name", "email"],
#   "row_count": 2,
#   "message": "Query returned 2 row(s)",
#   "error": null
# }
#
# INSERT | UPDATE | DELETE:
# {
#   "success": true,
#   "query_type": "UPDATE",
#   "data": null,
#   "columns": null,
#   "row_count": 5,
#   "message": "UPDATE affected 5 row(s)",
#   "error": null
# }
#
# ERROR
# {
#   "success": false,
#   "query_type": "SELECT",
#   "data": null,
#   "columns": null,
#   "row_count": 0,
#   "message": "Query execution failed",
#   "error": "relation \"nonexistent_table\" does not exist"
# }
class ExecuteQueryResult(BaseModel):
    success: bool = Field(description="Whether the query executed successfully")
    query_type: Literal["SELECT", "INSERT", "UPDATE", "DELETE", "OTHER"]
    data: Optional[List[Dict[str, Any]]] = Field(default=None, description="Query results as list of row dictionaries (for SELECT)")
    columns: Optional[List[str]] = Field(default=None, description="Column names from the result set")
    row_count: int = Field(description="Number of rows returned (SELECT) or affected (INSERT/UPDATE/DELETE)")
    message: str = Field(description="Human-readable summary of the result")
    error: Optional[str] = Field(default=None, description="Error message if query failed")

def detect_query_type(query: str) -> str:
    normalized = query.strip().upper()
    for qtype in ["SELECT", "INSERT", "UPDATE", "DELETE"]:
        if normalized.startswith(qtype):
            return qtype
    return "OTHER"

@tool
def execute_query(query: str) -> str:
    """
    Execute a SQL query against the database and return structured results.
    
    For SELECT queries: Returns the data rows with column names.
    For INSERT/UPDATE/DELETE: Returns the number of affected rows.
    
    Args:
        query: The SQL query to execute (PostgreSQL syntax)
    
    Returns:
        JSON string containing query results or error information.
    """
    query_type = detect_query_type(query)

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            if query_type == "SELECT":
                columns = list(result.keys())
                rows = [dict(row._mapping) for row in result.fetchall()]

                logger.info(f"Columns: {columns}")
                logger.info(f"Rows: {rows}")

                return ExecuteQueryResult(
                    success=True,
                    query_type=query_type,
                    data=rows,
                    columns=columns,
                    row_count=len(rows),
                    message=f"Query returned {len(rows)} row(s)"
                ).model_dump_json()
            else:
                conn.commit()
                affected = result.rowcount
                
                return ExecuteQueryResult(
                    success=True,
                    query_type=query_type,
                    row_count=affected,
                    message=f"{query_type} affected {affected} row(s)"
                ).model_dump_json()

    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return ExecuteQueryResult(
            success=False,
            query_type=query_type,
            row_count=0,
            message="Query execution failed",
            error=str(e)
        ).model_dump_json()
