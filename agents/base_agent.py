from abc import ABC
from typing import Annotated, List, Type
from typing_extensions import TypedDict
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from core.llm import llm
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode
from utils.logger import get_logger

logger = get_logger(__name__)

class BaseAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

class BaseAgent(ABC):    
    name: str
    description: str
    instructions: str
    system_prompt: str
    output_schema: Type[BaseModel]
    tools: List[BaseTool] = []
    
    def __init__(self) -> None:
        base_llm = llm.get_llm()
        
        # used in reasoning node
        self.llm_with_tools = base_llm.bind_tools(self.tools)
        
        # used at the end of handler to enforce output schema
        self.structured_llm = base_llm.with_structured_output(
            self.output_schema, 
            method="function_calling"
        )
    
    async def agent_node(self, state: BaseAgentState) -> BaseAgentState:
        messages = state["messages"]
        
        response = await self.llm_with_tools.ainvoke(messages)
        
        if response.tool_calls:
            for tc in response.tool_calls:
                logger.info(f"[{self.name}] Tool call: {tc['name']}({tc['args']})")
        
        return {"messages": [response]}

    def should_continue(self, state: BaseAgentState) -> str:
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return "end"

    def create_agent_graph(self) -> StateGraph:
        graph = StateGraph(BaseAgentState)

        graph.add_node("agent", self.agent_node)
        graph.add_node("tools", ToolNode(self.tools))

        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", self.should_continue, {"tools": "tools", "end": END})
        graph.add_edge("tools", "agent")
        
        return graph.compile()
        
    async def handler(self, user_input: str) -> BaseModel:
        graph = self.create_agent_graph()

        initial_state = {
            "messages": [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_input)
            ]
        }

        result = await graph.ainvoke(initial_state)
        
        for msg in result["messages"]:
            if isinstance(msg, ToolMessage):
                content_preview = str(msg.content)[:150]
                logger.info(f"[{self.name}] Tool result: {content_preview}...")
        
        logger.info(f"[{self.name}] Generating structured output...")
        structured_result = await self.structured_llm.ainvoke(result["messages"])
        
        logger.info(f"[{self.name}] Final output: {structured_result.model_dump_json()[:300]}...")
        return structured_result
