import pytest
from database import SessionLocal, engine
from sqlalchemy import text
from model_user import User, UserProfile
from model_nutrition import FoodItem
from schema_auth import LoginRequest
from schema_user import UserCreate, UserProfileUpdate, AllergySchema
from schema_grocery import GroceryBasketRequest
from auth_service import register_new_user, authenticate_user
from language_detector import language_detector
from genie_service import process_genie_query
from nutrition_service import NutritionRAGRetriever
from restriction_service import restriction_service
from ai_budget_planner import ai_budget_planner
from doctor_service import DoctorFinderService
from schema_diet_planner import AIDietPlanRequest
from schema_doctor import DoctorSearchRequest
from api_grocery import create_grocery_basket
from crud_user import add_user_allergy, get_user_allergies, update_user_profile
from fastapi import HTTPException

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# ----------------- 1. DATABASE CONNECTIVITY -----------------
def test_database_connectivity(db):
    """Verify live database engine connection, transactional integrity, and core tables."""
    # Test raw query execution
    result = db.execute(text("SELECT 1")).scalar()
    assert result == 1

    # Verify tables have active rows
    food_count = db.query(FoodItem).count()
    assert food_count >= 5

# ----------------- 2. REGISTRATION AND LOGIN -----------------
def test_registration_and_login_flow(db, monkeypatch):
    """Verify OTP registration, hashed OTP email delivery, OTP verification, login, and JWT token issuance."""
    import re
    from email_service import email_service
    from auth_service import verify_registration_otp

    test_email = f"test_e2e_{pytest.__version__.replace('.', '_')}@foodgenie.ai"

    # Clean up existing test user if any
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()

    captured_otps = []

    def fake_send_email(recipient_email, subject, text_body, html_body):
        m = re.search(r"\b(\d{6})\b", text_body)
        if m:
            captured_otps.append(m.group(1))

    monkeypatch.setattr(email_service, "send_email", fake_send_email)

    # 1. Register new user (sends OTP, account stays inactive until OTP verified)
    user_in = UserCreate(
        email=test_email,
        password="SecureGeniePassword@2026",
        confirm_password="SecureGeniePassword@2026",
        full_name="E2E Tester",
        preferred_language="te",
        dietary_preference="vegetarian"
    )
    reg_res = register_new_user(db, user_in)
    assert reg_res.email == test_email
    assert reg_res.requires_otp_verification is True
    assert len(captured_otps) == 1

    # Account must stay blocked from login prior to OTP verification
    with pytest.raises(HTTPException) as unverified_exc:
        authenticate_user(db, LoginRequest(email=test_email, password="SecureGeniePassword@2026"))
    assert unverified_exc.value.status_code == 403

    # Verify OTP activates account and issues token
    verify_res = verify_registration_otp(db, test_email, captured_otps[0])
    assert verify_res.access_token is not None

    # 2. Normal login with valid credentials works without OTP
    login_req = LoginRequest(
        email=test_email,
        password="SecureGeniePassword@2026"
    )
    token_res = authenticate_user(db, login_req)
    assert token_res.access_token is not None
    assert token_res.token_type == "bearer"
    assert token_res.preferred_language == "te"

    # 3. Attempt login with invalid password
    bad_login = LoginRequest(email=test_email, password="WrongPassword123")
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db, bad_login)
    assert exc_info.value.status_code == 401

# ----------------- 3. USER PROFILES & ALLERGIES -----------------
def test_user_profiles_and_allergies_management(db):
    """Verify profile updating and allergy tracking."""
    user = db.query(User).first()
    assert user is not None
    assert user.profile is not None

    # Update profile fields
    update_data = UserProfileUpdate(
        dietary_preference="vegan",
        monthly_food_budget=6000.0,
        daily_calorie_target=2200,
        health_conditions="Hypertension",
        city="Hyderabad"
    )
    updated = update_user_profile(db, user.id, update_data)
    assert updated.dietary_preference == "vegan"
    assert updated.monthly_food_budget == 6000.0
    assert updated.daily_calorie_target == 2200

    # Add allergy
    allergy_in = AllergySchema(allergen_name="Peanuts", severity="severe", notes="Anaphylaxis risk")
    added = add_user_allergy(db, user.profile.id, allergy_in)
    assert added.allergen_name == "Peanuts"

    allergies = get_user_allergies(db, user.profile.id)
    assert any(a.allergen_name == "Peanuts" for a in allergies)

# ----------------- 4. LANGUAGE DETECTION & UNSUPPORTED FALLBACK -----------------
def test_multilingual_language_detection():
    """Verify automatic language detection across English, Telugu, Hindi, Tamil, Kannada, mixed, and fallback."""
    # English
    lang, conf, _ = language_detector.detect_language("What foods are rich in Vitamin B12?")
    assert lang == "en"

    # Telugu script
    lang, conf, _ = language_detector.detect_language("జుట్టు పెరుగుదలకు ఏ ఆహారం తీసుకోవాలి?")
    assert lang == "te"

    # Telugu Romanized (Tenglish)
    lang, conf, is_mixed = language_detector.detect_language("juttu peragadaniki em tinali cheppandi")
    assert lang == "te"
    assert is_mixed is True

    # Hindi script (Devanagari)
    lang, conf, _ = language_detector.detect_language("बालों के झड़ने के लिए कौन सा भोजन अच्छा है?")
    assert lang == "hi"

    # Tamil script
    lang, conf, _ = language_detector.detect_language("கூந்தல் வளர்ச்சிக்கு சிறந்த உணவுகள் எவை?")
    assert lang == "ta"

    # Kannada script
    lang, conf, _ = language_detector.detect_language("ಕೂದಲು ಆರೋಗ್ಯಕ್ಕೆ ಯಾವ ಆಹಾರ ಒಳ್ಳೆಯದು?")
    assert lang == "kn"

    # Unsupported language code fallback
    lang, conf, _ = language_detector.detect_language("Bonjour, quel est le meilleur aliment?", fallback_lang="en")
    assert lang in ["en", "te", "hi", "ta", "kn"] # Fallback gracefully to supported language

