from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class MealNutrients(BaseModel):
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    vitamins_and_minerals: List[str] = []


class MealAlternative(BaseModel):
    food_name: str
    cost_inr: float
    savings_inr: float
    reason: str


class PlannedMealItem(BaseModel):
    meal_type: str  # breakfast, morning_snack, lunch, evening_snack, dinner
    meal_label: str
    timing: Optional[str] = None
    food_name: str
    food_name_regional: Optional[str] = None
    quantity: str
    unit_price_inr: Optional[float] = None
    unit_label: Optional[str] = None
    estimated_cost_inr: float
    price_type: str = "estimated_market_price"
    nutrients: MealNutrients
    health_benefits: List[str] = []
    affordable_alternatives: List[MealAlternative] = []


class DayMealPlan(BaseModel):
    day_number: int
    day_label: str
    focus: str
    meals: Dict[str, PlannedMealItem]
    daily_cost_inr: float
    daily_calories: int
    daily_protein_g: float
    daily_carbs_g: float = 0.0
    daily_fat_g: float = 0.0
    daily_fiber_g: float = 0.0


class GroceryItemDetail(BaseModel):
    name: str
    name_regional: Optional[str] = None
    category: str
    quantity: str
    unit_price_inr: float
    total_cost_inr: float
    price_type: str = "verified_live_price"
    affordable_swap: Optional[str] = None


class BudgetTrackingSummary(BaseModel):
    total_budget_inr: float
    total_expenditure_inr: float
    remaining_budget_inr: float
    budget_adherence_percent: float
    status: str  # "on_budget", "budget_surplus", "recalculated_to_fit", "insufficient_budget", "over_budget_allowed"
    savings_achieved_inr: float
    category_breakdown: Dict[str, float]


class AIDietPlanRequest(BaseModel):
    budget_inr: float = 1000.0
    budget_duration: str = "weekly"  # "daily", "weekly", "monthly", "custom"
    custom_days: Optional[int] = 7
    location: str = "Hyderabad"
    dietary_preference: str = "vegetarian"  # "vegetarian", "non-vegetarian", "vegan", "flexitarian"
    health_goal: str = "general_vitality"  # "weight_gain", "weight_loss", "maintain_weight", "hair_health", "iron_boost", "general_vitality"
    allergies: List[str] = []
    number_of_people: int = 1
    allow_over_budget: bool = False
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    activity_level: Optional[str] = "moderate"
    language: str = "en"

    @field_validator("budget_inr")
    @classmethod
    def budget_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Budget must be greater than ₹0")
        return float(v)

    @field_validator("number_of_people")
    @classmethod
    def people_must_be_positive(cls, v: int) -> int:
        return max(1, min(int(v), 20))


class AIDietPlanUpdate(BaseModel):
    title: Optional[str] = None
    estimated_cost_inr: Optional[float] = None
    target_calories_daily: Optional[int] = None
    meals_plan_data: Optional[Any] = None
    grocery_checklist: Optional[Any] = None


class AIDietPlanResponse(BaseModel):
    id: Optional[int] = None
    title: str
    summary: str
    budget_duration: str
    days_count: int
    number_of_people: int
    location: str
    target_budget_inr: float
    total_expenditure_inr: float
    remaining_budget_inr: float
    daily_budget_per_person_inr: float
    daily_cost_per_person_inr: float
    weekly_estimated_cost_inr: float = 0.0
    monthly_estimated_cost_inr: float = 0.0
    avg_daily_calories: float = 0.0
    avg_daily_protein_g: float = 0.0
    avg_daily_carbs_g: float = 0.0
    avg_daily_fat_g: float = 0.0
    avg_daily_fiber_g: float = 0.0
    budget_status: str
    was_recalculated: bool = False
    recalculation_note: Optional[str] = None
    budget_insufficient: bool = False
    budget_limitation_note: Optional[str] = None
    daily_plans: List[DayMealPlan]
    weekly_grocery_list: List[GroceryItemDetail]
    monthly_grocery_list: List[GroceryItemDetail]
    budget_tracking: BudgetTrackingSummary
    local_mandi_notes: str
    price_verification_notice: str = "Prices marked 'verified_live_price' reflect regional mandi benchmark tables; meal preparation costs are estimated from standardized ICMR-NIN serving sizes."
    language: str
    created_at: Optional[datetime] = None
