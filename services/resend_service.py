"""
Resend Email Service
Wrapper for Resend API to send emails.
"""

import resend
from typing import List, Dict, Optional, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class ResendService:
    """
    Service class for sending emails via Resend API.
    """
    
    def __init__(self, api_key: str, default_from_email: str = "noreply@example.com"):
        """
        Initialize the Resend service.
        
        Args:
            api_key: Resend API key.
            default_from_email: Default sender email address.
        """
        self.api_key = api_key
        self.default_from_email = default_from_email
        resend.api_key = api_key
        
    def send_email(
        self, 
        to: List[str], 
        subject: str, 
        html: str, 
        from_email: Optional[str] = None,
        text: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a single email to one or more recipients.
        
        Args:
            to: List of recipient email addresses.
            subject: Email subject line.
            html: HTML content of the email.
            from_email: Sender email address (uses default if not provided).
            text: Plain text version of the email (optional).
            reply_to: Reply-to email address (optional).
            
        Returns:
            Dictionary with success status and response data.
        """
        try:
            params = {
                "from": from_email or self.default_from_email,
                "to": to,
                "subject": subject,
                "html": html,
            }
            
            if text:
                params["text"] = text
            if reply_to:
                params["reply_to"] = reply_to
            
            response = resend.Emails.send(params)
            
            logger.info(f"Email sent successfully to {len(to)} recipient(s)")
            
            return {
                "success": True,
                "message": f"Email sent successfully to {len(to)} recipient(s)",
                "email_id": response.get("id") if isinstance(response, dict) else getattr(response, 'id', None),
                "recipients": to
            }
            
        except resend.exceptions.ResendError as e:
            logger.error(f"Resend API error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}",
                "error": str(e)
            }
    
    def send_batch(
        self, 
        emails: List[Dict[str, Any]],
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send multiple emails in a batch.
        
        Args:
            emails: List of email dictionaries, each containing:
                   - to: recipient email address or list of addresses
                   - subject: email subject
                   - html: HTML content
                   - text (optional): plain text content
            from_email: Sender email address for all emails (uses default if not provided).
            
        Returns:
            Dictionary with success status and batch results.
        """
        try:
            batch_params = []
            
            for email in emails:
                params = {
                    "from": from_email or self.default_from_email,
                    "to": email["to"] if isinstance(email["to"], list) else [email["to"]],
                    "subject": email["subject"],
                    "html": email["html"],
                }
                
                if "text" in email:
                    params["text"] = email["text"]
                    
                batch_params.append(params)
            
            response = resend.Batch.send(batch_params)
            
            logger.info(f"Batch of {len(emails)} emails sent successfully")
            
            return {
                "success": True,
                "message": f"Batch of {len(emails)} emails sent successfully",
                "sent_count": len(emails),
                "response": response
            }
            
        except resend.exceptions.ResendError as e:
            logger.error(f"Resend batch API error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send batch emails: {str(e)}",
                "error": str(e),
                "sent_count": 0
            }
        except Exception as e:
            logger.error(f"Unexpected error sending batch emails: {str(e)}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}",
                "error": str(e),
                "sent_count": 0
            }
    
    def validate_email(self, email: str) -> bool:
        """
        Basic email validation.
        
        Args:
            email: Email address to validate.
            
        Returns:
            bool: True if email format appears valid.
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_emails(self, emails: List[str]) -> Dict[str, List[str]]:
        """
        Validate a list of email addresses.
        
        Args:
            emails: List of email addresses to validate.
            
        Returns:
            Dictionary with 'valid' and 'invalid' lists.
        """
        valid = []
        invalid = []
        
        for email in emails:
            if self.validate_email(email):
                valid.append(email)
            else:
                invalid.append(email)
        
        return {
            "valid": valid,
            "invalid": invalid
        }
