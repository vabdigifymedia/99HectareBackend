import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.properties.models import Property


def unique_email() -> str:
    return f"fav_visit_{uuid.uuid4().hex[:8]}@example.com"


async def register_user(client: AsyncClient, role: str = "buyer") -> tuple[str, dict]:
    email = unique_email()
    payload = {
        "full_name": f"Test {role.capitalize()}",
        "email": email,
        "password": "Password123!",
        "role": role,
    }
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 200, f"Register failed: {res.text}"
    data = res.json()["data"]
    return data["access_token"], data


@pytest.mark.asyncio
async def test_favorites_crud_flow(client: AsyncClient, db_session: AsyncSession):
    # Fetch an existing property from DB
    res = await db_session.execute(select(Property.id).limit(1))
    prop_id = res.scalar_one_or_none()
    if not prop_id:
        pytest.skip("No properties available for favorite test")

    token, user_data = await register_user(client, role="buyer")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Check initial count (should be 0)
    res = await client.get("/api/v1/favorites/count", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"] == 0

    # 2. Add property to favorites
    res = await client.post("/api/v1/favorites/", headers=headers, json={"property_id": prop_id})
    assert res.status_code == 201
    assert res.json()["data"]["id"] == prop_id

    # 3. Check count updated to 1
    res = await client.get("/api/v1/favorites/count", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"] == 1

    # 4. List favorites
    res = await client.get("/api/v1/favorites/", headers=headers)
    assert res.status_code == 200
    favorites = res.json()["data"]
    assert len(favorites) >= 1
    assert any(f["id"] == prop_id for f in favorites)

    # 5. Get favorite by property id
    res = await client.get(f"/api/v1/favorites/{prop_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["id"] == prop_id

    # 6. Remove favorite
    res = await client.delete(f"/api/v1/favorites/{prop_id}", headers=headers)
    assert res.status_code == 200

    # 7. Check count back to 0
    res = await client.get("/api/v1/favorites/count", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"] == 0


@pytest.mark.asyncio
async def test_visits_crud_flow(client: AsyncClient, db_session: AsyncSession):
    res = await db_session.execute(select(Property.id).limit(1))
    prop_id = res.scalar_one_or_none()
    if not prop_id:
        pytest.skip("No properties available for visit test")

    token, user_data = await register_user(client, role="buyer")
    headers = {"Authorization": f"Bearer {token}"}
    user_id = user_data["user"]["id"]

    # 1. Create a visit
    visit_payload = {
        "property_id": prop_id,
        "requested_date": "2026-10-15T11:00:00Z",
        "user_notes": "Please confirm if morning slot works.",
    }
    res = await client.post("/api/v1/visits", headers=headers, json=visit_payload)
    assert res.status_code == 201
    visit = res.json()["data"]
    visit_id = visit["id"]
    assert visit["property_id"] == prop_id
    assert visit["status"] == "REQUESTED"

    # 2. Get visit by ID
    res = await client.get(f"/api/v1/visits/{visit_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["id"] == visit_id

    # 3. Get visits by user
    res = await client.get(f"/api/v1/visits/user/{user_id}", headers=headers)
    assert res.status_code == 200
    visits_list = res.json()["data"]
    assert any(v["id"] == visit_id for v in visits_list)

    # 4. Update status
    update_payload = {
        "status": "CANCELLED",
        "cancellation_reason": "Change of schedule",
    }
    res = await client.patch(f"/api/v1/visits/{visit_id}/status", headers=headers, json=update_payload)
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "CANCELLED"

    # 5. Delete visit
    res = await client.delete(f"/api/v1/visits/{visit_id}", headers=headers)
    assert res.status_code == 200
