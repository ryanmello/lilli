# LangGraph Implementation Guide

This document outlines how to implement a LangGraph setup with an **orchestrator pattern** that analyzes user questions and delegates to the appropriate agent.

## Overview

LangGraph is a library for building stateful, multi-actor applications with LLMs. Our setup will:

1. Receive a user question from a FastAPI endpoint
2. Pass the question to an **orchestrator** that analyzes available agents
3. Delegate to the most appropriate agent based on the question
4. Return the agent's response

## Architecture

```
                                    ┌─────────────────┐
                                    │   SQL Agent     │
                                    └────────▲────────┘
                                             │
┌─────────┐     ┌──────────────┐      ┌──────┴───────┐     ┌─────┐
│  START  │────▶│ Orchestrator │─────▶│ Execute Agent│────▶│ END │
└─────────┘     └──────────────┘      └──────┬───────┘     └─────┘
                       │                     │
                       │              ┌──────▼────────┐
                       │              │ General Agent │
                       ▼              └───────────────┘
                 Analyzes question
                 & selects agent
```

## 1. Install Dependencies

Add the following to `pyproject.toml` dependencies:

```toml
dependencies = [
    # ... existing dependencies ...
    "langgraph>=0.2.0",
    "langchain-openai>=0.2.0",
    "langchain-core>=0.3.0",
]
```

Then run:

```bash
uv sync
```

## 2. Define Agent Output Schemas

Create `agents/schemas.py` to define Pydantic models for validating agent outputs:

```python
from pydantic import BaseModel, Field
from typing import Optional


class GeneralAgentOutput(BaseModel):
    """Output schema for the general agent."""
    answer: str = Field(description="The answer to the user's question")
    confidence: float = Field(
        description="Confidence level from 0.0 to 1.0",
        ge=0.0,
        le=1.0
    )
    sources: Optional[list[str]] = Field(
        default=None,
        description="Optional list of sources or references"
    )


class SQLAgentOutput(BaseModel):
    """Output schema for the SQL agent."""
    query: str = Field(description="The generated SQL query")
    explanation: str = Field(description="Explanation of what the query does")
    tables_used: list[str] = Field(
        default_factory=list,
        description="List of tables referenced in the query"
    )
    warnings: Optional[list[str]] = Field(
        default=None,
        description="Any warnings about the query (performance, security, etc.)"
    )


class MathAgentOutput(BaseModel):
    """Output schema for the math agent."""
    result: str = Field(description="The final answer/result")
    steps: list[str] = Field(
        description="Step-by-step solution process"
    )
    formula_used: Optional[str] = Field(
        default=None,
        description="The main formula or method used"
    )


class CodeAgentOutput(BaseModel):
    """Output schema for the code agent."""
    code: str = Field(description="The generated code")
    language: str = Field(description="Programming language used")
    explanation: str = Field(description="Explanation of the code")
    usage_example: Optional[str] = Field(
        default=None,
        description="Example of how to use the code"
    )
```

## 3. Define the Agent Registry

Create `agents/registry.py` to define available agents:

```python
from typing import Callable, Type
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class AgentDefinition:
    """Definition of an available agent."""
    name: str
    description: str
    instructions: str
    output_schema: Type[BaseModel]
    handler: Callable  # The function that handles this agent's logic


class AgentRegistry:
    """Registry of all available agents in the system."""
    
    def __init__(self):
        self._agents: dict[str, AgentDefinition] = {}
    
    def register(
        self,
        name: str,
        description: str,
        instructions: str,
        output_schema: Type[BaseModel],
        handler: Callable
    ) -> None:
        """Register a new agent."""
        self._agents[name] = AgentDefinition(
            name=name,
            description=description,
            instructions=instructions,
            output_schema=output_schema,
            handler=handler
        )
    
    def get(self, name: str) -> AgentDefinition | None:
        """Get an agent by name."""
        return self._agents.get(name)
    
    def list_agents(self) -> list[AgentDefinition]:
        """List all registered agents."""
        return list(self._agents.values())
    
    def get_agents_prompt(self) -> str:
        """Generate a prompt describing all available agents."""
        lines = ["Available agents:"]
        for agent in self._agents.values():
            lines.append(f"- {agent.name}: {agent.description}")
        return "\n".join(lines)


# Global registry instance
registry = AgentRegistry()
```

