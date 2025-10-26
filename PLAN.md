# Lilli - AI Agent System for Flower Shops

## Executive Summary

Lilli is an intelligent multi-agent system designed specifically for flower shop operations. Built with Python, FastAPI, and LangGraph, it provides a web API with real-time WebSocket communication where frontend applications can submit natural language queries that are intelligently routed to specialized agents handling different aspects of flower shop management.

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Application                      │
│              (Web/Mobile/Desktop Interface)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                         │
│              (Query Classification & Routing)                │
│                                                              │
│  - Intent Detection                                          │
│  - Context Analysis                                          │
│  - Agent Selection                                           │
│  - Response Synthesis                                        │
└───────────┬────────┬────────┬────────┬────────┬─────────────┘
            │        │        │        │        │
    ┌───────┘        │        │        │        └───────┐
    │                │        │        │                │
    ▼                ▼        ▼        ▼                ▼
┌────────┐    ┌─────────┐ ┌──────┐ ┌────────┐   ┌──────────┐
│Inventory│    │Customer │ │Order │ │Design  │   │Delivery  │
│ Agent  │    │Service  │ │Agent │ │Agent   │   │Agent     │
│        │    │Agent    │ │      │ │        │   │          │
└────────┘    └─────────┘ └──────┘ └────────┘   └──────────┘
     │             │          │         │              │
     └─────────────┴──────────┴─────────┴──────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Shared Services  │
                  │                  │
                  │  - Database      │
                  │  - Tools         │
                  │  - Memory        │
                  │  - LLM Provider  │
                  └──────────────────┘
