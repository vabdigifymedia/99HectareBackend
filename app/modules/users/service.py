from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def get_by_id(self, user_id: int) -> User:
        user = await self.repo.get_by_id_with_profiles(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user

    async def list_users(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        offset = (max(1, page) - 1) * page_size
        return await self.repo.list_users(filters=filters, offset=offset, limit=page_size)

    async def update_user(self, user_id: int, data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(user, key, value)

        updated = await self.repo.update(user)
        await self.db.commit()
        return updated
