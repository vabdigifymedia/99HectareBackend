import uuid
from decimal import Decimal
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.amenities.models import Amenity
from app.modules.builders.models import Builder
from app.modules.projects.models import Project


def unique_email() -> str:
    return f"prop_test_{uuid.uuid4().hex[:8]}@example.com"


async def register_user(client: AsyncClient, role: str = "buyer", **extra) -> tuple[str, dict]:
    """Helper to register user and return (token, user_data)."""
    email = unique_email()
    payload = {
        "full_name": f"Test {role.capitalize()}",
        "email": email,
        "password": "Password123!",
        "role": role,
        **extra,
    }
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 200, f"Register failed: {res.text}"
    data = res.json()["data"]
    return data["access_token"], data


@pytest.mark.asyncio
async def test_user_owner_property_creation_flow(client: AsyncClient):
    """Test USER (owner) flow: USER -> create property."""
    token, _ = await register_user(client, role="buyer")

    prop_payload = {
        "title": "Luxury 3BHK Apartment in Downtown",
        "description": "Spacious flat with panoramic city views and modern interiors.",
        "property_type": "apartment",
        "listing_type": "SALE",
        "price": 12500000.00,
        "carpet_area": 1450.00,
        "bedrooms": 3,
        "bathrooms": 3,
        "furnishing_status": "SEMI_FURNISHED",
        "address": "123 Downtown Avenue",
        "pincode": "110001",
    }

    res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {token}"},
        json=prop_payload,
    )
    assert res.status_code == 201, res.text
    data = res.json()["data"]
    assert data["title"] == prop_payload["title"]
    assert data["owner_id"] is not None
    assert data["agent_id"] is None
    assert data["builder_id"] is None
    assert data["project_id"] is None
    assert data["owner"]["email"] is not None


@pytest.mark.asyncio
async def test_agent_property_creation_flow(client: AsyncClient):
    """Test AGENT flow: USER -> AGENT -> create property."""
    token, _ = await register_user(
        client,
        role="agent",
        agency_name="City Brokers",
        license_number=f"LIC-{uuid.uuid4().hex[:6]}",
        rera_registration_number=f"RERA-AG-{uuid.uuid4().hex[:6]}",
        experience_years=7,
    )

    prop_payload = {
        "title": "Prime Commercial Office Space in Tech Park",
        "description": "Grade A IT office space ready for immediate occupancy.",
        "property_type": "commercial",
        "listing_type": "RENT",
        "price": 85000.00,
        "carpet_area": 2200.00,
        "address": "Cyber Heights Sector 62",
    }

    res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {token}"},
        json=prop_payload,
    )
    assert res.status_code == 201, res.text
    data = res.json()["data"]
    assert data["agent_id"] is not None
    assert data["builder_id"] is None
    assert data["agent"]["agency_name"] == "City Brokers"


@pytest.mark.asyncio
async def test_builder_project_property_flow(client: AsyncClient, db_session: AsyncSession):
    """Test BUILDER flow: BUILDER -> PROJECT -> PROPERTY / UNIT."""
    # 1. Register Builder
    token, builder_user = await register_user(
        client,
        role="builder",
        company_name="Prestige Developers",
        license_number=f"BLD-{uuid.uuid4().hex[:6]}",
    )
    user_id = builder_user["user"]["id"]
    builder_res = await db_session.execute(
        select(Builder).where(Builder.user_id == user_id)
    )
    builder = builder_res.scalar_one()
    builder_id = builder.id

    # 2. Builder sets up a Project in the DB
    project = Project(
        builder_id=builder_id,
        name="Prestige Falcon City",
        project_type="residential",
        status="UNDER_CONSTRUCTION",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # 3. Builder adds a Property / Unit under this Project
    prop_payload = {
        "title": "2BHK Premium Tower Unit A-402",
        "description": "Tower A 4th floor facing the central garden courtyard.",
        "property_type": "apartment",
        "listing_type": "SALE",
        "price": 9500000.00,
        "carpet_area": 1150.00,
        "bedrooms": 2,
        "bathrooms": 2,
        "project_id": project.id,
    }

    res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {token}"},
        json=prop_payload,
    )
    assert res.status_code == 201, res.text
    data = res.json()["data"]
    assert data["builder_id"] == builder_id
    assert data["project_id"] == project.id
    assert data["builder"]["company_name"] == "Prestige Developers"
    assert data["project"]["name"] == "Prestige Falcon City"

    # 4. Another builder attempts to create property under the first builder's project -> 403 Forbidden
    other_token, _ = await register_user(
        client,
        role="builder",
        company_name="Rival Group",
        license_number=f"BLD-{uuid.uuid4().hex[:6]}",
    )
    hijack_res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {other_token}"},
        json={**prop_payload, "title": "Hijacked Unit"},
    )
    assert hijack_res.status_code == 403


