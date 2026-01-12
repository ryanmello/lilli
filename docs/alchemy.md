# SQLAlchemy in Lilli

This guide explains how to use SQLAlchemy alongside the existing Supabase setup in this project.

## Why Use SQLAlchemy?

While the Supabase Python SDK is great for simple queries, SQLAlchemy offers:
- Type-safe ORM models
- Complex query building with Python syntax
- Relationship handling and eager loading
- Migration support via Alembic
- Better IDE autocomplete and type checking

## Setup

### 1. Database Connection

The project already has `SUPABASE_DATABASE_URL` configured in `config/settings.py`. For Supabase, this URL follows the format:

```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

You can find this in your Supabase Dashboard under **Settings → Database → Connection string**.

### 2. Create the Database Engine

Create a new file `services/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import settings

# Create engine (use pool_pre_ping for connection health checks)
engine = create_engine(
    settings.SUPABASE_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3. Define Models

Create `models/` directory with your ORM models matching the existing schema.

**`models/__init__.py`**:
```python
from .customer import Customer
from .order import Order

__all__ = ["Customer", "Order"]
```

**`models/customer.py`**:
```python
from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship to orders
    orders: Mapped[List["Order"]] = relationship(back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Customer {self.email}>"
```

**`models/order.py`**:
```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, ForeignKey, Numeric, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.database import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')",
            name="orders_status_check"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    order_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship to customer
    customer: Mapped["Customer"] = relationship(back_populates="orders")

    def __repr__(self) -> str:
        return f"<Order {self.order_number}>"
```

## Usage Examples

### Basic CRUD Operations

```python
from sqlalchemy.orm import Session
from models import Customer, Order
from services.database import get_db

# Create
def create_customer(db: Session, email: str, name: str, phone: str | None = None) -> Customer:
    customer = Customer(email=email, name=name, phone=phone)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

# Read
def get_customer_by_email(db: Session, email: str) -> Customer | None:
    return db.query(Customer).filter(Customer.email == email).first()

# Update
def update_customer_name(db: Session, customer_id: UUID, new_name: str) -> Customer | None:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        customer.name = new_name
        db.commit()
        db.refresh(customer)
    return customer

# Delete
def delete_customer(db: Session, customer_id: UUID) -> bool:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()
        return True
    return False
```

### Using in FastAPI Routes

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.database import get_db
from models import Customer

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/")
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Customer).offset(skip).limit(limit).all()
```

### Eager Loading Relationships

```python
from sqlalchemy.orm import joinedload

# Get customer with all their orders in one query
def get_customer_with_orders(db: Session, customer_id: UUID) -> Customer | None:
    return (
        db.query(Customer)
        .options(joinedload(Customer.orders))
        .filter(Customer.id == customer_id)
        .first()
    )
```

### Complex Queries

```python
from sqlalchemy import select, and_, or_
from decimal import Decimal

# Get orders over a certain amount for a specific status
def get_high_value_orders(db: Session, min_amount: Decimal, status: str):
    return (
        db.query(Order)
        .filter(
            and_(
                Order.total_amount >= min_amount,
                Order.status == status
            )
        )
        .order_by(Order.created_at.desc())
        .all()
    )

# Search customers by name or email
def search_customers(db: Session, query: str):
    search = f"%{query}%"
    return (
        db.query(Customer)
        .filter(
            or_(
                Customer.name.ilike(search),
                Customer.email.ilike(search)
            )
        )
        .all()
    )
```

## SQLAlchemy vs Supabase SDK

| Use Case | Recommended |
|----------|-------------|
| Simple CRUD operations | Either works |
| Complex joins/queries | SQLAlchemy |
| Real-time subscriptions | Supabase SDK |
| Type-safe ORM models | SQLAlchemy |
| RPC/Edge Functions | Supabase SDK |
| Auth integration | Supabase SDK |
| Raw SQL needed | Either works |

**You can use both!** SQLAlchemy for complex data operations and the Supabase SDK for real-time features and auth.

## Environment Variables

Make sure your `.env` file includes:

```bash
SUPABASE_DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

> **Note**: Use the **Transaction pooler** connection string (port 6543) for serverless/short-lived connections, or the **Session pooler** (port 5432) for long-running processes.
