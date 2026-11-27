import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from config import settings
from crud_user import get_user_by_email, create_user
from security import verify_password, create_access_token, get_password_hash
from model_auth import EmailVerification
from model_user import User
from schema_auth import LoginRequest, Token, RegisterOTPResponse
from schema_user import UserCreate
from email_service import (
    email_service,
    EmailDeliveryNotConfiguredError,
    EmailDeliveryFailedError,
)


def _generate_otp_code() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


def _hash_otp(email: str, otp: str) -> str:
    msg = f"{email.strip().lower()}:{otp.strip()}".encode("utf-8")
    key = settings.SECRET_KEY.encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def _verify_otp_hash(email: str, otp: str, stored_hash: str) -> bool:
    expected = _hash_otp(email, otp)
    return hmac.compare_digest(expected, stored_hash or "")


def authenticate_user(db: Session, login_data: LoginRequest) -> Token:
    user = get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required. Please verify the OTP sent to your email address.",
        )

    preferred_lang = user.profile.preferred_language if user.profile else "en"
    token = create_access_token(user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        preferred_language=preferred_lang,
    )


def _dispatch_otp_record(
    db: Session,
    user: User,
    is_resend: bool = False,
) -> RegisterOTPResponse:
    now = datetime.utcnow()
    clean_email = user.email.strip().lower()
    cooldown = max(15, int(settings.OTP_RESEND_COOLDOWN_SECONDS or 60))
    expire_mins = max(1, int(settings.OTP_EXPIRE_MINUTES or 5))
    max_attempts = max(3, int(settings.OTP_MAX_ATTEMPTS or 5))
    max_per_hour = max(2, int(settings.OTP_MAX_REQUESTS_PER_HOUR or 5))

    latest: Optional[EmailVerification] = (
        db.query(EmailVerification)
        .filter(EmailVerification.user_id == user.id, EmailVerification.is_verified.is_(False))
        .order_by(EmailVerification.created_at.desc())
        .first()
    )

    requests_in_window = 1
    window_start = now
    resend_count = 0

    if latest:
        elapsed_since_send = (now - latest.last_sent_at).total_seconds()
        if elapsed_since_send < cooldown:
            wait_sec = int(cooldown - elapsed_since_send) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {wait_sec}s before requesting another verification OTP.",
                headers={"Retry-After": str(wait_sec)},
            )

        if (now - latest.window_started_at) < timedelta(hours=1):
            if latest.requests_in_window >= max_per_hour:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many OTP requests for this email. Please try again in an hour.",
                )
            requests_in_window = latest.requests_in_window + 1
            window_start = latest.window_started_at
        resend_count = latest.resend_count + (1 if is_resend else 0)

    otp_code = _generate_otp_code()
    otp_hash = _hash_otp(clean_email, otp_code)
    expires_at = now + timedelta(minutes=expire_mins)

    ver = EmailVerification(
        user_id=user.id,
        email=clean_email,
        otp_hash=otp_hash,
        expires_at=expires_at,
        attempts=0,
        max_attempts=max_attempts,
        resend_count=resend_count,
        requests_in_window=requests_in_window,
        window_started_at=window_start,
        last_sent_at=now,
        is_verified=False,
    )
    db.add(ver)

    try:
        email_service.send_otp_email(clean_email, user.full_name or "Friend", otp_code, expire_mins)
    except EmailDeliveryNotConfiguredError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except EmailDeliveryFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    db.commit()
    return RegisterOTPResponse(
        status="otp_sent",
        email=clean_email,
        full_name=user.full_name,
        requires_otp_verification=True,
        expires_in_seconds=expire_mins * 60,
        resend_cooldown_seconds=cooldown,
        message=f"A 6-digit verification OTP has been sent to {clean_email}.",
    )


def register_new_user(db: Session, user_in: UserCreate) -> RegisterOTPResponse:
    if len(user_in.password or "") < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")
    if user_in.confirm_password is not None and user_in.password != user_in.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    clean_email = user_in.email.strip().lower()
    existing = get_user_by_email(db, clean_email)

    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists",
            )
        # Update pending unverified user details cleanly & dispatch new OTP
        existing.hashed_password = get_password_hash(user_in.password)
        if user_in.full_name and user_in.full_name.strip():
            existing.full_name = user_in.full_name.strip()
        db.flush()
        return _dispatch_otp_record(db, existing, is_resend=False)

    user = create_user(db, user_in, is_active=False, commit=False)
    return _dispatch_otp_record(db, user, is_resend=False)


def verify_registration_otp(db: Session, email: str, otp: str) -> Token:
    clean_email = email.strip().lower()
    user = get_user_by_email(db, clean_email)
    if not user:
        raise HTTPException(status_code=404, detail="No pending registration found for this email.")
    if user.is_active:
        raise HTTPException(status_code=400, detail="Account is already verified. Please sign in with your password.")

    ver: Optional[EmailVerification] = (
        db.query(EmailVerification)
        .filter(EmailVerification.user_id == user.id, EmailVerification.is_verified.is_(False))
        .order_by(EmailVerification.created_at.desc())
        .first()
    )
    if not ver:
        raise HTTPException(status_code=400, detail="No active verification OTP found. Please request a new OTP.")

    now = datetime.utcnow()
    if now > ver.expires_at:
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new OTP.")

    if ver.attempts >= ver.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum incorrect OTP attempts reached. Please resend a new OTP.",
        )

    if not _verify_otp_hash(clean_email, otp, ver.otp_hash):
        ver.attempts += 1
        db.commit()
        remaining = max(0, ver.max_attempts - ver.attempts)
        if remaining == 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum incorrect OTP attempts reached. Please resend a new OTP.",
            )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid OTP code. {remaining} attempt(s) remaining.",
        )

    ver.is_verified = True
    ver.verified_at = now
    user.is_active = True
    db.commit()
    db.refresh(user)

    preferred_lang = user.profile.preferred_language if user.profile else "en"
    token = create_access_token(user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        preferred_language=preferred_lang,
    )


def resend_registration_otp(db: Session, email: str) -> RegisterOTPResponse:
    clean_email = email.strip().lower()
    user = get_user_by_email(db, clean_email)
    if not user:
        raise HTTPException(status_code=404, detail="No registration found for this email.")
    if user.is_active:
        raise HTTPException(status_code=400, detail="This account is already verified. Please sign in.")
    return _dispatch_otp_record(db, user, is_resend=True)
