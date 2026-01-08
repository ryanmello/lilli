"""
Get Recipients Tool
Fetches recipient email addresses based on criteria.
"""

from tools.base_tool import Tool
from services.database_service import DatabaseService
from utils.logger import get_logger
from bson import ObjectId
import json
from typing import Optional
from datetime import datetime, timedelta

logger = get_logger(__name__)


class GetRecipientsTool(Tool):
    """
    Tool for fetching recipient email addresses from the database.
    """
    
    def __init__(self, db_service: DatabaseService, shop_id: Optional[str] = None):
        """
        Initialize the GetRecipientsTool.
        
        Args:
            db_service: DatabaseService instance for database operations.
            shop_id: Optional shop ID for filtering customers.
        """
        self.db_service = db_service
        self.shop_id = shop_id
    
    def name(self) -> str:
        return "get_recipients"
    
    def description(self) -> str:
        return """Get a list of recipient email addresses based on criteria.
        Optional fields: group (str) - customer segment to fetch
        Available groups: "all" (all customers), "vip" (VIP customers), "subscribers" (marketing opt-in), 
                         "recent" (purchased in last 30 days), "inactive" (no purchase in 90+ days)
        Example: {"group": "vip"}
        Returns: {"recipients": ["email1@example.com", ...], "count": 10}"""
    
    def use(self, args) -> dict:
        """
        Fetch recipient emails based on the specified criteria.
        
        Args:
            args: Dictionary or JSON string containing:
                  - group: Customer segment to fetch
        
        Returns:
            Dictionary with list of recipient emails and count.
        """
        try:
            # Parse args if it's a string
            if isinstance(args, str):
                params = json.loads(args)
            else:
                params = args
            
            group = params.get("group", "all")
            
            # Build query based on group
            query = self._build_query(group)
            
            # Fetch customers
            customers = self.db_service.find_many("Customer", query)
            
            # Extract emails
            recipients = []
            for customer in customers:
                email = customer.get("email")
                if email and isinstance(email, str) and "@" in email:
                    recipients.append(email)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_recipients = []
            for email in recipients:
                email_lower = email.lower()
                if email_lower not in seen:
                    seen.add(email_lower)
                    unique_recipients.append(email)
            
            logger.info(f"Found {len(unique_recipients)} recipients for group: {group}")
            
            return {
                "success": True,
                "recipients": unique_recipients,
                "count": len(unique_recipients),
                "group": group,
                "message": f"Found {len(unique_recipients)} recipient(s) in the '{group}' group."
            }
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in args")
            return {
                "success": False,
                "message": "Invalid JSON format. Please provide valid parameters.",
                "recipients": [],
                "count": 0
            }
        except Exception as e:
            logger.error(f"Error fetching recipients: {str(e)}")
            return {
                "success": False,
                "message": f"Error fetching recipients: {str(e)}",
                "recipients": [],
                "count": 0
            }
    
    def _build_query(self, group: str) -> dict:
        """
        Build MongoDB query based on group identifier.
        
        Args:
            group: Customer segment identifier.
        
        Returns:
            MongoDB query dictionary.
        """
        query = {}
        
        # Add shop filter if available
        if self.shop_id:
            try:
                query["shopId"] = ObjectId(self.shop_id)
            except Exception:
                pass
        
        # Base filter: must have valid email
        email_filter = {"$exists": True, "$ne": None, "$ne": ""}
        
        if group == "all":
            query["email"] = email_filter
            
        elif group == "vip":
            query["email"] = email_filter
            query["$or"] = [
                {"isVip": True},
                {"customerType": "vip"},
                {"totalSpent": {"$gte": 1000}}
            ]
            
        elif group == "subscribers":
            query["email"] = email_filter
            query["$or"] = [
                {"marketingOptIn": True},
                {"emailSubscribed": True},
                {"subscribed": True}
            ]
            
        elif group == "recent":
            query["email"] = email_filter
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            query["$or"] = [
                {"lastPurchaseDate": {"$gte": thirty_days_ago}},
                {"lastOrderDate": {"$gte": thirty_days_ago}},
                {"updatedAt": {"$gte": thirty_days_ago}}
            ]
            
        elif group == "inactive":
            query["email"] = email_filter
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            query["$or"] = [
                {"lastPurchaseDate": {"$lt": ninety_days_ago}},
                {"lastOrderDate": {"$lt": ninety_days_ago}},
                {"lastPurchaseDate": {"$exists": False}}
            ]
            
        else:
            # Default: all with email
            query["email"] = email_filter
        
        return query
    
    def get_available_groups(self) -> dict:
        """
        Get information about available recipient groups.
        
        Returns:
            Dictionary with group names and descriptions.
        """
        return {
            "groups": {
                "all": "All customers with valid email addresses",
                "vip": "VIP customers or those with high total spending",
                "subscribers": "Customers who opted in for marketing emails",
                "recent": "Customers who made a purchase in the last 30 days",
                "inactive": "Customers with no activity in 90+ days"
            }
        }
