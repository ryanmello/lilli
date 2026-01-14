from core.registry import registry

class Prompts:
    def __init__(self):
        self.system_prompt = """You are an orchestrator that routes user requests to the appropriate agent. \n\n"""
    
    def get_system_prompt(self) -> str:
        return self.system_prompt
    
    def get_select_agent_prompt(self) -> str:
        agent_prompt: str = registry.get_agent_prompt()

        return f"""Available agents:
        {agent_prompt}

        Based on the user's request, respond with ONLY the name of the most appropriate agent.
        Do not include any explanation or additional text - just the agent name exactly as shown above. \n\n"""

prompts = Prompts()
