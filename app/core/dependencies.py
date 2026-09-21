from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.modules.agents.models import Agent
from app.modules.admin.models import Admin
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_profiles(int(user_id))
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    return current_user


def require_roles(*allowed_roles: str) -> Callable:
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Allowed roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


require_admin = require_roles("admin")
require_agent = require_roles("agent")
require_builder = require_roles("builder")


async def get_current_agent(
    current_user: Annotated[User, Depends(require_agent)],
) -> Agent:
    if not current_user.agent_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent profile not found for this account",
        )
    return current_user.agent_profile


async def get_current_admin(
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Admin:
    if not current_user.admin_profile:
        from sqlalchemy import select
        res = await db.execute(select(Admin).where(Admin.user_id == current_user.id))
        admin = res.scalar_one_or_none()
        if not admin:
            admin = Admin(user_id=current_user.id, admin_level="SUPER_ADMIN")
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
        current_user.admin_profile = admin
    return current_user.admin_profile

