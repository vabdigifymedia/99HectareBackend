from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_user
from app.modules.agents.schemas import AgentResponse
from app.modules.auth.controller import AuthController
from app.modules.auth.schemas import (
    BecomeAgentRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RequestOTPRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    VerifyOTPRequest,
)
from app.modules.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


def get_controller(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthController:
    return AuthController(db)


# ── Register ───────────────────────────────────────────────────────


@router.post("/register", response_model=SuccessResponse[TokenResponse])
async def register(
    body: RegisterRequest,
    controller: AuthController = Depends(get_controller),
):
    data = await controller.register(body)
    return SuccessResponse(message="Registration successful", data=data)


# ── Login ──────────────────────────────────────────────────────────


@router.post("/login", response_model=SuccessResponse[TokenResponse])
async def login(
    body: LoginRequest,
    controller: AuthController = Depends(get_controller),
):
    data = await controller.login(body)
    return SuccessResponse(message="Login successful", data=data)


# ── Refresh Token ──────────────────────────────────────────────────


@router.post("/refresh", response_model=SuccessResponse[TokenResponse])
async def refresh_token(
    body: RefreshTokenRequest,
    controller: AuthController = Depends(get_controller),
):
    data = await controller.refresh_token(body)
    return SuccessResponse(message="Token refreshed", data=data)


# ── Logout ─────────────────────────────────────────────────────────


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    body: RefreshTokenRequest,
    controller: AuthController = Depends(get_controller),
):
    await controller.logout(body)
    return SuccessResponse(message="Logged out successfully")


# ── Become Agent / Upgrade to Property Dealer ─────────────────────


@router.post("/become-agent", response_model=SuccessResponse[AgentResponse])
async def become_agent(
    body: BecomeAgentRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: AuthController = Depends(get_controller),
):
    agent = await controller.become_agent(current_user.id, body)
    return SuccessResponse(
        message="Successfully upgraded to Agent/Property Dealer", data=agent
    )


# ── Email Verification ─────────────────────────────────────────────


@router.post("/verify-email/request", response_model=SuccessResponse)
async def request_email_verification(
    body: RequestOTPRequest,
    controller: AuthController = Depends(get_controller),
):
    otp = await controller.request_email_verification(body)
    return SuccessResponse(
        message="Verification code sent to your email",
        data={"otp": otp},
    )


@router.post("/verify-email/confirm", response_model=SuccessResponse)
async def verify_email(
    body: VerifyOTPRequest,
    controller: AuthController = Depends(get_controller),
):
    await controller.verify_email(body)
    return SuccessResponse(message="Email verified successfully")


# ── Password Reset ─────────────────────────────────────────────────


@router.post("/forgot-password/request", response_model=SuccessResponse)
async def request_password_reset(
    body: ForgotPasswordRequest,
    controller: AuthController = Depends(get_controller),
):
    otp = await controller.request_password_reset(body)
    return SuccessResponse(
        message="Password reset code sent to your email",
        data={"otp": otp},
    )


@router.post("/forgot-password/confirm", response_model=SuccessResponse)
async def reset_password(
    body: ResetPasswordRequest,
    controller: AuthController = Depends(get_controller),
):
    await controller.reset_password(body)
    return SuccessResponse(message="Password reset successfully")


# ── Change Password ────────────────────────────────────────────────


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    body: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: AuthController = Depends(get_controller),
):
    await controller.change_password(user_id=current_user.id, body=body)
    return SuccessResponse(message="Password changed successfully")


# ── Current User ───────────────────────────────────────────────────


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    controller: AuthController = Depends(get_controller),
):
    user = await controller.get_current_user(user_id=current_user.id)
    return SuccessResponse(message="User profile", data=user)
