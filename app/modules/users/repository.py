from typing import Any
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.users.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_id_with_profiles(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.agent_profile),
                selectinload(User.builder_profile),
                selectinload(User.admin_profile),
            )
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()

    async def list_users(
        self,
        filters: dict[str, Any],
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        query = select(User).options(
            selectinload(User.agent_profile),
            selectinload(User.builder_profile),
            selectinload(User.admin_profile),
        )

        if filters.get("role"):
            query = query.where(User.role == filters["role"])
        if filters.get("is_active") is not None:
            query = query.where(User.is_active == filters["is_active"])
        if filters.get("is_verified") is not None:
            query = query.where(User.is_verified == filters["is_verified"])

        if filters.get("search"):
            term = f"%{filters['search']}%"
            query = query.where(
                or_(
                    User.full_name.ilike(term),
                    User.email.ilike(term),
                    User.phone.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one()

        query = query.order_by(User.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total