```

---

## Core Components

### 1. Orchestrator Agent (Router)

**Purpose**: Entry point that analyzes incoming queries and routes them to the appropriate specialized agent(s).

**Responsibilities**:
- **Query Analysis**: Parse and understand user intent
- **Multi-Intent Detection**: Identify if query requires multiple agents
- **Context Management**: Maintain conversation context and history
- **Agent Coordination**: Orchestrate complex multi-agent workflows
- **Response Synthesis**: Combine responses from multiple agents coherently
- **Fallback Handling**: Manage unclear or out-of-scope queries

**Key Features**:
- Intent classification with confidence scoring
- Dynamic agent selection based on query complexity
- Sequential vs. parallel agent execution decision
- Conversation state management
- Query preprocessing and normalization

**Example Query Routing**:
```
"Check if we have roses and lilies in stock" → Inventory Agent
"I want to order a wedding bouquet" → Design Agent → Order Agent
"Where is my order #1234?" → Order Agent (tracking)
"What flowers are good for anniversaries?" → Customer Service Agent + Design Agent
```

---

### 2. Specialized Agents

#### **2.1 Inventory Management Agent**

**Capabilities**:
- Check stock levels for specific flowers
- Search inventory by color, type, season
- Report low-stock items
- Update inventory counts
- Track flower freshness and expiration
- Suggest reorder quantities
- Provide supplier information

**Tools/Functions**:
```python
- check_stock(flower_type, color=None, quantity=None)
- search_inventory(filters)
- update_stock(flower_id, quantity, action="add/remove")
- get_low_stock_items(threshold)
- get_freshness_report()
- calculate_reorder_needs()
```

**Sample Interactions**:
- "Do we have red roses?"
- "What flowers are running low?"
- "How many stems of lilies do we have left?"
- "Show me all spring flowers in stock"

---

#### **2.2 Order Processing Agent**

**Capabilities**:
- Create new orders
- Track existing orders
- Modify/cancel orders
- Calculate pricing and discounts
- Process payments (integration ready)
- Generate order confirmations
- Schedule deliveries
- Handle bulk/corporate orders

**Tools/Functions**:
```python
- create_order(items, customer_info, delivery_info)
- get_order_status(order_id)
- update_order(order_id, changes)
- cancel_order(order_id, reason)
- calculate_total(items, discounts, tax)
- apply_discount(order_id, code)
- generate_invoice(order_id)
```

**Sample Interactions**:
- "Create an order for 2 dozen red roses"
- "What's the status of order #1234?"
- "Cancel order #5678"
- "Apply discount code SPRING20 to my order"

---

#### **2.3 Customer Service Agent**

**Capabilities**:
- Answer flower care questions
- Provide occasion recommendations
- Explain flower meanings and symbolism
- Handle customer complaints
- Provide store hours and policies
- Answer FAQs
- Manage customer preferences
- Send care instructions

**Tools/Functions**:
```python
- get_flower_care_instructions(flower_type)
- recommend_flowers_for_occasion(occasion, preferences)
- get_flower_meaning(flower_type)
- get_store_info()
- log_customer_feedback(customer_id, feedback)
- get_customer_history(customer_id)
```

**Sample Interactions**:
- "How do I care for tulips?"
- "What flowers are best for a sympathy arrangement?"
- "What do sunflowers symbolize?"
- "What are your store hours?"

---

#### **2.4 Floral Design Agent**

**Capabilities**:
- Suggest arrangement styles
- Create custom bouquet designs
- Recommend color combinations
- Provide seasonal arrangement ideas
- Calculate flower quantities for arrangements
- Suggest complementary flowers
- Design consultation for events (weddings, funerals, etc.)

**Tools/Functions**:
```python
- design_arrangement(occasion, style, budget, preferences)
- suggest_color_palette(theme, season)
- calculate_flowers_needed(arrangement_type, size)
- get_complementary_flowers(primary_flower)
- get_seasonal_designs()
- save_custom_design(design_spec)
```

**Sample Interactions**:
- "Design a rustic wedding bouquet"
- "What colors go well with lavender?"
- "How many roses do I need for a large centerpiece?"
- "Show me summer arrangement ideas"

---

#### **2.5 Delivery Management Agent**

**Capabilities**:
- Schedule deliveries
- Track delivery status
- Optimize delivery routes
- Check delivery availability
- Manage delivery fees
- Handle delivery issues
- Coordinate with delivery drivers

**Tools/Functions**:
```python
- schedule_delivery(order_id, address, date_time, priority)
- check_delivery_availability(zip_code, date)
- track_delivery(order_id)
- calculate_delivery_fee(address, urgency)
- update_delivery_status(delivery_id, status)
- optimize_routes(deliveries_list)
```

**Sample Interactions**:
- "Can you deliver to 90210 tomorrow?"
- "Schedule delivery for order #1234 at 2pm"
- "Where is my delivery?"
- "What's the delivery fee for this address?"

---

#### **2.6 Analytics & Reporting Agent** (Optional)

**Capabilities**:
- Generate sales reports
- Analyze popular flowers/arrangements
- Track seasonal trends
- Customer purchase patterns
- Inventory turnover analysis
- Revenue forecasting

**Tools/Functions**:
```python
- generate_sales_report(period, filters)
- get_top_sellers(time_range, category)
- analyze_seasonal_trends()
- customer_lifetime_value(customer_id)
- predict_demand(flower_type, date_range)
```

---

## LangGraph Implementation Design

### State Schema

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # Core conversation
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Query processing
    original_query: str
    processed_query: str
    query_intent: str
    confidence_score: float
    
    # Routing
    selected_agents: list[str]
    current_agent: str
    
    # Execution
    agent_responses: dict[str, str]
    tools_used: list[str]
    
    # Context
    customer_id: str | None
    order_context: dict | None
    conversation_history: list[dict]
    
    # Results
    final_response: str
    next_action: str
```

### Graph Workflow

