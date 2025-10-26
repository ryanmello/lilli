# 🏗️ Bloomer Agent Architecture

## System Overview

Bloomer Agent is a multi-agent AI system built on LangGraph that orchestrates specialized agents to handle various flower shop operations. This document provides a deep dive into the architectural decisions and implementation patterns.

## Core Architectural Principles

### 1. **Separation of Concerns**
Each agent handles a specific domain (inventory, orders, design, etc.) and operates independently while sharing common infrastructure.

### 2. **Orchestrator Pattern**
A central orchestrator analyzes queries and routes them to appropriate agents, enabling both simple single-agent queries and complex multi-agent workflows.

### 3. **State-Driven Workflow**
LangGraph manages state transitions through a well-defined state schema, ensuring consistent data flow between agents.

### 4. **Tool-Based Actions**
Agents use composable tools for database operations and external integrations, promoting reusability and testability.

### 5. **Extensibility**
New agents and tools can be added without modifying existing components, following the Open/Closed Principle.

---

## System Layers

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                      │
│                  (Terminal Interface)                    │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                 Orchestration Layer                      │
│                                                          │
│  ┌──────────────┐      ┌────────────────┐              │
│  │ Orchestrator │──────│ Intent         │              │
│  │              │      │ Classifier     │              │
│  └──────────────┘      └────────────────┘              │
│         │                                               │
│         │ Routes to appropriate agents                  │
└─────────┴──────────────────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                    Agent Layer                           │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Inventory │  │  Order   │  │Customer  │  ...        │
│  │  Agent   │  │  Agent   │  │ Service  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                     Tool Layer                           │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Inventory │  │  Order   │  │Database  │  ...        │
│  │  Tools   │  │  Tools   │  │ Tools    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                    Data Layer                            │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Database  │  │  Cache   │  │External  │             │
│  │          │  │          │  │  APIs    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

---

## LangGraph Workflow Architecture

### State Machine Design

```python
class AgentState(TypedDict):
    """Central state shared across all agents"""
    
    # Input/Output
    messages: Annotated[Sequence[BaseMessage], operator.add]
    original_query: str
    final_response: str
    
    # Routing
    query_intent: str
    confidence_score: float
    selected_agents: list[str]
    current_agent: str
    
    # Execution
    agent_responses: dict[str, str]
    tools_used: list[str]
    
    # Context
    customer_id: str | None
    conversation_history: list[dict]
    metadata: dict
```

### Graph Structure

```
                    START
                      │
                      ▼
              ┌──────────────┐
              │ Orchestrator │
              │    Node      │
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │Inventory│  │ Order │  │Customer│
   │  Node  │  │  Node │  │ Service│
   └───┬────┘  └───┬────┘  └───┬────┘
       │           │            │
       └───────────┼────────────┘
                   │
                   ▼
            ┌──────────────┐
            │  Synthesis   │
            │    Node      │
            └──────┬───────┘
                   │
                   ▼
                  END
```

### Routing Logic

```python
def route_query(state: AgentState) -> str:
    """
    Dynamic routing based on query intent.
    Supports:
    - Single agent routing
    - Multi-agent sequential workflows
    - Multi-agent parallel execution
    """
    intent = state["query_intent"]
    confidence = state["confidence_score"]
    
    # High confidence, single intent
    if confidence > 0.85 and len(state["selected_agents"]) == 1:
        return state["selected_agents"][0]
    
    # Multi-agent required
    if len(state["selected_agents"]) > 1:
        return "synthesis"  # Coordinate multiple agents
    
    # Low confidence fallback
    if confidence < 0.5:
        return "customer_service"  # General help
    
    # Default routing
    return INTENT_TO_AGENT_MAP[intent]
```

---

## Agent Architecture

### Base Agent Pattern

All specialized agents inherit from a base agent class:

