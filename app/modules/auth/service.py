import random
import string
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.modules.auth.models import OTPVerification, RefreshToken
from app.modules.auth.repository import AuthRepository
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_repo = AuthRepository(db)
        self.user_repo = UserRepository(db)

    # ── Register ───────────────────────────────────────────────────

    async def register(
        self, full_name: str, email: str, password: str, phone: str | None = None
    ) -> dict:
        if await self.user_repo.get_by_email(email):
            raise ConflictException("Email already registered")

        if phone and await self.user_repo.get_by_phone(phone):
            raise ConflictException("Phone number already registered")

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=pwd_context.hash(password),
        )
        user = await self.user_repo.create(user)
        await self.db.commit()

        return await self._generate_tokens(user)

    # ── Login ──────────────────────────────────────────────────────

    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user or not pwd_context.verify(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        return await self._generate_tokens(user)

    # ── Refresh Token ──────────────────────────────────────────────

    async def refresh_token(self, refresh_token_str: str) -> dict:
        try:
            payload = decode_token(refresh_token_str)
            user_id = payload.get("sub")
        except Exception:
            raise UnauthorizedException("Invalid refresh token")

        stored_token = await self.auth_repo.get_refresh_token(refresh_token_str)
        if not stored_token:
            raise UnauthorizedException("Refresh token not found or revoked")

        if stored_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
            timezone.utc
        ):
            raise UnauthorizedException("Refresh token expired")

        user = await self.user_repo.get_by_id(int(user_id))
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        await self.auth_repo.revoke_refresh_token(refresh_token_str)

        return await self._generate_tokens(user)

    # ── Logout ─────────────────────────────────────────────────────

    async def logout(self, refresh_token_str: str) -> None:
        await self.auth_repo.revoke_refresh_token(refresh_token_str)

    # ── Get Current User ───────────────────────────────────────────

    async def get_current_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")
        return user

    # ── Email Verification ─────────────────────────────────────────

    async def request_email_verification(self, email: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundException("User not found")

        if user.is_verified:
            raise BadRequestException("Email already verified")

        otp = self._generate_otp()
        otp_record = OTPVerification(
            user_id=user.id,
            otp=otp,
            purpose="email_verification",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        await self.auth_repo.create_otp(otp_record)
        await self.db.commit()

        return otp

    async def verify_email(self, email: str, otp: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundException("User not found")

        otp_record = await self.auth_repo.get_latest_otp(user.id, "email_verification")
        if not otp_record:
            raise BadRequestException("No verification code found. Request a new one.")

        if otp_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
            timezone.utc
        ):
            raise BadRequestException("Verification code expired. Request a new one.")

        if otp_record.otp != otp:
            raise BadRequestException("Invalid verification code")

        await self.auth_repo.mark_otp_verified(otp_record)
        user.is_verified = True
        await self.db.commit()

    # ── Password Reset ─────────────────────────────────────────────

    async def request_password_reset(self, email: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundException("User not found")

        otp = self._generate_otp()
        otp_record = OTPVerification(
            user_id=user.id,
            otp=otp,
            purpose="password_reset",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        await self.auth_repo.create_otp(otp_record)
        await self.db.commit()

        return otp

    async def reset_password(self, email: str, otp: str, new_password: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundException("User not found")

        otp_record = await self.auth_repo.get_latest_otp(user.id, "password_reset")
        if not otp_record:
            raise BadRequestException("No reset code found. Request a new one.")

        if otp_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
            timezone.utc
        ):
            raise BadRequestException("Reset code expired. Request a new one.")

        if otp_record.otp != otp:
            raise BadRequestException("Invalid reset code")

        await self.auth_repo.mark_otp_verified(otp_record)
        user.password_hash = pwd_context.hash(new_password)
        await self.auth_repo.revoke_all_user_tokens(user.id)
        await self.db.commit()

    # ── Change Password (authenticated) ────────────────────────────

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        if not pwd_context.verify(current_password, user.password_hash):
            raise BadRequestException("Current password is incorrect")

        user.password_hash = pwd_context.hash(new_password)
        await self.auth_repo.revoke_all_user_tokens(user.id)
        await self.db.commit()

    # ── Helpers ────────────────────────────────────────────────────

    async def _generate_tokens(self, user: User) -> dict:
        access = create_access_token(subject=str(user.id))
        refresh = create_refresh_token(subject=str(user.id))

        refresh_record = RefreshToken(
            user_id=user.id,
            token=refresh,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            is_revoked=False,
        )
        await self.auth_repo.create_refresh_token(refresh_record)
        await self.db.commit()

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    @staticmethod
    def _generate_otp(length: int = 6) -> str:
        return "".join(random.choices(string.digits, k=length))
