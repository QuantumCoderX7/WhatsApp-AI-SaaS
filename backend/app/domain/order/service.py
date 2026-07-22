import uuid
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.order.models import Order, OrderItem
from app.domain.inventory.service import InventoryService
from app.domain.inventory.models import Product, InventoryItem

class OrderService:
    """Manages transactional order execution and checkout."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.inventory_service = InventoryService(session)

    async def create_order(
        self,
        tenant_id: uuid.UUID,
        conversation_id: uuid.UUID,
        items: List[Dict[str, Any]]
    ) -> Order:
        """Creates order atomically, reserves inventory, and generates checkout total."""
        if not items:
            raise ValueError("Order must contain at least one item.")

        total_amount = Decimal("0.00")
        
        # 1. Create Base Order Entity
        order = Order(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            total_amount=total_amount,
            status="PENDING",
            payment_status="UNPAID"
        )
        self.session.add(order)
        await self.session.flush()

        # 2. Reserve Stock & Create Line Items
        for item in items:
            sku = item["sku"]
            quantity = int(item["quantity"])

            # Reserve Stock
            reservation = await self.inventory_service.reserve_stock(
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                sku=sku,
                quantity=quantity
            )

            # Fetch Product for Pricing
            prod_stmt = select(Product).where(Product.id == reservation.product_id)
            prod_res = await self.session.execute(prod_stmt)
            product = prod_res.scalar_one()

            unit_price = Decimal(str(product.price))
            line_total = unit_price * quantity
            total_amount += line_total

            order_item = OrderItem(
                tenant_id=tenant_id,
                order_id=order.id,
                product_id=product.id,
                unit_price=unit_price,
                quantity=quantity
            )
            self.session.add(order_item)

        order.total_amount = total_amount
        await self.session.flush()
        return order
