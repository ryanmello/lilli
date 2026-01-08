from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseService:
    """
    Service class for managing MongoDB database connections and operations.
    Aligned with Prisma schema structure.
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize the database service.
        
        Args:
            connection_string: MongoDB connection string with database name included.
                              Format: mongodb+srv://user:pass@host/database_name
        """
        self.connection_string = connection_string
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        
    def connect(self) -> bool:
        """
        Establish connection to MongoDB.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.admin.command('ping')
            
            # Use get_default_database() to automatically use the database from the connection string
            self.db = self.client.get_default_database()
            
            logger.info(f"Successfully connected to MongoDB database: {self.db.name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """
        Close the MongoDB connection.
        """
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str) -> Collection:
        """
        Get a specific collection from the database.
        
        Args:
            collection_name: Name of the collection to retrieve.
            
        Returns:
            Collection: The requested MongoDB collection.
            
        Raises:
            ValueError: If not connected to database.
        """
        if not self.db:
            raise ValueError("Not connected to database. Call connect() first.")
        return self.db[collection_name]
    
    # CREATE Operations
    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> Optional[str]:
        """
        Insert a single document into a collection.
        
        Args:
            collection_name: Name of the collection.
            document: Document to insert.
            
        Returns:
            str: The inserted document's ID, or None if failed.
        """
        try:
            collection = self.get_collection(collection_name)
            # Add timestamp if not present
            if 'createdAt' not in document:
                document['createdAt'] = datetime.utcnow()
            if 'updatedAt' not in document:
                document['updatedAt'] = datetime.utcnow()
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting document: {e}")
            return None
    
    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> Optional[List[str]]:
        """
        Insert multiple documents into a collection.
        
        Args:
            collection_name: Name of the collection.
            documents: List of documents to insert.
            
        Returns:
            List[str]: List of inserted document IDs, or None if failed.
        """
        try:
            collection = self.get_collection(collection_name)
            # Add timestamps to all documents
            now = datetime.utcnow()
            for doc in documents:
                if 'createdAt' not in doc:
                    doc['createdAt'] = now
                if 'updatedAt' not in doc:
                    doc['updatedAt'] = now
            result = collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            print(f"Error inserting documents: {e}")
            return None
    
    # READ Operations
    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document in a collection.
        
        Args:
            collection_name: Name of the collection.
            query: Query filter.
            
        Returns:
            Dict: The found document, or None if not found.
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.find_one(query)
            if result:
                result['_id'] = str(result['_id'])
                # Convert ObjectId fields to strings
                if 'shopId' in result and isinstance(result['shopId'], ObjectId):
                    result['shopId'] = str(result['shopId'])
                if 'productId' in result and isinstance(result['productId'], ObjectId):
                    result['productId'] = str(result['productId'])
            return result
        except Exception as e:
            print(f"Error finding document: {e}")
            return None
    
    def find_many(self, collection_name: str, query: Dict[str, Any] = None, 
                  limit: int = 0, sort_by: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """
        Find multiple documents in a collection.
        
        Args:
            collection_name: Name of the collection.
            query: Query filter. If None, returns all documents.
            limit: Maximum number of documents to return. 0 means no limit.
            sort_by: List of (field, direction) tuples for sorting. E.g., [('name', 1)] for ascending.
            
        Returns:
            List[Dict]: List of found documents.
        """
        try:
            collection = self.get_collection(collection_name)
            query = query or {}
            cursor = collection.find(query)
            
            if sort_by:
                cursor = cursor.sort(sort_by)
            
            if limit > 0:
                cursor = cursor.limit(limit)
            
            results = list(cursor)
            # Convert ObjectId fields to strings
            for doc in results:
                doc['_id'] = str(doc['_id'])
                if 'shopId' in doc and isinstance(doc['shopId'], ObjectId):
                    doc['shopId'] = str(doc['shopId'])
                if 'productId' in doc and isinstance(doc['productId'], ObjectId):
                    doc['productId'] = str(doc['productId'])
            return results
        except Exception as e:
            print(f"Error finding documents: {e}")
            return []
    
    def find_by_id(self, collection_name: str, id: str) -> Optional[Dict[str, Any]]:
        """
        Find a document by its ID.
        
        Args:
            collection_name: Name of the collection.
            id: Document ID as string.
            
        Returns:
            Dict: The found document, or None if not found.
        """
        try:
            return self.find_one(collection_name, {"_id": ObjectId(id)})
        except Exception as e:
            print(f"Error finding document by ID: {e}")
            return None
    
    def count_documents(self, collection_name: str, query: Dict[str, Any] = None) -> int:
        """
        Count documents matching a query.
        
        Args:
            collection_name: Name of the collection.
            query: Query filter. If None, counts all documents.
            
        Returns:
            int: Number of matching documents.
        """
        try:
            collection = self.get_collection(collection_name)
            query = query or {}
            return collection.count_documents(query)
        except Exception as e:
            print(f"Error counting documents: {e}")
            return 0
    
    # UPDATE Operations
    def update_one(self, collection_name: str, query: Dict[str, Any], 
                   update: Dict[str, Any]) -> bool:
        """
        Update a single document in a collection.
        
        Args:
            collection_name: Name of the collection.
            query: Query filter to find the document.
            update: Update operations to apply.
            
        Returns:
            bool: True if document was updated, False otherwise.
        """
        try:
            collection = self.get_collection(collection_name)
            # Add updated timestamp
            if '$set' not in update:
                update = {'$set': update}
            update['$set']['updatedAt'] = datetime.utcnow()
            
            result = collection.update_one(query, update)
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    def update_many(self, collection_name: str, query: Dict[str, Any], 
                    update: Dict[str, Any]) -> int:
        """
        Update multiple documents in a collection.
        
        Args:
            collection_name: Name of the collection.
            query: Query filter to find documents.
            update: Update operations to apply.
            
        Returns:
            int: Number of documents updated.
        """
        try:
            collection = self.get_collection(collection_name)
            # Add updated timestamp
            if '$set' not in update:
                update = {'$set': update}
            update['$set']['updatedAt'] = datetime.utcnow()
            
            result = collection.update_many(query, update)
            return result.modified_count
        except Exception as e:
            print(f"Error updating documents: {e}")
            return 0
    
    # DELETE Operations
    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """
        Delete a single document from a collection.
        
        Args:
            collection_name: Name of the collection.
            query: Query filter to find the document.
            
        Returns:
            bool: True if document was deleted, False otherwise.
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def delete_many(self, collection_name: str, query: Dict[str, Any]) -> int:
        """
        Delete multiple documents from a collection.
        
        Args:
            collection_name: Name of the collection.
            query: Query filter to find documents.
            
        Returns:
            int: Number of documents deleted.
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return 0
    
    # SEARCH Operations
    def search_text(self, collection_name: str, search_text: str, 
                   fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search documents using text search or regex pattern matching.
        
        Args:
            collection_name: Name of the collection.
            search_text: Text to search for.
            fields: List of fields to search in. If None, searches all text fields.
            
        Returns:
            List[Dict]: List of matching documents.
        """
        try:
            collection = self.get_collection(collection_name)
            
            if fields:
                # Create regex query for specified fields
                query = {
                    '$or': [
                        {field: {'$regex': search_text, '$options': 'i'}} 
                        for field in fields
                    ]
                }
            else:
                # Use text search (requires text index)
                query = {'$text': {'$search': search_text}}
            
            results = list(collection.find(query))
            # Convert ObjectId to string
            for doc in results:
                doc['_id'] = str(doc['_id'])
                if 'shopId' in doc and isinstance(doc['shopId'], ObjectId):
                    doc['shopId'] = str(doc['shopId'])
                if 'productId' in doc and isinstance(doc['productId'], ObjectId):
                    doc['productId'] = str(doc['productId'])
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def drop_collection(self, collection_name: str) -> bool:
        """
        Drop a collection from the database.
        
        Args:
            collection_name: Name of the collection to drop.
            
        Returns:
            bool: True if collection was dropped, False otherwise.
        """
        # try:
        #     collection = self.get_collection(collection_name)
        #     collection.drop()
        #     print(f"Collection {collection_name} dropped")
        #     return True
        # except Exception as e:
        #     print(f"Error dropping collection: {e}")
        #     return False
    
    # INVENTORY-SPECIFIC Operations
    def create_inventory_movement(self, product_id: str, shop_id: str, movement_type: str,
                                  quantity_change: int, previous_inventory: int,
                                  reason: Optional[str] = None, reference_id: Optional[str] = None,
                                  notes: Optional[str] = None) -> Optional[str]:
        """
        Create an inventory movement record.
        
        Args:
            product_id: Product ID
            shop_id: Shop ID
            movement_type: Type of movement (purchase, sale, adjustment, waste, return)
            quantity_change: Quantity change (positive for additions, negative for removals)
            previous_inventory: Previous inventory quantity
            reason: Reason for movement
            reference_id: Reference to related order/purchase
            notes: Additional notes
            
        Returns:
            str: Movement ID if successful, None otherwise
        """
        try:
            new_inventory = previous_inventory + quantity_change
            
            movement = {
                "productId": ObjectId(product_id),
                "shopId": ObjectId(shop_id),
                "type": movement_type,
                "quantity": quantity_change,
                "previousInventory": previous_inventory,
                "newInventory": new_inventory,
                "reason": reason,
                "referenceId": reference_id,
                "notes": notes,
                "createdAt": datetime.utcnow()
            }
            
            return self.insert_one("InventoryMovement", movement)
        except Exception as e:
            print(f"Error creating inventory movement: {e}")
            return None


# Context manager support
class DatabaseConnection:
    """
    Context manager for database connections.
    
    Example:
        with DatabaseConnection() as db:
            db.insert_one('Product', {'name': 'Item 1', 'quantity': 10})
    """
    
    def __init__(self, connection_string: Optional[str] = None, database_name: str = "inventory_db"):
        self.db_service = DatabaseService(connection_string, database_name)
    
    def __enter__(self) -> DatabaseService:
        self.db_service.connect()
        return self.db_service
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_service.disconnect()
        return False