```python
from langgraph.graph import StateGraph, END

# Define nodes
def orchestrator_node(state: AgentState) -> AgentState:
    """Analyzes query and determines routing"""
    pass

def inventory_agent_node(state: AgentState) -> AgentState:
    """Handles inventory queries"""
    pass

def order_agent_node(state: AgentState) -> AgentState:
    """Handles order processing"""
    pass

def customer_service_node(state: AgentState) -> AgentState:
    """Handles customer service queries"""
    pass

def design_agent_node(state: AgentState) -> AgentState:
    """Handles design recommendations"""
    pass

def delivery_agent_node(state: AgentState) -> AgentState:
    """Handles delivery management"""
    pass

def synthesis_node(state: AgentState) -> AgentState:
    """Combines multi-agent responses"""
    pass

# Build graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("inventory_agent", inventory_agent_node)
workflow.add_node("order_agent", order_agent_node)
workflow.add_node("customer_service", customer_service_node)
workflow.add_node("design_agent", design_agent_node)
workflow.add_node("delivery_agent", delivery_agent_node)
workflow.add_node("synthesis", synthesis_node)

# Define routing logic
def route_query(state: AgentState) -> str:
    """Determine which agent(s) to call based on intent"""
    intent = state["query_intent"]
    
    routing_map = {
        "inventory_check": "inventory_agent",
        "order_creation": "order_agent",
        "order_tracking": "order_agent",
        "customer_question": "customer_service",
        "design_request": "design_agent",
        "delivery_inquiry": "delivery_agent",
        "multi_intent": "synthesis"  # For complex queries
    }
    
    return routing_map.get(intent, "customer_service")

# Set entry point
workflow.set_entry_point("orchestrator")

# Add conditional edges from orchestrator
workflow.add_conditional_edges(
    "orchestrator",
    route_query,
    {
        "inventory_agent": "inventory_agent",
        "order_agent": "order_agent",
        "customer_service": "customer_service",
        "design_agent": "design_agent",
        "delivery_agent": "delivery_agent",
        "synthesis": "synthesis"
    }
)

# All agents flow to synthesis or END
workflow.add_edge("inventory_agent", "synthesis")
workflow.add_edge("order_agent", "synthesis")
workflow.add_edge("customer_service", "synthesis")
workflow.add_edge("design_agent", "synthesis")
workflow.add_edge("delivery_agent", "synthesis")
workflow.add_edge("synthesis", END)

# Compile
app = workflow.compile()
```

---

## Project Structure