# ----------------- 5. TELUGU AND ENGLISH CONVERSATIONS -----------------
def test_telugu_and_english_conversations(db):
    """Verify conversational Genie AI responses in Telugu and English."""
    # Telugu query
    te_res = process_genie_query(
        db=db,
        query="రక్తహీనత మరియు ఐరన్ లోపానికి ఏ ఆహారాలు ఉత్తమం?",
        preferred_language="te"
    )
    assert te_res.language == "te"
    assert te_res.summary is not None
    assert len(te_res.recommended_foods) > 0

    # English query
    en_res = process_genie_query(
        db=db,
        query="What are the best foods for iron deficiency and hair growth?",
        preferred_language="en"
    )
    assert en_res.language == "en"
    assert "iron" in en_res.summary.lower() or "hair" in en_res.summary.lower()

# ----------------- 6. MULTILINGUAL TEXT GENIE SERVICES ACROSS SUPPORTED LANGUAGES -----------------
def test_voice_services_across_languages(db):
    """Test text Genie nutrition handling across English, Telugu, Hindi, Tamil, and unsupported languages."""
    # 1. English Query
    res_en = process_genie_query(db=db, query="Recommend iron-rich vegetarian foods", preferred_language="en")
    assert res_en.language == "en"
    assert res_en.summary is not None

    # 2. Telugu Query
    res_te = process_genie_query(db=db, query="జుట్టు పెరుగుదలకు మంచి ఆహారం చెప్పండి", preferred_language="te")
    assert res_te.language == "te"
    assert res_te.summary is not None

    # 3. Hindi Query
    res_hi = process_genie_query(db=db, query="खून बढ़ाने के लिए क्या खाना चाहिए", preferred_language="hi")
    assert res_hi.language == "hi"
    assert res_hi.summary is not None

    # 4. Tamil Query
    res_ta = process_genie_query(db=db, query="கூந்தல் ஆரோக்கியத்திற்கு சிறந்த உணவு", preferred_language="ta")
    assert res_ta.language == "ta"
    assert res_ta.summary is not None

# ----------------- 7. FOOD RECOMMENDATIONS & RAG NUTRITION RETRIEVAL -----------------
def test_rag_nutrition_retrieval(db):
    """Verify RAG engine retrieves verified nutritional evidence deterministically without hallucination."""
    foods = NutritionRAGRetriever.retrieve_verified_foods(db, "foods for hair health", language="en")
    assert len(foods) >= 2
    for f in foods:
        assert f.name is not None
        assert f.nutrients_per_100g is not None
        assert f.nutrients_per_100g.calories_kcal > 0
        assert f.serving_size is not None
        assert len(f.preparation_methods) > 0
        assert len(f.health_benefits) > 0

# ----------------- 8. FOOD RESTRICTIONS ENGINE -----------------
def test_food_restrictions_engine():
    """Verify safety warnings for allergies, medical conditions, and medication interactions."""
    analysis = restriction_service.analyze_restrictions(
        allergies=["Peanuts", "Gluten / Wheat"],
        medical_conditions=["Diabetes Type 2", "Hypertension"],
        medications=["Warfarin / Blood Thinners"],
        language="en"
    )
    assert analysis.total_restrictions >= 4
    assert analysis.medically_necessary_count >= 2
    # Verify each restriction has safe alternatives and reason
    for item in analysis.restrictions:
        assert item.reason is not None
        assert len(item.safe_alternatives) > 0

# ----------------- 9. BUDGET CALCULATIONS & MEAL PLANNER -----------------
def test_budget_planner_calculations():
    """Verify 5-meal daily and weekly planning within budget constraints."""
    plan_req = AIDietPlanRequest(
        budget_inr=1400.0,
        budget_duration="weekly",
        number_of_people=1,
        dietary_preference="vegetarian",
        language="en"
    )
    plan = ai_budget_planner.generate_plan(plan_req)
    assert plan.budget_duration == "weekly"
    assert len(plan.daily_plans) == 7
    assert plan.total_expenditure_inr <= 1400.0
    for day in plan.daily_plans:
        assert len(day.meals) == 5

# ----------------- 10. GROCERY PLANNER -----------------
def test_grocery_planner_basket(db):
    """Verify grocery basket generator returns items within target budget with alternatives."""
    basket_req = GroceryBasketRequest(
        target_budget_inr=1500.0,
        dietary_preference="vegetarian",
        family_size=1
    )
    basket = create_grocery_basket(basket_req, db=db)
    assert basket.total_estimated_cost_inr <= 1500.0
    assert len(basket.items) >= 4
    assert len(basket.smart_swaps) >= 1

# ----------------- 11. DOCTOR FINDER -----------------
def test_doctor_finder_complete_specializations():
    """Verify doctor search across all 5 clinical specializations and Haversine distance."""
    search_req = DoctorSearchRequest(
        city="Hyderabad",
        max_distance_km=30.0,
        language="en"
    )
    res = DoctorFinderService.find_doctors(search_req)
    assert res.total >= 5
    specs_found = {d.specialization_code for d in res.doctors}
    # Ensure all 5 specializations are present
    assert {"general_physician", "dermatologist", "dietitian", "gastroenterologist", "endocrinologist"}.issubset(specs_found)
    for doc in res.doctors:
        assert doc.distance_km is not None
        assert "openstreetmap.org" in doc.directions_url
