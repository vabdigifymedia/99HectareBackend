from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.modules.amenities.models import Amenity
from app.modules.locations.models import City, Country, Locality, State, SubLocality
from app.modules.media.models import PropertyMedia
from app.modules.properties.models import Property
from app.modules.properties.repository import PropertyRepository
from app.modules.properties.schemas import (
    PropertyCreate,
    PropertyMediaCreateInput,
    PropertyUpdate,
)
from app.modules.users.models import User



class PropertyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PropertyRepository(db)

    # ── Role & Ownership Verification ─────────────────────────────────

    def _check_property_permission(self, prop: Property, current_user: User) -> None:
        """Verify that current_user has rights to modify or delete the property."""
        # 1. Admin has global override
        if current_user.role == "admin":
            return

        # 2. Individual owner
        if prop.owner_id is not None and prop.owner_id == current_user.id:
            return

        # 3. Listing agent
        if (
            current_user.agent_profile
            and prop.agent_id is not None
            and prop.agent_id == current_user.agent_profile.id
        ):
            return

        # 4. Builder owning the unit/project
        if (
            current_user.builder_profile
            and prop.builder_id is not None
            and prop.builder_id == current_user.builder_profile.id
        ):
            return

        raise ForbiddenException(
            "You do not have permission to perform this action on this property"
        )

    async def _validate_location_references(self, data: dict[str, Any]) -> None:
        """Validate that any provided location IDs exist in the database."""
        if data.get("country_id") is not None:
            if not await self.repo.location_exists(Country, data["country_id"]):
                raise BadRequestException(
                    f"Country with ID {data['country_id']} does not exist"
                )

        if data.get("state_id") is not None:
            if not await self.repo.location_exists(State, data["state_id"]):
                raise BadRequestException(
                    f"State with ID {data['state_id']} does not exist"
                )

        if data.get("city_id") is not None:
            if not await self.repo.location_exists(City, data["city_id"]):
                raise BadRequestException(
                    f"City with ID {data['city_id']} does not exist"
                )

        if data.get("locality_id") is not None:
            if not await self.repo.location_exists(Locality, data["locality_id"]):
                raise BadRequestException(
                    f"Locality with ID {data['locality_id']} does not exist"
                )

        if data.get("sub_locality_id") is not None:
            if not await self.repo.location_exists(SubLocality, data["sub_locality_id"]):
                raise BadRequestException(
                    f"Sub-locality with ID {data['sub_locality_id']} does not exist"
                )

    # ── Create Property ────────────────────────────────────────────────

    async def create_property(
        self, current_user: User, data: PropertyCreate
    ) -> Property:

        """
        Create a property listing adhering to 99acres role flows:
        1. USER Flow:
           USER -> create property (direct owner listing)
        2. AGENT Flow:
           USER -> AGENT -> create property (broker listing, optionally on behalf of owner)
        3. BUILDER Flow:
           BUILDER -> PROJECT -> PROPERTY / UNIT (developer units linked to a project)
        4. ADMIN Flow:
           Direct creation with arbitrary assignments
        """
        payload = data.model_dump(exclude_unset=True)
        amenity_ids = payload.pop("amenity_ids", None)

        owner_id: int | None = None
        agent_id: int | None = None
        builder_id: int | None = None
        project_id: int | None = payload.get("project_id")

        if current_user.role == "builder":
            # ── Builder Flow: BUILDER -> PROJECT -> PROPERTY / UNIT
            if not current_user.builder_profile:
                raise BadRequestException("Builder profile not found for this account")

            builder_id = current_user.builder_profile.id
            owner_id = current_user.id
            agent_id = None

            if project_id is not None:
                project = await self.repo.get_project(project_id)
                if not project:
                    raise NotFoundException(f"Project with ID {project_id} not found")
                if project.builder_id != builder_id:
                    raise ForbiddenException(
                        "You do not own the project associated with this property"
                    )

        elif current_user.role == "agent":
            # ── Agent Flow: USER -> AGENT -> create property
            if not current_user.agent_profile:
                raise BadRequestException("Agent profile not found for this account")

            agent_id = current_user.agent_profile.id
            builder_id = None
            # If agent specified a client's owner_id, use it; otherwise, agent's user_id
            owner_id = payload.get("owner_id") or current_user.id

        elif current_user.role in ("buyer", "user", "owner", "seller"):
            # ── User Flow: USER -> create property
            owner_id = current_user.id
            agent_id = None
            builder_id = None
            project_id = None

        elif current_user.role == "admin":
            # ── Admin Flow: full control
            owner_id = payload.get("owner_id") or current_user.id
            agent_id = payload.get("agent_id")
            builder_id = payload.get("builder_id")
            project_id = payload.get("project_id")
        else:
            owner_id = current_user.id

        # Update payload with verified IDs
        payload["owner_id"] = owner_id
        payload["agent_id"] = agent_id
        payload["builder_id"] = builder_id
        payload["project_id"] = project_id

        # Default status to ACTIVE if not set or DRAFT
        if not payload.get("status"):
            payload["status"] = "ACTIVE"

        # Validate location references if provided
        await self._validate_location_references(payload)

        prop = Property(**payload)


        # Attach amenities if provided
        if amenity_ids:
            amenities = await self.repo.get_amenities_by_ids(amenity_ids)
            prop.amenities = amenities

        created_prop = await self.repo.create(prop)
        await self.db.commit()
        # Fetch detailed for complete response representation
        return await self.repo.get_by_id_detailed(created_prop.id) or created_prop

    # ── List & Search Properties ───────────────────────────────────────

    async def list_properties(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "newest",
        current_user: User | None = None,
    ) -> tuple[list[Property], int]:
        """List properties with 99acres-style filters and pagination."""
        # For public/unauthenticated searches, only show active listings unless specified
        if "is_active" not in filters:
            filters["is_active"] = True

        offset = (max(1, page) - 1) * page_size
        return await self.repo.list_properties(
            filters=filters,
            offset=offset,
            limit=page_size,
            sort_by=sort_by,
        )

    # ── Get Property Details ───────────────────────────────────────────

    async def get_property(
        self, property_id: int, current_user: User | None = None
    ) -> Property:
        prop = await self.repo.get_by_id_detailed(property_id)
        if not prop:
            raise NotFoundException(f"Property with ID {property_id} not found")
        return prop

    # ── Update Property ────────────────────────────────────────────────

    async def update_property(
        self,
        property_id: int,
        current_user: User,
        data: PropertyUpdate,
    ) -> Property:
        prop = await self.repo.get_by_id(property_id)
        if not prop:
            raise NotFoundException(f"Property with ID {property_id} not found")

        self._check_property_permission(prop, current_user)

        update_data = data.model_dump(exclude_unset=True)

        # Validate location references if provided
        await self._validate_location_references(update_data)

        # Validate project ownership if builder attempts to link/change project

        if "project_id" in update_data and update_data["project_id"] is not None:
            if current_user.role == "builder":
                project = await self.repo.get_project(update_data["project_id"])
                if not project:
                    raise NotFoundException("Project not found")
                if (
                    current_user.builder_profile
                    and project.builder_id != current_user.builder_profile.id
                ):
                    raise ForbiddenException("You do not own this project")

        for key, value in update_data.items():
            setattr(prop, key, value)

        await self.repo.update(prop)
        await self.db.commit()
        return await self.repo.get_by_id_detailed(property_id) or prop

    # ── Delete Property ────────────────────────────────────────────────

    async def delete_property(self, property_id: int, current_user: User) -> None:
        prop = await self.repo.get_by_id(property_id)
        if not prop:
            raise NotFoundException(f"Property with ID {property_id} not found")

        self._check_property_permission(prop, current_user)
        await self.repo.delete(prop)
        await self.db.commit()

    # ── Add Media ──────────────────────────────────────────────────────

    async def add_media(
        self,
        property_id: int,
        current_user: User,
        data: PropertyMediaCreateInput,
    ) -> PropertyMedia:
        prop = await self.repo.get_by_id(property_id)
        if not prop:
            raise NotFoundException(f"Property with ID {property_id} not found")

        self._check_property_permission(prop, current_user)

        # If designated as primary media, reset existing primary media flags
        if data.is_primary:
            await self.repo.unset_primary_media(property_id)

        media = PropertyMedia(
            property_id=property_id,
            media_type=data.media_type,
            url=data.url,
            thumbnail_url=data.thumbnail_url,
            title=data.title,
            sort_order=data.sort_order,
            is_primary=data.is_primary,
        )
        saved_media = await self.repo.add_media(media)
        await self.db.commit()
        return saved_media

    # ── Assign Amenities ───────────────────────────────────────────────

    async def assign_amenities(
        self,
        property_id: int,
        current_user: User,
        amenity_ids: list[int],
    ) -> list[Amenity]:
        prop = await self.repo.get_by_id_detailed(property_id)
        if not prop:
            raise NotFoundException(f"Property with ID {property_id} not found")

        self._check_property_permission(prop, current_user)

        if amenity_ids:
            amenities = await self.repo.get_amenities_by_ids(amenity_ids)
            found_ids = {a.id for a in amenities}
            missing = set(amenity_ids) - found_ids
            if missing:
                raise BadRequestException(
                    f"Amenities with IDs {list(missing)} not found"
                )
        else:
            amenities = []

        updated_amenities = await self.repo.assign_amenities(prop, amenities)
        await self.db.commit()
        return updated_amenities
