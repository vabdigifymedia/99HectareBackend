from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.amenities.models import Amenity
from app.modules.locations.models import City, Country, Locality, State, SubLocality
from app.modules.media.models import PropertyMedia
from app.modules.projects.models import Project
from app.modules.properties.models import (
    CommercialPropertyDetails,
    PlotPropertyDetails,
    Property,
    ResidentialPropertyDetails,
)



class PropertyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, property_id: int) -> Property | None:
        """Fetch a property by ID."""
        result = await self.db.execute(
            select(Property)
            .options(
                selectinload(Property.media),
                selectinload(Property.city),
                selectinload(Property.locality),
            )
            .where(Property.id == property_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_detailed(self, property_id: int) -> Property | None:
        """Fetch a property with all related entities eagerly loaded."""
        return await self.get_by_slug_or_id(property_id)

    async def get_by_slug_or_id(self, slug_or_id: str | int) -> Property | None:
        """Fetch a property by ID or slug with all related entities eagerly loaded."""
        detailed_options = (
            selectinload(Property.media),
            selectinload(Property.amenities),
            selectinload(Property.residential_details),
            selectinload(Property.commercial_details),
            selectinload(Property.plot_details),
            selectinload(Property.owner),
            selectinload(Property.agent),
            selectinload(Property.builder),
            selectinload(Property.project),
            selectinload(Property.country),
            selectinload(Property.state),
            selectinload(Property.city),
            selectinload(Property.locality),
            selectinload(Property.sub_locality),
        )
        if isinstance(slug_or_id, int) or (isinstance(slug_or_id, str) and slug_or_id.isdigit()):
            prop_id = int(slug_or_id)
            result = await self.db.execute(
                select(Property).options(*detailed_options).where(Property.id == prop_id)
            )
            item = result.scalar_one_or_none()
            if item:
                return item

        if isinstance(slug_or_id, str):
            parts = slug_or_id.rsplit("-", 1)
            if len(parts) == 2 and parts[1].isdigit():
                prop_id = int(parts[1])
                result = await self.db.execute(
                    select(Property).options(*detailed_options).where(Property.id == prop_id)
                )
                item = result.scalar_one_or_none()
                if item:
                    return item
            # Try matching by title keyword
            first_words = slug_or_id.replace("-", " ").split()[:3]
            if first_words:
                query_term = f"%{'%'.join(first_words)}%"
                result = await self.db.execute(
                    select(Property).options(*detailed_options).where(Property.title.ilike(query_term)).limit(1)
                )
                item = result.scalar_one_or_none()
                if item:
                    return item

        return None


    async def list_properties(
        self,
        filters: dict[str, Any],
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "newest",
    ) -> tuple[list[Property], int]:
        """List properties with dynamic 99acres-style filters and pagination."""
        conditions = []

        if filters.get("property_type"):
            clean_pt = str(filters["property_type"]).strip().lower()
            conditions.append(func.lower(Property.property_type) == clean_pt)

        if filters.get("listing_type"):
            clean_lt = str(filters["listing_type"]).strip().upper()
            conditions.append(func.upper(Property.listing_type) == clean_lt)


        if filters.get("status"):
            conditions.append(Property.status == filters["status"])

        if filters.get("is_active") is not None:
            conditions.append(Property.is_active == filters["is_active"])

        if filters.get("is_featured") is not None:
            conditions.append(Property.is_featured == filters["is_featured"])

        if filters.get("is_verified") is not None:
            conditions.append(Property.is_verified == filters["is_verified"])

        if filters.get("city_id"):
            conditions.append(Property.city_id == filters["city_id"])

        if filters.get("state_id"):
            conditions.append(Property.state_id == filters["state_id"])

        if filters.get("locality_id"):
            conditions.append(Property.locality_id == filters["locality_id"])

        if filters.get("sub_locality_id"):
            conditions.append(Property.sub_locality_id == filters["sub_locality_id"])

        if filters.get("min_price") is not None:
            conditions.append(Property.price >= filters["min_price"])

        if filters.get("max_price") is not None:
            conditions.append(Property.price <= filters["max_price"])

        if filters.get("bedrooms") is not None:
            conditions.append(Property.bedrooms == filters["bedrooms"])

        if filters.get("bathrooms") is not None:
            conditions.append(Property.bathrooms == filters["bathrooms"])

        if filters.get("furnishing_status"):
            conditions.append(
                Property.furnishing_status == filters["furnishing_status"]
            )

        if filters.get("builder_id"):
            conditions.append(Property.builder_id == filters["builder_id"])

        if filters.get("project_id"):
            conditions.append(Property.project_id == filters["project_id"])

        if filters.get("agent_id"):
            conditions.append(Property.agent_id == filters["agent_id"])

        if filters.get("owner_id"):
            conditions.append(Property.owner_id == filters["owner_id"])

        # Location / City filter with Indian metro aliases (Gurgaon <-> Gurugram, etc.)
        loc_term = filters.get("location") or filters.get("city")
        if loc_term and loc_term.strip():
            raw_loc = loc_term.strip().lower()
            loc_aliases = [f"%{raw_loc}%"]
            if "gurgaon" in raw_loc or "gurugram" in raw_loc:
                loc_aliases.extend(["%gurgaon%", "%gurugram%"])
            if "bangalore" in raw_loc or "bengaluru" in raw_loc:
                loc_aliases.extend(["%bangalore%", "%bengaluru%"])
            if "delhi" in raw_loc:
                loc_aliases.extend(["%delhi%", "%new delhi%", "%south delhi%"])
            if "mumbai" in raw_loc or "bombay" in raw_loc:
                loc_aliases.extend(["%mumbai%", "%bombay%"])

            loc_subconds = []
            for a in loc_aliases:
                loc_subconds.extend([
                    Property.address.ilike(a),
                    Property.landmark.ilike(a),
                    Property.city_id.in_(select(City.id).where(City.name.ilike(a))),
                    Property.locality_id.in_(select(Locality.id).where(Locality.name.ilike(a))),
                ])
            conditions.append(or_(*loc_subconds))

        if filters.get("search") and filters["search"].strip():
            raw_s = filters["search"].strip().lower()
            s_aliases = [f"%{raw_s}%"]
            if "gurgaon" in raw_s or "gurugram" in raw_s:
                s_aliases.extend(["%gurgaon%", "%gurugram%"])
            if "bangalore" in raw_s or "bengaluru" in raw_s:
                s_aliases.extend(["%bangalore%", "%bengaluru%"])
            if "delhi" in raw_s:
                s_aliases.extend(["%delhi%", "%new delhi%", "%south delhi%"])
            if "mumbai" in raw_s or "bombay" in raw_s:
                s_aliases.extend(["%mumbai%", "%bombay%"])

            s_subconds = [
                Property.title.ilike(f"%{filters['search'].strip()}%"),
                Property.description.ilike(f"%{filters['search'].strip()}%"),
            ]
            for a in s_aliases:
                s_subconds.extend([
                    Property.address.ilike(a),
                    Property.landmark.ilike(a),
                    Property.city_id.in_(select(City.id).where(City.name.ilike(a))),
                    Property.locality_id.in_(select(Locality.id).where(Locality.name.ilike(a))),
                ])
            conditions.append(or_(*s_subconds))

        # Count total matches
        count_query = select(func.count(Property.id)).where(*conditions)
        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one() or 0

        # Determine sorting
        if sort_by == "price_asc":
            order_by = Property.price.asc()
        elif sort_by == "price_desc":
            order_by = Property.price.desc()
        elif sort_by == "area_asc":
            order_by = Property.carpet_area.asc().nullslast()
        elif sort_by == "area_desc":
            order_by = Property.carpet_area.desc().nullslast()
        else:
            order_by = Property.created_at.desc()

        # Query paginated rows
        query = (
            select(Property)
            .options(
                selectinload(Property.media),
                selectinload(Property.city),
                selectinload(Property.locality),
            )
            .where(*conditions)
            .order_by(order_by)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, prop: Property) -> Property:
        self.db.add(prop)
        await self.db.flush()
        await self.db.refresh(prop)
        return prop

    async def update(self, prop: Property) -> Property:
        await self.db.flush()
        await self.db.refresh(prop)
        return prop

    async def delete(self, prop: Property) -> None:
        await self.db.delete(prop)
        await self.db.flush()

    # ── Media ─────────────────────────────────────────────────────────

    async def add_media(self, media: PropertyMedia) -> PropertyMedia:
        self.db.add(media)
        await self.db.flush()
        await self.db.refresh(media)
        return media

    async def unset_primary_media(self, property_id: int) -> None:
        await self.db.execute(
            update(PropertyMedia)
            .where(PropertyMedia.property_id == property_id)
            .values(is_primary=False)
        )
        await self.db.flush()

    # ── Amenities ─────────────────────────────────────────────────────

    async def get_amenities_by_ids(self, amenity_ids: list[int]) -> list[Amenity]:
        if not amenity_ids:
            return []
        result = await self.db.execute(
            select(Amenity).where(Amenity.id.in_(amenity_ids))
        )
        return list(result.scalars().all())

    async def assign_amenities(
        self, prop: Property, amenities: list[Amenity]
    ) -> list[Amenity]:
        # Assign secondary relationship
        prop.amenities = amenities
        await self.db.flush()
        await self.db.refresh(prop, ["amenities"])
        return prop.amenities

    # ── Project ───────────────────────────────────────────────────────

    async def get_project(self, project_id: int) -> Project | None:
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    # ── Location Validation ───────────────────────────────────────────

    async def location_exists(self, model, entity_id: int) -> bool:
        result = await self.db.execute(select(model.id).where(model.id == entity_id))
        return result.scalar_one_or_none() is not None

