from typing import List
from dataclasses import dataclass
from typing import Callable, Type
from pydantic import BaseModel

from agents.base_agent import BaseAgent

@dataclass
class Agent:
    name: str
    description: str
    instructions: str
    output_schema: Type[BaseModel]
    handler: Callable

class AgentRegistry:
    def __init__(self):
        # key: name
        # val: class
        self.agents: dict[str, Agent] = {}
    
    # register an agent
    def register(self, agent: BaseAgent) -> None:
        self.agents[agent.name] = Agent(
            name=agent.name,
            description=agent.description,
            instructions=agent.instructions,
            output_schema=agent.output_schema,
            handler=agent.handler
        )
    
    # return an agent
    def get_agent(self, agent_name: str) -> Agent:
        for name, agent in self.agents.items():
            if name == agent_name:
                return agent

    # return a list of all agents
    def get_agents(self) -> List[Agent]:
        return [agent for agent in self.agents.values()]

    # return a string with agent names and descriptions
    def get_agent_prompt(self) -> str:
        prompt: List[str] = []
        for agent in self.agents.values():
            prompt.append(f"- {agent.name}: {agent.description} {agent.instructions} \n")
        return "".join(prompt)
    
    def get_agent_names(self) -> List[str]:
        return [agent for agent in self.agents.keys()]

registry = AgentRegistry()
