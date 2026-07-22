import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.domain.inventory.models import Product, InventoryItem, InventoryReservation
from app.domain.inventory.locking import RedisLockManager, DistributedLockError

class InsufficientStockError(Exception):
    pass

class InventoryService:
    """Manages stock reservation, release, and optimistic concurrency locks."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def reserve_stock(
        self,
        tenant_id: uuid.UUID,
        conversation_id: uuid.UUID,
        sku: str,
        quantity: int,
        ttl_minutes: int = 15
    ) -> InventoryReservation:
        """Reserves stock atomically using Redis Lock + PostgreSQL Optimistic Locking."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        # 1. Acquire Redis Distributed Lock
        async with RedisLockManager.acquire_inventory_lock(tenant_id, sku):
            # 2. Fetch Product & Inventory Item
            stmt = (
                select(Product, InventoryItem)
                .join(InventoryItem, Product.id == InventoryItem.product_id)
                .where(
                    Product.tenant_id == tenant_id,
                    Product.sku == sku.upper(),
                    Product.is_active.is_(True)
                )
            )
            result = await self.session.execute(stmt)
            row = result.first()
            if not row:
                raise InsufficientStockError(f"Product SKU '{sku}' not found.")

            product, inventory = row
            available = inventory.quantity_available - inventory.quantity_reserved

            if available < quantity:
                raise InsufficientStockError(f"Insufficient stock for SKU '{sku}'. Available: {max(0, available)}, requested: {quantity}")

            # 3. Apply Optimistic Locking Update
            current_version = inventory.version
            stmt_update = (
                update(InventoryItem)
                .where(
                    InventoryItem.id == inventory.id,
                    InventoryItem.version == current_version
                )
                .values(
                    quantity_reserved=inventory.quantity_reserved + quantity,
                    version=current_version + 1,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            update_res = await self.session.execute(stmt_update)
            if update_res.rowcount == 0:
                raise DistributedLockError("Optimistic concurrency collision. Retrying stock allocation...")

            # 4. Record Reservation Entity
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
            reservation = InventoryReservation(
                tenant_id=tenant_id,
                product_id=product.id,
                conversation_id=conversation_id,
                quantity=quantity,
                status="PENDING",
                expires_at=expires_at
            )
            self.session.add(reservation)
            await self.session.flush()
            return reservation

    async def release_reservation(self, reservation_id: uuid.UUID) -> None:
        """Releases an expired or cancelled reservation back into available stock."""
        stmt = select(InventoryReservation).where(InventoryReservation.id == reservation_id)
        result = await self.session.execute(stmt)
        res = result.scalar_one_or_none()
        if not res or res.status != "PENDING":
            return

        # Fetch Inventory Record
        inv_stmt = select(InventoryItem).where(InventoryItem.product_id == res.product_id)
        inv_res = await self.session.execute(inv_stmt)
        inventory = inv_res.scalar_one_or_none()

        if inventory:
            inventory.quantity_reserved = max(0, inventory.quantity_reserved - res.quantity)
            inventory.version += 1

        res.status = "RELEASED"
        await self.session.flush()
