from datetime import datetime

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    password: str
    role: str = "buyer"

    # Optional Agent/Dealer fields
    agency_name: str | None = None
    license_number: str | None = None
    rera_registration_number: str | None = None
    experience_years: int = 0

    # Optional Builder fields
    company_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    user: UserResponse | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class RequestOTPRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class MessageResponse(BaseModel):
    message: str


class BecomeAgentRequest(BaseModel):
    agency_name: str | None = None
    license_number: str | None = None
    rera_registration_number: str | None = None
    experience_years: int = 0
    phone: str | None = None
    website: str | None = None
    description: str | None = None
