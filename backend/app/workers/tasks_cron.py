from datetime import datetime, timezone
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.domain.inventory.models import InventoryReservation
from app.domain.inventory.service import InventoryService

async def expire_inventory_reservations_task(ctx):
    """Cron task running periodically to sweep and release expired inventory reservations."""
    print("Running scheduled cron task: Expiring stale inventory reservations...")

    async with AsyncSessionLocal() as session:
        now = datetime.now(timezone.utc)
        stmt = select(InventoryReservation).where(
            InventoryReservation.status == "PENDING",
            InventoryReservation.expires_at < now
        )
        res = await session.execute(stmt)
        expired_list = res.scalars().all()

        if not expired_list:
            print("No expired reservations found.")
            return

        service = InventoryService(session)
        for reservation in expired_list:
            await service.release_reservation(reservation.id)

        await session.commit()
        print(f"Successfully swept and released {len(expired_list)} expired stock reservations.")
