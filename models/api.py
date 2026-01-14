from pydantic import BaseModel

from core.registry import Agent

class AIRequest(BaseModel):
    input: str

class AIResponse(BaseModel):
    output: str
    agent_name: str
    error: str