@pytest.mark.asyncio
async def test_properties_listing_and_filtering(client: AsyncClient):
    """Test GET /properties filtering by search, price, property_type, and pagination."""
    token, _ = await register_user(client, role="buyer")

    unique_keyword = f"UniqueHaven_{uuid.uuid4().hex[:6]}"
    p1 = {
        "title": f"Villa {unique_keyword}",
        "property_type": "villa",
        "listing_type": "SALE",
        "price": 20000000.00,
        "bedrooms": 4,
        "carpet_area": 3500.00,
    }
    p2 = {
        "title": f"Budget Apartment {unique_keyword}",
        "property_type": "apartment",
        "listing_type": "SALE",
        "price": 4500000.00,
        "bedrooms": 1,
        "carpet_area": 600.00,
    }

    res1 = await client.post("/api/v1/properties", headers={"Authorization": f"Bearer {token}"}, json=p1)
    res2 = await client.post("/api/v1/properties", headers={"Authorization": f"Bearer {token}"}, json=p2)
    assert res1.status_code == 201
    assert res2.status_code == 201

    # 1. Search keyword
    res = await client.get(f"/api/v1/properties?search={unique_keyword}")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert len(data["data"]) == 2

    # 2. Filter by property_type
    res = await client.get(f"/api/v1/properties?search={unique_keyword}&property_type=villa")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["data"][0]["property_type"] == "villa"

    # 3. Filter by price range
    res = await client.get(f"/api/v1/properties?search={unique_keyword}&max_price=5000000")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert float(data["data"][0]["price"]) == 4500000.00

    # 4. Sorting price_asc
    res = await client.get(f"/api/v1/properties?search={unique_keyword}&sort_by=price_asc")
    assert res.status_code == 200
    items = res.json()["data"]
    assert float(items[0]["price"]) <= float(items[1]["price"])


@pytest.mark.asyncio
async def test_get_property_by_id(client: AsyncClient):
    """Test GET /properties/{id}."""
    token, _ = await register_user(client, role="buyer")

    create_res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Seaside Bungalow",
            "property_type": "house",
            "listing_type": "SALE",
            "price": 18000000.00,
        },
    )
    prop_id = create_res.json()["data"]["id"]

    res = await client.get(f"/api/v1/properties/{prop_id}")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["id"] == prop_id
    assert data["title"] == "Seaside Bungalow"

    # Non-existent ID returns 404
    missing_res = await client.get("/api/v1/properties/9999999")
    assert missing_res.status_code == 404


