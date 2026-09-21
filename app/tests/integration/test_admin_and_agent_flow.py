import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.models import Agent
from app.modules.builders.models import Builder
from app.modules.properties.models import Property


def unique_email(prefix: str = "test") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


async def register_user(client: AsyncClient, role: str = "buyer", **extra) -> tuple[str, dict]:
    email = unique_email(role)
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


# ── 1. Agent Module Flow ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_agent_module_and_bulk_properties_flow(client: AsyncClient):
    # Register agent user
    token, data = await register_user(
        client,
        role="agent",
        agency_name="Prime Realty Agency",
        license_number=f"AG-LIC-{uuid.uuid4().hex[:6]}",
        experience_years=5,
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get current agent profile
    res = await client.get("/api/v1/agents/me", headers=headers)
    assert res.status_code == 200, res.text
    agent_data = res.json()["data"]
    agent_id = agent_data["id"]
    assert agent_data["agency_name"] == "Prime Realty Agency"

    # 2. Update agent profile
    update_res = await client.put(
        "/api/v1/agents/me",
        headers=headers,
        json={"agency_name": "Prime Realty Global", "experience_years": 8},
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["agency_name"] == "Prime Realty Global"
    assert update_res.json()["data"]["experience_years"] == 8

    # 3. Agent adds a single property via /agents/me/properties
    prop_payload = {
        "title": "Agent Single Listing Flat",
        "description": "Exclusive listing by agent",
        "property_type": "apartment",
        "listing_type": "SALE",
        "price": 7500000.00,
        "carpet_area": 1100.00,
        "bedrooms": 2,
        "bathrooms": 2,
    }
    single_res = await client.post("/api/v1/agents/me/properties", headers=headers, json=prop_payload)
    assert single_res.status_code == 201, single_res.text
    created_single = single_res.json()["data"]
    assert created_single["agent_id"] == agent_id
    assert created_single["title"] == prop_payload["title"]

    # 4. Agent adds multiple properties in bulk via /agents/me/properties/bulk
    bulk_payload = {
        "properties": [
            {
                "title": "Bulk Property Alpha 1",
                "description": "First bulk property listing",
                "property_type": "villa",
                "listing_type": "SALE",
                "price": 18000000.00,
                "carpet_area": 2500.00,
                "bedrooms": 4,
                "bathrooms": 4,
            },
            {
                "title": "Bulk Property Beta 2",
                "description": "Second bulk property listing",
                "property_type": "apartment",
                "listing_type": "RENT",
                "price": 45000.00,
                "carpet_area": 950.00,
                "bedrooms": 2,
                "bathrooms": 2,
            },
        ]
    }
    bulk_res = await client.post("/api/v1/agents/me/properties/bulk", headers=headers, json=bulk_payload)
    assert bulk_res.status_code == 201, bulk_res.text
    bulk_data_res = bulk_res.json()["data"]
    assert bulk_data_res["created_count"] == 2
    assert len(bulk_data_res["properties"]) == 2
    for p in bulk_data_res["properties"]:
        assert p["agent_id"] == agent_id

    # 5. Get agent's own properties
    my_props_res = await client.get("/api/v1/agents/me/properties", headers=headers)
    assert my_props_res.status_code == 200
    my_props = my_props_res.json()["data"]
    assert len(my_props) >= 3

    # 6. Public agent endpoints
    pub_res = await client.get("/api/v1/agents")
    assert pub_res.status_code == 200
    assert any(a["id"] == agent_id for a in pub_res.json()["data"])

    detail_res = await client.get(f"/api/v1/agents/{agent_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["data"]["id"] == agent_id

    agent_props_res = await client.get(f"/api/v1/agents/{agent_id}/properties")
    assert agent_props_res.status_code == 200


# ── 2. Inquiry Middle-Payment & Contact Masking Flow ──────────────────


@pytest.mark.asyncio
async def test_inquiry_gatekeeper_and_middle_payment_flow(client: AsyncClient, db_session: AsyncSession):
    # 1. Register Agent
    agent_token, agent_user = await register_user(
        client,
        role="agent",
        agency_name="Gatekeeper Realty",
        license_number=f"GK-{uuid.uuid4().hex[:6]}",
    )
    agent_headers = {"Authorization": f"Bearer {agent_token}"}
    agent_profile_res = await client.get("/api/v1/agents/me", headers=agent_headers)
    agent_id = agent_profile_res.json()["data"]["id"]

    # 2. Agent creates a property listing
    prop_res = await client.post(
        "/api/v1/agents/me/properties",
        headers=agent_headers,
        json={
            "title": "Gatekeeper Luxury Apartment",
            "property_type": "apartment",
            "listing_type": "SALE",
            "price": 9500000.00,
        },
    )
    assert prop_res.status_code == 201
    prop_id = prop_res.json()["data"]["id"]

    # 3. Register Buyer and submit an inquiry on this property
    buyer_token, _ = await register_user(client, role="buyer")
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    buyer_phone = "9876543210"
    buyer_email = "buyer_secret@example.com"
    buyer_name = "Interested Alice"

    inq_res = await client.post(
        "/api/v1/inquiries",
        headers=buyer_headers,
        json={
            "property_id": prop_id,
            "name": buyer_name,
            "phone": buyer_phone,
            "email": buyer_email,
            "message": "I want to visit this property this Sunday.",
        },
    )
    assert inq_res.status_code == 201
    inquiry_id = inq_res.json()["data"]["id"]

    # 4. Agent checks received inquiries BEFORE admin confirmation:
    # Phone, email, and message details MUST be masked!
    received_res = await client.get("/api/v1/inquiries/received", headers=agent_headers)
    assert received_res.status_code == 200
    received_inqs = received_res.json()["data"]
    target_inq = next((i for i in received_inqs if i["id"] == inquiry_id), None)
    assert target_inq is not None
    assert target_inq["is_admin_approved"] is False
    assert target_inq["phone"] is None, "Buyer phone must be masked before admin approval"
    assert target_inq["email"] is None, "Buyer email must be masked before admin approval"
    assert "Pending Admin Approval" in target_inq["name"]

    # 5. Register Admin user
    admin_token, _ = await register_user(client, role="admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin checks GET /admin/inquiries: Admin CAN see full buyer details to discuss middle payment!
    admin_inqs_res = await client.get("/admin/inquiries", headers=admin_headers)
    assert admin_inqs_res.status_code == 200
    admin_target_inq = next((i for i in admin_inqs_res.json()["data"] if i["id"] == inquiry_id), None)
    assert admin_target_inq is not None
    assert admin_target_inq["phone"] == buyer_phone
    assert admin_target_inq["email"] == buyer_email
    assert admin_target_inq["name"] == buyer_name

    # 6. Admin confirms middle payment discussion and APPROVES the inquiry
    approve_res = await client.patch(
        f"/admin/inquiries/{inquiry_id}/approve",
        headers=admin_headers,
        json={"admin_notes": "Middle payment fee of 2% received manually via bank transfer."},
    )
    assert approve_res.status_code == 200, approve_res.text
    assert approve_res.json()["data"]["is_admin_approved"] is True
    assert approve_res.json()["data"]["status"] == "APPROVED"

    # 7. Agent checks received inquiries AFTER admin approval:
    # Full buyer contact details are now UNLOCKED!
    received_after_res = await client.get("/api/v1/inquiries/received", headers=agent_headers)
    assert received_after_res.status_code == 200
    unlocked_inq = next((i for i in received_after_res.json()["data"] if i["id"] == inquiry_id), None)
    assert unlocked_inq is not None
    assert unlocked_inq["is_admin_approved"] is True
    assert unlocked_inq["phone"] == buyer_phone
    assert unlocked_inq["email"] == buyer_email
    assert unlocked_inq["name"] == buyer_name


# ── 3. All Admin Management Routes ────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_routes_complete(client: AsyncClient, db_session: AsyncSession):
    admin_token, _ = await register_user(client, role="admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # ── GET /admin/users
    users_res = await client.get("/admin/users", headers=admin_headers)
    assert users_res.status_code == 200, users_res.text
    assert "data" in users_res.json()
    assert users_res.json()["total"] >= 1

    # ── Register a property to test approve and reject
    owner_token, _ = await register_user(client, role="buyer")
    prop_res = await client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "Admin Review Property",
            "property_type": "apartment",
            "listing_type": "SALE",
            "price": 5000000.00,
        },
    )
    prop_id = prop_res.json()["data"]["id"]

    # ── GET /admin/properties
    props_res = await client.get("/admin/properties", headers=admin_headers)
    assert props_res.status_code == 200
    assert any(p["id"] == prop_id for p in props_res.json()["data"])

    # ── PATCH /admin/properties/{id}/approve
    approve_prop_res = await client.patch(
        f"/admin/properties/{prop_id}/approve",
        headers=admin_headers,
    )
    assert approve_prop_res.status_code == 200, approve_prop_res.text
    assert approve_prop_res.json()["data"]["status"] == "ACTIVE"
    assert approve_prop_res.json()["data"]["is_verified"] is True
    assert approve_prop_res.json()["data"]["is_active"] is True

    # ── PATCH /admin/properties/{id}/reject
    reject_prop_res = await client.patch(
        f"/admin/properties/{prop_id}/reject",
        headers=admin_headers,
        json={"reason": "Incomplete legal documents submitted"},
    )
    assert reject_prop_res.status_code == 200, reject_prop_res.text
    assert reject_prop_res.json()["data"]["status"] == "REJECTED"
    assert reject_prop_res.json()["data"]["is_verified"] is False
    assert reject_prop_res.json()["data"]["is_active"] is False

    # ── PATCH /admin/agents/{id}/verify
    _, agent_reg = await register_user(
        client,
        role="agent",
        agency_name="Verify Agent Test",
        license_number=f"LIC-{uuid.uuid4().hex[:6]}",
    )
    agent_uid = agent_reg["user"]["id"]
    agent_db = await db_session.execute(select(Agent).where(Agent.user_id == agent_uid))
    agent_obj = agent_db.scalar_one()

    verify_agent_res = await client.patch(
        f"/admin/agents/{agent_obj.id}/verify",
        headers=admin_headers,
    )
    assert verify_agent_res.status_code == 200, verify_agent_res.text
    assert verify_agent_res.json()["data"]["verification_status"] == "VERIFIED"
    assert verify_agent_res.json()["data"]["is_active"] is True

    # ── PATCH /admin/builders/{id}/verify
    _, builder_reg = await register_user(
        client,
        role="builder",
        company_name="Verify Builder Test",
        license_number=f"BLD-{uuid.uuid4().hex[:6]}",
    )
    builder_uid = builder_reg["user"]["id"]
    builder_db = await db_session.execute(select(Builder).where(Builder.user_id == builder_uid))
    builder_obj = builder_db.scalar_one()

    verify_builder_res = await client.patch(
        f"/admin/builders/{builder_obj.id}/verify",
        headers=admin_headers,
    )
    assert verify_builder_res.status_code == 200, verify_builder_res.text
    assert verify_builder_res.json()["data"]["verification_status"] == "VERIFIED"
    assert verify_builder_res.json()["data"]["is_active"] is True

    # ── Reports: Create -> GET /admin/reports -> PATCH /admin/reports/{id}/resolve
    user_token, _ = await register_user(client, role="buyer")
    report_res = await client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "property_id": prop_id,
            "reason": "Misleading photos",
            "description": "Photos show pool but no pool exists.",
        },
    )
    assert report_res.status_code == 201
    report_id = report_res.json()["data"]["id"]

    reports_list_res = await client.get("/admin/reports", headers=admin_headers)
    assert reports_list_res.status_code == 200
    assert any(r["id"] == report_id for r in reports_list_res.json()["data"])

    resolve_report_res = await client.patch(
        f"/admin/reports/{report_id}/resolve",
        headers=admin_headers,
        json={"admin_notes": "Contacted owner to update photos with accurate images."},
    )
    assert resolve_report_res.status_code == 200, resolve_report_res.text
    assert resolve_report_res.json()["data"]["status"] == "RESOLVED"
    assert resolve_report_res.json()["data"]["admin_notes"] == "Contacted owner to update photos with accurate images."
