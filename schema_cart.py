from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class CartItemAddRequest(BaseModel):
    food_id: Optional[int] = None
    food_name: Optional[str] = None
    image_url: Optional[str] = None
    meal_category: str = "Lunch"
    quantity: float = 1.0
    serving_size: Optional[str] = None
    calories_per_unit: Optional[float] = None
    protein_per_unit: Optional[float] = None
    carbs_per_unit: Optional[float] = None
    fat_per_unit: Optional[float] = None
    fiber_per_unit: Optional[float] = None
    estimated_price_inr_per_unit: Optional[float] = None
    price_type: str = "estimated_market_price"
    vitamins_summary: Optional[List[str]] = None
    minerals_summary: Optional[List[str]] = None
    health_benefits: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def qty_valid(cls, v: float) -> float:
        if v <= 0 or v > 50:
            raise ValueError("Quantity must be between 0.25 and 50")
        return float(v)


class CartItemUpdateRequest(BaseModel):
    food_name: Optional[str] = None
    meal_category: Optional[str] = None
    quantity: Optional[float] = None
    serving_size: Optional[str] = None
    estimated_price_inr_per_unit: Optional[float] = None
    notes: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def qty_optional_valid(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v <= 0 or v > 50):
            raise ValueError("Quantity must be between 0.25 and 50")
        return float(v) if v is not None else None


class CartItemResponse(BaseModel):
    id: int
    food_id: Optional[int] = None
    food_name: str
    image_url: Optional[str] = None
    meal_category: str
    quantity: float
    serving_size: str
    calories_per_unit: float
    protein_per_unit: float
    carbs_per_unit: float
    fat_per_unit: float
    fiber_per_unit: float
    estimated_price_inr_per_unit: float
    price_type: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    total_estimated_cost_inr: float
    vitamins_summary: List[str] = []
    minerals_summary: List[str] = []
    health_benefits: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartTotalsSummary(BaseModel):
    total_items: int
    total_units: float
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    total_estimated_cost_inr: float
    daily_calorie_target: int
    daily_budget_inr: float
    calorie_target_percent: float


class CartSaveRequest(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    save_as_meal_plan: bool = False


class CartResponse(BaseModel):
    id: int
    user_id: int
    title: str
    notes: Optional[str] = None
    updated_at: datetime
    items: List[CartItemResponse]
    grouped_meals: Dict[str, List[CartItemResponse]]
    totals: CartTotalsSummary

