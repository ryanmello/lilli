# 🌸 Lilli

An intelligent multi-agent AI system for flower shop management, built with Python, FastAPI, and LangGraph.

## Overview

Lilli is a sophisticated AI assistant that helps flower shops manage their operations through natural language interactions via a web API with real-time WebSocket communication. It uses an orchestrator-based architecture to route queries to specialized agents handling different aspects of the business.

## Features

- 🎯 **Intelligent Query Routing**: Orchestrator analyzes queries and routes to appropriate specialized agents
- 📦 **Inventory Management**: Check stock, track freshness, manage reorders
- 🛒 **Order Processing**: Create, track, modify, and cancel orders
- 💬 **Customer Service**: Answer questions about flower care, meanings, and recommendations
- 🎨 **Floral Design**: Generate arrangement ideas, color palettes, and design consultations
- 🚚 **Delivery Management**: Schedule deliveries, track status, calculate fees
- 🤖 **Multi-Agent Coordination**: Handle complex queries requiring multiple agents

## Architecture

The system uses FastAPI and LangGraph to orchestrate multiple specialized agents:

```
Frontend (WebSocket) ↔ FastAPI Server → Orchestrator → [Specialized Agents] → Response Synthesis
```

**Specialized Agents:**
- Inventory Agent
- Order Processing Agent
- Customer Service Agent
- Floral Design Agent
- Delivery Management Agent

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp ENV_TEMPLATE.txt .env
# Add your API keys to .env

# Run the API Server
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
# Server will be available at http://localhost:8000
# WebSocket endpoint: ws://localhost:8000/ws
```

## Tech Stack

- **Python 3.10+**
- **FastAPI**: High-performance web framework
- **WebSockets**: Real-time bidirectional communication
- **LangGraph**: Workflow orchestration
- **LangChain**: LLM integration and tools
- **SQLite/PostgreSQL**: Data persistence
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Documentation

- 📋 [Detailed Plan](PLAN.md) - Complete system design and implementation roadmap
- 🏗️ Architecture documentation (coming soon)
- 📚 API Reference (coming soon)
- 🎓 Agent Development Guide (coming soon)

## Project Status

🚧 **In Planning Phase** - See [PLAN.md](PLAN.md) for the complete implementation roadmap.

## Example API Usage

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Send query
ws.send(JSON.stringify({
  type: 'query',
  content: 'Do we have red roses in stock?'
}));

// Receive response
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log(response.message);
  // "Yes, we have 150 stems of red roses available."
};
```

## Development Roadmap

- **Phase 1**: Foundation & Infrastructure (Weeks 1-2)
- **Phase 2**: Orchestrator Development (Week 3)
- **Phase 3**: Core Agents (Weeks 4-6)
- **Phase 4**: Specialized Agents (Weeks 7-8)
- **Phase 5**: Integration & Enhancement (Weeks 9-10)
- **Phase 6**: Testing & Documentation (Weeks 11-12)

See [PLAN.md](PLAN.md) for detailed phase breakdowns.

## Contributing

This is currently in the planning and development phase. Contribution guidelines will be added soon.

## License

[To be determined]

## Contact

[Your contact information]

