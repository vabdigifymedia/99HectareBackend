from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.locations.models import City, Country, Locality, State, SubLocality
from app.modules.locations.repository import LocationRepository


class LocationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LocationRepository(db)

    async def get_countries(self) -> list[Country]:
        return await self.repo.list_countries()

    async def get_states(self, country_id: int | None = None) -> list[State]:
        return await self.repo.list_states(country_id=country_id)

    async def get_cities(
        self, state_id: int | None = None, search: str | None = None
    ) -> list[City]:
        return await self.repo.list_cities(state_id=state_id, search=search)

    async def get_localities(
        self, city_id: int | None = None, search: str | None = None
    ) -> list[Locality]:
        return await self.repo.list_localities(city_id=city_id, search=search)

    async def get_sub_localities(
        self, locality_id: int | None = None, search: str | None = None
    ) -> list[SubLocality]:
        return await self.repo.list_sub_localities(
            locality_id=locality_id, search=search
        )
