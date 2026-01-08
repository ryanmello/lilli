"""
Update Inventory Tool
Allows updating existing products in the inventory database.
Aligned with Prisma Product model schema.
"""

from tools.base_tool import Tool
from services.database_service import DatabaseService
from utils.logger import get_logger
from bson import ObjectId
import json

logger = get_logger(__name__)


class UpdateInventoryTool(Tool):
    """
    Tool for updating existing products in the inventory.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize the UpdateInventoryTool.
        
        Args:
            db_service: DatabaseService instance for database operations.
        """
        self.db_service = db_service
        self.collection_name = "Product"
    
    def name(self) -> str:
        return "update_inventory"
    
    def description(self) -> str:
        return """Update existing products in inventory. 
        Required: name (str) or product_id (str) to identify the product
        Optional fields to update: description, category, color, costPrice, retailPrice, quantity, 
                                   lowInventoryAlert, trackInventory, shelfLifeDays, stemLength, 
                                   image, isActive, notes
        For quantity changes, specify: quantity_change (int) and movement_type (purchase/sale/adjustment/waste/return)
        Example: {"name": "Red Rose", "quantity": 120, "retailPrice": 6.99}
        Example with movement: {"name": "Red Rose", "quantity_change": 20, "movement_type": "purchase", "reason": "Restocking"}"""
    
    def use(self, args):
        """
        Update an existing product in the inventory.
        
        Args:
            args: Dictionary or JSON string containing product identifier and fields to update.
        
        Returns:
            Dictionary with success status and message.
        """
        try:
            # Parse args if it's a string
            if isinstance(args, str):
                update_data = json.loads(args)
            else:
                update_data = args
            
            # Identify the product to update
            query = {}
            if 'product_id' in update_data:
                try:
                    query = {"_id": ObjectId(update_data['product_id'])}
                    identifier = f"ID: {update_data['product_id']}"
                except:
                    return {
                        "success": False,
                        "message": "Invalid product_id format."
                    }
            elif 'name' in update_data:
                query = {"name": update_data['name']}
                identifier = update_data['name']
            else:
                return {
                    "success": False,
                    "message": "Please provide 'name' or 'product_id' to identify the product to update."
                }
            
            # Check if product exists
            existing_product = self.db_service.find_one(self.collection_name, query)
            if not existing_product:
                logger.warning(f"Product not found: {identifier}")
                return {
                    "success": False,
                    "message": f"Product '{identifier}' not found in inventory."
                }
            
            # Handle quantity changes with inventory movement tracking
            quantity_change = update_data.get('quantity_change')
            movement_type = update_data.get('movement_type')
            
            if quantity_change is not None:
                try:
                    quantity_change = int(quantity_change)
                    current_quantity = existing_product.get('quantity', 0)
                    new_quantity = current_quantity + quantity_change
                    
                    if new_quantity < 0:
                        return {
                            "success": False,
                            "message": f"Cannot reduce quantity by {abs(quantity_change)}. Current quantity is {current_quantity}."
                        }
                    
                    # Update quantity
                    update_data['quantity'] = new_quantity
                    
                    # Create inventory movement if tracking is enabled
                    if existing_product.get('trackInventory', True):
                        if not movement_type:
                            # Auto-determine movement type
                            movement_type = "purchase" if quantity_change > 0 else "sale"
                        
                        self.db_service.create_inventory_movement(
                            product_id=existing_product['_id'],
                            shop_id=existing_product['shopId'],
                            movement_type=movement_type,
                            quantity_change=quantity_change,
                            previous_inventory=current_quantity,
                            reason=update_data.get('reason'),
                            reference_id=update_data.get('reference_id'),
                            notes=update_data.get('notes')
                        )
                    
                    # Remove these from update_data as they're not product fields
                    update_data.pop('quantity_change', None)
                    update_data.pop('movement_type', None)
                    update_data.pop('reason', None)
                    update_data.pop('reference_id', None)
                    
                except (ValueError, TypeError):
                    return {
                        "success": False,
                        "message": "quantity_change must be a valid number."
                    }
            
            # Prepare update fields (exclude identifier fields)
            update_fields = {k: v for k, v in update_data.items() 
                           if k not in ['name', 'product_id', 'shopId'] and v is not None}
            
            if not update_fields:
                return {
                    "success": False,
                    "message": "No fields provided to update."
                }
            
            # Validate numeric fields
            if 'costPrice' in update_fields:
                try:
                    update_fields['costPrice'] = float(update_fields['costPrice'])
                    if update_fields['costPrice'] < 0:
                        return {"success": False, "message": "costPrice must be positive."}
                except (ValueError, TypeError):
                    return {"success": False, "message": "costPrice must be a valid number."}
            
            if 'retailPrice' in update_fields:
                try:
                    update_fields['retailPrice'] = float(update_fields['retailPrice'])
                    if update_fields['retailPrice'] < 0:
                        return {"success": False, "message": "retailPrice must be positive."}
                except (ValueError, TypeError):
                    return {"success": False, "message": "retailPrice must be a valid number."}
            
            if 'quantity' in update_fields and 'quantity_change' not in update_data:
                try:
                    update_fields['quantity'] = int(update_fields['quantity'])
                    if update_fields['quantity'] < 0:
                        return {"success": False, "message": "Quantity must be positive."}
                except (ValueError, TypeError):
                    return {"success": False, "message": "Quantity must be a valid number."}
            
            if 'lowInventoryAlert' in update_fields:
                try:
                    update_fields['lowInventoryAlert'] = int(update_fields['lowInventoryAlert'])
                except (ValueError, TypeError):
                    return {"success": False, "message": "lowInventoryAlert must be a valid number."}
            
            if 'shelfLifeDays' in update_fields:
                try:
                    update_fields['shelfLifeDays'] = int(update_fields['shelfLifeDays'])
                except (ValueError, TypeError):
                    return {"success": False, "message": "shelfLifeDays must be a valid number."}
            
            # Update the product
            success = self.db_service.update_one(
                self.collection_name,
                query,
                update_fields
            )
            
            if success:
                logger.info(f"Successfully updated product: {identifier}")
                updated_product = self.db_service.find_one(self.collection_name, query)
                
                # Check low inventory alert
                alert_message = ""
                if (updated_product.get('trackInventory', True) and 
                    updated_product.get('quantity', 0) <= updated_product.get('lowInventoryAlert', 10)):
                    alert_message = f" Warning: Low inventory! Current: {updated_product.get('quantity', 0)}, Alert threshold: {updated_product.get('lowInventoryAlert', 10)}"
                
                return {
                    "success": True,
                    "message": f"Successfully updated '{identifier}' in inventory.{alert_message}",
                    "updated_product": updated_product
                }
            else:
                logger.error(f"Failed to update product: {identifier}")
                return {
                    "success": False,
                    "message": "Failed to update product. No changes were made."
                }
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in args")
            return {
                "success": False,
                "message": "Invalid JSON format. Please provide valid update data."
            }
        except Exception as e:
            logger.error(f"Error updating inventory: {str(e)}")
            return {
                "success": False,
                "message": f"Error updating inventory: {str(e)}"
            }
