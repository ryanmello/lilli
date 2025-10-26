# 🚀 Quick Start Guide

This guide will help you get Lilli API server up and running in minutes.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- An API key from OpenAI or Anthropic
- A modern web browser (for testing WebSocket connections)
- Optional: Node.js (if you want to run a frontend application)

## Installation Steps

### 1. Clone or Download the Project

```bash
cd lilli
```

### 2. Create a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# On macOS/Linux
cp .env.example .env

# On Windows
copy .env.example .env
```

Edit `.env` and add your API key:

**For OpenAI:**
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
LLM_PROVIDER=openai
```

**For Anthropic (Claude):**
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
LLM_PROVIDER=anthropic
```

### 5. Initialize the Database

Once implemented, this will set up the initial database:

```bash
python -m src.database.init_db
```

### 6. Run the API Server

```bash
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
```

The server will start and you'll see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**API Endpoints Available:**
- WebSocket: `ws://localhost:8000/ws/{client_id}`
- REST API: `http://localhost:8000/api/query`
- Health Check: `http://localhost:8000/api/health`
- Interactive API Docs: `http://localhost:8000/docs`
- Alternative API Docs: `http://localhost:8000/redoc`

## First Interaction

### Option 1: Using the Interactive API Documentation

1. Open your browser and go to `http://localhost:8000/docs`
2. Try the `/api/health` endpoint first
3. Use the `/api/query` endpoint to send queries

### Option 2: Using WebSocket (JavaScript Example)

Create an HTML file or use browser console:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Lilli Test Client</title>
</head>
<body>
    <h1>Lilli AI Agent Test</h1>
    <input type="text" id="query" placeholder="Ask a question..." size="50">
    <button onclick="sendQuery()">Send</button>
    <div id="response"></div>

    <script>
        const ws = new WebSocket('ws://localhost:8000/ws/test-client-123');
        
        ws.onopen = () => {
            console.log('Connected to Lilli');
            document.getElementById('response').innerHTML = '✅ Connected';
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            document.getElementById('response').innerHTML += 
                `<p><strong>${data.type}:</strong> ${data.message}</p>`;
        };
        
        function sendQuery() {
            const query = document.getElementById('query').value;
            ws.send(JSON.stringify({
                query: query,
                context: {}
            }));
        }
    </script>
</body>
</html>
```

### Option 3: Using cURL (REST API)

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Do we have red roses?",
    "session_id": "test-session"
  }'
```

Try these sample API requests:

### Simple Queries
```json
{
  "query": "Do we have red roses?",
  "session_id": "user-123"
}

{
  "query": "What are your store hours?",
  "session_id": "user-123"
}

{
  "query": "How do I care for tulips?",
  "session_id": "user-123"
}
```

### Order Queries
```json
{
  "query": "I want to order 2 dozen red roses",
  "session_id": "user-123",
  "context": {
    "customer_id": "cust-456"
  }
}

{
  "query": "What's the status of order #1234?",
  "session_id": "user-123"
}
```

### Design Queries
```json
{
  "query": "Design a wedding bouquet with roses and lilies",
  "session_id": "user-123"
}

{
  "query": "What colors go well with sunflowers?",
  "session_id": "user-123"
}
```

### Complex Queries
```json
{
  "query": "I need a sympathy arrangement delivered tomorrow to 90210",
  "session_id": "user-123",
  "context": {
    "customer_id": "cust-456",
    "preferred_budget": 75
  }
}
```

## Troubleshooting

### Issue: "Module not found" errors
**Solution**: Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "API key not found" error
**Solution**: Double-check your `.env` file has the correct API key with no extra spaces:
```env
OPENAI_API_KEY=sk-your-key-here
```

### Issue: Database errors
**Solution**: Initialize or reset the database:
```bash
python -m src.database.init_db --reset
```

### Issue: LangGraph import errors
**Solution**: Ensure you have the latest version:
```bash
pip install --upgrade langgraph langchain langchain-core
```

### Issue: "Address already in use" error
**Solution**: Port 8000 is occupied. Use a different port:
```bash
uvicorn src.api.server:app --reload --port 8001
```

### Issue: CORS errors from frontend
**Solution**: Update CORS_ORIGINS in `.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://your-frontend-domain.com
```

