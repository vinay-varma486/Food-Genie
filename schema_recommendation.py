from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

class NutrientDetail(BaseModel):
    name: str
    category: str # vitamin, mineral, macronutrient
    amount_per_100g: float
    amount_per_serving: float
    unit: str
    percent_daily_value: Optional[float] = None

class MacroBreakdown(BaseModel):
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float

class RecommendedFoodItem(BaseModel):
    id: Optional[int] = None
    name: str
    name_te: Optional[str] = None
    name_hi: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    meal_category: Optional[str] = None
    serving_size: str = "100g"
    serving_weight_g: float = 100.0
    estimated_price_inr: float = 15.0
    price_type: str = "estimated_market_price"
    how_to_consume: Optional[str] = None
    benefit: str
    health_benefits: List[str] = []
    nutrients_per_100g: Optional[MacroBreakdown] = None
    nutrients_per_serving: Optional[MacroBreakdown] = None
    vitamins: List[NutrientDetail] = []
    minerals: List[NutrientDetail] = []
    preparation_methods: Optional[str] = None
    cautions: Optional[str] = None
    verified_source: str = "ICMR-NIN Indian Food Composition Tables / USDA FoodData Central"

class FoodRestrictionItem(BaseModel):
    id: Optional[str] = None
    food_name: str
    reason: str
    restriction_type: str = "general_suggestion"  # "medically_necessary" | "general_suggestion"
    category: str = "medical_condition"  # "allergy" | "intolerance" | "dietary_preference" | "medical_condition" | "medication_interaction"
    severity: str = "moderate"  # "critical" | "high" | "moderate" | "mild"
    safe_alternatives: List[str] = []
    clinical_note: Optional[str] = None
    scientific_basis: Optional[str] = None
    action_type: str = "avoid"  # "avoid" | "limit" | "time_separate"

class AvoidFoodItem(BaseModel):
    name: str
    reason: str
    food_name: Optional[str] = None
    restriction_type: str = "general_suggestion"
    category: str = "medical_condition"
    severity: str = "moderate"
    safe_alternatives: List[str] = []
    clinical_note: Optional[str] = None
    action_type: str = "avoid"

class RecommendationRequest(BaseModel):
    query: str
    language: str = "en"
    dietary_preference: Optional[str] = None
    health_goal: Optional[str] = None # hair_health, skin_nutrition, iron_boost, vitamin_deficiency, protein_rich, calcium_rich, general_nutrition
    session_id: Optional[str] = None
    is_voice: bool = False
    selected_food: Optional[Dict[str, Any]] = None

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class RecommendationResponse(BaseModel):
    id: Optional[int] = None
    query: str
    language: str
    intent: str
    summary: str
    recommended_foods: List[RecommendedFoodItem] = []
    foods_to_avoid: List[AvoidFoodItem] = []
    restrictions: List[FoodRestrictionItem] = []
    cautions: Optional[str] = None
    disclaimer: str = "FoodGenie provides evidence-based nutritional suggestions (ICMR-NIN & USDA FoodData Central). Food suggestions support normal physiology and do not replace medical diagnosis, treatment, or prescribed clinical cures."
    doctor_referral: Optional[str] = "Always consult a registered clinical dietitian or licensed physician for chronic conditions or prescription medication management."
    created_at: Optional[datetime] = None

class RestrictionAnalysisRequest(BaseModel):
    query: Optional[str] = None
    allergies: Optional[List[str]] = []
    intolerances: Optional[List[str]] = []
    medical_conditions: Optional[List[str]] = []
    medications: Optional[List[str]] = []
    dietary_preference: Optional[str] = None
    language: str = "en"

class RestrictionAnalysisResponse(BaseModel):
    total_restrictions: int
    medically_necessary_count: int
    general_suggestions_count: int
    restrictions: List[FoodRestrictionItem]
    clinical_disclaimer: str
    doctor_referral: str
    language: str

class DietPlanRequest(BaseModel):
    title: Optional[str] = None
    duration_type: str = "weekly" # daily, weekly, monthly
    budget_tier: str = "budget"   # budget, moderate, premium
    monthly_budget_inr: Optional[float] = 4000.0
    dietary_preference: str = "vegetarian"
    target_calories_daily: int = 2000
    language: str = "en"

class MealDay(BaseModel):
    breakfast: str
    lunch: str
    snack: str
    dinner: str
    estimated_cost_day_inr: float
    nutritional_focus: str

class DietPlanResponse(BaseModel):
    id: Optional[int] = None
    title: str
    duration_type: str
    budget_tier: str
    estimated_cost_inr: float
    target_calories_daily: int
    meals_plan_data: Dict[str, Any]
    grocery_checklist: Optional[List[str]] = []
    language: str
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
