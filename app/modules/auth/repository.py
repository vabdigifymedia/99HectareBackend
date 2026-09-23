from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import RefreshToken, OTPVerification


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Refresh Token ──────────────────────────────────────────────

    async def create_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.db.add(refresh_token)
        await self.db.flush()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,
            )
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: str) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(is_revoked=True)
        )
        await self.db.flush()

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
            )
            .values(is_revoked=True)
        )
        await self.db.flush()

    async def delete_expired_tokens(self) -> None:
        now = datetime.now(timezone.utc)
        await self.db.execute(
            select(RefreshToken).where(RefreshToken.expires_at < now)
        )
        await self.db.flush()

    # ── OTP ────────────────────────────────────────────────────────

    async def create_otp(self, otp_record: OTPVerification) -> OTPVerification:
        self.db.add(otp_record)
        await self.db.flush()
        await self.db.refresh(otp_record)
        return otp_record

    async def get_latest_otp(
        self, user_id: int, purpose: str
    ) -> OTPVerification | None:
        result = await self.db.execute(
            select(OTPVerification)
            .where(
                OTPVerification.user_id == user_id,
                OTPVerification.purpose == purpose,
                OTPVerification.is_verified == False,
            )
            .order_by(OTPVerification.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_otp_for_user(
        self, user_id: int, purpose: str | None = None
    ) -> OTPVerification | None:
        conditions = [
            OTPVerification.user_id == user_id,
            OTPVerification.is_verified == False,
        ]
        if purpose:
            conditions.append(OTPVerification.purpose == purpose)
        result = await self.db.execute(
            select(OTPVerification)
            .where(*conditions)
            .order_by(OTPVerification.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def mark_otp_verified(self, otp_record: OTPVerification) -> None:
        otp_record.is_verified = True
        await self.db.flush()