```
lilli/
│
├── README.md
├── requirements.txt
├── ENV_TEMPLATE.txt
├── setup.py
│
├── src/
│   ├── __init__.py
│   │
│   ├── main.py                 # Application entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── server.py           # FastAPI application
│   │   ├── websocket.py        # WebSocket handler
│   │   ├── routes.py           # REST API routes
│   │   ├── models.py           # API request/response models
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   └── middleware.py       # CORS, auth, etc.
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Main orchestrator logic
│   │   ├── intent_classifier.py
│   │   └── router.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Base agent class
│   │   ├── inventory_agent.py
│   │   ├── order_agent.py
│   │   ├── customer_service_agent.py
│   │   ├── design_agent.py
│   │   └── delivery_agent.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── inventory_tools.py
│   │   ├── order_tools.py
│   │   ├── customer_tools.py
│   │   ├── design_tools.py
│   │   └── delivery_tools.py
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py            # State definitions
│   │   ├── workflow.py         # LangGraph workflow
│   │   └── nodes.py            # Graph node implementations
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py           # Database models
│   │   ├── connection.py
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── inventory_repo.py
│   │       ├── order_repo.py
│   │       ├── customer_repo.py
│   │       └── delivery_repo.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── provider.py         # LLM provider abstraction
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── orchestrator_prompts.py
│   │       ├── inventory_prompts.py
│   │       ├── order_prompts.py
│   │       ├── customer_service_prompts.py
│   │       ├── design_prompts.py
│   │       └── delivery_prompts.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── config.py
│       └── validators.py
│
├── data/
│   ├── flowers_catalog.json    # Flower database
│   ├── sample_orders.json
│   └── design_templates.json
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_websocket.py
│   ├── test_orchestrator.py
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_workflow.py
│
└── docs/
    ├── architecture.md
    ├── api_reference.md
    ├── agent_guide.md
    └── deployment.md
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goals**: Set up project structure and core infrastructure

- [ ] Initialize Python project with proper structure
- [ ] Set up virtual environment and dependencies (including FastAPI, Uvicorn)
- [ ] Configure LangGraph and LLM provider (OpenAI/Anthropic)
- [ ] Implement basic state schema
- [ ] Create database schema and models
- [ ] Set up logging and configuration management
- [ ] Build FastAPI server with WebSocket support
- [ ] Implement CORS and basic security middleware
- [ ] Create API request/response models

**Deliverables**:
- Working project structure
- Database schema
- FastAPI server running with WebSocket endpoint
- LLM connection established
- Basic API documentation (auto-generated by FastAPI)

---

### Phase 2: Orchestrator Development (Week 3)

**Goals**: Build the core routing system

- [ ] Implement intent classification system
- [ ] Create orchestrator agent with routing logic
- [ ] Build confidence scoring mechanism
- [ ] Implement multi-intent detection
- [ ] Add conversation context management
- [ ] Create fallback handling

**Deliverables**:
- Functional orchestrator that can classify intents
- Routing logic for all agent types
- Context-aware conversation flow

---

### Phase 3: Core Agents (Week 4-6)

**Goals**: Implement the three most critical agents

#### Week 4: Inventory Agent
- [ ] Define inventory data model
- [ ] Implement inventory tools (check_stock, update_stock, etc.)
- [ ] Create inventory agent with LangGraph node
- [ ] Build inventory search and reporting
- [ ] Test inventory queries end-to-end

#### Week 5: Order Agent
- [ ] Define order data model
- [ ] Implement order tools (create, track, update, cancel)
- [ ] Create order agent with LangGraph node
- [ ] Build pricing and calculation logic
- [ ] Implement order workflow

#### Week 6: Customer Service Agent
- [ ] Build knowledge base for flower information
- [ ] Implement customer service tools
- [ ] Create FAQ system
- [ ] Build recommendation engine
- [ ] Implement care instructions database

**Deliverables**:
- Three fully functional agents
- End-to-end query processing for inventory, orders, and customer service
- Integration with orchestrator

---

### Phase 4: Specialized Agents (Week 7-8)

**Goals**: Add design and delivery agents

#### Week 7: Design Agent
- [ ] Create design templates database
- [ ] Implement design generation logic
- [ ] Build color palette and flower pairing system
- [ ] Create arrangement calculator
- [ ] Implement seasonal recommendations

#### Week 8: Delivery Agent
- [ ] Define delivery data model
- [ ] Implement delivery scheduling
- [ ] Build delivery tracking system
- [ ] Create route optimization (basic)
- [ ] Implement delivery fee calculation

**Deliverables**:
- Complete set of five specialized agents
- All agents integrated with orchestrator
- Full multi-agent workflow support

---

### Phase 5: Integration & Enhancement (Week 9-10)

**Goals**: Polish and enhance the system

- [ ] Implement multi-agent coordination for complex queries
- [ ] Build response synthesis logic
- [ ] Add conversation memory and context persistence
- [ ] Implement error handling and retry logic
- [ ] Add input validation and sanitization
- [ ] Create comprehensive logging
- [ ] Build metrics and monitoring

**Deliverables**:
- Robust, production-ready system
- Comprehensive error handling
- Full logging and monitoring

---

### Phase 6: Testing & Documentation (Week 11-12)

**Goals**: Ensure quality and usability

- [ ] Write unit tests for all agents
- [ ] Create integration tests for workflows
- [ ] Implement end-to-end test scenarios
- [ ] Write user documentation
- [ ] Create API reference
- [ ] Build deployment guide
- [ ] Performance testing and optimization

**Deliverables**:
- 80%+ test coverage
- Complete documentation
- Optimized performance
- Deployment-ready system

---

## Technical Requirements

### Dependencies

```
# Core
python>=3.10
langgraph>=0.2.0
langchain>=0.2.0
langchain-openai>=0.1.0  # or langchain-anthropic

# Web Framework & API
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
websockets>=12.0
python-multipart>=0.0.6

# Security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Database
sqlalchemy>=2.0
sqlite3  # or postgresql adapter

# Utilities
pydantic>=2.0
python-dotenv>=1.0
structlog>=23.0  # Structured logging

# Optional
pandas>=2.0  # For analytics agent
numpy>=1.24  # For calculations
```

### Environment Variables

```env
# LLM Provider
OPENAI_API_KEY=your_key_here
# or
ANTHROPIC_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///lilli.db
# or for PostgreSQL
# DATABASE_URL=postgresql://user:pass@localhost/lilli

# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Application
LOG_LEVEL=INFO
DEBUG_MODE=false

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=100