## 4. Create Individual Agents

Create `agents/handlers.py` with the agent implementations:

```python
from typing import Type
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ValidationError
from config.settings import settings
from utils.logger import get_logger
from agents.schemas import (
    GeneralAgentOutput,
    SQLAgentOutput,
    MathAgentOutput,
    CodeAgentOutput
)

logger = get_logger(__name__)


def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    """Create and return a ChatOpenAI instance."""
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
    )


def execute_with_structured_output(
    question: str,
    instructions: str,
    output_schema: Type[BaseModel],
    temperature: float = 0.7
) -> BaseModel:
    """
    Execute an LLM call with structured output validation.
    
    Args:
        question: The user's question
        instructions: System instructions for the agent
        output_schema: Pydantic model to validate the output
        temperature: LLM temperature setting
        
    Returns:
        Validated Pydantic model instance
        
    Raises:
        ValidationError: If the LLM output doesn't match the schema
    """
    llm = get_llm(temperature=temperature)
    
    # Use LangChain's structured output feature
    structured_llm = llm.with_structured_output(output_schema)
    
    messages = [
        SystemMessage(content=instructions),
        HumanMessage(content=question)
    ]
    
    # This returns a validated Pydantic model instance
    result = structured_llm.invoke(messages)
    
    return result


def general_agent(question: str, instructions: str, output_schema: Type[BaseModel]) -> dict:
    """
    General-purpose agent for answering any question.
    Handles general knowledge, explanations, and conversations.
    """
    logger.info(f"General agent processing: {question}")
    
    try:
        result = execute_with_structured_output(
            question=question,
            instructions=instructions,
            output_schema=output_schema,
            temperature=0.7
        )
        logger.info(f"General agent response validated successfully")
        return result.model_dump()
    
    except ValidationError as e:
        logger.error(f"Output validation failed: {e}")
        raise


def sql_agent(question: str, instructions: str, output_schema: Type[BaseModel]) -> dict:
    """
    SQL agent for database-related questions.
    Can generate SQL queries, explain database concepts, etc.
    """
    logger.info(f"SQL agent prcoessing: {question}")
    
    try:
        result = execute_with_structured_output(
            question=question,
            instructions=instructions,
            output_schema=output_schema,
            temperature=0.3  # Lower temperature for more precise SQL
        )
        logger.info(f"SQL agent response validated successfully")
        return result.model_dump()
    
    except ValidationError as e:
        logger.error(f"Output validation failed: {e}")
        raise


def math_agent(question: str, instructions: str, output_schema: Type[BaseModel]) -> dict:
    """
    Math agent for calculations and mathematical problems.
    """
    logger.info(f"Math agent processing: {question}")
    
    try:
        result = execute_with_structured_output(
            question=question,
            instructions=instructions,
            output_schema=output_schema,
            temperature=0.1  # Very low temperature for math accuracy
        )
        logger.info(f"Math agent response validated successfully")
        return result.model_dump()
    
    except ValidationError as e:
        logger.error(f"Output validation failed: {e}")
        raise


def code_agent(question: str, instructions: str, output_schema: Type[BaseModel]) -> dict:
    """
    Code agent for programming and software development questions.
    """
    logger.info(f"Code agent processing: {question}")
    
    try:
        result = execute_with_structured_output(
            question=question,
            instructions=instructions,
            output_schema=output_schema,
            temperature=0.3
        )
        logger.info(f"Code agent response validated successfully")
        return result.model_dump()
    
    except ValidationError as e:
        logger.error(f"Output validation failed: {e}")
        raise
```

