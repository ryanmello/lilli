from abc import ABC
from typing import Type
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage
from core.llm import llm

# TODO: allow agents to have tools that they can call
class BaseAgent(ABC):    
    name: str
    description: str
    instructions: str
    system_prompt: str
    output_schema: Type[BaseModel]
    
    def __init__(self) -> None:
        self.structured_llm = llm.get_llm().with_structured_output(self.output_schema)
    
    async def handler(self, user_input: str) -> BaseModel:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_input)
        ]
        
        result = await self.structured_llm.ainvoke(messages)
        return result
