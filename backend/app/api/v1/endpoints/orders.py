from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.api.dependencies import get_db_session, get_current_user, get_current_tenant_id
from app.domain.tenant.models import User
from app.domain.order.models import Order, OrderItem
from app.domain.inventory.service import InventoryService

router = APIRouter()

class OrderItemOut(BaseModel):
    id: UUID
    product_id: UUID
    unit_price: float
    quantity: int

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: UUID
    tenant_id: UUID
    conversation_id: UUID
    total_amount: float
    currency: str
    status: str
    payment_status: str
    items: List[OrderItemOut]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[OrderOut])
async def list_orders(
    status: Optional[str] = Query(None),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """Lists customer orders for the tenant."""
    stmt = select(Order).where(Order.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(Order.status == status)
    stmt = stmt.order_by(Order.created_at.desc())

    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{order_id}", response_model=OrderOut)
async def get_order_by_id(
    order_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves order details by ID."""
    stmt = select(Order).where(Order.id == order_id, Order.tenant_id == tenant_id)
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order
