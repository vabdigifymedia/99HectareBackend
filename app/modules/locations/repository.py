from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.locations.models import City, Country, Locality, State, SubLocality


class LocationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Countries ───────────────────────────────────────────────────────

    async def list_countries(self) -> list[Country]:
        result = await self.db.execute(select(Country).order_by(Country.name.asc()))
        return list(result.scalars().all())

    async def get_country(self, country_id: int) -> Country | None:
        result = await self.db.execute(
            select(Country).where(Country.id == country_id)
        )
        return result.scalar_one_or_none()

    # ── States ──────────────────────────────────────────────────────────

    async def list_states(self, country_id: int | None = None) -> list[State]:
        query = select(State)
        if country_id is not None:
            query = query.where(State.country_id == country_id)
        query = query.order_by(State.name.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_state(self, state_id: int) -> State | None:
        result = await self.db.execute(select(State).where(State.id == state_id))
        return result.scalar_one_or_none()

    # ── Cities ──────────────────────────────────────────────────────────

    async def list_cities(
        self, state_id: int | None = None, search: str | None = None
    ) -> list[City]:
        query = select(City)
        if state_id is not None:
            query = query.where(City.state_id == state_id)
        if search:
            query = query.where(City.name.ilike(f"%{search.strip()}%"))
        query = query.order_by(City.name.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_city(self, city_id: int) -> City | None:
        result = await self.db.execute(select(City).where(City.id == city_id))
        return result.scalar_one_or_none()

    # ── Localities ──────────────────────────────────────────────────────

    async def list_localities(
        self, city_id: int | None = None, search: str | None = None
    ) -> list[Locality]:
        query = select(Locality)
        if city_id is not None:
            query = query.where(Locality.city_id == city_id)
        if search:
            query = query.where(Locality.name.ilike(f"%{search.strip()}%"))
        query = query.order_by(Locality.name.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_locality(self, locality_id: int) -> Locality | None:
        result = await self.db.execute(
            select(Locality).where(Locality.id == locality_id)
        )
        return result.scalar_one_or_none()

    # ── SubLocalities ───────────────────────────────────────────────────

    async def list_sub_localities(
        self, locality_id: int | None = None, search: str | None = None
    ) -> list[SubLocality]:
        query = select(SubLocality)
        if locality_id is not None:
            query = query.where(SubLocality.locality_id == locality_id)
        if search:
            query = query.where(SubLocality.name.ilike(f"%{search.strip()}%"))
        query = query.order_by(SubLocality.name.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_sub_locality(self, sub_locality_id: int) -> SubLocality | None:
        result = await self.db.execute(
            select(SubLocality).where(SubLocality.id == sub_locality_id)
        )
        return result.scalar_one_or_none()
