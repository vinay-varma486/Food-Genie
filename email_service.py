"""
FoodGenie Email Delivery Service
Sends real verification OTP emails using configured backend environment variables
(SMTP with TLS/SSL or Resend HTTP API). Never exposes OTP codes in logs or API responses.
"""

import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import Dict, Any
import httpx
from config import settings

logger = logging.getLogger("foodgenie_email")


class EmailDeliveryNotConfiguredError(RuntimeError):
    """Raised when no legitimate email delivery provider is configured in .env."""


class EmailDeliveryFailedError(RuntimeError):
    """Raised when the configured email provider fails to accept/deliver the email."""


class EmailService:
    def provider_status(self) -> Dict[str, Any]:
        smtp_ready = bool(
            (settings.SMTP_HOST or "").strip()
            and (settings.SMTP_USER or "").strip()
            and (settings.SMTP_PASSWORD or "").strip()
        )
        resend_ready = bool(
            (settings.RESEND_API_KEY or "").strip()
            and "your-" not in (settings.RESEND_API_KEY or "").lower()
        )
        if resend_ready:
            return {"configured": True, "provider": "resend"}
        if smtp_ready:
            return {"configured": True, "provider": "smtp"}
        return {"configured": False, "provider": "unconfigured"}

    def is_configured(self) -> bool:
        return bool(self.provider_status()["configured"])

    def send_email(self, recipient_email: str, subject: str, text_body: str, html_body: str) -> None:
        status = self.provider_status()
        if not status["configured"]:
            raise EmailDeliveryNotConfiguredError(
                "Email delivery provider is not configured on the server. "
                "Please set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD (or RESEND_API_KEY) in .env."
            )

        if status["provider"] == "resend":
            self._send_via_resend(recipient_email, subject, text_body, html_body)
        else:
            self._send_via_smtp(recipient_email, subject, text_body, html_body)

    @staticmethod
    def _send_via_resend(recipient_email: str, subject: str, text_body: str, html_body: str) -> None:
        from_addr = (settings.RESEND_FROM_EMAIL or settings.SMTP_FROM_EMAIL or "FoodGenie <onboarding@resend.dev>").strip()
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY.strip()}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": from_addr,
                        "to": [recipient_email],
                        "subject": subject,
                        "text": text_body,
                        "html": html_body,
                    },
                )
                if res.status_code not in (200, 201, 202):
                    logger.error("Resend email delivery failed with HTTP %s", res.status_code)
                    raise EmailDeliveryFailedError(f"Email provider returned HTTP {res.status_code}.")
        except EmailDeliveryFailedError:
            raise
        except Exception as exc:
            logger.error("Resend request error: %s", type(exc).__name__)
            raise EmailDeliveryFailedError("Could not connect to email delivery provider.")

    @staticmethod
    def _send_via_smtp(recipient_email: str, subject: str, text_body: str, html_body: str) -> None:
        host = settings.SMTP_HOST.strip()
        port = int(settings.SMTP_PORT or 587)
        user = settings.SMTP_USER.strip()
        password = settings.SMTP_PASSWORD
        from_addr = (settings.SMTP_FROM_EMAIL or user).strip()

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = recipient_email
        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")

        try:
            context = ssl.create_default_context()
            if port == 465:
                with smtplib.SMTP_SSL(host, port, timeout=15, context=context) as server:
                    server.login(user, password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(host, port, timeout=15) as server:
                    server.ehlo()
                    if settings.SMTP_USE_TLS:
                        server.starttls(context=context)
                        server.ehlo()
                    server.login(user, password)
                    server.send_message(msg)
            logger.info("Verification email dispatched via SMTP to %s", recipient_email)
        except Exception as exc:
            logger.error("SMTP delivery failed (%s)", type(exc).__name__)
            raise EmailDeliveryFailedError("Failed to send verification email through SMTP server.")

    def send_otp_email(self, recipient_email: str, full_name: str, otp_code: str, expire_minutes: int) -> None:
        safe_name = (full_name or "Friend").strip()
        subject = "FoodGenie — Verify Your Email Address"
        text_body = (
            f"Hello {safe_name},\n\n"
            f"Your FoodGenie account verification code is: {otp_code}\n"
            f"This OTP expires in {expire_minutes} minutes.\n\n"
            "If you did not request this registration, please ignore this email.\n"
        )
        html_body = f"""
        <div style="font-family: 'Plus Jakarta Sans', Arial, sans-serif; background:#F2ECFF; padding:24px;">
          <div style="max-width:480px; margin:0 auto; background:#FFFFFF; border-radius:16px; border:1px solid #ADD8E6; overflow:hidden;">
            <div style="background:#351078; color:#FFFFFF; padding:20px 24px;">
              <h2 style="margin:0; font-size:20px;">Food<span style="color:#C6FF00;">Genie</span> Verification</h2>
            </div>
            <div style="padding:24px; color:#230852;">
              <p style="margin-top:0;">Hello <strong>{safe_name}</strong>,</p>
              <p>Use the verification code below to activate your FoodGenie account:</p>
              <div style="margin:20px 0; padding:16px; background:#F2ECFF; border:2px solid #ADD8E6; border-radius:12px; text-align:center;">
                <span style="font-size:28px; font-weight:800; letter-spacing:8px; color:#351078;">{otp_code}</span>
              </div>
              <p style="font-size:13px; color:#475569;">This OTP expires in <strong>{expire_minutes} minutes</strong>. Do not share it with anyone.</p>
            </div>
          </div>
        </div>
        """
        self.send_email(recipient_email, subject, text_body, html_body)


email_service = EmailService()
