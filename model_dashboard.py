from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from database import Base


class FoodLog(Base):
    """Stores actual user-logged meals and food purchases for dashboard analytics."""
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    food_id = Column(Integer, ForeignKey("food_items.id", ondelete="SET NULL"), nullable=True)

    food_name = Column(String(200), nullable=False)
    food_category = Column(String(100), default="General Nutrition", index=True)
    diet_category = Column(String(60), default="general_nutrition", index=True)
    meal_type = Column(String(40), default="Lunch")  # Breakfast, Morning Snack, Lunch, Evening Snack, Dinner, Grocery Purchase
    entry_type = Column(String(20), default="meal")  # meal | purchase

    quantity_g = Column(Float, default=100.0)
    servings = Column(Float, default=1.0)
    cost_inr = Column(Float, default=0.0)

    # Verified / user-recorded nutritional amounts for this logged serving
    calories_kcal = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    fiber_g = Column(Float, default=0.0)
    sugar_g = Column(Float, nullable=True)  # Null unless explicitly provided (never invented)
    micronutrients_json = Column(JSON, nullable=True)  # e.g. {"Iron": {"amount": 2.7, "unit": "mg"}, ...}

    logged_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DashboardActivity(Base):
    """Stores timestamped user events: meals, purchases, budget & nutrition goal updates."""
    __tablename__ = "dashboard_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)

    activity_type = Column(String(50), nullable=False, index=True)  # meal_added | food_purchase | budget_update | nutrition_goal_update | plan_saved
    title = Column(String(200), nullable=False)
    subtitle = Column(String(300), nullable=True)
    amount_inr = Column(Float, nullable=True)
    calories_kcal = Column(Float, nullable=True)
    status = Column(String(40), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