### Issue: WebSocket connection fails
**Solution**: 
1. Check if server is running
2. Verify WebSocket URL format: `ws://localhost:8000/ws/{client_id}`
3. Check browser console for errors
4. Test with the `/api/health` endpoint first

## Development Mode

To run in development mode with debug logging and auto-reload:

Edit `.env`:
```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

Run with reload (auto-restarts on code changes):
```bash
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
```

Run with multiple workers (production):
```bash
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing the System

Once tests are implemented, run:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py
```

## Next Steps

1. **Explore the Agents**: Try different types of queries to see how the orchestrator routes them
2. **Check the Logs**: Look at `logs/lilli.log` to see how queries are processed
3. **Read the Plan**: See [PLAN.md](PLAN.md) for detailed architecture and implementation details
4. **Customize**: Modify agent behaviors in `src/agents/`

## Command Reference

### API Server Commands
```bash
# Start the API server (development)
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000

# Start with custom port
uvicorn src.api.server:app --reload --port 8001

# Start for production (multiple workers)
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --workers 4

# Start with SSL (production)
uvicorn src.api.server:app --host 0.0.0.0 --port 443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem

# Run tests
pytest

# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

### WebSocket Client Commands (JavaScript)
```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws/my-client-id');

// Send query
ws.send(JSON.stringify({
  query: "Your question here",
  context: {}
}));

// Receive messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

// Close connection
ws.close();
```

## Getting Help

If you encounter issues:
1. Check the logs in `logs/lilli.log`
2. Review [PLAN.md](PLAN.md) for architecture details
3. Check that all dependencies are installed correctly
4. Verify your API keys are valid and have credits

## Sample API Session

Here's what a complete interaction looks like via WebSocket:

**Client Connects:**
```javascript
ws://localhost:8000/ws/customer-123
// Connection established ✅
```

**Client Sends Query:**
```json
{
  "query": "Do we have roses?",
  "context": {}
}
```

**Server Responds (Processing):**
```json
{
  "type": "processing",
  "message": "Processing your request..."
}
```

**Server Responds (Final):**
```json
{
  "type": "response",
  "message": "Yes! We currently have roses in stock:\n• Red Roses: 150 stems\n• White Roses: 80 stems\n• Pink Roses: 120 stems\n• Yellow Roses: 95 stems\n\nAll are fresh and in excellent condition. Would you like to place an order?",
  "intent": "inventory_check",
  "agents_used": ["inventory"],
  "metadata": {
    "confidence": 0.95,
    "processing_time": 1.8
  }
}
```

**Client Sends Follow-up:**
```json
{
  "query": "I'd like 2 dozen red roses delivered tomorrow",
  "context": {
    "previous_intent": "inventory_check"
  }
}
```

**Server Responds:**
```json
{
  "type": "response",
  "message": "Perfect! I can help you with that order:\n\nOrder Details:\n• 24 Red Roses: $72.00\n• Delivery (Standard): $12.00\n• Tax: $6.72\n• Total: $90.72\n\nDelivery available tomorrow between 9 AM - 6 PM.\n\nTo confirm this order, I'll need:\n1. Delivery address\n2. Recipient name\n3. Any special message for the card\n\nWould you like to proceed?",
  "intent": "order_creation",
  "agents_used": ["design", "inventory", "delivery", "order"],
  "metadata": {
    "confidence": 0.92,
    "processing_time": 3.5,
    "requires_user_info": true
  }
}
```

## Configuration Tips

### For Better Performance
```env
ENABLE_QUERY_CACHING=true
MAX_CONTEXT_MESSAGES=10
API_WORKERS=4
WS_MAX_CONNECTIONS=100
```

### For Development
```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
LANGSMITH_TRACING=true  # If you have LangSmith
```

### For Production
```env
DEBUG_MODE=false
LOG_LEVEL=INFO
ENABLE_RATE_LIMITING=true
DATABASE_URL=postgresql://user:pass@host/db
API_WORKERS=4
CORS_ORIGINS=https://yourdomain.com
# Add SSL certificate configuration
```

---

**Ready to start building?** Follow the implementation phases in [PLAN.md](PLAN.md)!

