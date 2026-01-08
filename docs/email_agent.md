# Email Agent - Implementation Plan

## Overview

The Email Agent is a specialized agent responsible for drafting and sending emails on behalf of users. It integrates with **Resend** as the email delivery service and follows the existing agent architecture pattern established in the codebase.

---

## User Flow

```
User Request → Orchestrator → Email Agent → Tools → Resend API → Response
```

### Example User Requests
- "Send my customers a valentines day reminder email"
- "Draft a thank you email to all subscribers"
- "Email my VIP customers about the upcoming sale"
- "Send a promotional email about our new product launch"

---

## 1. Intent Classification & Routing

### How the Orchestrator Identifies Email Intent

The `AgentOrchestrator` already uses LLM-based intent classification to route requests to the appropriate agent. When the Email Agent is registered, the orchestrator will:

1. Receive user input (e.g., "send my customers a valentines day reminder email")
2. Include the Email Agent in the list of available agents with its description
3. Use the LLM to classify the intent and select `Email Agent` as the action
4. Rewrite the input to be optimized for the Email Agent
5. Route the request to the Email Agent's `process_input()` method

### Registration in Orchestrator

The Email Agent needs to be instantiated and added to the orchestrator's agent list:

```python
from agents.email_agent import EmailAgent

email_agent = EmailAgent(shop_id="your_shop_id")
orchestrator = AgentOrchestrator(agents=[inventory_agent, email_agent])
```

---

## 2. Email Agent Structure

### Location
`agents/email_agent.py`

### Class Design

```python
class EmailAgent(Agent):
    def __init__(self, shop_id: str):
        # Initialize Resend client with API key from settings
        # Initialize database service for customer data
        # Initialize email tools
        
        tools = [
            DraftEmailTool(...),
            SendEmailTool(...),
            GetRecipientsListTool(...)  # Optional: fetch customer emails
        ]
        
        super().__init__(
            Name="Email Agent",
            Description="An intelligent agent that handles email operations including:
                - Drafting professional email templates based on user intent
                - Sending emails to customers via Resend
                - Managing recipient lists (customers, subscribers, VIPs, etc.)",
            Tools=tools,
            Model=settings.OPENAI_MODEL
        )
```

---

## 3. Email Tools

Following the existing tools pattern (see `tools/inventory/`), create email-specific tools:

### Tool 1: DraftEmailTool
**Location:** `tools/email/draft_email.py`

**Purpose:** Uses LLM to generate an email template based on the user's request.

**Input:**
- `purpose`: The intent/occasion (e.g., "valentines day reminder")
- `tone`: Optional tone preference (professional, casual, friendly)
- `key_points`: Optional specific points to include

**Output:**
- `subject`: Generated email subject line
- `body`: Generated email body (HTML or plain text)

**How it works:**
1. Takes the user's request context
2. Constructs a prompt for the LLM to generate an appropriate email
3. Returns the drafted subject and body for review or immediate sending

---

### Tool 2: SendEmailTool
**Location:** `tools/email/send_email.py`

**Purpose:** Sends emails using the Resend API.

**Input:**
- `to`: List of recipient email addresses OR a recipient group identifier (e.g., "all_customers", "vip_customers")
- `subject`: Email subject line
- `body`: Email body content (HTML supported)
- `from_email`: Optional sender email (defaults to configured sender)

**Output:**
- `success`: Boolean indicating if emails were sent
- `sent_count`: Number of emails successfully sent
- `failed`: List of any failed recipients

**How it works:**
1. Resolves recipient list (if group identifier provided, fetch from database)
2. Validates email addresses
3. Calls Resend API to send emails
4. Returns delivery status

---

### Tool 3: GetRecipientsListTool (Optional)
**Location:** `tools/email/get_recipients.py`

**Purpose:** Fetches recipient email addresses based on criteria.

**Input:**
- `group`: Customer segment (e.g., "all", "vip", "subscribers", "recent_buyers")
- `filters`: Optional additional filters

**Output:**
- `recipients`: List of email addresses
- `count`: Total count of recipients

---

## 4. Resend Integration

### Configuration
Add to `config/settings.py`:

```python
RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
DEFAULT_FROM_EMAIL: str = os.getenv("DEFAULT_FROM_EMAIL", "noreply@yourdomain.com")
```

### Resend Service
**Location:** `services/resend_service.py`

A service class to wrap Resend API calls:

```python
import resend

class ResendService:
    def __init__(self, api_key: str):
        resend.api_key = api_key
    
    def send_email(self, to: list, subject: str, html: str, from_email: str) -> dict:
        # Call Resend API
        # Handle errors and return response
        pass
    
    def send_batch(self, emails: list) -> dict:
        # For sending to multiple recipients efficiently
        pass
```

---

## 5. Complete Request Flow Example

### User Says: "Send my customers a valentines day reminder email"

**Step 1: Orchestrator receives request**
- Context is built from memory
- LLM classifies intent as email-related
- Returns: `{"action": "Email Agent", "input": "draft and send valentines day reminder email to all customers"}`

**Step 2: Email Agent processes input**
- Agent's `process_input()` is called
- LLM determines tools needed: first `DraftEmailTool`, then `SendEmailTool`
- Returns action: `{"action": "draft_email", "args": {"purpose": "valentines day reminder", "tone": "friendly"}}`

**Step 3: DraftEmailTool executes**
- LLM generates subject: "💕 Happy Valentine's Day from [Business Name]!"
- LLM generates body with valentine's themed content
- Returns draft to agent

**Step 4: SendEmailTool executes**
- Fetches customer email list from database
- Calls Resend API with the drafted email
- Returns: `{"success": true, "sent_count": 150, "failed": []}`

**Step 5: Response returned to user**
- Agent compiles response: "Successfully sent Valentine's Day reminder email to 150 customers!"

---

## 6. File Structure

```
agents/
  └── email_agent.py

tools/
  └── email/
      ├── __init__.py
      ├── draft_email.py
      ├── send_email.py
      └── get_recipients.py

services/
  └── resend_service.py

config/
  └── settings.py  (add RESEND_API_KEY, DEFAULT_FROM_EMAIL)
```

---

## 7. Dependencies

Add to `requirements.txt`:
```
resend
```

---

## 8. Environment Variables

```
RESEND_API_KEY=re_xxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=hello@yourdomain.com
```

---

## 9. Considerations

### Error Handling
- Handle Resend API rate limits
- Validate email addresses before sending
- Log failed deliveries for retry

### Security
- Store API keys securely in environment variables
- Validate that users have permission to send to recipient groups
- Sanitize email content to prevent injection

### Scalability
- Use Resend's batch API for large recipient lists
- Consider queueing for very large sends
- Implement retry logic for transient failures

### User Experience
- Consider adding a confirmation step before sending (optional tool)
- Provide preview of drafted email before sending
- Return clear success/failure messages

---

## 10. Future Enhancements

- **Template Library:** Save and reuse email templates
- **Scheduling:** Schedule emails for future delivery
- **Analytics:** Track open rates and click-through rates (if Resend supports)
- **Attachments:** Support for email attachments
- **A/B Testing:** Test different subject lines or content
