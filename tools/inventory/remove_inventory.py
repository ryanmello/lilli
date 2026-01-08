"""
Remove Inventory Tool
Allows removing products from the inventory database.
Aligned with Prisma Product model schema.
"""

from tools.base_tool import Tool
from services.database_service import DatabaseService
from utils.logger import get_logger
from bson import ObjectId
import json

logger = get_logger(__name__)


class RemoveInventoryTool(Tool):
    """
    Tool for removing products from the inventory (soft or hard delete).
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize the RemoveInventoryTool.
        
        Args:
            db_service: DatabaseService instance for database operations.
        """
        self.db_service = db_service
        self.collection_name = "Product"
    
    def name(self) -> str:
        return "remove_inventory"
    
    def description(self) -> str:
        return """Remove products from the inventory or mark them as inactive. 
        Required: name (str) or product_id (str) to identify the product
        Optional: soft_delete (bool, default=true) - if true, marks as inactive; if false, permanently deletes
        Example: {"name": "Red Rose"} or {"product_id": "507f1f77bcf86cd799439011", "soft_delete": false}"""
    
    def use(self, args):
        """
        Remove a product from the inventory or mark it as inactive.
        
        Args:
            args: Dictionary or JSON string containing product identifier.
        
        Returns:
            Dictionary with success status and message.
        """
        try:
            # Parse args if it's a string
            if isinstance(args, str):
                remove_data = json.loads(args)
            else:
                remove_data = args
            
            # Check for soft delete flag (default to true)
            soft_delete = remove_data.get('soft_delete', True)
            
            # Identify the product to remove
            query = {}
            if 'product_id' in remove_data:
                try:
                    query = {"_id": ObjectId(remove_data['product_id'])}
                    identifier = f"ID: {remove_data['product_id']}"
                except:
                    return {
                        "success": False,
                        "message": "Invalid product_id format."
                    }
            elif 'name' in remove_data:
                query = {"name": remove_data['name']}
                identifier = remove_data['name']
            else:
                return {
                    "success": False,
                    "message": "Please provide 'name' or 'product_id' to identify the product to remove."
                }
            
            # Check if product exists
            existing_product = self.db_service.find_one(self.collection_name, query)
            if not existing_product:
                logger.warning(f"Product not found: {identifier}")
                return {
                    "success": False,
                    "message": f"Product '{identifier}' not found in inventory."
                }
            
            # Store product details before removal
            product_name = existing_product.get('name', 'Unknown')
            product_quantity = existing_product.get('quantity', 0)
            
            if soft_delete:
                # Soft delete: Mark product as inactive
                success = self.db_service.update_one(
                    self.collection_name,
                    query,
                    {'isActive': False}
                )
                
                if success:
                    logger.info(f"Successfully marked product as inactive: {identifier}")
                    return {
                        "success": True,
                        "message": f"Successfully marked '{product_name}' as inactive in inventory.",
                        "action": "soft_delete",
                        "product": existing_product
                    }
                else:
                    logger.error(f"Failed to mark product as inactive: {identifier}")
                    return {
                        "success": False,
                        "message": "Failed to mark product as inactive."
                    }
            else:
                # Hard delete: Permanently remove product
                # Note: Cascade delete should handle related InventoryMovements if using Prisma
                # With raw MongoDB, you may need to manually delete related records
                
                # Create final inventory movement for tracking
                if existing_product.get('trackInventory', True) and product_quantity > 0:
                    self.db_service.create_inventory_movement(
                        product_id=existing_product['_id'],
                        shop_id=existing_product['shopId'],
                        movement_type="adjustment",
                        quantity_change=-product_quantity,
                        previous_inventory=product_quantity,
                        reason="Product deleted",
                        notes=f"Product '{product_name}' removed from system"
                    )
                
                # Delete the product
                success = self.db_service.delete_one(self.collection_name, query)
                
                if success:
                    logger.info(f"Successfully deleted product: {identifier}")
                    
                    # Optionally delete associated inventory movements
                    # self.db_service.delete_many("InventoryMovement", {"productId": ObjectId(existing_product['_id'])})
                    
                    return {
                        "success": True,
                        "message": f"Successfully removed '{product_name}' from inventory.",
                        "action": "hard_delete",
                        "removed_product": existing_product
                    }
                else:
                    logger.error(f"Failed to delete product: {identifier}")
                    return {
                        "success": False,
                        "message": "Failed to remove product from inventory."
                    }
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in args")
            return {
                "success": False,
                "message": "Invalid JSON format. Please provide valid product identifier."
            }
        except Exception as e:
            logger.error(f"Error removing inventory: {str(e)}")
            return {
                "success": False,
                "message": f"Error removing inventory: {str(e)}"
            }