## 5. Register the Agents

Create `agents/setup.py` to register all agents with their full definitions:

```python
from agents.registry import registry
from agents.handlers import general_agent, sql_agent, math_agent, code_agent
from agents.schemas import (
    GeneralAgentOutput,
    SQLAgentOutput,
    MathAgentOutput,
    CodeAgentOutput
)


# Agent instructions define the behavior and persona of each agent
GENERAL_AGENT_INSTRUCTIONS = """You are a helpful general-purpose assistant.

Your role is to:
- Answer questions clearly and concisely
- Provide accurate information on a wide range of topics
- Explain complex concepts in simple terms
- Be helpful, harmless, and honest

Always assess your confidence level in your answer. If you're uncertain, indicate this clearly.
If you reference any sources or common knowledge, list them."""

SQL_AGENT_INSTRUCTIONS = """You are an expert SQL database assistant.

Your role is to:
- Write efficient, correct SQL queries
- Explain database concepts clearly
- Optimize queries for performance
- Follow SQL best practices and security guidelines

When generating queries:
- Use clear, readable formatting
- Add appropriate WHERE clauses to prevent full table scans
- Consider indexes and query performance
- Warn about potential issues (N+1 queries, missing indexes, SQL injection risks)

Always explain what your query does and list the tables it references."""

MATH_AGENT_INSTRUCTIONS = """You are an expert mathematics assistant.

Your role is to:
- Solve mathematical problems accurately
- Show your work step by step
- Explain the reasoning behind each step
- Use proper mathematical notation

When solving problems:
- Break down complex problems into smaller steps
- State any formulas or theorems you use
- Double-check calculations
- Provide the final answer clearly

Always show your complete solution process so the user can follow along."""

CODE_AGENT_INSTRUCTIONS = """You are an expert programming assistant.

Your role is to:
- Write clean, efficient, and well-documented code
- Follow best practices for the chosen language
- Explain your code clearly
- Provide usage examples when helpful

When writing code:
- Use meaningful variable and function names
- Add comments for complex logic
- Handle edge cases appropriately
- Follow the language's style conventions

Always specify the programming language and explain how the code works."""


def register_all_agents() -> None:
    """Register all available agents with the registry."""
    
    registry.register(
        name="general",
        description="General-purpose agent for answering any question, explanations, and conversations",
        instructions=GENERAL_AGENT_INSTRUCTIONS,
        output_schema=GeneralAgentOutput,
        handler=general_agent
    )
    
    registry.register(
        name="sql",
        description="SQL expert for database queries, database design, and SQL optimization",
        instructions=SQL_AGENT_INSTRUCTIONS,
        output_schema=SQLAgentOutput,
        handler=sql_agent
    )
    
    registry.register(
        name="math",
        description="Mathematics expert for calculations, equations, statistics, and mathematical problems",
        instructions=MATH_AGENT_INSTRUCTIONS,
        output_schema=MathAgentOutput,
        handler=math_agent
    )
    
    registry.register(
        name="code",
        description="Programming expert for writing code, debugging, and software development questions",
        instructions=CODE_AGENT_INSTRUCTIONS,
        output_schema=CodeAgentOutput,
        handler=code_agent
    )
```

## 6. Create the Orchestrator

Create `agents/orchestrator.py` with the LangGraph implementation:

