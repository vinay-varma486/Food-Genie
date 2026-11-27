from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    scientific_name = Column(String(200), nullable=True)
    category = Column(String(100), index=True, nullable=False) # e.g. leafy green, legume, millet, dairy, fruit
    
    # Regional Names for Multilingual Genie
    name_te = Column(String(200), nullable=True) # Telugu name (e.g., పాలకూర, రాగులు)
    name_hi = Column(String(200), nullable=True) # Hindi name (e.g., पालक, रागी)
    
    # Macronutrients per 100g
    calories_kcal = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    fiber_g = Column(Float, default=0.0)
    glycemic_index = Column(Integer, nullable=True) # Low (<55), Medium (56-69), High (70+)
    
    # Serving & Preparation Details
    image_url = Column(String(500), nullable=True)
    serving_size = Column(String(100), default="100g")
    serving_weight_g = Column(Float, default=100.0)
    preparation_methods = Column(Text, nullable=True)
    preparation_methods_te = Column(Text, nullable=True)
    preparation_methods_hi = Column(Text, nullable=True)

    description = Column(Text, nullable=True)
    benefits_summary = Column(Text, nullable=True)
    cautions = Column(Text, nullable=True)
    verified_source = Column(String(200), default="ICMR-NIN Indian Food Composition Tables / USDA FoodData Central")

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    food_nutrients = relationship("FoodNutrient", back_populates="food_item", cascade="all, delete-orphan")
    saved_by_users = relationship("SavedFood", back_populates="food_item", cascade="all, delete-orphan")

class Nutrient(Base):
    __tablename__ = "nutrients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False) # e.g., Iron, Vitamin B12, Vitamin C
    nutrient_code = Column(String(50), nullable=True)                    # e.g., FE, B12, VITA
    category = Column(String(50), nullable=False)                       # vitamin, mineral, essential_fatty_acid
    daily_rda_adult = Column(Float, nullable=True)                      # e.g. 19.0 (mg) for Iron
    unit = Column(String(20), default="mg")                             # mg, mcg, g, IU
    physiological_role = Column(Text, nullable=True)

    food_nutrients = relationship("FoodNutrient", back_populates="nutrient", cascade="all, delete-orphan")

class FoodNutrient(Base):
    __tablename__ = "food_nutrients"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    nutrient_id = Column(Integer, ForeignKey("nutrients.id", ondelete="CASCADE"), nullable=False)
    amount_per_100g = Column(Float, nullable=False)
    unit = Column(String(20), default="mg")
    percent_daily_value = Column(Float, nullable=True)

    food_item = relationship("FoodItem", back_populates="food_nutrients")
    nutrient = relationship("Nutrient", back_populates="food_nutrients")

class SavedFood(Base):
    __tablename__ = "saved_foods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_id = Column(Integer, ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_foods")
    food_item = relationship("FoodItem", back_populates="saved_by_users")

