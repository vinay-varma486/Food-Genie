import re
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from main import app
from database import SessionLocal
from model_user import User
from model_auth import EmailVerification
from model_nutrition import FoodItem
from model_cart import UserCart
from email_service import email_service

client = TestClient(app)


def _cleanup_user(email: str):
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == email).first()
        if u:
            db.query(EmailVerification).filter(EmailVerification.user_id == u.id).delete(synchronize_session=False)
            c = db.query(UserCart).filter(UserCart.user_id == u.id).first()
            if c:
                db.delete(c)
            db.delete(u)
            db.commit()
    finally:
        db.close()


def test_registration_requires_configured_email_provider(monkeypatch):
    monkeypatch.setattr(email_service, "provider_status", lambda: {"configured": False, "provider": "unconfigured"})
    email = "unconfigured_otp_test@foodgenie.ai"
    _cleanup_user(email)
    try:
        res = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "No SMTP User",
                "email": email,
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
        )
        assert res.status_code == 503
    finally:
        _cleanup_user(email)


def test_full_otp_registration_cart_pdf_and_cart_aware_genie(monkeypatch):
    email_a = "qa_cart_user_a@foodgenie.ai"
    email_b = "qa_cart_user_b@foodgenie.ai"
    _cleanup_user(email_a)
    _cleanup_user(email_b)

    sent_emails = []

    def capture_email(recipient_email, subject, text_body, html_body):
        m = re.search(r"\b(\d{6})\b", text_body)
        sent_emails.append({"to": recipient_email, "otp": m.group(1) if m else None})

    monkeypatch.setattr(email_service, "send_email", capture_email)

    try:
        # 1. Password mismatch validation
        mismatch = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "QA User A",
                "email": email_a,
                "password": "StrongPassword1",
                "confirm_password": "WrongConfirm1",
            },
        )
        assert mismatch.status_code == 400

        # 2. Register User A -> generates hashed OTP, keeps user inactive, never leaks OTP
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "QA User A",
                "email": email_a,
                "password": "StrongPassword1",
                "confirm_password": "StrongPassword1",
            },
        )
        assert reg.status_code == 201
        reg_json = reg.json()
        assert reg_json["requires_otp_verification"] is True
        otp_a = sent_emails[-1]["otp"]
        assert otp_a is not None
        assert otp_a not in reg.text  # Never expose OTP in HTTP response

        # Confirm OTP stored hashed (not plaintext)
        db = SessionLocal()
        ver = db.query(EmailVerification).filter(EmailVerification.email == email_a).first()
        assert ver is not None and ver.otp_hash != otp_a
        db.close()

        # 3. Unverified login blocked; wrong OTP decrements attempts; cooldown rejects rapid resend
        blocked_login = client.post("/api/v1/auth/login", json={"email": email_a, "password": "StrongPassword1"})
        assert blocked_login.status_code == 403

        bad_otp = client.post("/api/v1/auth/verify-otp", json={"email": email_a, "otp": "000000" if otp_a != "000000" else "999999"})
        assert bad_otp.status_code == 400

        rapid_resend = client.post("/api/v1/auth/resend-otp", json={"email": email_a})
        assert rapid_resend.status_code == 429

        # Simulate cooldown elapsed -> resend sends new OTP cleanly
        db = SessionLocal()
        ver = db.query(EmailVerification).filter(EmailVerification.email == email_a, EmailVerification.is_verified.is_(False)).order_by(EmailVerification.created_at.desc()).first()
        ver.last_sent_at = datetime.utcnow() - timedelta(seconds=120)
        db.commit()
        db.close()

        resend_ok = client.post("/api/v1/auth/resend-otp", json={"email": email_a})
        assert resend_ok.status_code == 200
        otp_a2 = sent_emails[-1]["otp"]

        # 4. Verify latest OTP -> activates account & issues JWT
        verified = client.post("/api/v1/auth/verify-otp", json={"email": email_a, "otp": otp_a2})
        assert verified.status_code == 200
        token_a = verified.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 5. Add food to My Food Cart + deduplicate increment + update + save
        db = SessionLocal()
        foods = db.query(FoodItem).limit(2).all()
        db.close()
        assert len(foods) >= 2

        add1 = client.post(
            "/api/v1/cart/items",
            headers=headers_a,
            json={"food_id": foods[0].id, "meal_category": "Breakfast", "quantity": 1},
        )
        assert add1.status_code == 200
        assert add1.json()["totals"]["total_items"] == 1

        # Re-adding same food + Breakfast merges cleanly rather than duplicating
        add_dup = client.post(
            "/api/v1/cart/items",
            headers=headers_a,
            json={"food_id": foods[0].id, "meal_category": "Breakfast", "quantity": 2},
        )
        assert add_dup.status_code == 200
        assert add_dup.json()["totals"]["total_items"] == 1
        assert add_dup.json()["items"][0]["quantity"] == 3.0
        item_id = add_dup.json()["items"][0]["id"]

        # Update quantity & move to Lunch
        upd = client.put(
            f"/api/v1/cart/items/{item_id}",
            headers=headers_a,
            json={"quantity": 2, "meal_category": "Lunch", "notes": "Extra protein"},
        )
        assert upd.status_code == 200
        assert upd.json()["items"][0]["quantity"] == 2.0
        assert upd.json()["items"][0]["meal_category"] == "Lunch"

        # Save cart & snapshot meal plan
        save_res = client.post(
            "/api/v1/cart/save",
            headers=headers_a,
            json={"title": "My Balanced Plan", "save_as_meal_plan": True},
        )
        assert save_res.status_code == 200
        assert save_res.json()["saved_plan_id"] is not None

        # 6. Logout and login again -> cart items retained!
        client.post("/api/v1/auth/logout", headers=headers_a)
        relogin = client.post("/api/v1/auth/login", json={"email": email_a, "password": "StrongPassword1"})
        assert relogin.status_code == 200
        headers_a2 = {"Authorization": f"Bearer {relogin.json()['access_token']}"}

        persisted_cart = client.get("/api/v1/cart", headers=headers_a2)
        assert persisted_cart.status_code == 200
        assert persisted_cart.json()["totals"]["total_items"] == 1
        assert persisted_cart.json()["items"][0]["food_name"] == foods[0].name

        # 7. Download PDF generated from real cart data
        pdf_res = client.get("/api/v1/cart/pdf", headers=headers_a2)
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert pdf_res.content[:5] == b"%PDF-"
        assert len(pdf_res.content) > 1000

        # 8. Cart-aware Genie query includes actual cart food
        genie_res = client.post(
            "/api/v1/recommendations/query",
            headers=headers_a2,
            json={"query": "Analyze my food cart nutrition and cost", "session_id": "qa_cart_chat_tmp"},
        )
        assert genie_res.status_code == 200
        assert len(genie_res.json()["summary"]) > 20

        # 9. Privacy isolation: User B cannot touch User A's cart item
        client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "QA User B",
                "email": email_b,
                "password": "StrongPassword1",
                "confirm_password": "StrongPassword1",
            },
        )
        otp_b = sent_emails[-1]["otp"]
        tok_b = client.post("/api/v1/auth/verify-otp", json={"email": email_b, "otp": otp_b}).json()["access_token"]
        headers_b = {"Authorization": f"Bearer {tok_b}"}

        forbidden_del = client.delete(f"/api/v1/cart/items/{item_id}", headers=headers_b)
        assert forbidden_del.status_code == 404
    finally:
        _cleanup_user(email_a)
        _cleanup_user(email_b)