```python
import json
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError
from config.settings import settings
from utils.logger import get_logger
from agents.registry import registry
from agents.setup import register_all_agents

logger = get_logger(__name__)

# Ensure agents are registered
register_all_agents()


class OrchestratorState(TypedDict):
    """State that flows through the orchestrator graph."""
    question: str
    selected_agent: str
    response: dict[str, Any]  # Structured response from the agent
    error: str | None


def get_llm(temperature: float = 0) -> ChatOpenAI:
    """Create ChatOpenAI instance for orchestrator decisions."""
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,  # Low temperature for consistent routing
    )


def analyze_and_route(state: OrchestratorState) -> OrchestratorState:
    """
    Orchestrator node that analyzes the question and selects the best agent.
    Uses an LLM to understand the question and match it to available agents.
    """
    logger.info(f"Orchestrator analyzing: {state['question']}")
    
    # Get the list of available agents
    agents_prompt = registry.get_agents_prompt()
    agent_names = [agent.name for agent in registry.list_agents()]
    
    llm = get_llm()
    
    system_prompt = f"""You are an orchestrator that routes user questions to the most appropriate agent.

{agents_prompt}

Analyze the user's question and determine which agent is best suited to handle it.
Respond with ONLY the agent name (one of: {', '.join(agent_names)}).
Do not include any explanation, just the agent name."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Question: {state['question']}")
    ]
    
    response = llm.invoke(messages)
    selected_agent = response.content.strip().lower()
    
    # Fallback to general agent if selection is invalid
    if selected_agent not in agent_names:
        logger.warning(f"Invalid agent selection '{selected_agent}', falling back to 'general'")
        selected_agent = "general"
    
    logger.info(f"Orchestrator selected agent: {selected_agent}")
    
    return {
        "question": state["question"],
        "selected_agent": selected_agent,
        "response": {},
        "error": None
    }


def execute_agent(state: OrchestratorState) -> OrchestratorState:
    """
    Execute the selected agent to process the question.
    Passes the agent's instructions and output_schema to the handler.
    """
    agent_name = state["selected_agent"]
    question = state["question"]
    
    logger.info(f"Executing agent: {agent_name}")
    
    agent = registry.get(agent_name)
    if agent is None:
        logger.error(f"Agent '{agent_name}' not found in registry")
        return {
            "question": question,
            "selected_agent": agent_name,
            "response": {},
            "error": f"Agent '{agent_name}' not found"
        }
    
    try:
        # Pass instructions and output_schema to the handler
        response = agent.handler(
            question=question,
            instructions=agent.instructions,
            output_schema=agent.output_schema
        )
        
        logger.info(f"Agent '{agent_name}' executed successfully")
        logger.info(f"Response validated against schema: {agent.output_schema.__name__}")
        
        return {
            "question": question,
            "selected_agent": agent_name,
            "response": response,
            "error": None
        }
    
    except ValidationError as e:
        logger.error(f"Output validation failed for agent '{agent_name}': {e}")
        return {
            "question": question,
            "selected_agent": agent_name,
            "response": {},
            "error": f"Output validation failed: {str(e)}"
        }
    
    except Exception as e:
        logger.error(f"Agent '{agent_name}' failed: {e}")
        return {
            "question": question,
            "selected_agent": agent_name,
            "response": {},
            "error": str(e)
        }


def create_orchestrator_graph() -> StateGraph:
    """Create and compile the orchestrator LangGraph."""
    
    graph = StateGraph(OrchestratorState)
    
    # Add nodes
    graph.add_node("analyze_and_route", analyze_and_route)
    graph.add_node("execute_agent", execute_agent)
    
    # Define the flow
    graph.add_edge(START, "analyze_and_route")
    graph.add_edge("analyze_and_route", "execute_agent")
    graph.add_edge("execute_agent", END)
    
    return graph.compile()


# Singleton graph instance
_graph = None


def get_graph():
    """Get or create the compiled graph (singleton pattern)."""
    global _graph
    if _graph is None:
        _graph = create_orchestrator_graph()
    return _graph


async def process_question(question: str) -> dict:
    """
    Main entry point for processing a user question.
    
    Args:
        question: The user's question string
        
    Returns:
        Dict with 'response', 'agent', and 'error' keys
    """
    graph = get_graph()
    
    initial_state: OrchestratorState = {
        "question": question,
        "selected_agent": "",
        "response": {},
        "error": None
    }
    
    result = await graph.ainvoke(initial_state)
    
    return {
        "response": result["response"],
        "agent": result["selected_agent"],
        "error": result["error"]
    }
```

