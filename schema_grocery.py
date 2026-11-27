from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class GroceryItemBase(BaseModel):
    name: str
    name_te: Optional[str] = None
    name_hi: Optional[str] = None
    category: str
    standard_quantity: str = "1 kg"
    avg_price_inr: float
    is_staple: bool = True
    is_budget_hero: bool = False
    affordable_substitute_for: Optional[str] = None
    nutritional_perks: Optional[str] = None

class GroceryItemResponse(GroceryItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class GroceryBasketRequest(BaseModel):
    target_budget_inr: float = 1200.0 # for weekly basket
    dietary_preference: str = "vegetarian"
    family_size: int = 1
    language: str = "en"

class GroceryBasketResponse(BaseModel):
    total_estimated_cost_inr: float
    budget_limit_inr: float
    savings_vs_premium_inr: float
    items_count: int
    items: List[GroceryItemResponse]
    smart_swaps: List[dict] # e.g. [{"swap_from": "Almonds", "swap_to": "Roasted Peanuts", "savings": "70%"}]
    language: str

