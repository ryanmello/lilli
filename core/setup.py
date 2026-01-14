from core.registry import registry
from agents.sql_agent import SQLAgentOutput, sql_agent_handler

def register_agents():
    registry.register(
        name="sql_agent",
        description="Handles database queries and SQL operations",
        instructions="Generate SQL queries based on user requests",
        output_schema=SQLAgentOutput,
        handler=sql_agent_handler
    )

