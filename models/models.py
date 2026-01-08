"""
Pydantic models for MongoDB collections.
Aligned with Prisma schema for Product and InventoryMovement.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId that works with Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class ProductBase(BaseModel):
    """Base Product model with common fields"""
    name: str
    description: Optional[str] = None
    category: str
    color: Optional[str] = None
    costPrice: float
    retailPrice: float
    quantity: int = 0
    lowInventoryAlert: int = 10
    trackInventory: bool = True
    shelfLifeDays: Optional[int] = None
    stemLength: Optional[str] = None
    image: Optional[str] = None
    isActive: bool = True
    notes: Optional[str] = None
    shopId: str  # ObjectId as string

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }


class ProductCreate(ProductBase):
    """Model for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Model for updating a product (all fields optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    costPrice: Optional[float] = None
    retailPrice: Optional[float] = None
    quantity: Optional[int] = None
    lowInventoryAlert: Optional[int] = None
    trackInventory: Optional[bool] = None
    shelfLifeDays: Optional[int] = None
    stemLength: Optional[str] = None
    image: Optional[str] = None
    isActive: Optional[bool] = None
    notes: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }


class Product(ProductBase):
    """Complete Product model with database fields"""
    id: str = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }


class InventoryMovementBase(BaseModel):
    """Base InventoryMovement model"""
    type: str  # "purchase", "sale", "adjustment", "waste", "return"
    quantity: int  # Positive for additions, negative for removals
    previousInventory: int
    newInventory: int
    reason: Optional[str] = None
    referenceId: Optional[str] = None  # Link to order/purchase if applicable
    notes: Optional[str] = None
    productId: str  # ObjectId as string
    shopId: str  # ObjectId as string

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }


class InventoryMovementCreate(InventoryMovementBase):
    """Model for creating a new inventory movement"""
    pass


class InventoryMovement(InventoryMovementBase):
    """Complete InventoryMovement model with database fields"""
    id: str = Field(alias="_id")
    createdAt: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }


# Response models for API endpoints
class ProductResponse(BaseModel):
    """Response model for product operations"""
    success: bool
    message: str
    product: Optional[Product] = None
    product_id: Optional[str] = None


class ProductListResponse(BaseModel):
    """Response model for listing products"""
    success: bool
    message: str
    count: int
    products: List[Product]
    low_stock_count: Optional[int] = None
    warning: Optional[str] = None


class InventoryMovementResponse(BaseModel):
    """Response model for inventory movement operations"""
    success: bool
    message: str
    movement: Optional[InventoryMovement] = None
    movement_id: Optional[str] = None


class InventoryMovementListResponse(BaseModel):
    """Response model for listing inventory movements"""
    success: bool
    message: str
    count: int
    movements: List[InventoryMovement]
    total_quantity_changes: Optional[int] = None
    type_breakdown: Optional[dict] = None


# Validation constants
MOVEMENT_TYPES = ["purchase", "sale", "adjustment", "waste", "return"]


def validate_movement_type(movement_type: str) -> bool:
    """Validate that movement type is one of the allowed types"""
    return movement_type in MOVEMENT_TYPES

