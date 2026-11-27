from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: Optional[str] = None
    preferred_language: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterOTPResponse(BaseModel):
    status: str = "otp_sent"
    email: EmailStr
    full_name: Optional[str] = None
    requires_otp_verification: bool = True
    expires_in_seconds: int
    resend_cooldown_seconds: int
    message: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

    @field_validator("otp")
    @classmethod
    def otp_digits(cls, v: str) -> str:
        clean = (v or "").strip()
        if not clean.isdigit() or len(clean) != 6:
            raise ValueError("Please enter a valid 6-digit OTP code")
        return clean


class ResendOTPRequest(BaseModel):
    email: EmailStr
