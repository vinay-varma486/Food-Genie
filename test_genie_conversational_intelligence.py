"""
Test Suite for Genie AI Conversational Intelligence, 12 Core User Scenarios,
and Weekly Budget-Based Diet Planner.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from init_db import init_db
from genie_ai_service import genie_ai
from ai_budget_planner import ai_budget_planner
from schema_diet_planner import AIDietPlanRequest

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    init_db_session = SessionLocal()
    init_db(init_db_session)
    init_db_session.close()
    session = SessionLocal()
    yield session
    session.close()

# Scenario 1: User says Hi -> Genie gives a friendly greeting
def test_scenario_1_user_says_hi(db):
    res = genie_ai.generate_friendly_response(db, query="Hi")
    assert ("hi" in res.summary.lower() or "hello" in res.summary.lower() or "😊" in res.summary)
    assert res.recommended_foods == []
    assert res.foods_to_avoid == []

# Scenario 2: User says How are you -> Genie responds naturally
def test_scenario_2_user_says_how_are_you(db):
    res = genie_ai.generate_friendly_response(db, query="How are you?")
    assert "great" in res.summary.lower() or "doing" in res.summary.lower()
    assert res.recommended_foods == []

# Scenario 3: User asks about iron -> Genie provides food recommendations with table
def test_scenario_3_user_asks_about_iron(db):
    res = genie_ai.generate_friendly_response(db, query="What foods are rich in iron?")
    assert len(res.recommended_foods) >= 20
    assert "|" in res.summary  # Contains structured markdown table
    assert "Protein" in res.summary
    assert "Calories" in res.summary
    assert "₹" in res.summary

# Scenario 4: User asks in Telugu -> Genie responds in Telugu
def test_scenario_4_user_asks_in_telugu(db):
    res = genie_ai.generate_friendly_response(db, query="హాయ్, జుట్టు రాలడం తగ్గడానికి ఏ ఆహారాలు తినాలి?")
    assert res.language == "te"
    assert ("జుట్టు" in res.summary or "ఆహారం" in res.summary or "ప్రోటీన్" in res.summary)

# Scenario 5: User asks in Hindi -> Genie responds in Hindi
def test_scenario_5_user_asks_in_hindi(db):
    res = genie_ai.generate_friendly_response(db, query="नमस्ते, बालों के लिए क्या खाना चाहिए?")
    assert res.language == "hi"
    assert ("बालों" in res.summary or "भोजन" in res.summary or "प्रोटीन" in res.summary)

# Scenario 6: User requests food prices -> Genie displays estimated prices
def test_scenario_6_user_requests_food_prices(db):
    res = genie_ai.generate_friendly_response(db, query="What is the price of high protein foods?")
    assert "₹" in res.summary
    for f in res.recommended_foods[:5]:
        assert f.estimated_price_inr > 0

# Scenario 7: User selects Weight Gain -> Genie asks for missing details (age, weight, height)
def test_scenario_7_user_selects_weight_gain(db):
    res_chat = genie_ai.generate_friendly_response(db, query="I want to gain weight.")
    s = res_chat.summary.lower()
    assert "weight" in s or "gain" in s
    assert any(k in s for k in ["age", "weight", "height"])

# Scenario 8: User selects Weight Loss -> Genie asks for missing details or adapts
def test_scenario_8_user_selects_weight_loss(db):
    res_chat = genie_ai.generate_friendly_response(db, query="I want to lose weight.")
    s = res_chat.summary.lower()
    assert "weight" in s or "loss" in s or "healthy" in s

# Scenario 9: User selects Maintain Weight -> Diet recommendations adapt
def test_scenario_9_user_selects_maintain_weight(db):
    res_chat = genie_ai.generate_friendly_response(db, query="maintain weight")
    assert "maintaining" in res_chat.summary.lower() or "fantastic" in res_chat.summary.lower()

# Scenario 10: User enters a weekly budget -> Genie generates a seven-day plan
def test_scenario_10_weekly_budget_seven_day_plan():
    req = AIDietPlanRequest(
        budget_inr=700.0,
        budget_duration="weekly",
        custom_days=7,
        health_goal="weight_gain",
        dietary_preference="vegetarian",
        number_of_people=1
    )
    plan = ai_budget_planner.generate_plan(req)
    assert len(plan.daily_plans) == 7
    days = [d.day_label for d in plan.daily_plans]
    assert any("Monday" in d for d in days)
    assert any("Sunday" in d for d in days)

# Scenario 11: Weekly plan -> Displays food quantities, prices and nutritional values
def test_scenario_11_weekly_plan_quantities_prices_nutrition():
    req = AIDietPlanRequest(
        budget_inr=700.0,
        budget_duration="weekly",
        health_goal="weight_gain",
        dietary_preference="vegetarian",
        number_of_people=1
    )
    plan = ai_budget_planner.generate_plan(req)
    day1 = plan.daily_plans[0]
    for mk, meal in day1.meals.items():
        assert meal.food_name
        assert meal.quantity
        assert meal.estimated_cost_inr > 0
        assert meal.nutrients.calories_kcal > 0
        assert meal.nutrients.protein_g > 0
        assert len(meal.nutrients.vitamins_and_minerals) > 0

# Scenario 12: Grocery planner -> Calculates estimated grocery expenditure
def test_scenario_12_grocery_planner_expenditure():
    req = AIDietPlanRequest(
        budget_inr=700.0,
        budget_duration="weekly",
        health_goal="weight_gain",
        dietary_preference="vegetarian",
        number_of_people=1
    )
    plan = ai_budget_planner.generate_plan(req)
    assert len(plan.weekly_grocery_list) > 0
    total_grocery = sum(item.total_cost_inr for item in plan.weekly_grocery_list)
    assert total_grocery > 0
    assert any("moong" in item.name.lower() or "dal" in item.name.lower() or "rice" in item.name.lower() for item in plan.weekly_grocery_list)

# Scenario 13: Simple greeting does not dump unsolicited diet plans in English
def test_scenario_13_diet_plan_followup_english(db):
    res = genie_ai.generate_friendly_response(db, query="Hi")
    assert "|" not in res.summary
    assert res.recommended_foods == []

# Scenario 14: Casual Telugu greeting responds naturally in Telugu without food dump
def test_scenario_14_diet_plan_followup_telugu(db):
    res = genie_ai.generate_friendly_response(db, query="హాయ్ ఎలా ఉన్నావు")
    assert res.language == "te"
    assert any("\u0C00" <= c <= "\u0C7F" for c in res.summary)
    assert res.recommended_foods == []

# Scenario 15: Casual Hindi greeting responds naturally in Hindi without food dump
def test_scenario_15_diet_plan_followup_hindi(db):
    res = genie_ai.generate_friendly_response(db, query="नमस्ते कैसे हो")
    assert res.language == "hi"
    assert any("\u0900" <= c <= "\u097F" for c in res.summary)
    assert res.recommended_foods == []

# Scenario 18: "What are you doing?" natural response
def test_scenario_18_what_are_you_doing(db):
    res = genie_ai.generate_friendly_response(db, query="What are you doing?")
    assert res.intent == "casual_activity"
    assert res.recommended_foods == []
    assert len(res.summary.strip()) > 10

# Scenario 19: "Suggest healthy breakfast" returns breakfast recommendations
def test_scenario_19_healthy_breakfast(db):
    res = genie_ai.generate_friendly_response(db, query="Suggest healthy breakfast")
    assert len(res.recommended_foods) >= 1
    assert len(res.summary.strip()) > 20

# Scenario 16: Vegetarian preference excludes non-veg foods like eggs
def test_scenario_16_vegetarian_filter(db):
    res = genie_ai.generate_friendly_response(db, query="I want vegetarian food rich in protein")
    food_names = [f.name.lower() for f in res.recommended_foods]
    assert not any("egg" in name for name in food_names)

# Scenario 17: Casual Goodbye has warm send-off and does not force diet plan
def test_scenario_17_casual_goodbye_no_forced_diet_plan(db):
    res = genie_ai.generate_friendly_response(db, query="Bye")
    assert "take care" in res.summary.lower() or "day" in res.summary.lower()
    assert "diet plan" not in res.summary.lower()

