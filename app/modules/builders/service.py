from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.modules.builders.models import Builder
from app.modules.builders.repository import BuilderRepository
from app.modules.builders.schemas import BuilderUpdate
from app.modules.users.models import User


class BuilderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BuilderRepository(db)

    async def get_by_id(self, builder_id: int) -> Builder:
        builder = await self.repo.get_by_id(builder_id)
        if not builder:
            raise NotFoundException(f"Builder with ID {builder_id} not found")
        return builder

    async def get_by_user_id(self, user_id: int) -> Builder:
        builder = await self.repo.get_by_user_id(user_id)
        if not builder:
            raise NotFoundException(f"Builder profile not found for user {user_id}")
        return builder

    async def list_builders(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Builder], int]:
        offset = (max(1, page) - 1) * page_size
        return await self.repo.list(filters=filters, offset=offset, limit=page_size)

    async def update_profile(self, current_user: User, data: BuilderUpdate) -> Builder:
        builder = await self.repo.get_by_user_id(current_user.id)
        if not builder:
            raise NotFoundException("Builder profile not found for this account")

        payload = data.model_dump(exclude_unset=True)
        if "website" in payload and payload["website"] is not None:
            payload["website"] = str(payload["website"])

        for key, value in payload.items():
            setattr(builder, key, value)

        updated = await self.repo.update(builder)
        await self.db.commit()
        return updated
