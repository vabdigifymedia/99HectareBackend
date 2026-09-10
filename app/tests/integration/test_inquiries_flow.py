import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.models import Agent
from app.modules.builders.models import Builder


def unique_email() -> str:
    return f"inq_test_{uuid.uuid4().hex[:8]}@example.com"


async def register_user(client: AsyncClient, role: str = "buyer", **extra) -> tuple[str, dict]:
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
async def test_inquiry_crud_flow(client: AsyncClient, db_session: AsyncSession):
    token, user = await register_user(client, role="buyer")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Inquiry
    inquiry_payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "9876543210",
        "message": "I am interested in this property.",
        "source": "website",
    }
    res = await client.post("/api/v1/inquiries", headers=headers, json=inquiry_payload)
    assert res.status_code == 201, res.text
    inquiry_data = res.json()["data"]
    inquiry_id = inquiry_data["id"]
    assert inquiry_data["message"] == "I am interested in this property."
    assert inquiry_data["status"] == "NEW"

    # 2. Get My Inquiries
    res = await client.get("/api/v1/inquiries/my", headers=headers)
    assert res.status_code == 200
    my_inquiries = res.json()["data"]
    assert any(item["id"] == inquiry_id for item in my_inquiries)

    # 3. Get Inquiry by ID
    res = await client.get(f"/api/v1/inquiries/{inquiry_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["id"] == inquiry_id

    # 4. Get Inquiry Status
    res = await client.get(f"/api/v1/inquiries/{inquiry_id}/status", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"] == "NEW"

    # 5. Update Inquiry
    update_payload = {
        "status": "CONTACTED",
        "message": "Updated inquiry message.",
    }
    res = await client.patch(f"/api/v1/inquiries/{inquiry_id}", headers=headers, json=update_payload)
    assert res.status_code == 200
    updated_data = res.json()["data"]
    assert updated_data["status"] == "CONTACTED"
    assert updated_data["message"] == "Updated inquiry message."

    # 6. Get All Inquiries
    res = await client.get("/api/v1/inquiries", headers=headers)
    assert res.status_code == 200
    all_inquiries = res.json()["data"]
    assert any(item["id"] == inquiry_id for item in all_inquiries)

    # 7. Agent Inquiries
    _, agent_data = await register_user(
        client,
        role="agent",
        agency_name="Inquiry Test Agency",
        license_number=f"LIC-{uuid.uuid4().hex[:6]}",
    )
    agent_user_id = agent_data["user"]["id"]
    agent_res = await db_session.execute(
        select(Agent).where(Agent.user_id == agent_user_id)
    )
    agent = agent_res.scalar_one()
    agent_id = agent.id

    agent_inquiry_payload = {
        "name": "Jane Agent Inquiry",
        "agent_id": agent_id,
        "message": "Inquiry directed to agent",
    }
    res = await client.post("/api/v1/inquiries", headers=headers, json=agent_inquiry_payload)
    assert res.status_code == 201
    agent_inq_id = res.json()["data"]["id"]

    res = await client.get(f"/api/v1/inquiries/agent/{agent_id}", headers=headers)
    assert res.status_code == 200
    agent_inqs = res.json()["data"]
    assert any(item["id"] == agent_inq_id for item in agent_inqs)

    # 8. Builder Inquiries
    _, builder_data = await register_user(
        client,
        role="builder",
        company_name="Inquiry Test Builders",
        license_number=f"BLD-{uuid.uuid4().hex[:6]}",
    )
    builder_user_id = builder_data["user"]["id"]
    builder_res = await db_session.execute(
        select(Builder).where(Builder.user_id == builder_user_id)
    )
    builder = builder_res.scalar_one()
    builder_id = builder.id

    builder_inquiry_payload = {
        "name": "Bob Builder Inquiry",
        "builder_id": builder_id,
        "message": "Inquiry directed to builder",
    }
    res = await client.post("/api/v1/inquiries", headers=headers, json=builder_inquiry_payload)
    assert res.status_code == 201
    builder_inq_id = res.json()["data"]["id"]

    res = await client.get(f"/api/v1/inquiries/builder/{builder_id}", headers=headers)
    assert res.status_code == 200
    builder_inqs = res.json()["data"]
    assert any(item["id"] == builder_inq_id for item in builder_inqs)

    # 9. Delete Inquiry
    res = await client.delete(f"/api/v1/inquiries/{inquiry_id}", headers=headers)
    assert res.status_code == 200

    # 10. Verify 404 after deletion
    res = await client.get(f"/api/v1/inquiries/{inquiry_id}", headers=headers)
    assert res.status_code == 404
