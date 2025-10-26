# 🚀 Quick Start Guide

This guide will help you get Lilli up and running in minutes.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- An API key from OpenAI or Anthropic

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

### 6. Run the Agent

```bash
python -m src.main
```

## First Interaction

Once the terminal interface starts, you'll see:

```
╭─────────────────────────────────╮
│  lilli AI Agent               │
│  Your intelligent flower shop   │
│  assistant                      │
╰─────────────────────────────────╯

🌸 You: _
```

Try these sample queries:

### Simple Queries
```
Do we have red roses?
What are your store hours?
How do I care for tulips?
```

### Order Queries
```
I want to order 2 dozen red roses
What's the status of order #1234?
Cancel order #5678
```

### Design Queries
```
Design a wedding bouquet with roses and lilies
What colors go well with sunflowers?
Show me autumn arrangement ideas
```

### Complex Queries
```
I need a sympathy arrangement delivered tomorrow to 90210
Create a birthday bouquet with bright colors under $50
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

## Development Mode

To run in development mode with debug logging:

Edit `.env`:
```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
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

### Terminal Commands
- Type your query naturally
- `exit`, `quit`, or `bye` to exit
- `Ctrl+C` to interrupt
- Arrow keys to navigate history

### System Commands (once implemented)
```bash
# Start the agent
python -m src.main

# Run tests
pytest

# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## Getting Help

If you encounter issues:
1. Check the logs in `logs/lilli.log`
2. Review [PLAN.md](PLAN.md) for architecture details
3. Check that all dependencies are installed correctly
4. Verify your API keys are valid and have credits

## Sample Session

Here's what a complete interaction looks like:

```
🌸 You: Do we have roses?

🤖 lilli: Yes! We currently have roses in stock:
• Red Roses: 150 stems
• White Roses: 80 stems
• Pink Roses: 120 stems
• Yellow Roses: 95 stems

All are fresh and in excellent condition. Would you like to place an order?

🌸 You: I'd like 2 dozen red roses delivered tomorrow

🤖 lilli: Perfect! I can help you with that order:

Order Details:
• 24 Red Roses: $72.00
• Delivery (Standard): $12.00
• Tax: $6.72
• Total: $90.72

Delivery available tomorrow between 9 AM - 6 PM.

To confirm this order, I'll need:
1. Delivery address
2. Recipient name
3. Any special message for the card

Would you like to proceed?

🌸 You: exit

Thank you for using Lilli! Have a great day! 🌸
```

## Configuration Tips

### For Better Performance
```env
ENABLE_QUERY_CACHING=true
MAX_CONTEXT_MESSAGES=10
```

### For Development
```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
LANGSMITH_TRACING=true  # If you have LangSmith
```

### For Production
```env
DEBUG_MODE=false
LOG_LEVEL=INFO
ENABLE_RATE_LIMITING=true
DATABASE_URL=postgresql://user:pass@host/db
```

---

**Ready to start building?** Follow the implementation phases in [PLAN.md](PLAN.md)!

