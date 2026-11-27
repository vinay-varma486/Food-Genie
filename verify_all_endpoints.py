"""
Live Endpoint Verification Script: Tests every active API endpoint in FoodGenie
and cleans up any temporary test user records.
"""
import os
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from model_user import User

client = TestClient(app)


def test_endpoints():
    print("==================================================")
    print("Testing All FoodGenie API Endpoints")
    print("==================================================")

    # 1. Health & Status
    res = client.get("/health")
    assert res.status_code == 200, f"/health failed: {res.status_code}"
    print("PASS: GET /health -> 200 OK")

    res = client.get("/api/status")
    assert res.status_code == 200, f"/api/status failed: {res.status_code}"
    print("PASS: GET /api/status -> 200 OK")

    # 2. AI Health & Status Endpoints (report connected when online, graceful status otherwise)
    gem_res = client.get("/api/health/gemini")
    assert gem_res.status_code == 200
    print(f"PASS: GET /api/health/gemini -> {gem_res.json().get('status')}")

    or_res = client.get("/api/health/openrouter")
    assert or_res.status_code == 200
    print(f"PASS: GET /api/health/openrouter -> {or_res.json().get('status')}")

    status_res = client.get("/api/status")
    assert status_res.status_code == 200
    assert "ai_provider" in status_res.json()
    print(f"PASS: GET /api/status -> provider={status_res.json().get('ai_provider')}")

    # 3. Auth: Registration with Full Name, Email, Password, Confirm Password & Email OTP Verification
    import re
    from email_service import email_service
    orig_send_email = email_service.send_email
    captured_otp = []
    email_service.send_email = lambda to, subj, txt, html: captured_otp.extend(re.findall(r"\b(\d{6})\b", txt))

    test_email = f"audit_tester_{os.getpid()}@foodgenie.ai"
    try:
        reg_res = client.post("/api/v1/auth/register", json={
            "full_name": "Audit Tester",
            "email": test_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        assert reg_res.status_code in (200, 201), f"Register failed: {reg_res.text}"
        assert len(captured_otp) == 1
        print(f"PASS: POST /api/v1/auth/register (OTP sent) -> {reg_res.status_code}")

        ver_res = client.post("/api/v1/auth/verify-otp", json={
            "email": test_email,
            "otp": captured_otp[0]
        })
        assert ver_res.status_code == 200, f"OTP Verify failed: {ver_res.text}"
        print("PASS: POST /api/v1/auth/verify-otp -> 200 OK")
    finally:
        email_service.send_email = orig_send_email

    # 4. Auth: Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "Password123!"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("PASS: POST /api/v1/auth/login -> 200 OK")

    # 5. Auth: /me & Profile GET/PUT
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == test_email

    prof_res = client.get("/api/v1/profile/me", headers=headers)
    assert prof_res.status_code == 200

    up_res = client.put("/api/v1/profile/me", headers=headers, json={
        "full_name": "Audit Tester",
        "age": 26,
        "weight_kg": 62.0,
        "target_weight_kg": 68.0,
        "height_cm": 172.0,
        "health_goals": "weight_gain",
        "dietary_preference": "vegetarian",
        "allergies": ["Peanuts"]
    })
    assert up_res.status_code == 200, f"Profile update failed: {up_res.text}"
    assert up_res.json()["target_weight_kg"] == 68.0
    print("PASS: GET/PUT /api/v1/profile/me -> 200 OK")

    # 6. Chat Privacy Check (unauthenticated without session_id returns empty list)
    anon_hist = client.get("/api/v1/chat/history")
    assert anon_hist.status_code == 200
    assert anon_hist.json() == []
    print("PASS: GET /api/v1/chat/history (unauthenticated privacy check) -> []")

    # 7. Genie Conversational Endpoints (Hi, Healthy Breakfast, Telugu, Iron)
    sid = f"audit-session-{os.getpid()}"
    r_hi = client.post("/api/v1/recommendations/query", headers=headers, json={
        "query": "Hi", "session_id": sid
    })
    assert r_hi.status_code == 200
    assert r_hi.json()["recommended_foods"] == []

    r_bf = client.post("/api/v1/recommendations/query", headers=headers, json={
        "query": "Suggest healthy breakfast", "session_id": sid
    })
    assert r_bf.status_code == 200
    assert len(r_bf.json()["summary"]) > 20

    r_te = client.post("/api/v1/recommendations/query", headers=headers, json={
        "query": "నాకు జుట్టు రాలడం తగ్గడానికి ఆహారం చెప్పండి", "session_id": sid
    })
    assert r_te.status_code == 200
    assert r_te.json()["language"] == "te"
    print("PASS: POST /api/v1/recommendations/query (Greeting, Breakfast, Telugu) -> 200 OK")

    # 8. Nutrition Catalog & Saved Foods
    foods_res = client.get("/api/v1/nutrition/foods?limit=5")
    assert foods_res.status_code == 200
    food_id = foods_res.json()[0]["id"]

    save_food = client.post("/api/v1/nutrition/saved", headers=headers, json={"food_id": food_id, "notes": "Test"})
    assert save_food.status_code in (200, 201)
    assert len(client.get("/api/v1/nutrition/saved", headers=headers).json()) >= 1
    del_food = client.delete(f"/api/v1/nutrition/saved/{food_id}", headers=headers)
    assert del_food.status_code == 200
    print("PASS: Nutrition Catalog & Saved Foods CRUD -> 200 OK")

    # 8b. My Food Cart CRUD + PDF Export + Dashboard Overview
    c_add = client.post("/api/v1/cart/items", headers=headers, json={"food_id": food_id, "meal_category": "Breakfast", "quantity": 1})
    assert c_add.status_code == 200 and c_add.json()["totals"]["total_items"] == 1
    c_pdf = client.get("/api/v1/cart/pdf", headers=headers)
    assert c_pdf.status_code == 200 and c_pdf.content[:5] == b"%PDF-"
    dash_res = client.get("/api/v1/dashboard/overview?date_range=weekly&category=weight_loss", headers=headers)
    assert dash_res.status_code == 200
    print("PASS: My Food Cart CRUD, PDF Export & Dashboard Overview -> 200 OK")

    # 9. Budget Planner: Generate, Save, Update, List, Delete
    b_res = client.post("/api/v1/budget/ai-plan", headers=headers, json={
        "budget_inr": 1000.0,
        "budget_duration": "weekly",
        "dietary_preference": "vegetarian",
        "health_goal": "maintain_weight",
        "location": "Hyderabad"
    })
    assert b_res.status_code == 200
    plan_json = b_res.json()
    assert len(plan_json["daily_plans"]) == 7

    save_p = client.post("/api/v1/budget/ai-plan/save", headers=headers, json=plan_json)
    assert save_p.status_code == 200
    plan_id = save_p.json()["plan_id"]

    upd_p = client.put(f"/api/v1/budget/plans/{plan_id}", headers=headers, json={"title": "Updated Weekly Plan"})
    assert upd_p.status_code == 200

    del_p = client.delete(f"/api/v1/budget/plans/{plan_id}", headers=headers)
    assert del_p.status_code == 200
    print("PASS: Budget Planner Generate / Save / Update / Delete -> 200 OK")

    # 10. Restrictions & Doctors
    restr_res = client.post("/api/v1/recommendations/restrictions/analyze", json={
        "allergies": ["Peanuts"],
        "medical_conditions": ["Diabetes"],
        "language": "en"
    })
    assert restr_res.status_code == 200
    assert restr_res.json()["total_restrictions"] >= 2

    specs = client.get("/api/v1/doctors/specializations")
    assert specs.status_code == 200 and len(specs.json()) == 5
    docs = client.post("/api/v1/doctors/nearby", json={"city": "Hyderabad", "max_distance_km": 25.0})
    assert docs.status_code == 200 and docs.json()["total"] > 0
    print("PASS: Restrictions & Doctors Finder -> 200 OK")

    # 11. Logout & Account Cleanup
    out_res = client.post("/api/v1/auth/logout", headers=headers)
    assert out_res.status_code == 200
    del_acc = client.delete("/api/v1/profile/me", headers=headers)
    assert del_acc.status_code == 200
    print("PASS: Logout & Test User Cleanup -> 200 OK")

    db = SessionLocal()
    try:
        assert db.query(User).filter(User.email == test_email).first() is None
    finally:
        db.close()

    print("==================================================")
    print("ALL ENDPOINTS VERIFIED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    test_endpoints()
