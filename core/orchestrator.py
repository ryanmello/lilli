from typing import Annotated, Any, TypedDict, List
from langchain_core.messages import HumanMessage, SystemMessage
from core.registry import registry
from core.prompts import prompts
from core.llm import llm
from langgraph.graph import StateGraph, START, END
import operator
from utils.logger import get_logger

logger = get_logger(__name__)

class OrchestratorState(TypedDict):
    user_input: str
    delegated_agent: str
    response: dict[str, Any]
    error: Annotated[list[str], operator.add]

class OrchestratorResponse(TypedDict):
    delegated_agent: str
    response: str
    error: List[str]

class Orchestrator:
    def __init__(self):
        self.llm = llm.get_llm()
        self.agents = registry.get_agents()
        self.system_prompt = prompts.get_system_prompt()

    # select an agent from available agents based on user request
    async def select_agent(self, state: OrchestratorState) -> OrchestratorState:
        user_input = state["user_input"]

        agent_names: List[str] = registry.get_agent_names()

        select_agent_prompt = self.system_prompt + prompts.get_select_agent_prompt()

        logger.info(f"select_agent_prompt: {select_agent_prompt}")

        messages = [
            SystemMessage(content=select_agent_prompt),
            HumanMessage(content=f"User request: {user_input}")
        ]

        response = self.llm.invoke(messages)
        selected_agent = response.content.strip().lower()

        logger.info(f"selected_agent: {selected_agent}")

        if selected_agent not in agent_names:
            return {"error": [f"Unknown agent: {selected_agent}"]}

        return {"delegated_agent": selected_agent}
    
    # execute the agent defined in the graph state
    async def delegate_to_agent(self, state: OrchestratorState) -> OrchestratorState:
        user_input = state["user_input"]
        delegated_agent = state["delegated_agent"]

        agent = registry.get_agent(delegated_agent)

        try:
            result = await agent.handler(user_input)
            return {"response": result.model_dump()}
        except Exception as e:
            return {"error": [f"Error in executing agent: {e}"]}

    def create_orchestrator_graph(self) -> StateGraph:
        graph = StateGraph(OrchestratorState)
        
        # Add nodes
        graph.add_node("select_agent", self.select_agent)
        graph.add_node("delegate_to_agent", self.delegate_to_agent)
        
        # Define the flow
        graph.add_edge(START, "select_agent")
        graph.add_edge("select_agent", "delegate_to_agent")
        graph.add_edge("delegate_to_agent", END)
        
        return graph.compile()
    
    async def orchestrate(self, user_input: str) -> OrchestratorResponse:
        print(user_input)

        graph = self.create_orchestrator_graph()

        initial_state: OrchestratorState = {
            "user_input": user_input,
            "delegated_agent": "",
            "response": {},
            "error": []
        }
        
        result = await graph.ainvoke(initial_state)

        response = OrchestratorResponse(
            delegated_agent=result["delegated_agent"],
            response=result["response"],
            error=result["error"]
        )

        return response

orchestrator = Orchestrator()
