from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.users.schemas import UserUpdate
from app.modules.users.service import UserService


class UserController:
    def __init__(self, db: AsyncSession):
        self.service = UserService(db)

    async def get_by_id(self, user_id: int) -> User:
        return await self.service.get_by_id(user_id=user_id)

    async def list_users(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        return await self.service.list_users(filters=filters, page=page, page_size=page_size)

    async def update_user(self, user_id: int, data: UserUpdate) -> User:
        return await self.service.update_user(user_id=user_id, data=data)