# Optional
MAX_CONTEXT_MESSAGES=10
AGENT_TIMEOUT=30
```

---

## Key Implementation Details

### 1. Intent Classification

Use LLM-based classification with structured output:

```python
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class QueryIntent(BaseModel):
    primary_intent: str = Field(description="Main intent category")
    secondary_intents: list[str] = Field(description="Additional intents")
    confidence: float = Field(description="Confidence score 0-1")
    entities: dict = Field(description="Extracted entities")
    requires_multi_agent: bool = Field(description="Need multiple agents")

intent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an intent classifier for a flower shop AI system.
    Classify queries into these categories:
    - inventory_check: Questions about stock, availability
    - order_creation: Creating new orders
    - order_tracking: Checking order status
    - customer_question: General questions, FAQs, flower care
    - design_request: Arrangement design, recommendations
    - delivery_inquiry: Delivery scheduling, tracking
    
    Extract relevant entities (flower types, colors, dates, order IDs, etc.)
    """),
    ("user", "{query}")
])

# Use with structured output
classifier = intent_prompt | llm.with_structured_output(QueryIntent)
```

### 2. Agent Base Class

```python
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel
from typing import Any

class BaseAgent(ABC):
    def __init__(self, llm: BaseChatModel, tools: list):
        self.llm = llm
        self.tools = tools
        self.name = self.__class__.__name__
    
    @abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """Process the query and update state"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent-specific system prompt"""
        pass
    
    def log_action(self, action: str, details: dict):
        """Log agent actions"""
        pass
```

### 3. Tool Definition Pattern

```python
from langchain_core.tools import tool

@tool
def check_stock(flower_type: str, color: str = None) -> dict:
    """
    Check inventory stock for a specific flower type.
    
    Args:
        flower_type: Type of flower (e.g., "rose", "lily")
        color: Optional color filter (e.g., "red", "white")
    
    Returns:
        Dictionary with stock information
    """
    # Implementation
    pass
```

### 4. FastAPI Server & WebSocket Handler

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import json

app = FastAPI(title="Lilli AI Agent", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None
    context: Dict | None = None

class QueryResponse(BaseModel):
    message: str
    intent: str | None = None
    agents_used: List[str] | None = None
    metadata: Dict | None = None

class ConnectionManager:
    """Manage WebSocket connections"""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process query through LangGraph workflow
            query = message.get("query", "")
            context = message.get("context", {})
            
            # Stream processing updates
            await manager.send_message(client_id, {
                "type": "processing",
                "message": "Processing your request..."
            })
            
            # Process through workflow
            response = await process_query_async(query, context)
            
            # Send final response
            await manager.send_message(client_id, {
                "type": "response",
                "message": response["message"],
                "intent": response.get("intent"),
                "agents_used": response.get("agents_used"),
                "metadata": response.get("metadata")
            })
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        await manager.send_message(client_id, {
            "type": "error",
            "message": str(e)
        })

@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """REST API endpoint for queries (alternative to WebSocket)"""
    response = await process_query_async(
        request.query, 
        request.context or {}
    )
    return QueryResponse(**response)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "lilli-api"}

async def process_query_async(query: str, context: dict) -> dict:
    """Process query through LangGraph workflow"""
    # Connect to LangGraph workflow
    # Return formatted response
    pass
```

---

## Example Query Flows

### Simple Query Flow

**Query**: "Do we have red roses?"

```
1. Frontend sends WebSocket message with query
2. FastAPI WebSocket handler receives message
3. Sends "processing" status to frontend
4. Orchestrator analyzes:
   - Intent: inventory_check
   - Entities: {flower: "rose", color: "red"}
   - Agent: inventory_agent
   - Confidence: 0.95
5. Routes to Inventory Agent
6. Inventory Agent:
   - Calls check_stock("rose", "red")
   - Formats response
7. Synthesis node formats final output
8. FastAPI sends response via WebSocket
9. Frontend displays: "Yes, we have 150 stems of red roses in stock."
```

### Complex Multi-Agent Flow

**Query**: "I need a wedding bouquet with roses and lilies, can you deliver it tomorrow to 90210?"

