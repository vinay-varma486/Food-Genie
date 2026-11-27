from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class NutrientBase(BaseModel):
    name: str
    nutrient_code: Optional[str] = None
    category: str
    daily_rda_adult: Optional[float] = None
    unit: str = "mg"
    physiological_role: Optional[str] = None

class NutrientResponse(NutrientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class FoodNutrientResponse(BaseModel):
    id: int
    nutrient_name: str
    nutrient_category: str
    amount_per_100g: float
    unit: str
    percent_daily_value: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class FoodItemBase(BaseModel):
    name: str
    name_te: Optional[str] = None
    name_hi: Optional[str] = None
    scientific_name: Optional[str] = None
    category: str
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    glycemic_index: Optional[int] = None
    description: Optional[str] = None
    benefits_summary: Optional[str] = None
    cautions: Optional[str] = None
    image_url: Optional[str] = None
    serving_size: str = "100g"
    serving_weight_g: float = 100.0
    preparation_methods: Optional[str] = None
    preparation_methods_te: Optional[str] = None
    preparation_methods_hi: Optional[str] = None

class FoodItemCreate(FoodItemBase):
    pass

class FoodItemResponse(FoodItemBase):
    id: int
    verified_source: str
    nutrients: List[FoodNutrientResponse] = []
    model_config = ConfigDict(from_attributes=True)

class FoodSearchQuery(BaseModel):
    query: str
    category: Optional[str] = None
    language: str = "en"
    page: int = 1
    limit: int = 20

class SavedFoodCreate(BaseModel):
    food_id: int
    notes: Optional[str] = None

class SavedFoodResponse(BaseModel):
    id: int
    food_id: int
    food_name: str
    food_name_te: Optional[str] = None
    food_name_hi: Optional[str] = None
    category: Optional[str] = None
    calories_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fiber_g: Optional[float] = None
    image_url: Optional[str] = None
    benefits_summary: Optional[str] = None
    notes: Optional[str] = None
    saved_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WaterIntakeRequest(BaseModel):
    weight_kg: float
    activity_minutes: int = 30
    climate: str = "moderate" # moderate, hot, humid, cold
    age: Optional[int] = None
    gender: Optional[str] = "unspecified"
    language: str = "en"

class HourlyScheduleItem(BaseModel):
    time_window: str
    amount_ml: int
    glasses: float
    tip: str

class WaterIntakeResponse(BaseModel):
    weight_kg: float
    base_requirement_ml: int
    activity_adjustment_ml: int
    climate_adjustment_ml: int
    total_daily_water_ml: int
    total_daily_water_liters: float
    total_glasses: float
    schedule: List[HourlyScheduleItem]
    conversational_advice: str
    language: str


