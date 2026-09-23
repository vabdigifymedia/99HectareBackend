from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.favorites.repository import FavoriteRepository
from app.modules.favorites.schemas import FavoriteCreate
from app.modules.properties.models import Property
from app.modules.properties.repository import PropertyRepository
from app.modules.users.models import User
from app.common.exceptions import BadRequestException, NotFoundException
from app.modules.favorites.models import Favorite



class FavoriteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FavoriteRepository(db)
        self.property_repo = PropertyRepository(db)

    async def create_favorite(self, current_user: User, data: FavoriteCreate) -> Property:
        property = await self.property_repo.get_by_id(data.property_id)

        if not property:
            raise NotFoundException("Property not found")

        favorite = await self.repo.get_by_id(current_user.id, data.property_id)
        if favorite:
            raise BadRequestException("Property already favorited")

        await self.repo.create(Favorite(user_id=current_user.id, property_id=data.property_id))
        await self.db.commit()

        return property

    async def delete_favorite(self, current_user: User, property_id: int) -> Property:
        property = await self.property_repo.get_by_id(property_id)

        if not property:
            raise NotFoundException("Property not found")

        favorite = await self.repo.get_by_id(current_user.id, property_id)
        if not favorite:
            raise NotFoundException("Favorite not found")

        await self.repo.delete(current_user.id, property_id)
        await self.db.commit()

        return property

    async def list_favorites(self, current_user: User) -> list[Property]:
        return await self.repo.list_favorites(current_user.id)

    async def get_total_count(self, current_user: User) -> int:
        return await self.repo.get_total_count(current_user.id)

    async def get_by_id(self, current_user: User, property_id: int) -> Favorite | None:
        return await self.repo.get_by_id(current_user.id, property_id)
