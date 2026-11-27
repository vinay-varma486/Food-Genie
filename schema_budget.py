from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class BudgetPlanRequest(BaseModel):
    monthly_budget_inr: float = 4000.0
    family_members: int = 1
    dietary_preference: str = "vegetarian" # vegetarian, vegan, non-vegetarian
    language: str = "en"

class BudgetCategoryAllocation(BaseModel):
    category: str # Grains & Millets, Pulses & Legumes, Fresh Vegetables & Greens, Dairy / Soy, Fruits & Seeds, Spices & Oils
    allocated_inr: float
    percentage: float
    recommended_staples: List[str]

class BudgetPlanResponse(BaseModel):
    monthly_budget_inr: float
    per_person_day_inr: float
    dietary_preference: str
    tier: str # "Cost Saver", "Balanced Vitality", "Premium Wellness"
    categories: List[BudgetCategoryAllocation]
    money_saving_hacks: List[str]
    sample_weekly_cost_breakdown: Dict[str, float]
    language: str

