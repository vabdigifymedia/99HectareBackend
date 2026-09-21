from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.models import Admin, AdminActionLog


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, admin_id: int) -> Admin | None:
        result = await self.db.execute(
            select(Admin).where(Admin.id == admin_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Admin | None:
        result = await self.db.execute(
            select(Admin).where(Admin.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def log_action(
        self,
        admin_id: int,
        action: str,
        entity_type: str | None = None,
        entity_id: int | None = None,
        description: str | None = None,
        ip_address: str | None = None,
    ) -> AdminActionLog:
        log = AdminActionLog(
            admin_id=admin_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
        )
        self.db.add(log)
        await self.db.flush()
        return log
