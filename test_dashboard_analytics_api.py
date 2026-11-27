import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from model_nutrition import FoodItem
from model_dashboard import FoodLog, DashboardActivity


client = TestClient(app)


def test_dashboard_overview_empty_state_and_categories():
    sid = "dash_empty_test_session"
    res = client.get(f"/api/v1/dashboard/overview?date_range=weekly&category=all&session_id={sid}")
    assert res.status_code == 200
    data = res.json()

    assert data["date_range"] == "weekly"
    assert data["selected_category"] == "all"
    assert data["total_spent_card"]["value"] == 0.0
    assert data["total_calories_card"]["value"] == 0.0
    assert data["has_expense_logs"] is False
    assert data["has_nutrition_logs"] is False
    assert data["sugar_data_available"] is False

    # Check all 10 category options exist (All Categories + 9 specific categories)
    cat_ids = {c["id"] for c in data["categories_catalog"]}
    expected = {
        "all", "weight_loss", "weight_gain", "muscle_building", "healthy_diet",
        "low_budget", "high_protein", "vegetarian", "non_vegetarian", "general_nutrition"
    }
    assert expected.issubset(cat_ids)

    # Switch category to muscle_building and verify dynamic updates
    mb_res = client.get(f"/api/v1/dashboard/overview?date_range=daily&category=muscle_building&session_id={sid}&budget_override=6000")
    assert mb_res.status_code == 200
    mb_data = mb_res.json()
    assert mb_data["selected_category"] == "muscle_building"
    assert mb_data["budget_configured"] is True
    assert mb_data["monthly_budget_inr"] == 6000.0
    assert mb_data["daily_budget_inr"] == 200.0
    assert mb_data["active_category_info"]["recommend_professional_advice"] is True
    assert len(mb_data["category_recommended_foods"]) > 0
    assert len(mb_data["category_suggested_meals"]) == 5


def test_dashboard_log_meal_purchase_and_analytics_cleanup():
    sid = "dash_log_test_session"
    db = SessionLocal()
    food = db.query(FoodItem).first()
    db.close()
    assert food is not None

    try:
        # Log verified DB food without sugar -> sugar_data_available stays False
        post_res = client.post(
            "/api/v1/dashboard/logs",
            json={
                "food_id": food.id,
                "meal_type": "Breakfast",
                "entry_type": "meal",
                "servings": 1.0,
                "cost_inr": 25.0,
                "diet_category": "high_protein",
                "session_id": sid,
            },
        )
        assert post_res.status_code == 200
        logged = post_res.json()
        log_id = logged["id"]
        assert logged["cost_inr"] == 25.0
        assert logged["calories_kcal"] > 0

        ov = client.get(
            f"/api/v1/dashboard/overview?date_range=weekly&category=high_protein&session_id={sid}&budget_override=3000"
        )
        assert ov.status_code == 200
        ov_data = ov.json()
        assert ov_data["has_expense_logs"] is True
        assert ov_data["has_nutrition_logs"] is True
        assert ov_data["sugar_data_available"] is False
        assert ov_data["total_spent_card"]["value"] == 25.0
        assert ov_data["total_calories_card"]["value"] == logged["calories_kcal"]
        assert len(ov_data["recent_activity"]) >= 1
        assert len(ov_data["smart_insights"]) >= 1

        # Delete logged entry
        del_res = client.delete(f"/api/v1/dashboard/logs/{log_id}?session_id={sid}")
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "deleted"
    finally:
        db = SessionLocal()
        try:
            db.query(FoodLog).filter(FoodLog.session_id == sid).delete(synchronize_session=False)
            db.query(DashboardActivity).filter(DashboardActivity.session_id == sid).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()

