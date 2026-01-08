from agents.base_agent import Agent
from services.database_service import DatabaseService
from tools.inventory.add_inventory import AddInventoryTool
from tools.inventory.update_inventory import UpdateInventoryTool
from tools.inventory.remove_inventory import RemoveInventoryTool
from tools.inventory.search_inventory import SearchInventoryTool
from tools.inventory.view_movements import ViewMovementsTool
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

class InventoryAgent(Agent):
    """
    Agent specialized in product inventory management operations.
    Supports full CRUD operations and inventory movement tracking.
    """
    
    def __init__(self, shop_id: str):
        """
        Initialize the Inventory Agent with all inventory tools.
        
        Args:
            shop_id: shop ID for operations.
        """
        # Initialize database service
        connection_string = settings.DATABASE_URL
        
        self.db_service = DatabaseService(connection_string)
        self.shop_id = shop_id
        
        # Connect to database
        if not self.db_service.connect():
            logger.error("Failed to connect to MongoDB. Please check your connection string.")
            raise ConnectionError("Could not establish database connection")
        
        # Initialize tools
        tools = [
            AddInventoryTool(self.db_service, shop_id),
            UpdateInventoryTool(self.db_service, shop_id),
            RemoveInventoryTool(self.db_service, shop_id),
            SearchInventoryTool(self.db_service, shop_id),
            ViewMovementsTool(self.db_service, shop_id)
        ]
        
        # Initialize base agent
        super().__init__(
            Name="Inventory Agent",
            Description="""An intelligent agent that manages product inventory operations including:
            - Adding new products with full details (name, category, prices, quantities, etc.)
            - Updating product information and quantities with automatic movement tracking
            - Removing products (soft delete by marking inactive or hard delete)
            - Searching products by various criteria (name, category, color, stock levels)
            - Viewing inventory movement history (purchases, sales, adjustments, waste, returns)
            - Monitoring low inventory alerts and stock levels""",
            Tools=tools,
            Model=settings.OPENAI_MODEL
        )
        
        logger.info("Inventory Agent initialized successfully")
    
    def cleanup(self):
        """
        Clean up resources, including database connection.
        """
        if self.db_service:
            self.db_service.disconnect()
            logger.info("Inventory Agent cleaned up successfully")
    
    def get_inventory_summary(self, shop_id: str = None) -> dict:
        """
        Get a summary of the current inventory.
        
        Args:
            shop_id: Optional shop ID to filter by specific shop
        
        Returns:
            Dictionary containing inventory statistics.
        """
        try:
            query = {"isActive": True}
            if shop_id:
                from bson import ObjectId
                query["shopId"] = ObjectId(shop_id)
            
            total_products = self.db_service.count_documents("Product", query)
            all_products = self.db_service.find_many("Product", query)
            
            total_quantity = sum(p.get('quantity', 0) for p in all_products)
            total_value_cost = sum(p.get('costPrice', 0) * p.get('quantity', 0) for p in all_products)
            total_value_retail = sum(p.get('retailPrice', 0) * p.get('quantity', 0) for p in all_products)
            
            # Count by category
            categories = {}
            for product in all_products:
                category = product.get('category', 'Uncategorized')
                categories[category] = categories.get(category, 0) + 1
            
            # Find low stock products
            low_stock = [p for p in all_products 
                        if p.get('trackInventory', True) and 
                        p.get('quantity', 0) <= p.get('lowInventoryAlert', 10)]
            
            # Find out of stock products
            out_of_stock = [p for p in all_products if p.get('quantity', 0) == 0]
            
            # Count inactive products
            inactive_query = {"isActive": False}
            if shop_id:
                from bson import ObjectId
                inactive_query["shopId"] = ObjectId(shop_id)
            inactive_count = self.db_service.count_documents("Product", inactive_query)
            
            return {
                "total_products": total_products,
                "total_quantity": total_quantity,
                "total_value_cost": round(total_value_cost, 2),
                "total_value_retail": round(total_value_retail, 2),
                "potential_profit": round(total_value_retail - total_value_cost, 2),
                "categories": categories,
                "low_stock_count": len(low_stock),
                "low_stock_products": [
                    {
                        "name": p.get('name'),
                        "quantity": p.get('quantity', 0),
                        "alert_threshold": p.get('lowInventoryAlert', 10)
                    } 
                    for p in low_stock
                ],
                "out_of_stock_count": len(out_of_stock),
                "out_of_stock_products": [p.get('name') for p in out_of_stock],
                "inactive_products": inactive_count
            }
        except Exception as e:
            logger.error(f"Error getting inventory summary: {e}")
            return {
                "error": str(e)
            }
    
    def get_movement_summary(self, shop_id: str = None, days: int = 30) -> dict:
        """
        Get a summary of inventory movements.
        
        Args:
            shop_id: Optional shop ID to filter by specific shop
            days: Number of days to look back (default 30)
        
        Returns:
            Dictionary containing movement statistics.
        """
        try:
            from datetime import datetime, timedelta
            from bson import ObjectId
            
            # Calculate date threshold
            date_threshold = datetime.utcnow() - timedelta(days=days)
            
            query = {"createdAt": {"$gte": date_threshold}}
            if shop_id:
                query["shopId"] = ObjectId(shop_id)
            
            movements = self.db_service.find_many("InventoryMovement", query)
            
            # Analyze movements
            total_movements = len(movements)
            type_stats = {}
            total_added = 0
            total_removed = 0
            
            for movement in movements:
                m_type = movement.get('type', 'unknown')
                quantity = movement.get('quantity', 0)
                
                if m_type not in type_stats:
                    type_stats[m_type] = {"count": 0, "total_quantity": 0}
                
                type_stats[m_type]["count"] += 1
                type_stats[m_type]["total_quantity"] += quantity
                
                if quantity > 0:
                    total_added += quantity
                else:
                    total_removed += abs(quantity)
            
            return {
                "period_days": days,
                "total_movements": total_movements,
                "total_added": total_added,
                "total_removed": total_removed,
                "net_change": total_added - total_removed,
                "by_type": type_stats
            }
        except Exception as e:
            logger.error(f"Error getting movement summary: {e}")
            return {
                "error": str(e)
            }
