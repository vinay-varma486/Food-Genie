from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class AllergySchema(BaseModel):
    id: Optional[int] = None
    allergen_name: str
    severity: str = "moderate"
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserProfileBase(BaseModel):
    preferred_language: str = "en"
    dietary_preference: str = "vegetarian"
    budget_mode: str = "moderate"
    monthly_food_budget: Optional[float] = 5000.0
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    activity_level: str = "moderate"
    daily_calorie_target: int = 2000
    health_goals: Optional[str] = None
    health_conditions: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserProfileCreate(UserProfileBase):
    allergies: Optional[List[AllergySchema]] = []

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None
    dietary_preference: Optional[str] = None
    budget_mode: Optional[str] = None
    monthly_food_budget: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    activity_level: Optional[str] = None
    daily_calorie_target: Optional[int] = None
    health_goals: Optional[str] = None
    health_conditions: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    allergies: Optional[List[str]] = None

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    allergies: List[AllergySchema] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    confirm_password: Optional[str] = None
    preferred_language: str = "en"
    dietary_preference: str = "vegetarian"
    age: Optional[int] = None
    monthly_food_budget: Optional[float] = 5000.0
    health_goals: Optional[str] = None
    health_conditions: Optional[str] = None
    allergies: Optional[List[str]] = []

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    profile: Optional[UserProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)

class LanguagePreferenceUpdate(BaseModel):
    preferred_language: str

