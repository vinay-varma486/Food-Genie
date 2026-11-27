from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    saved_foods = relationship("SavedFood", back_populates="user", cascade="all, delete-orphan")
    diet_plans = relationship("DietPlan", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Language Preference (en, te, hi, ta, kn)
    preferred_language = Column(String(10), default="en", nullable=False)
    
    # Dietary & Health Attributes
    dietary_preference = Column(String(50), default="vegetarian")  # vegetarian, vegan, flexitarian, non-vegetarian
    budget_mode = Column(String(50), default="moderate")           # budget, moderate, premium
    monthly_food_budget = Column(Float, nullable=True, default=5000.0) # In INR / local currency
    
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    weight_kg = Column(Float, nullable=True)
    target_weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    activity_level = Column(String(50), default="moderate")        # sedentary, light, moderate, active
    daily_calorie_target = Column(Integer, default=2000)
    
    # Health Goals & Conditions
    health_goals = Column(Text, nullable=True)        # JSON or comma-separated: hair_health, iron_boost, muscle_gain, etc.
    health_conditions = Column(Text, nullable=True)   # JSON or comma-separated: diabetes, hypertension, pcos, anemia, none

    # Location for doctor finder
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")
    allergies = relationship("Allergy", back_populates="profile", cascade="all, delete-orphan")

class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    allergen_name = Column(String(100), nullable=False)      # e.g., Peanuts, Lactose, Gluten, Shellfish
    severity = Column(String(50), default="moderate")        # mild, moderate, severe
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="allergies")

