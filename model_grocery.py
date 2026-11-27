from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from database import Base

class GroceryItem(Base):
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    name_te = Column(String(200), nullable=True) # Telugu name
    name_hi = Column(String(200), nullable=True) # Hindi name
    
    category = Column(String(100), index=True, nullable=False) # pulses, grains, leafy_greens, vegetables, dairy, seeds
    standard_quantity = Column(String(50), default="1 kg")
    avg_price_inr = Column(Float, nullable=False) # e.g. 120.0 for 1kg Toor Dal
    
    is_staple = Column(Boolean, default=True)
    is_budget_hero = Column(Boolean, default=False) # High nutrition at lowest cost
    affordable_substitute_for = Column(String(200), nullable=True) # e.g. "Peanuts substitute for Almonds"
    nutritional_perks = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

