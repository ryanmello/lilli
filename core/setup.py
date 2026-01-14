from core.registry import registry
from agents.sql_agent import sql_agent

def register_agents():
    registry.register(sql_agent)
