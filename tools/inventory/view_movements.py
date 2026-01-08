"""
View Inventory Movements Tool
Allows viewing inventory movement history for products.
Aligned with Prisma InventoryMovement model schema.
"""

from tools.base_tool import Tool
from services.database_service import DatabaseService
from utils.logger import get_logger
from bson import ObjectId
import json

logger = get_logger(__name__)


class ViewMovementsTool(Tool):
    """
    Tool for viewing inventory movement history.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize the ViewMovementsTool.
        
        Args:
            db_service: DatabaseService instance for database operations.
        """
        self.db_service = db_service
        self.collection_name = "InventoryMovement"
    
    def name(self) -> str:
        return "view_movements"
    
    def description(self) -> str:
        return """View inventory movement history for products. 
        Optional fields: product_id (str), product_name (str), type (str), shopId (str), limit (int, default=50)
        Movement types: purchase, sale, adjustment, waste, return
        Examples: 
        - {"product_name": "Red Rose"} - view movements for specific product
        - {"type": "sale"} - view all sales
        - {"product_id": "507f1f77bcf86cd799439011", "limit": 10} - last 10 movements
        - {} - view recent movements (last 50)"""
    
    def use(self, args):
        """
        View inventory movements.
        
        Args:
            args: Dictionary or JSON string containing search criteria.
        
        Returns:
            Dictionary with success status and list of movements.
        """
        try:
            # Parse args if it's a string
            if isinstance(args, str):
                search_data = json.loads(args) if args.strip() else {}
            else:
                search_data = args if args else {}
            
            # Build query
            query = {}
            
            # Get limit (default 50)
            limit = search_data.get('limit', 50)
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = 50
            
            # Search by product_id
            if 'product_id' in search_data:
                try:
                    query['productId'] = ObjectId(search_data['product_id'])
                except:
                    return {
                        "success": False,
                        "message": "Invalid product_id format."
                    }
            
            # Search by product name (need to look up product first)
            elif 'product_name' in search_data:
                product = self.db_service.find_one("Product", {"name": search_data['product_name']})
                if not product:
                    return {
                        "success": False,
                        "message": f"Product '{search_data['product_name']}' not found."
                    }
                try:
                    query['productId'] = ObjectId(product['_id'])
                except:
                    return {
                        "success": False,
                        "message": "Error processing product ID."
                    }
            
            # Search by movement type
            if 'type' in search_data:
                valid_types = ['purchase', 'sale', 'adjustment', 'waste', 'return']
                if search_data['type'] in valid_types:
                    query['type'] = search_data['type']
                else:
                    return {
                        "success": False,
                        "message": f"Invalid type. Must be one of: {', '.join(valid_types)}"
                    }
            
            # Search by shopId
            if 'shopId' in search_data:
                try:
                    query['shopId'] = ObjectId(search_data['shopId'])
                except:
                    return {
                        "success": False,
                        "message": "Invalid shopId format."
                    }
            
            # Get movements, sorted by createdAt descending (most recent first)
            movements = self.db_service.find_many(
                self.collection_name,
                query,
                limit=limit,
                sort_by=[('createdAt', -1)]
            )
            
            count = len(movements)
            
            if count == 0:
                logger.info("No movements found matching criteria")
                return {
                    "success": True,
                    "message": "No inventory movements found matching your criteria.",
                    "count": 0,
                    "movements": []
                }
            
            logger.info(f"Found {count} inventory movements")
            
            # Format movements for response
            formatted_movements = []
            for movement in movements:
                # Get product name
                product_name = "Unknown"
                if 'productId' in movement:
                    try:
                        product = self.db_service.find_by_id("Product", movement['productId'])
                        if product:
                            product_name = product.get('name', 'Unknown')
                    except:
                        pass
                
                formatted_movement = {
                    "movement_id": movement.get('_id'),
                    "product_id": movement.get('productId'),
                    "product_name": product_name,
                    "type": movement.get('type'),
                    "quantity": movement.get('quantity'),
                    "previous_inventory": movement.get('previousInventory'),
                    "new_inventory": movement.get('newInventory'),
                    "reason": movement.get('reason', 'N/A'),
                    "reference_id": movement.get('referenceId', 'N/A'),
                    "notes": movement.get('notes', 'N/A'),
                    "shop_id": movement.get('shopId'),
                    "created_at": str(movement.get('createdAt', 'N/A'))
                }
                formatted_movements.append(formatted_movement)
            
            # Calculate summary statistics
            total_quantity_changes = sum(m.get('quantity', 0) for m in movements)
            type_counts = {}
            for m in movements:
                m_type = m.get('type', 'unknown')
                type_counts[m_type] = type_counts.get(m_type, 0) + 1
            
            return {
                "success": True,
                "message": f"Found {count} inventory movement(s).",
                "count": count,
                "total_quantity_changes": total_quantity_changes,
                "type_breakdown": type_counts,
                "movements": formatted_movements
            }
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in args")
            return {
                "success": False,
                "message": "Invalid JSON format. Please provide valid search criteria."
            }
        except Exception as e:
            logger.error(f"Error viewing movements: {str(e)}")
            return {
                "success": False,
                "message": f"Error viewing movements: {str(e)}"
            }

