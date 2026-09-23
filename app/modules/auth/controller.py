from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schemas import (
    BecomeAgentRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RequestOTPRequest,
    ResetPasswordRequest,
    SendOTPRequest,
    VerifyOTPAuthRequest,
    VerifyOTPRequest,
)
from app.modules.auth.service import AuthService



class AuthController:
    def __init__(self, db: AsyncSession):
        self.service = AuthService(db)

    async def register(self, body: RegisterRequest) -> dict:
        return await self.service.register(
            full_name=body.full_name,
            email=body.email,
            password=body.password,
            phone=body.phone,
            role=body.role,
            agency_name=body.agency_name,
            license_number=body.license_number,
            rera_registration_number=body.rera_registration_number,
            experience_years=body.experience_years,
            company_name=body.company_name,
        )

    async def login(self, body: LoginRequest) -> dict:
        return await self.service.login(email=body.email, password=body.password)

    async def refresh_token(self, body: RefreshTokenRequest) -> dict:
        return await self.service.refresh_token(refresh_token_str=body.refresh_token)

    async def logout(self, body: RefreshTokenRequest) -> None:
        await self.service.logout(refresh_token_str=body.refresh_token)

    async def become_agent(self, user_id: int, body: BecomeAgentRequest):
        return await self.service.become_agent(
            user_id=user_id,
            agent_data=body.model_dump(),
        )

    async def request_email_verification(self, body: RequestOTPRequest) -> str:
        return await self.service.request_email_verification(email=body.email)

    async def verify_email(self, body: VerifyOTPRequest) -> None:
        await self.service.verify_email(email=body.email, otp=body.otp)

    async def request_password_reset(self, body: ForgotPasswordRequest) -> str:
        return await self.service.request_password_reset(email=body.email)

    async def reset_password(self, body: ResetPasswordRequest) -> None:
        await self.service.reset_password(
            email=body.email, otp=body.otp, new_password=body.new_password
        )

    async def change_password(
        self, user_id: int, body: ChangePasswordRequest
    ) -> None:
        await self.service.change_password(
            user_id=user_id,
            current_password=body.current_password,
            new_password=body.new_password,
        )

    async def get_current_user(self, user_id: int):
        return await self.service.get_current_user(user_id=user_id)

    async def send_otp(self, body: SendOTPRequest) -> dict:
        return await self.service.send_otp(identifier=body.identifier, purpose=body.purpose)

    async def verify_otp_auth(self, body: VerifyOTPAuthRequest) -> dict:
        return await self.service.verify_otp_auth(
            identifier=body.identifier,
            otp=body.otp,
            full_name=body.full_name,
            role=body.role,
        )

