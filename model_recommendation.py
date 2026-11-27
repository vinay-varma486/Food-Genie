from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    query = Column(String(500), nullable=False)
    intent = Column(String(100), nullable=True) # e.g. hair_growth, iron_deficiency, muscle_building, budget_meal
    language = Column(String(10), default="en")
    
    summary = Column(Text, nullable=False)
    recommended_foods = Column(JSON, nullable=True) # Array of {name, benefit, portion}
    foods_to_avoid = Column(JSON, nullable=True)    # Array of {name, reason}
    cautions = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")

class DietPlan(Base):
    __tablename__ = "diet_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    title = Column(String(200), nullable=False)
    duration_type = Column(String(50), default="weekly") # daily, weekly, monthly
    budget_tier = Column(String(50), default="budget")   # budget, moderate, premium
    estimated_cost_inr = Column(Float, nullable=True)
    target_calories_daily = Column(Integer, default=2000)
    
    # Structured Meals breakdown stored in JSON
    # e.g., {"monday": {"breakfast": "Sprouted Moong + Ragi Malt", "lunch": "Brown Rice + Dal + Spinach", ...}}
    meals_plan_data = Column(JSON, nullable=False)
    grocery_checklist = Column(JSON, nullable=True)
    
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="diet_plans")