## 7. Update the API Endpoint

Update `api/lilli.py` to use the orchestrator:

```python
import time
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.orchestrator import process_question
from utils.logger import get_logger

logger = get_logger(__name__)
start_time = time.time()

router = APIRouter()


class AIRequest(BaseModel):
    input: str


class AIResponse(BaseModel):
    output: dict[str, Any]  # Structured output from the agent
    agent: str  # Which agent handled the request
    error: str | None = None  # Error message if validation failed


@router.get("/health")
async def health_check():
    return {"status": "healthy", "uptime": time.time() - start_time}


@router.post("/response", response_model=AIResponse)
async def get_ai_response(request: AIRequest):
    """
    Process a user question through the orchestrator.
    
    The orchestrator analyzes the question and delegates to the appropriate agent.
    Each agent returns a structured response validated against its output schema.
    
    Example request:
        POST /api/response
        {"input": "What's the capital of France?"}
    
    Example response (general agent):
        {
            "output": {
                "answer": "The capital of France is Paris.",
                "confidence": 0.95,
                "sources": null
            },
            "agent": "general",
            "error": null
        }
    
    Example response (sql agent):
        {
            "output": {
                "query": "SELECT * FROM customers WHERE country = 'France';",
                "explanation": "This query retrieves all customers from France.",
                "tables_used": ["customers"],
                "warnings": null
            },
            "agent": "sql",
            "error": null
        }
    """
    try:
        logger.info(f"Received question: {request.input}")
        
        result = await process_question(request.input)
        
        logger.info(f"Question handled by agent: {result['agent']}")
        
        if result["error"]:
            logger.warning(f"Agent returned error: {result['error']}")
        
        return AIResponse(
            output=result["response"],
            agent=result["agent"],
            error=result["error"]
        )
    
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 8. Update the API Models

Update `models/api.py` to include the structured response:

```python
from typing import Any
from pydantic import BaseModel


class AIRequest(BaseModel):
    input: str


class AIResponse(BaseModel):
    output: dict[str, Any]  # Structured output validated against agent's schema
    agent: str = ""  # Which agent handled the request
    error: str | None = None  # Error message if validation failed
```

## 9. How the Orchestrator Works

### Flow Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR GRAPH                              │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────┐                                                              │
│  │  START  │                                                              │
│  └────┬────┘                                                              │
│       │                                                                   │
│       ▼                                                                   │
│  ┌────────────────────────┐                                               │
│  │   analyze_and_route    │◄── LLM analyzes question                      │
│  │                        │    Reviews available agents                   │
│  │  • Gets agent registry │    Selects best match                         │
│  │  • Calls LLM to decide │                                               │
│  │  • Sets selected_agent │                                               │
│  └───────────┬────────────┘                                               │
│              │                                                            │
│              ▼                                                            │
│  ┌─────────────────────────────┐    ┌───────────────────────────────────┐ │
│  │       execute_agent         │───▶│  Agent Registry                   │ │
│  │                             │    │                                   │ │
│  │  • Looks up agent           │    │  Each agent has:                  │ │
│  │  • Passes instructions      │    │  • name                           │ │
│  │  • Passes output_schema     │    │  • description                    │ │
│  │  • Validates LLM response   │    │  • instructions                   │ │
│  │  • Returns structured dict  │    │  • output_schema (Pydantic)       │ │
│  └───────────┬─────────────────┘    │  • handler                        │ │
│              │                      └───────────────────────────────────┘ │
│              │                                                            │
│              ▼                      ┌───────────────────────────────────┐ │
│  ┌────────────────────────┐         │  Output Schemas                   │ │
│  │  Validation Check      │◄───────▶│  • GeneralAgentOutput             │ │
│  │                        │         │  • SQLAgentOutput                 │ │
│  │  LLM output validated  │         │  • MathAgentOutput                │ │
│  │  against Pydantic      │         │  • CodeAgentOutput                │ │
│  │  output_schema         │         └───────────────────────────────────┘ │
│  └───────────┬────────────┘                                               │
│              │                                                            │
│              ▼                                                            │
│         ┌────────┐                                                        │
│         │  END   │◄── Returns structured response or error                │
│         └────────┘                                                        │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### State Flow

The `OrchestratorState` TypedDict carries:

| Field | Description |
|-------|-------------|
| `question` | The user's input question |
| `selected_agent` | The agent chosen by the orchestrator |
| `response` | Structured dict response validated against the agent's output_schema |
| `error` | Error message if validation or execution failed (null on success) |

### Decision Process

1. **analyze_and_route**: 
   - Retrieves all registered agents and their descriptions
   - Constructs a prompt for the LLM with available agents
   - LLM analyzes the question and returns the best agent name
   - Falls back to "general" if selection is invalid

2. **execute_agent**:
   - Looks up the selected agent in the registry
   - Passes the agent's `instructions` and `output_schema` to the handler
   - Handler uses structured output to get validated LLM response
   - Returns the validated response or captures validation errors

## 10. Testing the Orchestrator

Start the server:

```bash
python main.py
```

### Test General Questions

```bash
curl -X POST "http://localhost:8000/api/response" \
  -H "Content-Type: application/json" \
  -d '{"input": "What is the capital of France?"}'