```python
from abc import ABC, abstractmethod
from typing import Any
from langchain_core.language_models import BaseChatModel

class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(
        self, 
        llm: BaseChatModel, 
        tools: list,
        name: str
    ):
        self.llm = llm
        self.tools = tools
        self.name = name
        self.system_prompt = self.get_system_prompt()
    
    @abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """
        Main processing logic for the agent.
        Receives state, performs operations, updates state.
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent-specific system prompt"""
        pass
    
    def should_use_tool(self, query: str) -> bool:
        """Determine if tools are needed for this query"""
        pass
    
    def format_response(self, raw_response: str) -> str:
        """Format response for end user"""
        pass
```

### Agent Lifecycle

1. **Initialization**: Load tools, configure LLM, set system prompt
2. **Receive State**: Get current state from LangGraph
3. **Process Query**: Analyze query in agent's context
4. **Tool Execution**: Call tools if needed
5. **Generate Response**: Create natural language response
6. **Update State**: Return updated state
7. **Handoff**: Pass to next node (synthesis or END)

---

## Tool Architecture

### Tool Design Pattern

```python
from langchain_core.tools import tool
from typing import Dict, Any
from pydantic import BaseModel, Field

class CheckStockInput(BaseModel):
    """Input schema for check_stock tool"""
    flower_type: str = Field(description="Type of flower")
    color: str | None = Field(default=None, description="Color filter")
    min_quantity: int = Field(default=1, description="Minimum quantity")

@tool(args_schema=CheckStockInput)
def check_stock(
    flower_type: str, 
    color: str | None = None,
    min_quantity: int = 1
) -> Dict[str, Any]:
    """
    Check inventory stock for specific flowers.
    
    Returns:
        Dictionary with stock information including:
        - available: bool
        - quantity: int
        - variants: list of available colors/types
        - freshness: str
    """
    # Implementation
    pass
```

### Tool Categories

**1. Read Tools**
- Query data without side effects
- Examples: `check_stock`, `get_order_status`, `search_inventory`

**2. Write Tools**
- Modify system state
- Examples: `create_order`, `update_stock`, `schedule_delivery`

**3. Computation Tools**
- Perform calculations
- Examples: `calculate_pricing`, `optimize_route`, `estimate_flowers_needed`

**4. External Tools**
- Integrate with external services
- Examples: `send_email`, `process_payment`, `track_shipment`

---

## Data Architecture

### Database Schema

```sql
-- Flowers/Inventory
CREATE TABLE flowers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50),
    color VARCHAR(50),
    quantity INTEGER,
    price_per_stem DECIMAL(10,2),
    supplier VARCHAR(100),
    received_date DATE,
    freshness_score INTEGER,  -- 1-10
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Orders
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_number VARCHAR(50) UNIQUE,
    status VARCHAR(50),  -- pending, confirmed, in_progress, completed, cancelled
    total_amount DECIMAL(10,2),
    order_date TIMESTAMP,
    delivery_date TIMESTAMP,
    delivery_address TEXT,
    special_instructions TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Order Items
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    flower_id INTEGER,
    quantity INTEGER,
    price_per_unit DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (flower_id) REFERENCES flowers(id)
);

-- Customers
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    customer_since DATE,
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Deliveries
CREATE TABLE deliveries (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    delivery_address TEXT,
    scheduled_date TIMESTAMP,
    actual_delivery_time TIMESTAMP,
    status VARCHAR(50),  -- scheduled, in_transit, delivered, failed
    driver_name VARCHAR(100),
    delivery_fee DECIMAL(10,2),
    special_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Design Templates
CREATE TABLE design_templates (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    occasion VARCHAR(50),
    style VARCHAR(50),
    description TEXT,
    primary_flowers TEXT,  -- JSON array
    color_palette TEXT,    -- JSON array
    estimated_cost DECIMAL(10,2),
    popularity_score INTEGER,
    created_at TIMESTAMP
);

-- Conversation History (for context)
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(100),
    customer_id INTEGER,
    query TEXT,
    intent VARCHAR(50),
    agent_used VARCHAR(50),
    response TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

### Repository Pattern

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository for database operations"""
    
    def __init__(self, session):
        self.session = session
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def update(self, id: int, entity: T) -> T:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

class FlowerRepository(BaseRepository[Flower]):
    """Specific repository for Flower operations"""
    
    def get_by_type_and_color(
        self, 
        flower_type: str, 
        color: str
    ) -> List[Flower]:
        """Custom query for flowers"""
        pass
    
    def get_low_stock(self, threshold: int = 50) -> List[Flower]:
        """Get flowers below stock threshold"""
        pass
```

