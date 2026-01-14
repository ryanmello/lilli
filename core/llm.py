from langchain_openai import ChatOpenAI
from config.settings import settings

class LLM:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL, 
            temperature=0, 
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    def get_llm(self):
        return self.llm

llm = LLM()