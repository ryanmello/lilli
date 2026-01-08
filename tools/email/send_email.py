"""
Send Email Tool
Sends emails using the Resend service.
"""

from tools.base_tool import Tool
from services.resend_service import ResendService
from services.database_service import DatabaseService
from utils.logger import get_logger
from bson import ObjectId
import json
from typing import List, Optional

logger = get_logger(__name__)


class SendEmailTool(Tool):
    """
    Tool for sending emails via Resend API.
    """
    
    def __init__(
        self, 
        resend_service: ResendService, 
        db_service: Optional[DatabaseService] = None,
        shop_id: Optional[str] = None
    ):
        """
        Initialize the SendEmailTool.
        
        Args:
            resend_service: ResendService instance for sending emails.
            db_service: Optional DatabaseService for fetching recipient lists.
            shop_id: Optional shop ID for filtering customers.
        """
        self.resend_service = resend_service
        self.db_service = db_service
        self.shop_id = shop_id
    
    def name(self) -> str:
        return "send_email"
    
    def description(self) -> str:
        return """Send an email to recipients via Resend.
        Required fields: subject (str), body (str) - HTML content
        Optional fields: to (list of emails OR group name like "all_customers", "vip_customers"), 
                        from_email (str) - sender address
        Groups: "all_customers", "vip_customers", "subscribers", "recent_customers"
        Example: {"to": "all_customers", "subject": "Hello!", "body": "<h1>Hi there</h1>"}
        Example with specific emails: {"to": ["user1@example.com", "user2@example.com"], "subject": "Hello!", "body": "<h1>Hi</h1>"}"""
    
    def use(self, args) -> dict:
        """
        Send an email to the specified recipients.
        
        Args:
            args: Dictionary or JSON string containing:
                  - to: List of email addresses OR a group identifier
                  - subject: Email subject line
                  - body: HTML email body
                  - from_email: Optional sender email address
        
        Returns:
            Dictionary with success status and send results.
        """
        try:
            # Parse args if it's a string
            if isinstance(args, str):
                params = json.loads(args)
            else:
                params = args
            
            subject = params.get("subject", "")
            body = params.get("body", "")
            to = params.get("to", "all_customers")
            from_email = params.get("from_email")
            
            # Validate required fields
            if not subject:
                return {
                    "success": False,
                    "message": "Subject is required."
                }
            
            if not body:
                return {
                    "success": False,
                    "message": "Email body is required."
                }
            
            # Resolve recipients
            recipients = self._resolve_recipients(to)
            
            if not recipients:
                return {
                    "success": False,
                    "message": "No valid recipients found."
                }
            
            # Validate email addresses
            validation = self.resend_service.validate_emails(recipients)
            
            if validation["invalid"]:
                logger.warning(f"Found {len(validation['invalid'])} invalid email addresses")
            
            valid_recipients = validation["valid"]
            
            if not valid_recipients:
                return {
                    "success": False,
                    "message": "No valid email addresses found.",
                    "invalid_emails": validation["invalid"]
                }
            
            # Send the email
            logger.info(f"Sending email to {len(valid_recipients)} recipients")
            
            result = self.resend_service.send_email(
                to=valid_recipients,
                subject=subject,
                html=body,
                from_email=from_email
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Successfully sent email to {len(valid_recipients)} recipient(s).",
                    "sent_count": len(valid_recipients),
                    "subject": subject,
                    "invalid_count": len(validation["invalid"]),
                    "email_id": result.get("email_id")
                }
            else:
                return {
                    "success": False,
                    "message": result.get("message", "Failed to send email."),
                    "error": result.get("error")
                }
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in args")
            return {
                "success": False,
                "message": "Invalid JSON format. Please provide valid parameters."
            }
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                "success": False,
                "message": f"Error sending email: {str(e)}"
            }
    
    def _resolve_recipients(self, to) -> List[str]:
        """
        Resolve recipient list from group identifier or email list.
        
        Args:
            to: Either a list of email addresses or a group identifier string.
        
        Returns:
            List of email addresses.
        """
        # If it's already a list of emails, return it
        if isinstance(to, list):
            return to
        
        # If it's a string, check if it's a group identifier
        if isinstance(to, str):
            # Check if it looks like an email address
            if "@" in to:
                return [to]
            
            # It's a group identifier, fetch from database
            return self._fetch_recipients_by_group(to)
        
        return []
    
    def _fetch_recipients_by_group(self, group: str) -> List[str]:
        """
        Fetch recipient emails from database based on group.
        
        Args:
            group: Group identifier (all_customers, vip_customers, etc.)
        
        Returns:
            List of email addresses.
        """
        if not self.db_service:
            logger.warning("No database service configured, cannot fetch recipients by group")
            return []
        
        try:
            query = {}
            
            # Add shop filter if available
            if self.shop_id:
                query["shopId"] = ObjectId(self.shop_id)
            
            # Define group filters
            if group == "all_customers":
                # All customers with valid email
                query["email"] = {"$exists": True, "$ne": None, "$ne": ""}
                
            elif group == "vip_customers":
                # VIP or high-value customers
                query["email"] = {"$exists": True, "$ne": None, "$ne": ""}
                query["$or"] = [
                    {"isVip": True},
                    {"totalSpent": {"$gte": 1000}}  # Example threshold
                ]
                
            elif group == "subscribers":
                # Customers who opted in for marketing
                query["email"] = {"$exists": True, "$ne": None, "$ne": ""}
                query["marketingOptIn"] = True
                
            elif group == "recent_customers":
                # Customers with recent activity
                from datetime import datetime, timedelta
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                query["email"] = {"$exists": True, "$ne": None, "$ne": ""}
                query["lastPurchaseDate"] = {"$gte": thirty_days_ago}
                
            else:
                # Default: all customers with email
                query["email"] = {"$exists": True, "$ne": None, "$ne": ""}
            
            # Fetch customers from database
            customers = self.db_service.find_many("Customer", query)
            
            # Extract email addresses
            emails = [c.get("email") for c in customers if c.get("email")]
            
            logger.info(f"Found {len(emails)} recipients for group: {group}")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching recipients by group: {str(e)}")
            return []