---

## Communication Patterns

### 1. Single Agent Flow

```
User Query → Orchestrator → Single Agent → Synthesis → Response
```

**Example**: "Do we have red roses?"
- Orchestrator identifies: `inventory_check`
- Routes to: Inventory Agent
- Agent uses: `check_stock("rose", "red")`
- Synthesis: Formats response
- Output: "Yes, we have 150 stems of red roses"

### 2. Sequential Multi-Agent Flow

```
User Query → Orchestrator → Agent 1 → Agent 2 → Agent 3 → Synthesis → Response
```

**Example**: "I want to order a wedding bouquet with roses"
- Orchestrator identifies: `design_request` + `order_creation`
- Routes to: Design Agent
  - Design Agent creates bouquet design
  - State updated with design details
- Routes to: Inventory Agent
  - Checks flower availability
  - State updated with availability
- Routes to: Order Agent
  - Prepares order details
  - State updated with pricing
- Synthesis combines all information
- Output: Complete design + availability + pricing

### 3. Parallel Multi-Agent Flow

```
User Query → Orchestrator → ┌─ Agent 1 ─┐
                             ├─ Agent 2 ─┤ → Synthesis → Response
                             └─ Agent 3 ─┘
```

**Example**: "What's popular this season and do we have stock?"
- Orchestrator identifies: Multiple independent queries
- Parallel execution:
  - Customer Service Agent: Seasonal recommendations
  - Inventory Agent: Current stock levels
- Synthesis combines responses
- Output: Integrated response with recommendations and availability

---

## Error Handling Strategy

### 1. Graceful Degradation

```python
def orchestrator_node(state: AgentState) -> AgentState:
    try:
        intent = classify_intent(state["original_query"])
        state["query_intent"] = intent.primary_intent
        state["confidence_score"] = intent.confidence
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        # Fallback: route to customer service
        state["query_intent"] = "general_question"
        state["confidence_score"] = 0.5
    
    return state
```

### 2. Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_llm(prompt: str) -> str:
    """Call LLM with automatic retries"""
    return llm.invoke(prompt)
```

### 3. Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Prevent repeated calls to failing services"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
```

---

## Performance Considerations

### 1. Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache frequently accessed data
@lru_cache(maxsize=100)
def get_flower_catalog():
    """Cache flower catalog for 1 hour"""
    pass

# Cache LLM responses for identical queries
class ResponseCache:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, query_hash: str) -> str | None:
        if query_hash in self.cache:
            response, timestamp = self.cache[query_hash]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return response
        return None
```

### 2. Async Operations

```python
import asyncio

async def process_parallel_agents(
    state: AgentState, 
    agents: list
) -> dict:
    """Execute multiple agents in parallel"""
    tasks = [agent.process_async(state) for agent in agents]
    results = await asyncio.gather(*tasks)
    return combine_results(results)
```

### 3. Database Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

---

## Security Considerations

### 1. Input Sanitization

```python
def sanitize_input(query: str) -> str:
    """Sanitize user input before processing"""
    # Remove potential injection attempts
    # Validate length
    # Filter malicious patterns
    pass
```

### 2. Rate Limiting

```python
from datetime import datetime
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        now = datetime.now()
        # Clean old requests
        # Check if under limit
        pass
