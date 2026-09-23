import random
import secrets
import string
from datetime import datetime, timedelta, timezone

from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


from app.common.enums import UserRole
from app.common.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.admin.models import Admin
from app.modules.agents.models import Agent
from app.modules.agents.repository import AgentRepository
from app.modules.auth.models import OTPVerification, RefreshToken
from app.modules.auth.repository import AuthRepository
from app.modules.builders.models import Builder
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.utils.mail_service import EmailService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_repo = AuthRepository(db)
        self.user_repo = UserRepository(db)
        self.agent_repo = AgentRepository(db)

    # ── Register ───────────────────────────────────────────────────

    async def register(
        self,
        full_name: str,
        email: str,
        password: str,
        phone: str | None = None,
        role: str = "buyer",
        agency_name: str | None = None,
        license_number: str | None = None,
        rera_registration_number: str | None = None,
        experience_years: int = 0,
        company_name: str | None = None,
    ) -> dict:
        normalized_role = role.lower()
        allowed_roles = [r.value for r in UserRole]
        if normalized_role not in allowed_roles:
            raise BadRequestException(
                f"Invalid role '{role}'. Allowed roles: {', '.join(allowed_roles)}"
            )

        if await self.user_repo.get_by_email(email):
            raise ConflictException("Email already registered")

        if phone and await self.user_repo.get_by_phone(phone):
            raise ConflictException("Phone number already registered")

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            role=normalized_role,
        )
        user = await self.user_repo.create(user)

        # Profile provisioning based on role
        if normalized_role == UserRole.AGENT.value:
            agent = Agent(
                user_id=user.id,
                agency_name=agency_name,
                license_number=license_number,
                rera_registration_number=rera_registration_number,
                experience_years=experience_years,
                phone=phone,
                email=email,
            )
            self.db.add(agent)
            await self.db.flush()

        elif normalized_role == UserRole.BUILDER.value:
            builder = Builder(
                user_id=user.id,
                company_name=company_name or full_name,
                license_number=license_number,
                rera_registration_number=rera_registration_number,
                phone=phone,
                email=email,
            )
            self.db.add(builder)
            await self.db.flush()

        elif normalized_role == UserRole.ADMIN.value:
            admin = Admin(
                user_id=user.id,
                admin_level="SUPER_ADMIN",
            )
            self.db.add(admin)
            await self.db.flush()

        await self.db.commit()

        user = await self.user_repo.get_by_id_with_profiles(user.id)
        return await self._generate_tokens(user)

    # ── Login ──────────────────────────────────────────────────────

    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
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

    # ── Become Agent / Upgrade to Property Dealer ─────────────────

    async def become_agent(self, user_id: int, agent_data: dict) -> Agent:
        user = await self.user_repo.get_by_id_with_profiles(user_id)
        if not user:
            raise NotFoundException("User not found")

        agent = await self.agent_repo.get_by_user_id(user_id)
        if agent:
            for k, v in agent_data.items():
                if v is not None and hasattr(agent, k):
                    setattr(agent, k, v)
        else:
            agent = Agent(
                user_id=user.id,
                agency_name=agent_data.get("agency_name"),
                license_number=agent_data.get("license_number"),
                rera_registration_number=agent_data.get("rera_registration_number"),
                experience_years=agent_data.get("experience_years", 0),
                phone=agent_data.get("phone") or user.phone,
                email=agent_data.get("email") or user.email,
                website=str(agent_data["website"]) if agent_data.get("website") else None,
                description=agent_data.get("description"),
            )
            self.db.add(agent)

        user.role = UserRole.AGENT.value
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

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

        await EmailService.send_template_email(
            to_email=settings.EMAIL,
            subject="99-Hectare Email Verification Code",
            template_name="emails/otp.html",
            context={
                "otp": otp,
                "expiry_minutes": 10,
            },
        )

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

        await EmailService.send_template_email(
            to_email=settings.EMAIL,
            subject="99-Hectare Password Reset Code",
            template_name="emails/otp.html",
            context={
                "otp": otp,
                "expiry_minutes": 10,
            },
        )

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
        user.password_hash = hash_password(new_password)
        await self.auth_repo.revoke_all_user_tokens(user.id)
        await self.db.commit()

    # ── Change Password (authenticated) ────────────────────────────

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        if not verify_password(current_password, user.password_hash):
            raise BadRequestException("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        await self.auth_repo.revoke_all_user_tokens(user.id)
        await self.db.commit()

    # ── OTP Authentication (Login & Signup) ────────────────────────

    async def _find_user_by_identifier(self, identifier: str) -> User | None:
        clean_id = identifier.strip()
        if "@" in clean_id:
            return await self.user_repo.get_by_email(clean_id.lower())

        # Phone match
        user = await self.user_repo.get_by_phone(clean_id)
        if user:
            return user

        digits = "".join(c for c in clean_id if c.isdigit())
        if len(digits) >= 10:
            last10 = digits[-10:]
            result = await self.db.execute(
                select(User).where(User.phone.like(f"%{last10}%"))
            )
            return result.scalar_one_or_none()
        return None

    async def send_otp(self, identifier: str, purpose: str = "login") -> dict:
        clean_id = identifier.strip()
        user = await self._find_user_by_identifier(clean_id)

        if not user:
            # Auto-provision user for seamless OTP authentication flow
            digits = "".join(c for c in clean_id if c.isdigit())
            if "@" in clean_id:
                user_email = clean_id.lower()
                user_phone = None
                user_name = clean_id.split("@")[0].replace(".", " ").title()
            else:
                user_phone = clean_id
                clean_phone_digits = digits[-10:] if len(digits) >= 10 else digits
                user_email = f"user_{clean_phone_digits}@99hectares.com"
                user_name = f"User {clean_phone_digits[-4:]}"

            # Check if auto-generated email happens to exist
            existing = await self.user_repo.get_by_email(user_email)
            if existing:
                user = existing
            else:
                user = User(
                    full_name=user_name,
                    email=user_email,
                    phone=user_phone,
                    password_hash=hash_password(secrets.token_urlsafe(16)),
                    role=UserRole.BUYER.value,
                    is_active=True,
                    is_verified=False,
                )
                user = await self.user_repo.create(user)
                await self.db.commit()

        otp = self._generate_otp(6)
        otp_record = OTPVerification(
            user_id=user.id,
            otp=otp,
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
        await self.auth_repo.create_otp(otp_record)
        await self.db.commit()

        await EmailService.send_template_email(
            to_email=settings.EMAIL,
            subject="99-Hectare OTP Code",
            template_name="emails/otp.html",
            context={
                "otp": otp,
                "expiry_minutes": 15,
            },
        )

        return {
            "otp": otp,
            "message": f"OTP successfully sent to {settings.EMAIL}",
            "identifier": identifier,
            "user_id": user.id,
        }

    async def verify_otp_auth(
        self,
        identifier: str,
        otp: str,
        full_name: str | None = None,
        role: str = "buyer",
    ) -> dict:
        clean_id = identifier.strip()
        user = await self._find_user_by_identifier(clean_id)
        if not user:
            raise NotFoundException("No account or OTP request found for this identifier. Please request OTP first.")

        otp_record = await self.auth_repo.get_latest_otp_for_user(user.id)
        if not otp_record:
            raise BadRequestException("No active OTP found. Please request a new OTP.")

        if otp_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise BadRequestException("OTP expired. Please request a new OTP.")

        if otp_record.otp != otp.strip():
            raise BadRequestException("Invalid OTP code. Please check and try again.")

        await self.auth_repo.mark_otp_verified(otp_record)
        user.is_verified = True

        if full_name and full_name.strip():
            user.full_name = full_name.strip()

        normalized_role = role.lower()
        if normalized_role in [r.value for r in UserRole]:
            user.role = normalized_role
            if normalized_role == UserRole.AGENT.value:
                existing_agent = await self.agent_repo.get_by_user_id(user.id)
                if not existing_agent:
                    self.db.add(Agent(user_id=user.id, phone=user.phone, email=user.email))
            elif normalized_role == UserRole.BUILDER.value:
                res = await self.db.execute(select(Builder).where(Builder.user_id == user.id))
                if not res.scalar_one_or_none():
                    self.db.add(Builder(user_id=user.id, company_name=user.full_name, phone=user.phone, email=user.email))

        await self.db.commit()
        user = await self.user_repo.get_by_id_with_profiles(user.id)
        return await self._generate_tokens(user)

    # ── Helpers ────────────────────────────────────────────────────

    async def _generate_tokens(self, user: User) -> dict:
        access = create_access_token(
            subject=str(user.id),
            claims={"role": user.role, "email": user.email},
        )
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
            "role": user.role,
            "user": user,
        }

    @staticmethod
    def _generate_otp(length: int = 6) -> str:
        return "".join(random.choices(string.digits, k=length))
