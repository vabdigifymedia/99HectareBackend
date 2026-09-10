
from app.modules.favorites.schemas import FavoriteCreate
from app.modules.favorites.service import FavoriteService

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


class FavoriteController:
    def __init__(self, db: AsyncSession):
        self.service = FavoriteService(db)

    async def create_favorite(self, current_user: User, data: FavoriteCreate):
        return await self.service.create_favorite(current_user=current_user, data=data)

    async def delete_favorite(self, current_user: User, property_id: int):
        return await self.service.delete_favorite(current_user=current_user, property_id=property_id)

    async def list_favorites(self, current_user: User):
        return await self.service.list_favorites(current_user=current_user)

    async def get_total_count(self, current_user: User):
        return await self.service.get_total_count(current_user=current_user)

    async def get_by_id(self, current_user: User, property_id: int):
        return await self.service.get_by_id(current_user=current_user, property_id=property_id) 