```
1. Frontend sends WebSocket message with query
2. FastAPI WebSocket handler receives message
3. Sends "processing" status update to frontend
4. Orchestrator analyzes:
   - Primary intent: design_request
   - Secondary intents: [inventory_check, order_creation, delivery_inquiry]
   - Requires multi-agent: true
   - Entities: {
       occasion: "wedding",
       flowers: ["rose", "lily"],
       delivery_date: "tomorrow",
       zip_code: "90210"
     }
5. Routes to multiple agents (sequential):
   a. Design Agent:
      - Sends status: "Creating design..."
      - Creates bouquet design
      - Calculates needed flowers
   b. Inventory Agent:
      - Sends status: "Checking inventory..."
      - Checks availability of roses and lilies
   c. Delivery Agent:
      - Sends status: "Verifying delivery..."
      - Checks delivery availability for 90210 tomorrow
      - Calculates delivery fee
   d. Order Agent:
      - Sends status: "Calculating pricing..."
      - Prepares order summary with pricing
6. Synthesis node combines all responses:
   - Design description
   - Availability confirmation
   - Delivery confirmation
   - Total pricing
   - Next steps for order confirmation
7. FastAPI sends final response via WebSocket
8. Frontend displays comprehensive response with real-time updates
```

---

## Advanced Features (Future Enhancements)

### 1. Voice Interface
- Integration with speech-to-text
- Voice-based order placement
- Phone system integration

### 2. Multi-Channel Support
- Web API for web/mobile apps
- SMS/WhatsApp integration
- Email processing

### 3. Personalization
- Customer preference learning
- Purchase history analysis
- Personalized recommendations

### 4. Proactive Agents
- Low stock alerts
- Delivery delay notifications
- Special occasion reminders
- Seasonal promotion suggestions

### 5. Integration Ecosystem
- POS system integration
- Accounting software connection
- CRM integration
- Delivery service APIs (DoorDash, etc.)

### 6. Advanced Analytics
- Sales forecasting
- Demand prediction
- Customer segmentation
- Marketing campaign analysis

---

## Best Practices

### 1. Error Handling
- Always validate inputs
- Graceful degradation for LLM failures
- Clear error messages to users
- Fallback to simpler responses

### 2. Performance
- Cache frequent queries
- Optimize tool calls
- Use streaming for long responses
- Implement timeout handling

### 3. Security
- Sanitize all inputs
- No sensitive data in logs
- Rate limiting for API calls
- Secure database access

### 4. Testing
- Unit test each agent independently
- Integration tests for workflows
- Mock LLM responses for consistent testing
- Test edge cases and error scenarios

### 5. Monitoring
- Log all queries and responses
- Track agent selection accuracy
- Monitor response times
- Alert on error rates

---

## Success Metrics

### Technical Metrics
- **Intent Classification Accuracy**: >90%
- **Response Time**: <3 seconds for simple queries
- **Tool Call Success Rate**: >95%
- **System Uptime**: >99%

### User Experience Metrics
- **Query Resolution Rate**: >85% resolved without escalation
- **User Satisfaction**: Measure through feedback
- **Multi-Turn Conversation Success**: Handle 3+ turn conversations
- **Appropriate Agent Selection**: >90% correct routing

---

## Getting Started - Quick Setup

Once implementation begins:

```bash
# Clone and setup
git clone <repo>
cd lilli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp ENV_TEMPLATE.txt .env
# Edit .env with your API keys

# Initialize database
python -m src.database.init_db

# Run the API server
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000

# Alternative: Run with custom settings
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --workers 4

# For production
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --workers 4 --no-access-log
```

**API Endpoints:**
- WebSocket: `ws://localhost:8000/ws/{client_id}`
- REST API: `http://localhost:8000/api/query`
- Health Check: `http://localhost:8000/api/health`
- API Docs: `http://localhost:8000/docs`

---

## Conclusion

This plan provides a comprehensive blueprint for building a sophisticated, multi-agent AI system for flower shops. The modular architecture allows for incremental development, with each agent operating independently while being coordinated by the orchestrator through LangGraph's powerful workflow management.

The system is designed to be:
- **Scalable**: Easy to add new agents and capabilities
- **Maintainable**: Clear separation of concerns
- **Extensible**: Plugin architecture for tools and agents
- **Production-Ready**: Built with error handling, logging, and monitoring

Start with Phase 1 and build incrementally, testing each component thoroughly before moving to the next phase.