```

### 3. Data Privacy

- Never log sensitive customer information
- Encrypt sensitive data at rest
- Mask PII in logs and responses
- Implement data retention policies

---

## Monitoring and Observability

### 1. Logging Structure

```python
import structlog

logger = structlog.get_logger()

def orchestrator_node(state: AgentState) -> AgentState:
    logger.info(
        "orchestrator.processing",
        query=state["original_query"],
        session_id=state.get("session_id")
    )
    
    # Process...
    
    logger.info(
        "orchestrator.routed",
        intent=state["query_intent"],
        confidence=state["confidence_score"],
        selected_agent=state["current_agent"]
    )
    
    return state
```

### 2. Metrics Collection

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class QueryMetrics:
    query_id: str
    intent: str
    agent_used: str
    latency_ms: float
    tools_called: list[str]
    success: bool
    timestamp: datetime
    
    def log(self):
        """Log metrics for analysis"""
        pass
```

### 3. LangSmith Integration

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "bloomer-agent"

# Automatic tracing of all LangChain operations
```

---

## Extensibility Patterns

### Adding a New Agent

1. Create agent class inheriting from `BaseAgent`
2. Define agent-specific tools
3. Write system prompt
4. Add to workflow graph
5. Update routing logic
6. Add tests

```python
# 1. Create agent
class PricingAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return "You are a pricing specialist..."
    
    def process(self, state: AgentState) -> AgentState:
        # Implementation
        pass

# 2. Add tools
@tool
def calculate_dynamic_pricing(flower_type: str, season: str) -> float:
    pass

# 3. Register in workflow
workflow.add_node("pricing_agent", pricing_agent_node)
workflow.add_conditional_edges(
    "orchestrator",
    route_query,
    {"pricing_agent": "pricing_agent"}
)
```

---

## Testing Strategy

### 1. Unit Tests

```python
def test_intent_classification():
    classifier = IntentClassifier(llm)
    result = classifier.classify("Do we have roses?")
    
    assert result.primary_intent == "inventory_check"
    assert result.confidence > 0.8
    assert "flower" in result.entities
```

### 2. Integration Tests

```python
def test_inventory_agent_workflow():
    state = AgentState(
        original_query="Check rose inventory",
        messages=[HumanMessage(content="Check rose inventory")]
    )
    
    result = app.invoke(state)
    
    assert result["query_intent"] == "inventory_check"
    assert result["current_agent"] == "inventory_agent"
    assert "check_stock" in result["tools_used"]
```

### 3. End-to-End Tests

```python
def test_complete_order_flow():
    """Test full order creation workflow"""
    query = "I want to order 2 dozen red roses for delivery tomorrow"
    
    result = process_query(query)
    
    assert "design" in result.agents_used
    assert "inventory" in result.agents_used
    assert "order" in result.agents_used
    assert result.success is True
```

---

## Deployment Architecture

### Development
```
Local Machine → SQLite → Terminal Interface
```

### Production
```
                    ┌──────────────┐
User Terminal  ──────│   Load       │
                    │   Balancer   │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌────▼──────┐
    │ Instance 1│    │ Instance 2│    │Instance 3 │
    └─────┬─────┘    └─────┬─────┘    └────┬──────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼───────┐
                    │  PostgreSQL  │
                    │   (Primary)  │
                    └──────────────┘
```

---

## Future Architecture Enhancements

1. **Microservices**: Split agents into separate services
2. **Message Queue**: Use RabbitMQ/Kafka for agent communication
3. **GraphQL API**: Add GraphQL layer for multi-channel support
4. **Vector Database**: Add Pinecone/Weaviate for semantic search
5. **Real-time Sync**: WebSocket support for live updates
6. **Distributed Tracing**: OpenTelemetry integration
7. **Kubernetes**: Container orchestration for scaling

---

This architecture provides a solid foundation for building a production-ready, multi-agent AI system that's maintainable, scalable, and extensible.

