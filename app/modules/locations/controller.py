from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.locations.service import LocationService


class LocationController:
    def __init__(self, db: AsyncSession):
        self.service = LocationService(db)

    async def get_countries(self):
        return await self.service.get_countries()

    async def get_states(self, country_id: int | None = None):
        return await self.service.get_states(country_id=country_id)

    async def get_cities(
        self, state_id: int | None = None, search: str | None = None
    ):
        return await self.service.get_cities(state_id=state_id, search=search)

    async def get_localities(
        self, city_id: int | None = None, search: str | None = None
    ):
        return await self.service.get_localities(city_id=city_id, search=search)

    async def get_sub_localities(
        self, locality_id: int | None = None, search: str | None = None
    ):
        return await self.service.get_sub_localities(
            locality_id=locality_id, search=search
        )
