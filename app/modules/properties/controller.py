from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.properties.schemas import (
    PropertyCreate,
    PropertyMediaCreateInput,
    PropertyUpdate,
)
from app.modules.properties.service import PropertyService
from app.modules.users.models import User


class PropertyController:
    def __init__(self, db: AsyncSession):
        self.service = PropertyService(db)

    async def create_property(self, current_user: User, data: PropertyCreate):
        return await self.service.create_property(current_user=current_user, data=data)

    async def list_properties(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "newest",
        current_user: User | None = None,
    ):
        return await self.service.list_properties(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            current_user=current_user,
        )

    async def get_property(self, property_id: int, current_user: User | None = None):
        return await self.service.get_property(
            property_id=property_id, current_user=current_user
        )

    async def update_property(
        self,
        property_id: int,
        current_user: User,
        data: PropertyUpdate,
    ):
        return await self.service.update_property(
            property_id=property_id, current_user=current_user, data=data
        )

    async def delete_property(self, property_id: int, current_user: User) -> None:
        await self.service.delete_property(
            property_id=property_id, current_user=current_user
        )

    async def add_media(
        self,
        property_id: int,
        current_user: User,
        data: PropertyMediaCreateInput,
    ):
        return await self.service.add_media(
            property_id=property_id, current_user=current_user, data=data
        )

    async def assign_amenities(
        self,
        property_id: int,
        current_user: User,
        amenity_ids: list[int],
    ):
        return await self.service.assign_amenities(
            property_id=property_id,
            current_user=current_user,
            amenity_ids=amenity_ids,
        )
