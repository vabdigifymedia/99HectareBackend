import uuid
import pytest
from fastapi import APIRouter, Depends
from httpx import AsyncClient

from app.core.dependencies import get_current_user, require_admin, require_agent
from app.main import app
from app.modules.users.models import User

# Test router to verify RBAC protection with live endpoints
rbac_router = APIRouter(prefix="/api/v1/test-rbac", tags=["test-rbac"])


@rbac_router.get("/agent-only")
async def agent_only_endpoint(agent_user: User = Depends(require_agent)):
    return {"message": "Welcome Agent", "user_id": agent_user.id}


@rbac_router.get("/admin-only")
async def admin_only_endpoint(admin_user: User = Depends(require_admin)):
    return {"message": "Welcome Admin", "user_id": admin_user.id}


app.include_router(rbac_router)


def unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.mark.asyncio
async def test_register_buyer(client: AsyncClient):
    """Test standard buyer user registration."""
    email = unique_email()
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Buyer",
            "email": email,
            "password": "Password123!",
            "role": "buyer",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "access_token" in data
    assert data["role"] == "buyer"
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "buyer"


@pytest.mark.asyncio
async def test_register_agent_dealer(client: AsyncClient):
    """Test agent (property dealer) registration with auto-provisioned agent profile."""
    email = unique_email()
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Prime Realty Agent",
            "email": email,
            "password": "Password123!",
            "role": "agent",
            "agency_name": "Prime Realty",
            "license_number": f"LIC-{uuid.uuid4().hex[:6]}",
            "rera_registration_number": f"RERA-{uuid.uuid4().hex[:6]}",
            "experience_years": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["role"] == "agent"

    # Access agent-protected endpoint
    token = data["access_token"]
    agent_res = await client.get(
        "/api/v1/test-rbac/agent-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert agent_res.status_code == 200
    assert agent_res.json()["message"] == "Welcome Agent"


@pytest.mark.asyncio
async def test_register_admin(client: AsyncClient):
    """Test admin registration with auto-provisioned admin profile and RBAC check."""
    email = unique_email()
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Portal Admin",
            "email": email,
            "password": "Password123!",
            "role": "admin",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["role"] == "admin"

    # Access admin-protected endpoint
    token = data["access_token"]
    admin_res = await client.get(
        "/api/v1/test-rbac/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert admin_res.status_code == 200
    assert admin_res.json()["message"] == "Welcome Admin"


@pytest.mark.asyncio
async def test_rbac_buyer_denied_agent_and_admin_endpoints(client: AsyncClient):
    """Test that buyer cannot access agent or admin guarded endpoints."""
    email = unique_email()
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Standard Buyer",
            "email": email,
            "password": "Password123!",
            "role": "buyer",
        },
    )
    token = reg.json()["data"]["access_token"]

    # Try agent endpoint
    agent_res = await client.get(
        "/api/v1/test-rbac/agent-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert agent_res.status_code == 403

    # Try admin endpoint
    admin_res = await client.get(
        "/api/v1/test-rbac/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert admin_res.status_code == 403


@pytest.mark.asyncio
async def test_rbac_agent_denied_admin_endpoint(client: AsyncClient):
    """Test that agent cannot access admin guarded endpoints."""
    email = unique_email()
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Agent Smith",
            "email": email,
            "password": "Password123!",
            "role": "agent",
        },
    )
    token = reg.json()["data"]["access_token"]

    # Try admin endpoint
    admin_res = await client.get(
        "/api/v1/test-rbac/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert admin_res.status_code == 403


@pytest.mark.asyncio
async def test_become_agent_flow(client: AsyncClient):
    """Test upgrading from a buyer account to an agent/property dealer."""
    email = unique_email()
    # 1. Register as buyer
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Upgrading User",
            "email": email,
            "password": "Password123!",
            "role": "buyer",
        },
    )
    token = reg.json()["data"]["access_token"]

    # 2. Upgrade to agent
    upgrade_res = await client.post(
        "/api/v1/auth/become-agent",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "agency_name": "New Horizons Realty",
            "license_number": f"UPG-{uuid.uuid4().hex[:6]}",
            "experience_years": 3,
        },
    )
    assert upgrade_res.status_code == 200
    agent_data = upgrade_res.json()["data"]
    assert agent_data["agency_name"] == "New Horizons Realty"

    # 3. Login to get new JWT reflecting agent role
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    new_token = login_res.json()["data"]["access_token"]

    # 4. Agent-only endpoint should now succeed
    agent_res = await client.get(
        "/api/v1/test-rbac/agent-only",
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert agent_res.status_code == 200


@pytest.mark.asyncio
async def test_login_and_refresh_token(client: AsyncClient):
    """Test login and refresh token lifecycle."""
    email = unique_email()
    password = "SecurePassword99!"
    await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Token Tester", "email": email, "password": password},
    )

    # Login
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    tokens = login_res.json()["data"]
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Refresh
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()["data"]
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
