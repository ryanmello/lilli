from typing import Any
from pydantic import BaseModel

class AIRequest(BaseModel):
    input: str

class AIResponse(BaseModel):
    output: dict[str, Any]
    agent_name: str
    error: str
