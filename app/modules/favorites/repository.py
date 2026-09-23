from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.favorites.models import Favorite
from app.modules.properties.models import Property


class FavoriteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, favorite: Favorite) -> Favorite:
        self.db.add(favorite)
        await self.db.flush()
        return favorite

    async def delete(self, user_id: int, property_id: int) -> bool:
        result = await self.db.execute(
            delete(Favorite)
            .where(Favorite.user_id == user_id)
            .where(Favorite.property_id == property_id)
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
        self, user_id: int, offset: int = 0, limit: int = 50
    ) -> list[Property]:
        result = await self.db.execute(
            select(Property)
            .join(Favorite, Favorite.property_id == Property.id)
            .options(
                selectinload(Property.media),
                selectinload(Property.city),
                selectinload(Property.locality),
            )
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
        )
        return result.scalar_one() or 0