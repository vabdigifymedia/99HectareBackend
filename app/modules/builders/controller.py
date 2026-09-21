from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.builders.models import Builder
from app.modules.builders.schemas import BuilderUpdate
from app.modules.builders.service import BuilderService
from app.modules.users.models import User


class BuilderController:
    def __init__(self, db: AsyncSession):
        self.service = BuilderService(db)

    async def get_by_id(self, builder_id: int) -> Builder:
        return await self.service.get_by_id(builder_id)

    async def get_by_user_id(self, user_id: int) -> Builder:
        return await self.service.get_by_user_id(user_id)

    async def list_builders(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Builder], int]:
        return await self.service.list_builders(filters=filters, page=page, page_size=page_size)

    async def update_profile(self, current_user: User, data: BuilderUpdate) -> Builder:
        return await self.service.update_profile(current_user=current_user, data=data)
