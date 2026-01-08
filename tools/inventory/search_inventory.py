"""
Search Inventory Tool
Allows searching and retrieving products from the inventory database.
Aligned with Prisma Product model schema.
"""

from tools.base_tool import Tool
from services.database_service import DatabaseService
from utils.logger import get_logger
from bson import ObjectId
import json

logger = get_logger(__name__)


class SearchInventoryTool(Tool):
    """
    Tool for searching products in the inventory.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize the SearchInventoryTool.
        
        Args:
            db_service: DatabaseService instance for database operations.
        """
        self.db_service = db_service
        self.collection_name = "Product"
    
    def name(self) -> str:
        return "search_inventory"
    
    def description(self) -> str:
        return """Search for products in the inventory. 
        Optional fields: name (str), category (str), color (str), shopId (str), 
                        min_quantity (int), max_quantity (int), isActive (bool, default=true),
                        low_stock (bool) - finds items at or below lowInventoryAlert threshold,
                        search_text (str) - searches across name, description, category
        Leave empty to retrieve all active products
        Examples: 
        - {"name": "Red Rose"} - find specific product by name
        - {"category": "Flowers"} - find all flowers
        - {"low_stock": true} - find products with low inventory
        - {"color": "Red", "isActive": true} - find active red products
        - {"search_text": "Rose"} - search for "Rose" in text fields
        - {} - retrieve all active products"""
    
    def use(self, args):
        """
        Search for products in the inventory.
        
        Args:
            args: Dictionary or JSON string containing search criteria.
        
        Returns:
            Dictionary with success status and list of matching products.
        """
        try:
            # Parse args if it's a string
            if isinstance(args, str):
                search_data = json.loads(args) if args.strip() else {}
            else:
                search_data = args if args else {}
            
            # Build search query
            query = {}
            
            # Default to active products only unless specified
            if 'isActive' not in search_data:
                query['isActive'] = True
            elif search_data.get('isActive') is not None:
                query['isActive'] = search_data['isActive']
            
            # Search by name (exact match)
            if 'name' in search_data:
                query['name'] = search_data['name']
            
            # Search by category
            if 'category' in search_data:
                query['category'] = search_data['category']
            
            # Search by color
            if 'color' in search_data:
                query['color'] = search_data['color']
            
            # Search by shopId
            if 'shopId' in search_data:
                try:
                    query['shopId'] = ObjectId(search_data['shopId'])
                except:
                    return {
                        "success": False,
                        "message": "Invalid shopId format."
                    }
            
            # Search by quantity range
            if 'min_quantity' in search_data or 'max_quantity' in search_data:
                quantity_query = {}
                if 'min_quantity' in search_data:
                    try:
                        quantity_query['$gte'] = int(search_data['min_quantity'])
                    except (ValueError, TypeError):
                        return {
                            "success": False,
                            "message": "min_quantity must be a valid number."
                        }
                if 'max_quantity' in search_data:
                    try:
                        quantity_query['$lte'] = int(search_data['max_quantity'])
                    except (ValueError, TypeError):
                        return {
                            "success": False,
                            "message": "max_quantity must be a valid number."
                        }
                query['quantity'] = quantity_query
            
            # Search for low stock items
            if search_data.get('low_stock'):
                # MongoDB: quantity <= lowInventoryAlert
                query['$expr'] = {'$lte': ['$quantity', '$lowInventoryAlert']}
            
            # Text search across multiple fields
            if 'search_text' in search_data and not any(k in search_data for k in ['name', 'category']):
                search_text = search_data['search_text']
                products = self.db_service.search_text(
                    self.collection_name,
                    search_text,
                    fields=['name', 'description', 'category', 'color', 'notes']
                )
            else:
                # Standard query
                products = self.db_service.find_many(
                    self.collection_name,
                    query,
                    sort_by=[('name', 1)]  # Sort by name ascending
                )
            
            count = len(products)
            
            if count == 0:
                logger.info("No products found matching search criteria")
                return {
                    "success": True,
                    "message": "No products found matching your search criteria.",
                    "count": 0,
                    "products": []
                }
            
            logger.info(f"Found {count} products matching search criteria")
            
            # Format products for response
            formatted_products = []
            for product in products:
                # Check if low inventory
                is_low_stock = (
                    product.get('trackInventory', True) and
                    product.get('quantity', 0) <= product.get('lowInventoryAlert', 10)
                )
                
                formatted_product = {
                    "product_id": product.get('_id'),
                    "name": product.get('name'),
                    "description": product.get('description', 'N/A'),
                    "category": product.get('category'),
                    "color": product.get('color', 'N/A'),
                    "costPrice": product.get('costPrice'),
                    "retailPrice": product.get('retailPrice'),
                    "quantity": product.get('quantity', 0),
                    "lowInventoryAlert": product.get('lowInventoryAlert', 10),
                    "trackInventory": product.get('trackInventory', True),
                    "shelfLifeDays": product.get('shelfLifeDays', 'N/A'),
                    "stemLength": product.get('stemLength', 'N/A'),
                    "image": product.get('image', 'N/A'),
                    "isActive": product.get('isActive', True),
                    "notes": product.get('notes', 'N/A'),
                    "shopId": product.get('shopId'),
                    "is_low_stock": is_low_stock,
                    "createdAt": str(product.get('createdAt', 'N/A')),
                    "updatedAt": str(product.get('updatedAt', 'N/A'))
                }
                formatted_products.append(formatted_product)
            
            # Count low stock items
            low_stock_count = sum(1 for p in formatted_products if p.get('is_low_stock'))
            
            response = {
                "success": True,
                "message": f"Found {count} product(s) in inventory.",
                "count": count,
                "low_stock_count": low_stock_count,
                "products": formatted_products
            }
            
            if low_stock_count > 0:
                response["warning"] = f"{low_stock_count} product(s) have low inventory!"
            
            return response
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in args")
            return {
                "success": False,
                "message": "Invalid JSON format. Please provide valid search criteria."
            }
        except Exception as e:
            logger.error(f"Error searching inventory: {str(e)}")
            return {
                "success": False,
                "message": f"Error searching inventory: {str(e)}"
            }
