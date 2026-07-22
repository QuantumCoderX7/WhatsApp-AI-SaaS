from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from datetime import datetime

from app.api.dependencies import get_db_session, get_current_user, get_current_tenant_id
from app.domain.tenant.models import User
from app.domain.inventory.models import Product, InventoryItem

router = APIRouter()

class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    initial_stock: int = Field(0, ge=0)

class InventoryOut(BaseModel):
    quantity_available: int
    quantity_reserved: int
    version: int

    class Config:
        from_attributes = True

class ProductOut(BaseModel):
    id: UUID
    tenant_id: UUID
    sku: str
    name: str
    description: Optional[str]
    price: float
    currency: str
    is_active: bool
    inventory_item: Optional[InventoryOut]
    created_at: datetime

    class Config:
        from_attributes = True

class StockAdjustRequest(BaseModel):
    quantity_change: int = Field(..., description="Positive value to add stock, negative to reduce")

@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Creates a new product SKU in tenant catalog and initializes inventory."""
    # Check duplicate SKU
    stmt = select(Product).where(Product.tenant_id == current_user.tenant_id, Product.sku == payload.sku.upper())
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Product with SKU '{payload.sku}' already exists.")

    product = Product(
        tenant_id=current_user.tenant_id,
        sku=payload.sku.upper(),
        name=payload.name,
        description=payload.description,
        price=payload.price,
        currency=payload.currency.upper()
    )
    db.add(product)
    await db.flush()

    inventory = InventoryItem(
        tenant_id=current_user.tenant_id,
        product_id=product.id,
        quantity_available=payload.initial_stock,
        quantity_reserved=0
    )
    db.add(inventory)
    await db.commit()
    await db.refresh(product)

    return product

@router.get("", response_model=List[ProductOut])
async def list_products(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """Lists products in tenant catalog with real-time stock levels."""
    stmt = (
        select(Product)
        .where(Product.tenant_id == tenant_id, Product.deleted_at.is_(None))
        .order_by(Product.created_at.desc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/{product_id}/adjust-stock", response_model=ProductOut)
async def adjust_product_stock(
    product_id: UUID,
    payload: StockAdjustRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Adjusts available stock count for a product."""
    stmt = select(Product).where(Product.id == product_id, Product.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    product = res.scalar_one_or_none()

    if not product or not product.inventory_item:
        raise HTTPException(status_code=404, detail="Product not found.")

    new_qty = product.inventory_item.quantity_available + payload.quantity_change
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Stock count cannot be negative.")

    product.inventory_item.quantity_available = new_qty
    product.inventory_item.version += 1
    await db.commit()
    await db.refresh(product)

    return product
