from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from deps import get_db, get_current_user
from model_user import User
from schema_auth import LoginRequest, Token, RegisterOTPResponse, VerifyOTPRequest, ResendOTPRequest
from schema_user import UserCreate, UserResponse
from auth_service import (
    authenticate_user,
    register_new_user,
    verify_registration_otp,
    resend_registration_otp,
)
from email_service import email_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/email-status",
    summary="Check whether backend email OTP delivery provider is configured",
)
def get_email_provider_status():
    return email_service.provider_status()


@router.post(
    "/register",
    response_model=RegisterOTPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account and send email verification OTP",
    description="Creates an unactivated user account, securely hashes a 6-digit OTP, and emails it via the configured SMTP or Resend provider.",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return register_new_user(db, user_in)


@router.post(
    "/verify-otp",
    response_model=Token,
    summary="Verify email OTP and activate account",
    description="Validates the hashed 6-digit OTP, enforces expiry/attempt limits, activates the account, and returns a JWT session token.",
)
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    return verify_registration_otp(db, req.email, req.otp)


@router.post(
    "/resend-otp",
    response_model=RegisterOTPResponse,
    summary="Resend registration email OTP with cooldown protection",
)
def resend_otp(req: ResendOTPRequest, db: Session = Depends(get_db)):
    return resend_registration_otp(db, req.email)


@router.post(
    "/login",
    response_model=Token,
    summary="Login with registered email and password",
    description="Authenticates verified users with email and password, returning a JWT Bearer token.",
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return authenticate_user(db, login_data)


@router.post(
    "/logout",
    summary="Log out user and invalidate session",
)
def logout(current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "message": f"Successfully logged out user {current_user.email}",
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