```

Response:
```json
{
  "output": {
    "answer": "The capital of France is Paris. It has been the capital since the late 10th century and is the country's largest city.",
    "confidence": 0.98,
    "sources": ["Common geographical knowledge"]
  },
  "agent": "general",
  "error": null
}
```

### Test SQL Questions

```bash
curl -X POST "http://localhost:8000/api/response" \
  -H "Content-Type: application/json" \
  -d '{"input": "Write a SQL query to find all customers who ordered more than 5 items"}'
```

Response:
```json
{
  "output": {
    "query": "SELECT c.id, c.name, c.email, COUNT(o.id) as order_count\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.id, c.name, c.email\nHAVING COUNT(o.id) > 5;",
    "explanation": "This query joins the customers and orders tables, groups by customer, and filters to only include customers with more than 5 orders.",
    "tables_used": ["customers", "orders"],
    "warnings": ["Consider adding an index on orders.customer_id for better performance"]
  },
  "agent": "sql",
  "error": null
}
```

### Test Math Questions

```bash
curl -X POST "http://localhost:8000/api/response" \
  -H "Content-Type: application/json" \
  -d '{"input": "Calculate the compound interest on $1000 at 5% for 3 years"}'
```

Response:
```json
{
  "output": {
    "result": "$1157.63",
    "steps": [
      "Using the compound interest formula: A = P(1 + r)^t",
      "Where P = $1000, r = 0.05, t = 3",
      "A = 1000(1 + 0.05)^3",
      "A = 1000(1.05)^3",
      "A = 1000 × 1.157625",
      "A = $1157.63"
    ],
    "formula_used": "A = P(1 + r)^t"
  },
  "agent": "math",
  "error": null
}
```

### Test Code Questions

```bash
curl -X POST "http://localhost:8000/api/response" \
  -H "Content-Type: application/json" \
  -d '{"input": "Write a Python function to reverse a string"}'
```

Response:
```json
{
  "output": {
    "code": "def reverse_string(s: str) -> str:\n    \"\"\"Reverse a string and return the result.\"\"\"\n    return s[::-1]",
    "language": "python",
    "explanation": "This function uses Python's slice notation with a step of -1 to reverse the string. The [::-1] syntax creates a new string with characters in reverse order.",
    "usage_example": "result = reverse_string('hello')  # Returns 'olleh'"
  },
  "agent": "code",
  "error": null
}
```

## 11. Adding New Agents

To add a new agent, follow these steps:

### 1. Define the output schema in `agents/schemas.py`:

```python
class ResearchAgentOutput(BaseModel):
    """Output schema for the research agent."""
    summary: str = Field(description="Summary of the research findings")
    key_points: list[str] = Field(description="Key points from the research")
    sources: list[str] = Field(description="List of sources and references")
    confidence: float = Field(
        description="Confidence level from 0.0 to 1.0",
        ge=0.0,
        le=1.0
    )
    further_reading: Optional[list[str]] = Field(
        default=None,
        description="Suggested topics for further reading"
    )
