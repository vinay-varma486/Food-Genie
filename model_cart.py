from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base


class UserCart(Base):
    """Persistent personal food cart belonging to a single authenticated user."""
    __tablename__ = "user_carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    title = Column(String(200), default="My Food Cart", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("UserCartItem", back_populates="cart", cascade="all, delete-orphan", order_by="UserCartItem.id.asc()")


class UserCartItem(Base):
    """Individual saved food item with editable quantity, meal category, nutrition, and price estimate."""
    __tablename__ = "user_cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("user_carts.id", ondelete="CASCADE"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("food_items.id", ondelete="SET NULL"), nullable=True)

    food_name = Column(String(200), nullable=False)
    image_url = Column(String(500), nullable=True)
    meal_category = Column(String(60), default="Lunch", nullable=False)  # Breakfast, Morning Snack, Lunch, Evening Snacks, Dinner
    quantity = Column(Float, default=1.0, nullable=False)
    serving_size = Column(String(120), default="1 serving (100g)")

    calories_per_unit = Column(Float, default=0.0)
    protein_per_unit = Column(Float, default=0.0)
    carbs_per_unit = Column(Float, default=0.0)
    fat_per_unit = Column(Float, default=0.0)
    fiber_per_unit = Column(Float, default=0.0)
    estimated_price_inr_per_unit = Column(Float, default=0.0)
    price_type = Column(String(50), default="estimated_market_price")

    vitamins_summary = Column(JSON, nullable=True)
    minerals_summary = Column(JSON, nullable=True)
    health_benefits = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart = relationship("UserCart", back_populates="items")

