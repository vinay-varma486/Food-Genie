import pytest
from database import SessionLocal
from model_user import User, UserProfile
from model_nutrition import FoodItem
from crud_chat import record_chat_message, get_chat_history, delete_chat_history
from crud_nutrition import save_food_for_user, get_saved_foods_by_user, remove_saved_food
from crud_diet import save_diet_plan, get_diet_plans_by_user, delete_diet_plan
from crud_user import update_user_profile
from schema_user import UserProfileUpdate
from api_chat import clear_user_chat_history
from api_budget import get_user_saved_diet_plans, delete_user_diet_plan
from api_nutrition import delete_saved_food

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_delete_chat_history_crud_and_endpoint(db):
    """Verify chat history creation, retrieval, and deletion for session/user."""
    test_session = "test-session-dashboard-123"
    
    # 1. Record 2 sample chat messages
    msg1 = record_chat_message(
        db=db,
        user_query="Best high-protein foods for vegetarian diet?",
        genie_response="Sprouted green gram, paneer, and lentils are optimal.",
        language_code="en",
        session_id=test_session,
        intent="muscle_building"
    )
    msg2 = record_chat_message(
        db=db,
        user_query="How much iron is in spinach?",
        genie_response="Spinach has approximately 2.7mg iron per 100g.",
        language_code="en",
        session_id=test_session,
        intent="iron_deficiency"
    )
    
    # Verify retrieval
    history = get_chat_history(db, session_id=test_session)
    assert len(history) >= 2
    
    # 2. Test deletion via API endpoint function
    result = clear_user_chat_history(session_id=test_session, db=db, current_user=None)
    assert result["status"] == "cleared"
    assert result["deleted_messages"] >= 2
    
    # Verify records are gone
    remaining = get_chat_history(db, session_id=test_session)
    assert len(remaining) == 0

def test_save_and_delete_saved_food(db):
    """Verify bookmarking and removing a food item."""
    # Ensure a food item exists
    food = db.query(FoodItem).first()
    if not food:
        food = FoodItem(name="Test Moong", category="legume", calories_kcal=100)
        db.add(food)
        db.commit()
        db.refresh(food)

    # Use a dummy user_id
    user = db.query(User).first()
    if not user:
        user = User(email="dash_test@foodgenie.ai", hashed_password="hashed_pw_test")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 1. Save food for user
    saved = save_food_for_user(db, user_id=user.id, food_id=food.id, notes="Great source of bio-protein")
    assert saved.id is not None
    assert saved.food_id == food.id

    # 2. Retrieve saved foods
    saved_list = get_saved_foods_by_user(db, user_id=user.id)
    assert any(s.food_id == food.id for s in saved_list)

    # 3. Test removal endpoint function
    del_result = delete_saved_food(food_id=food.id, db=db, current_user=user)
    assert del_result["status"] == "removed"

    # Verify no longer in user's saved list
    after_list = get_saved_foods_by_user(db, user_id=user.id)
    assert not any(s.food_id == food.id for s in after_list)

def test_save_and_delete_diet_plan(db):
    """Verify saving a diet plan to user account, retrieving it, and deleting it."""
    user = db.query(User).first()
    if not user:
        user = User(email="dash_diet_user@foodgenie.ai", hashed_password="hashed_pw_test")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 1. Save diet plan
    sample_meals = {
        "day_1": {
            "breakfast": "Sprouted Moong + Ragi Malt",
            "lunch": "Brown Rice + Dal Palak"
        }
    }
    sample_grocery = [{"item_name": "Moong Dal", "quantity": "1 kg", "estimated_cost_inr": 140}]
    
    plan = save_diet_plan(
        db=db,
        title="Dashboard Test Weekly Plan",
        duration_type="weekly",
        budget_tier="within_budget",
        estimated_cost_inr=1050.0,
        target_calories=2000,
        meals_data=sample_meals,
        grocery_checklist=sample_grocery,
        language="en",
        user_id=user.id
    )
    assert plan.id is not None

    # 2. Retrieve plans via endpoint function
    plans = get_user_saved_diet_plans(db=db, current_user=user)
    assert any(p["id"] == plan.id for p in plans)

    # 3. Delete plan via endpoint function
    del_res = delete_user_diet_plan(plan_id=plan.id, db=db, current_user=user)
    assert del_res["status"] == "deleted"

    # Verify gone
    after_plans = get_diet_plans_by_user(db, user.id)
    assert not any(p.id == plan.id for p in after_plans)

def test_user_profile_crud_update(db):
    """Verify updating dietary preference, budget, and calorie goals in user profile."""
    user = db.query(User).first()
    if not user:
        user = User(email="profile_test@foodgenie.ai", hashed_password="hashed_pw_test")
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.profile:
        profile = UserProfile(user_id=user.id, preferred_language="en", dietary_preference="vegetarian")
        db.add(profile)
        db.commit()
        db.refresh(user)

    # Update profile
    update_data = UserProfileUpdate(
        dietary_preference="vegan",
        monthly_food_budget=6500.0,
        daily_calorie_target=2100,
        health_conditions="None",
        city="Bengaluru"
    )
    updated = update_user_profile(db, user.id, update_data)
    assert updated.dietary_preference == "vegan"
    assert updated.monthly_food_budget == 6500.0
    assert updated.daily_calorie_target == 2100
    assert updated.city == "Bengaluru"

