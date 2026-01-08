"""
Draft Email Tool
Uses LLM to generate email templates based on user requests.
"""

from tools.base_tool import Tool
from utils.llm import query_llm
from utils.logger import get_logger
import json

logger = get_logger(__name__)


class DraftEmailTool(Tool):
    """
    Tool for drafting email content using LLM.
    """
    
    def __init__(self, business_name: str = "Our Business"):
        """
        Initialize the DraftEmailTool.
        
        Args:
            business_name: Name of the business for email branding.
        """
        self.business_name = business_name
    
    def name(self) -> str:
        return "draft_email"
    
    def description(self) -> str:
        return """Draft an email based on purpose and context.
        Required fields: purpose (str) - the intent/occasion for the email (e.g., "valentines day reminder", "sale announcement", "thank you")
        Optional fields: tone (str, default="friendly") - email tone (professional, casual, friendly, urgent),
                        key_points (list) - specific points to include in the email,
                        recipient_type (str) - who the email is for (customers, subscribers, vip, etc.)
        Example: {"purpose": "valentines day reminder", "tone": "friendly", "key_points": ["20% off roses", "free delivery"]}
        Returns: {"subject": "...", "body": "...html content..."}"""
    
    def use(self, args) -> dict:
        """
        Draft an email based on the provided purpose and context.
        
        Args:
            args: Dictionary or JSON string containing:
                  - purpose: The intent/occasion for the email
                  - tone: Optional tone preference
                  - key_points: Optional list of points to include
                  - recipient_type: Optional recipient description
        
        Returns:
            Dictionary with subject and body of the drafted email.
        """
        try:
            # Parse args if it's a string
            if isinstance(args, str):
                params = json.loads(args)
            else:
                params = args
            
            purpose = params.get("purpose", "")
            if not purpose:
                return {
                    "success": False,
                    "message": "Purpose is required for drafting an email."
                }
            
            tone = params.get("tone", "friendly")
            key_points = params.get("key_points", [])
            recipient_type = params.get("recipient_type", "customers")
            
            # Build the prompt for LLM
            key_points_text = ""
            if key_points:
                key_points_text = f"\nKey points to include:\n" + "\n".join(f"- {point}" for point in key_points)
            
            prompt = f"""You are an expert email copywriter. Draft a professional marketing email for {self.business_name}.

Purpose: {purpose}
Tone: {tone}
Target audience: {recipient_type}
{key_points_text}

Create an engaging email with:
1. An attention-grabbing subject line
2. A compelling HTML email body with proper formatting

Respond ONLY with a valid JSON object in this exact format (no markdown, no extra text):
{{"subject": "Your subject line here", "body": "<html email content here>"}}

Make the HTML body visually appealing with:
- A greeting
- Main message content
- Clear call-to-action if appropriate
- Professional sign-off
- Use inline CSS for basic styling (colors, fonts, spacing)

Keep the email concise but impactful."""

            logger.info(f"Drafting email for purpose: {purpose}")
            
            # Query LLM for email content
            response = query_llm(prompt)
            
            # Parse the LLM response
            try:
                # Clean up the response if needed
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                email_content = json.loads(response)
                
                if "subject" not in email_content or "body" not in email_content:
                    raise ValueError("Missing subject or body in response")
                
                logger.info(f"Successfully drafted email with subject: {email_content['subject']}")
                
                return {
                    "success": True,
                    "subject": email_content["subject"],
                    "body": email_content["body"],
                    "purpose": purpose,
                    "tone": tone,
                    "message": "Email drafted successfully. Ready to send."
                }
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse LLM response: {e}")
                # Fallback: create a simple template
                return self._create_fallback_email(purpose, tone, recipient_type, key_points)
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in args")
            return {
                "success": False,
                "message": "Invalid JSON format. Please provide valid parameters."
            }
        except Exception as e:
            logger.error(f"Error drafting email: {str(e)}")
            return {
                "success": False,
                "message": f"Error drafting email: {str(e)}"
            }
    
    def _create_fallback_email(
        self, 
        purpose: str, 
        tone: str, 
        recipient_type: str,
        key_points: list
    ) -> dict:
        """
        Create a fallback email template if LLM parsing fails.
        """
        subject = f"{purpose.title()} - A Message from {self.business_name}"
        
        key_points_html = ""
        if key_points:
            key_points_html = "<ul>" + "".join(f"<li>{point}</li>" for point in key_points) + "</ul>"
        
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4a90d9; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.business_name}</h1>
    </div>
    <div class="content">
        <p>Dear Valued {recipient_type.title()},</p>
        <p>We wanted to reach out to you regarding: <strong>{purpose}</strong></p>
        {key_points_html}
        <p>Thank you for your continued support!</p>
        <p>Best regards,<br>{self.business_name} Team</p>
    </div>
    <div class="footer">
        <p>© {self.business_name}. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        return {
            "success": True,
            "subject": subject,
            "body": body,
            "purpose": purpose,
            "tone": tone,
            "message": "Email drafted using fallback template."
        }
