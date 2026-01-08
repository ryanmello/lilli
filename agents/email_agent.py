"""
Email Agent
Specialized agent for drafting and sending emails via Resend.
"""

from agents.base_agent import Agent
from services.database_service import DatabaseService
from services.resend_service import ResendService
from tools.email.draft_email import DraftEmailTool
from tools.email.send_email import SendEmailTool
from tools.email.get_recipients import GetRecipientsTool
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class EmailAgent(Agent):
    """
    Agent specialized in email operations including drafting and sending emails.
    Integrates with Resend for email delivery.
    """
    
    def __init__(self, shop_id: str, business_name: str = "Our Business"):
        """
        Initialize the Email Agent with all email tools.
        
        Args:
            shop_id: Shop ID for customer operations.
            business_name: Name of the business for email branding.
        """
        self.shop_id = shop_id
        self.business_name = business_name
        
        # Initialize Resend service
        if not settings.RESEND_API_KEY:
            logger.warning("RESEND_API_KEY not configured. Email sending will fail.")
        
        self.resend_service = ResendService(
            api_key=settings.RESEND_API_KEY,
            default_from_email=settings.DEFAULT_FROM_EMAIL
        )
        
        # Initialize database service for customer data
        connection_string = settings.DATABASE_URL
        self.db_service = DatabaseService(connection_string)
        
        # Connect to database
        if not self.db_service.connect():
            logger.warning("Failed to connect to MongoDB. Recipient fetching will be limited.")
            self.db_service = None
        
        # Initialize tools
        tools = [
            DraftEmailTool(business_name=business_name),
            SendEmailTool(
                resend_service=self.resend_service,
                db_service=self.db_service,
                shop_id=shop_id
            ),
            GetRecipientsTool(
                db_service=self.db_service,
                shop_id=shop_id
            ) if self.db_service else None
        ]
        
        # Filter out None tools
        tools = [t for t in tools if t is not None]
        
        # Initialize base agent
        super().__init__(
            Name="Email Agent",
            Description="""An intelligent agent that handles email operations including:
            - Drafting professional email templates based on user intent and occasion
            - Sending emails to customers via Resend email service
            - Managing recipient lists (all customers, VIP customers, subscribers, recent customers)
            - Creating marketing emails, announcements, reminders, and promotional content
            Use this agent when the user wants to send emails, create email campaigns, or communicate with customers via email.""",
            Tools=tools,
            Model=settings.OPENAI_MODEL
        )
        
        logger.info("Email Agent initialized successfully")
    
    def cleanup(self):
        """
        Clean up resources, including database connection.
        """
        if self.db_service:
            self.db_service.disconnect()
            logger.info("Email Agent cleaned up successfully")
    
    def draft_and_send(
        self,
        purpose: str,
        recipient_group: str = "all_customers",
        tone: str = "friendly",
        key_points: list = None
    ) -> dict:
        """
        Convenience method to draft and send an email in one operation.
        
        Args:
            purpose: The purpose/occasion for the email.
            recipient_group: Target recipient group.
            tone: Email tone preference.
            key_points: Optional key points to include.
        
        Returns:
            Dictionary with the operation results.
        """
        try:
            # Step 1: Draft the email
            draft_tool = None
            send_tool = None
            
            for tool in self.tools:
                if tool.name() == "draft_email":
                    draft_tool = tool
                elif tool.name() == "send_email":
                    send_tool = tool
            
            if not draft_tool or not send_tool:
                return {
                    "success": False,
                    "message": "Required tools not available."
                }
            
            # Draft the email
            draft_args = {
                "purpose": purpose,
                "tone": tone,
                "recipient_type": recipient_group
            }
            if key_points:
                draft_args["key_points"] = key_points
            
            draft_result = draft_tool.use(draft_args)
            
            if not draft_result.get("success"):
                return {
                    "success": False,
                    "message": f"Failed to draft email: {draft_result.get('message')}"
                }
            
            # Step 2: Send the email
            send_args = {
                "to": recipient_group,
                "subject": draft_result["subject"],
                "body": draft_result["body"]
            }
            
            send_result = send_tool.use(send_args)
            
            return {
                "success": send_result.get("success", False),
                "message": send_result.get("message"),
                "subject": draft_result["subject"],
                "sent_count": send_result.get("sent_count", 0),
                "email_id": send_result.get("email_id")
            }
            
        except Exception as e:
            logger.error(f"Error in draft_and_send: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def get_recipient_count(self, group: str = "all") -> dict:
        """
        Get the count of recipients in a specific group.
        
        Args:
            group: Customer segment to count.
        
        Returns:
            Dictionary with recipient count.
        """
        try:
            for tool in self.tools:
                if tool.name() == "get_recipients":
                    result = tool.use({"group": group})
                    return {
                        "success": True,
                        "group": group,
                        "count": result.get("count", 0)
                    }
            
            return {
                "success": False,
                "message": "Get recipients tool not available."
            }
            
        except Exception as e:
            logger.error(f"Error getting recipient count: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
