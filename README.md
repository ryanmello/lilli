# Lilli - Multi-Agent LLM Orchestration System

Lilli is an intelligent multi-agent system that uses LLM-powered orchestration to handle complex tasks by routing user requests to specialized agents with specific tools and capabilities.

## Architecture Overview

The system follows a hierarchical agent architecture with three main layers:

```
User Input → Orchestrator → Agents → Tools → Response
```

### Core Components

#### 1. **Orchestrator** (`core/orchestrator.py`)
The brain of the system that coordinates all agent activities. It:
- Receives user input and maintains conversation context
- Uses an LLM to classify intent and select the appropriate agent
- Manages task routing to specialized agents
- Handles multi-step tasks by chaining agent calls
- Maintains memory of previous actions (last 10 interactions)
- Determines when to respond directly vs. delegating to agents

#### 2. **Agents** (`agents/base_agent.py`)
Specialized workers that handle specific domains. Each agent:
- Has a name, description, and set of tools
- Maintains its own conversation memory
- Processes user input within its domain
- Decides whether to use a tool or respond directly
- Uses LLM to parse input and select appropriate tools

#### 3. **Tools** (`tools/`)
Concrete capabilities that agents can use. Tools:
- Follow an abstract base class pattern (`Tool`)
- Must implement: `name()`, `description()`, `use()`
- Execute specific actions (e.g., fetch weather, get time)
- Return results back to the agent

#### 4. **LLM Operations** (`core/llm_ops.py`)
Centralized interface for LLM interactions:
- Handles OpenAI API communication
- Manages prompt formatting and token limits
- Provides consistent LLM responses across the system

## How It Works: The Thinking Process

### Step 1: Intent Classification
When a user sends a message, the orchestrator:
1. Analyzes the input using the conversation context
2. Uses an LLM to understand the user's intent
3. Identifies which specialized agent should handle the task
4. Rewrites the input for optimal agent processing

### Step 2: Agent Selection
The orchestrator:
- Compares the classified intent against available agents
- Selects the agent whose description best matches the task
- Can identify when multiple agents are needed for complex requests
- Routes the request to the selected agent

### Step 3: Tool Execution
The selected agent:
1. Receives the rewritten input
2. Examines its available tools
3. Uses LLM to decide: use a tool or respond directly
4. If using a tool, extracts the necessary arguments
5. Executes the tool and captures the result

### Step 4: Response Generation
The system:
- Agent returns tool result or direct response to orchestrator
- Orchestrator updates memory with the action taken
- Determines if more steps are needed
- Returns final response to user or continues the loop

### Step 5: Multi-Step Handling
For complex, multi-step tasks:
1. Orchestrator identifies there are more actions to take
2. Uses context memory to track completed steps
3. Automatically triggers next agent with updated input
4. Continues until all tasks are complete
5. Sends final consolidated response to user

## Example Flow

**User:** "What's the weather in New York and what time is it there?"

1. **Orchestrator** analyzes: Two tasks detected (weather + time)
2. Routes to **Weather Agent** first
   - Agent uses **Weather Tool** with "New York"
   - Returns: "The weather in New York is currently clear with a temperature of 15°C"
3. Context updated with weather result
4. **Orchestrator** detects next action needed
5. Routes to **Time Agent**
   - Agent uses **Time Tool** with "America/New_York"
   - Returns: "The current time is 2025-11-10 14:30:00 EST"
6. **Orchestrator** determines all tasks complete
7. Returns consolidated response to user

## Key Design Patterns

### Memory Management
- Both orchestrator and agents maintain sliding window memory (last 10 items)
- Prevents context overflow while maintaining relevant history
- Enables stateful conversations and multi-turn interactions

### Flexible Tool System
- Tools use abstract base class for extensibility
- New tools can be added without modifying agent logic
- Tools are composable and reusable across agents

### JSON-Based Communication
- Structured responses using JSON format
- Consistent schema: `{"action": "", "args": "", "next_action": ""}`
- Enables reliable parsing and decision-making

### Dynamic Routing
- LLM-powered intent classification eliminates hardcoded rules
- System adapts to new agents without code changes
- Natural language understanding for agent selection

## Project Structure

```
lilli/
├── agents/          # Agent implementations
│   └── base_agent.py
├── core/            # Core orchestration logic
│   ├── orchestrator.py
│   └── llm_ops.py
├── tools/           # Tool implementations
│   ├── base_tool.py
│   ├── weather_tool.py
│   └── time_tool.py
├── config/          # Configuration settings
│   └── settings.py
├── utils/           # Utility functions
│   └── logger.py
├── api/             # API endpoints (future)
│   └── websocket.py
└── main.py          # Entry point
```

## Adding New Capabilities

### To add a new tool:
1. Create a class inheriting from `Tool`
2. Implement `name()`, `description()`, `use()` methods
3. Add to an existing agent's tool list

### To add a new agent:
1. Instantiate `Agent` with name, description, tools, and model
2. Add to the orchestrator's agent list
3. The system automatically routes appropriate requests

## Configuration

Set environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENWEATHERMAP_API_KEY`: For weather functionality
- Other settings in `config/settings.py`

## Running the System

### FastAPI Server (Recommended)

```bash
python main.py
```

This starts the FastAPI server with WebSocket support at `http://127.0.0.1:8000`

- API Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/api/health
- WebSocket endpoint: `ws://127.0.0.1:8000/ws/{task_id}`

---

*Lilli demonstrates how modular agent architectures can handle complex, multi-domain tasks through intelligent orchestration and specialized tool-equipped agents.*
