from typing import Any

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.favorites.models import Favorite


class FavoriteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, favorite: Favorite) -> Favorite:
        self.db.add(favorite)
        await self.db.flush()
        return favorite

    async def delete(self, user_id: int, property_id: int) -> bool:
        result = await self.db.execute(
            update(Favorite)
            .where(Favorite.user_id == user_id)
            .where(Favorite.property_id == property_id)
            .values(is_active=False)
        )
        await self.db.flush()
        return result.rowcount > 0

    async def get_by_id(self, user_id: int, property_id: int) -> Favorite | None:
        result = await self.db.execute(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .where(Favorite.property_id == property_id)
        )
        return result.scalar_one_or_none()

    async def list_favorites(
        self, user_id: int, offset: int = 0, limit: int = 20
    ) -> tuple[list[Favorite], int]:
        result = await self.db.execute(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        items = list(result.scalars().all())

        count_result = await self.db.execute(
            select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
        )
        total = count_result.scalar_one()

        return items, total

    async def get_total_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
        )
        return result.scalar_one() or 0