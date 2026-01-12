from pydantic import BaseModel

class AIRequest(BaseModel):
    input: str

class AIResponse(BaseModel):
    output: str
