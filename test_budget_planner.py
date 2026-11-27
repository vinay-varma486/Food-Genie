import pytest
from ai_budget_planner import ai_budget_planner, MEAL_TEMPLATES_LIBRARY
from schema_diet_planner import AIDietPlanRequest, AIDietPlanResponse
from api_budget import generate_ai_budget_diet

def test_meal_templates_library_integrity():
    """Verify that all meal templates have all 5 meals with nutrients, benefits, and costs."""
    assert len(MEAL_TEMPLATES_LIBRARY) >= 3
    required_meals = ["breakfast", "morning_snack", "lunch", "evening_snack", "dinner"]
    
    for tmpl in MEAL_TEMPLATES_LIBRARY:
        assert "id" in tmpl
        assert "focus_en" in tmpl
        assert "focus_te" in tmpl
        assert "focus_hi" in tmpl
        assert "meals" in tmpl
        for rm in required_meals:
            assert rm in tmpl["meals"]
            m = tmpl["meals"][rm]
            assert "name_en" in m
            assert "name_te" in m
            assert "portion_base" in m
            assert m["cost_base"] > 0
            assert m["kcal"] > 0
            assert m["protein"] >= 0
            assert len(m["vitamins_minerals"]) > 0
            assert len(m["benefits_en"]) > 0
            assert m["price_type"] in ["verified_live_price", "estimated_market_price"]

def test_daily_budget_plan():
    """Verify 1-day daily budget plan generation with all 5 meals."""
    req = AIDietPlanRequest(
        budget_inr=300.0,
        budget_duration="daily",
        number_of_people=1,
        location="Hyderabad",
        dietary_preference="vegetarian",
        language="en"
    )
    plan = ai_budget_planner.generate_plan(req)
    assert plan.days_count == 1
    assert plan.budget_duration == "daily"
    assert len(plan.daily_plans) == 1
    
    day1 = plan.daily_plans[0]
    assert len(day1.meals) == 5
    for meal_key in ["breakfast", "morning_snack", "lunch", "evening_snack", "dinner"]:
        assert meal_key in day1.meals
        m = day1.meals[meal_key]
        assert m.food_name is not None
        assert m.quantity is not None
        assert m.estimated_cost_inr > 0
        assert m.nutrients.calories_kcal > 0
        assert len(m.nutrients.vitamins_and_minerals) > 0
        assert len(m.health_benefits) > 0

def test_weekly_budget_and_grocery_lists():
    """Verify 7-day weekly budget plan and weekly grocery list with verified prices."""
    req = AIDietPlanRequest(
        budget_inr=1500.0,
        budget_duration="weekly",
        number_of_people=2,
        location="Hyderabad",
        dietary_preference="vegetarian",
        language="en"
    )
    plan = ai_budget_planner.generate_plan(req)
    assert plan.days_count == 7
    assert len(plan.daily_plans) == 7
    assert plan.number_of_people == 2
    
    # Weekly grocery checklist
    assert len(plan.weekly_grocery_list) >= 5
    for item in plan.weekly_grocery_list:
        assert item.name is not None
        assert item.category is not None
        assert item.total_cost_inr > 0
        assert item.price_type in ["verified_live_price", "estimated_market_price"]

    # Monthly grocery list
    assert len(plan.monthly_grocery_list) >= 4

def test_over_budget_auto_recalculation():
    """Verify that when initial meal cost slightly exceeds target budget, the system auto-recalculates to fit."""
    req = AIDietPlanRequest(
        budget_inr=600.0,
        budget_duration="weekly",
        number_of_people=1,
        location="Hyderabad",
        language="en"
    )
    plan = ai_budget_planner.generate_plan(req)
    assert plan.was_recalculated is True
    assert plan.recalculation_note is not None
    assert plan.budget_tracking.savings_achieved_inr > 0
    assert plan.budget_status == "recalculated_to_fit"
    assert plan.total_expenditure_inr <= 600.0


def test_insufficient_budget_limitation_note():
    """Verify honest limitation explanation when budget is below minimum realistic meal cost."""
    req = AIDietPlanRequest(
        budget_inr=150.0,
        budget_duration="weekly",
        number_of_people=2,
        location="Hyderabad",
        language="en"
    )
    plan = ai_budget_planner.generate_plan(req)
    assert plan.budget_insufficient is True
    assert plan.budget_status == "insufficient_budget"
    assert plan.budget_limitation_note is not None
    assert plan.avg_daily_carbs_g > 0
    assert plan.avg_daily_fat_g > 0

def test_family_size_scaling():
    """Verify that costs and meal quantities properly scale with family size."""
    req1 = AIDietPlanRequest(budget_inr=5000.0, budget_duration="monthly", number_of_people=1, location="Hyderabad")
    req4 = AIDietPlanRequest(budget_inr=15000.0, budget_duration="monthly", number_of_people=4, location="Hyderabad")
    
    plan1 = ai_budget_planner.generate_plan(req1)
    plan4 = ai_budget_planner.generate_plan(req4)
    
    # Day 1 lunch cost for 4 people should be ~4x that of 1 person
    lunch1 = plan1.daily_plans[0].meals["lunch"].estimated_cost_inr
    lunch4 = plan4.daily_plans[0].meals["lunch"].estimated_cost_inr
    assert lunch4 == pytest.approx(lunch1 * 4, rel=1e-2)

def test_allergy_filtering():
    """Verify that user allergies are excluded from meals."""
    req = AIDietPlanRequest(
        budget_inr=2000.0,
        budget_duration="weekly",
        number_of_people=1,
        allergies=["Peanuts"],
        language="en"
    )
    plan = ai_budget_planner.generate_plan(req)
    # Check evening snack (which usually has peanuts) is swapped
    evening_snack = plan.daily_plans[0].meals["evening_snack"]
    assert "peanut" not in evening_snack.food_name.lower() or "swap" in evening_snack.food_name.lower() or "sunflower" in evening_snack.food_name.lower()

def test_multilingual_telugu_diet_plan():
    """Verify complete Telugu localization of plan title, meals, and focus."""
    req = AIDietPlanRequest(
        budget_inr=1200.0,
        budget_duration="weekly",
        number_of_people=1,
        location="Hyderabad",
        language="te"
    )
    plan = ai_budget_planner.generate_plan(req)
    assert plan.language == "te"
    assert "ప్లాన్" in plan.title or "రోజు" in plan.title
    
    day1 = plan.daily_plans[0]
    assert any('\u0C00' <= c <= '\u0C7F' for c in day1.day_label)
    assert any('\u0C00' <= c <= '\u0C7F' for c in day1.meals["breakfast"].food_name)
    assert any('\u0C00' <= c <= '\u0C7F' for c in day1.meals["breakfast"].health_benefits[0])

def test_api_endpoint_generate_ai_budget_diet():
    """Verify the FastAPI endpoint generate_ai_budget_diet."""
    req = AIDietPlanRequest(
        budget_inr=1000.0,
        budget_duration="weekly",
        number_of_people=1,
        location="Hyderabad",
        dietary_preference="vegetarian",
        health_goal="hair_health",
        language="en"
    )
    res = generate_ai_budget_diet(req)
    assert isinstance(res, AIDietPlanResponse)
    assert res.days_count == 7
    assert len(res.daily_plans) == 7
    assert res.total_expenditure_inr > 0
    assert len(res.weekly_grocery_list) > 0
    assert "verified_live_price" in res.price_verification_notice

