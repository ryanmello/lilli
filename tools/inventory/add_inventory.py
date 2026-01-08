"""
Add Inventory Tool
Allows adding new products to the inventory database.
Aligned with Prisma Product model schema.
"""

from tools.base_tool import Tool
from services.database_service import DatabaseService
from utils.logger import get_logger
from bson import ObjectId
import json

logger = get_logger(__name__)

class AddInventoryTool(Tool):
    """
    Tool for adding new products to the inventory.
    """
    
    def __init__(self, db_service: DatabaseService, default_shop_id: str = None):
        """
        Initialize the AddInventoryTool.
        
        Args:
            db_service: DatabaseService instance for database operations.
            default_shop_id: Default shop ID if not provided in requests.
        """
        self.db_service = db_service
        self.collection_name = "Product"
        self.default_shop_id = default_shop_id
    
    def name(self) -> str:
        return "add_inventory"
    
    def description(self) -> str:
        return """Add new products to the inventory. 
        Required fields: name (str), category (str), costPrice (float), retailPrice (float), shopId (str)
        Optional fields: description (str), color (str), quantity (int, default=0), lowInventoryAlert (int, default=10),
                        trackInventory (bool, default=true), shelfLifeDays (int), stemLength (str), 
                        image (str), isActive (bool, default=true), notes (str)
        Example: {"name": "Red Rose", "category": "Flowers", "costPrice": 2.50, "retailPrice": 5.99, 
                 "quantity": 100, "color": "Red", "stemLength": "Long", "shelfLifeDays": 7, "shopId": "shop123"}"""
    
    def use(self, args):
        """
        Add a new product to the inventory.
        
        Args:
            args: Dictionary or JSON string containing product details.
        
        Returns:
            Dictionary with success status and message or product_id.
        """
        try:
            # Parse args if it's a string
            if isinstance(args, str):
                product_data = json.loads(args)
            else:
                product_data = args
            
            # Validate required fields
            required_fields = ['name', 'category', 'costPrice', 'retailPrice']
            missing_fields = [field for field in required_fields if field not in product_data]
            
            if missing_fields:
                logger.error(f"Missing required fields: {', '.join(missing_fields)}")
                return {
                    "success": False,
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            # Handle shopId - use default if not provided
            if 'shopId' not in product_data:
                if self.default_shop_id:
                    product_data['shopId'] = self.default_shop_id
                else:
                    return {
                        "success": False,
                        "message": "shopId is required. Please provide a valid shop ID."
                    }
            
            # Convert shopId to ObjectId
            try:
                product_data['shopId'] = ObjectId(product_data['shopId'])
            except Exception:
                return {
                    "success": False,
                    "message": "Invalid shopId format."
                }
            
            # Validate and set numeric fields
            try:
                product_data['costPrice'] = float(product_data['costPrice'])
                product_data['retailPrice'] = float(product_data['retailPrice'])
                
                if product_data['costPrice'] < 0 or product_data['retailPrice'] < 0:
                    return {
                        "success": False,
                        "message": "Prices must be positive numbers."
                    }
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "message": "costPrice and retailPrice must be valid numbers."
                }
            
            # Set default values for optional fields
            product_data.setdefault('quantity', 0)
            product_data.setdefault('lowInventoryAlert', 10)
            product_data.setdefault('trackInventory', True)
            product_data.setdefault('isActive', True)
            
            # Validate quantity
            if 'quantity' in product_data:
                try:
                    product_data['quantity'] = int(product_data['quantity'])
                    if product_data['quantity'] < 0:
                        return {
                            "success": False,
                            "message": "Quantity must be a positive number."
                        }
                except (ValueError, TypeError):
                    return {
                        "success": False,
                        "message": "Quantity must be a valid number."
                    }
            
            # Validate lowInventoryAlert
            if 'lowInventoryAlert' in product_data:
                try:
                    product_data['lowInventoryAlert'] = int(product_data['lowInventoryAlert'])
                except (ValueError, TypeError):
                    return {
                        "success": False,
                        "message": "lowInventoryAlert must be a valid number."
                    }
            
            # Validate shelfLifeDays if provided
            if 'shelfLifeDays' in product_data and product_data['shelfLifeDays'] is not None:
                try:
                    product_data['shelfLifeDays'] = int(product_data['shelfLifeDays'])
                except (ValueError, TypeError):
                    return {
                        "success": False,
                        "message": "shelfLifeDays must be a valid number."
                    }
            
            # Check if product already exists for this shop
            existing_product = self.db_service.find_one(
                self.collection_name, 
                {"name": product_data['name'], "shopId": product_data['shopId']}
            )
            
            if existing_product:
                logger.warning(f"Product '{product_data['name']}' already exists for this shop")
                return {
                    "success": False,
                    "message": f"Product '{product_data['name']}' already exists. Use update_inventory to modify it."
                }
            
            # Store initial quantity for movement tracking
            initial_quantity = product_data.get('quantity', 0)
            
            # Add product to database
            product_id = self.db_service.insert_one(self.collection_name, product_data)
            
            if product_id:
                # Create inventory movement if quantity > 0
                if initial_quantity > 0 and product_data.get('trackInventory', True):
                    self.db_service.create_inventory_movement(
                        product_id=product_id,
                        shop_id=str(product_data['shopId']),
                        movement_type="purchase",
                        quantity_change=initial_quantity,
                        previous_inventory=0,
                        reason="Initial stock",
                        notes="Product created with initial inventory"
                    )
                
                logger.info(f"Successfully added product: {product_data['name']} (ID: {product_id})")
                
                # Prepare response data
                response_data = product_data.copy()
                response_data['shopId'] = str(response_data['shopId'])
                
                return {
                    "success": True,
                    "message": f"Successfully added '{product_data['name']}' to inventory.",
                    "product_id": product_id,
                    "product": response_data
                }
            else:
                logger.error("Failed to add product to database")
                return {
                    "success": False,
                    "message": "Failed to add product to inventory."
                }
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in args")
            return {
                "success": False,
                "message": "Invalid JSON format. Please provide valid product data."
            }
        except Exception as e:
            logger.error(f"Error adding inventory: {str(e)}")
            return {
                "success": False,
                "message": f"Error adding inventory: {str(e)}"
            }