```

### 2. Create the handler in `agents/handlers.py`:

```python
def research_agent(question: str, instructions: str, output_schema: Type[BaseModel]) -> dict:
    """Research agent for in-depth analysis and research tasks."""
    logger.info(f"Research agent processing: {question}")
    
    try:
        result = execute_with_structured_output(
            question=question,
            instructions=instructions,
            output_schema=output_schema,
            temperature=0.5
        )
        logger.info(f"Research agent response validated successfully")
        return result.model_dump()
    
    except ValidationError as e:
        logger.error(f"Output validation failed: {e}")
        raise
```

### 3. Register it in `agents/setup.py`:

```python
from agents.handlers import research_agent
from agents.schemas import ResearchAgentOutput

RESEARCH_AGENT_INSTRUCTIONS = """You are an expert research assistant.

Your role is to:
- Conduct thorough research on any topic
- Provide well-organized summaries
- Cite sources and references
- Identify key insights and patterns

When researching:
- Present information objectively
- Distinguish between facts and opinions
- Note any limitations or gaps in available information
- Suggest areas for further exploration

Always provide your sources and assess your confidence level."""

def register_all_agents() -> None:
    # ... existing registrations ...
    
    registry.register(
        name="research",
        description="Research assistant for in-depth analysis, summaries, and comparative studies",
        instructions=RESEARCH_AGENT_INSTRUCTIONS,
        output_schema=ResearchAgentOutput,
        handler=research_agent
    )
```

The orchestrator will automatically include the new agent in its routing decisions!

## 12. Project Structure

```
lilli/
├── agents/
│   ├── handlers.py       # Individual agent implementations
│   ├── orchestrator.py   # LangGraph orchestrator
│   ├── registry.py       # Agent registry system
│   ├── schemas.py        # Pydantic output schemas for each agent
│   └── setup.py          # Agent registration with instructions
├── api/
│   └── lilli.py          # FastAPI endpoint
├── config/
│   └── settings.py
├── core/
│   └── app.py
├── models/
│   └── api.py            # Request/Response models
└── ...
```

## 13. Environment Variables

Ensure these are set in your `.env` file:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

## Summary

This orchestrator pattern provides:

1. **Dynamic Routing**: LLM-based analysis to select the best agent
2. **Structured Output**: Each agent has a defined output schema for validation
3. **Output Validation**: LLM responses are validated against Pydantic schemas
4. **Extensibility**: Easy to add new agents with name, description, instructions, and output_schema
5. **Transparency**: Response includes which agent handled the request and any errors
6. **Fallback Handling**: Defaults to general agent for edge cases
7. **Clean Architecture**: Separation of concerns between routing and execution

### Agent Definition Components

Each agent is defined with four key components:

| Component | Purpose |
|-----------|---------|
| `name` | Unique identifier for routing |
| `description` | Brief description for the orchestrator to understand capabilities |
| `instructions` | Detailed system prompt that defines the agent's behavior and persona |
| `output_schema` | Pydantic model that validates and structures the LLM output |

### Key Concepts

- **Agent Registry**: Central registration of agents with full definitions
- **Output Schemas**: Pydantic models that ensure consistent, validated responses
- **Structured Output**: LangChain's `with_structured_output()` for schema enforcement
- **Orchestrator Node**: Uses LLM to analyze questions and select agents
- **Execution Node**: Passes instructions and schema to the selected agent
- **State Flow**: Carries question, agent selection, structured response, and errors through the graph