@pytest.mark.asyncio
async def test_update_and_delete_property_permissions(client: AsyncClient):
    """Test PUT /properties/{id} and DELETE /properties/{id} with authorization enforcement."""
    owner_token, _ = await register_user(client, role="buyer")
    other_token, _ = await register_user(client, role="buyer")

    # 1. Create property as owner
    create_res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "Modern Studio Apartment",
            "property_type": "apartment",
            "listing_type": "RENT",
            "price": 25000.00,
        },
    )
    prop_id = create_res.json()["data"]["id"]

    # 2. Other user attempts to update -> 403 Forbidden
    other_update = await client.put(
        f"/api/v1/properties/{prop_id}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"title": "Hacked Title"},
    )
    assert other_update.status_code == 403

    # 3. Owner updates property -> 200 OK
    owner_update = await client.put(
        f"/api/v1/properties/{prop_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"price": 28000.00, "description": "Updated price and description."},
    )
    assert owner_update.status_code == 200
    assert float(owner_update.json()["data"]["price"]) == 28000.00

    # 4. Other user attempts to delete -> 403 Forbidden
    other_delete = await client.delete(
        f"/api/v1/properties/{prop_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert other_delete.status_code == 403

    # 5. Owner deletes property -> 200 OK
    owner_delete = await client.delete(
        f"/api/v1/properties/{prop_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert owner_delete.status_code == 200

    # 6. Verify property no longer exists
    get_res = await client.get(f"/api/v1/properties/{prop_id}")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_property_media_and_amenities(client: AsyncClient, db_session: AsyncSession):
    """Test POST /properties/{id}/media and POST /properties/{id}/amenities."""
    owner_token, _ = await register_user(client, role="buyer")
    other_token, _ = await register_user(client, role="buyer")

    # 1. Create property
    create_res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "Garden Penthouse with Terrace",
            "property_type": "apartment",
            "listing_type": "SALE",
            "price": 35000000.00,
        },
    )
    prop_id = create_res.json()["data"]["id"]

    # 2. Add Media: Unauthorized user receives 403
    media_payload = {
        "media_type": "IMAGE",
        "url": "https://images.example.com/penthouse-living.jpg",
        "thumbnail_url": "https://images.example.com/penthouse-living-thumb.jpg",
        "title": "Living Room",
        "sort_order": 1,
        "is_primary": True,
    }
    unauth_media = await client.post(
        f"/api/v1/properties/{prop_id}/media",
        headers={"Authorization": f"Bearer {other_token}"},
        json=media_payload,
    )
    assert unauth_media.status_code == 403

    # 3. Add Media: Owner succeeds with 201
    media_res = await client.post(
        f"/api/v1/properties/{prop_id}/media",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=media_payload,
    )
    assert media_res.status_code == 201
    media_data = media_res.json()["data"]
    assert media_data["url"] == media_payload["url"]
    assert media_data["is_primary"] is True

    # 4. Amenities: Create test amenities in database
    a1 = Amenity(name=f"Infinity Pool {uuid.uuid4().hex[:4]}")
    a2 = Amenity(name=f"Gymnasium {uuid.uuid4().hex[:4]}")
    db_session.add_all([a1, a2])
    await db_session.commit()
    await db_session.refresh(a1)
    await db_session.refresh(a2)

    # 5. Assign Amenities: Unauthorized user receives 403
    unauth_amenities = await client.post(
        f"/api/v1/properties/{prop_id}/amenities",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"amenity_ids": [a1.id, a2.id]},
    )
    assert unauth_amenities.status_code == 403

    # 6. Assign Amenities: Owner succeeds with 200
    amenities_res = await client.post(
        f"/api/v1/properties/{prop_id}/amenities",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"amenity_ids": [a1.id, a2.id]},
    )
    assert amenities_res.status_code == 200
    amenities_data = amenities_res.json()["data"]
    assert len(amenities_data) == 2
    assigned_ids = {a["id"] for a in amenities_data}
    assert a1.id in assigned_ids
    assert a2.id in assigned_ids

    # 7. Detailed property fetch now includes both media and amenities
    detail_res = await client.get(f"/api/v1/properties/{prop_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()["data"]
    assert len(detail_data["media"]) == 1
    assert len(detail_data["amenities"]) == 2


@pytest.mark.asyncio
async def test_property_creation_with_locations(client: AsyncClient):
    """Test creating a property with valid location references (country, state, city, locality, sub_locality)."""
    token, _ = await register_user(client, role="buyer")

    prop_payload = {
        "title": "3 BHK Premium Apartment in Sector 57",
        "description": "Spacious 3 BHK apartment with modern amenities and excellent connectivity.",
        "property_type": "apartment",
        "listing_type": "SALE",
        "price": 12500000.00,
        "carpet_area": 950.00,
        "country_id": 1,
        "state_id": 1,
        "city_id": 1,
        "locality_id": 1,
        "sub_locality_id": 1,
        "address": "Sector 57, Gurugram, Haryana",
        "landmark": "Near Golf Course Road",
        "pincode": "122011",
    }

    res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {token}"},
        json=prop_payload,
    )
    assert res.status_code == 201, res.text
    data = res.json()["data"]
    assert data["title"] == prop_payload["title"]
    assert data["city_id"] == 1
    assert data["state_id"] == 1
    assert data["country_id"] == 1
    assert data["locality_id"] == 1
    assert data["sub_locality_id"] == 1


@pytest.mark.asyncio
async def test_property_creation_invalid_location_fails(client: AsyncClient):
    """Test that creating a property with a non-existent city_id returns a 400 Bad Request, not a 500 crash."""
    token, _ = await register_user(client, role="buyer")

    prop_payload = {
        "title": "Invalid Location Apartment",
        "description": "Testing invalid foreign key handling.",
        "property_type": "apartment",
        "listing_type": "SALE",
        "price": 5000000.00,
        "city_id": 99999,
    }

    res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {token}"},
        json=prop_payload,
    )
    assert res.status_code == 400
    assert "City with ID 99999 does not exist" in res.json()["detail"]


@pytest.mark.asyncio
async def test_locations_endpoints(client: AsyncClient):
    """Test that location endpoints return seeded countries, states, and cities."""
    # List countries
    res = await client.get("/api/v1/locations/countries")
    assert res.status_code == 200
    countries = res.json()["data"]
    assert len(countries) >= 1
    assert any(c["name"] == "India" for c in countries)

    # List states
    res = await client.get("/api/v1/locations/states")
    assert res.status_code == 200
    states = res.json()["data"]
    assert len(states) >= 1
    assert any(s["name"] == "Haryana" for s in states)

    # List cities
    res = await client.get("/api/v1/locations/cities?search=Gurugram")
    assert res.status_code == 200
    cities = res.json()["data"]
    assert len(cities) >= 1
    assert cities[0]["name"] == "Gurugram"

