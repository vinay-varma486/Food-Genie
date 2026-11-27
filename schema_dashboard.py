from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class FoodLogCreate(BaseModel):
    food_id: Optional[int] = None
    food_name: Optional[str] = None
    food_category: Optional[str] = None
    diet_category: str = "general_nutrition"
    meal_type: str = "Lunch"
    entry_type: str = "meal"
    quantity_g: float = 100.0
    servings: float = 1.0
    cost_inr: Optional[float] = None
    calories_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    sugar_g: Optional[float] = None
    logged_at: Optional[datetime] = None
    session_id: Optional[str] = None

    @field_validator("quantity_g")
    @classmethod
    def qty_positive(cls, v: float) -> float:
        if v <= 0 or v > 10000:
            raise ValueError("Quantity must be between 1g and 10000g")
        return float(v)

    @field_validator("servings")
    @classmethod
    def servings_positive(cls, v: float) -> float:
        if v <= 0 or v > 50:
            raise ValueError("Servings must be between 0.1 and 50")
        return float(v)


class FoodLogResponse(BaseModel):
    id: int
    food_id: Optional[int] = None
    food_name: str
    food_category: str
    diet_category: str
    meal_type: str
    entry_type: str
    quantity_g: float
    servings: float
    cost_inr: float
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sugar_g: Optional[float] = None
    micronutrients_json: Optional[Dict[str, Any]] = None
    logged_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplyCategoryMealRequest(BaseModel):
    diet_category: str = "general_nutrition"
    meal_types: Optional[List[str]] = None  # Defaults to all 5 daily meals if omitted
    session_id: Optional[str] = None
    budget_inr: Optional[float] = None


class SummaryCardMetric(BaseModel):
    label: str
    value: float
    unit: str
    progress_percent: Optional[float] = None
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    comparison_note: str
    status: str = "neutral"  # neutral | success | warning | danger


class BudgetPoint(BaseModel):
    label: str
    planned_budget: float
    actual_spent: float


class DailyExpensePoint(BaseModel):
    date_label: str
    amount_inr: float
    calories_kcal: float
    meals_count: int


class CategorySpendSlice(BaseModel):
    category: str
    amount_inr: float
    percentage: float


class NutrientProgressItem(BaseModel):
    name: str
    category: str
    actual: Optional[float] = None
    goal: Optional[float] = None
    unit: str
    percent_achieved: Optional[float] = None
    data_available: bool = True
    note: Optional[str] = None


class MacroSlice(BaseModel):
    name: str
    grams: float
    kcal: float
    percentage: float


class CategoryMetadata(BaseModel):
    id: str
    label: str
    description: str
    daily_calorie_target: int
    protein_goal_g: float
    carbs_goal_g: float
    fat_goal_g: float
    fiber_goal_g: float
    focus_nutrients: List[str]
    informational_guidance: str
    recommend_professional_advice: bool = False
    budget_allocation: Dict[str, float]


class SuggestedMealSlot(BaseModel):
    meal_type: str
    meal_label: str
    timing: str
    food_name: str
    quantity: str
    estimated_cost_inr: float
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    vitamins_and_minerals: List[str] = []


class InsightItem(BaseModel):
    id: str
    type: str  # budget | nutrition | category | saving | empty
    severity: str  # info | success | warning
    title: str
    detail: str


class ActivityFeedItem(BaseModel):
    id: str
    activity_type: str
    title: str
    subtitle: Optional[str] = None
    amount_inr: Optional[float] = None
    calories_kcal: Optional[float] = None
    status: str
    timestamp: datetime


class NotificationItem(BaseModel):
    id: str
    title: str
    message: str
    severity: str  # info | warning | success
    timestamp: datetime


class DashboardOverviewResponse(BaseModel):
    user_name: str
    is_authenticated: bool
    budget_configured: bool
    date_range: str  # daily | weekly | monthly
    selected_category: str
    period_label: str
    last_updated: datetime

    # Top 4 KPI summary cards
    total_budget_card: SummaryCardMetric
    total_spent_card: SummaryCardMetric
    remaining_budget_card: SummaryCardMetric
    total_calories_card: SummaryCardMetric

    # Budget Analysis section
    daily_budget_inr: float
    weekly_budget_inr: float
    monthly_budget_inr: float
    total_food_expenses_inr: float
    remaining_balance_inr: float
    avg_daily_spending_inr: float
    budget_utilization_percent: float
    has_expense_logs: bool
    budget_vs_spending: List[BudgetPoint]
    daily_expenses_series: List[DailyExpensePoint]
    category_spending: List[CategorySpendSlice]
    planned_category_allocation: List[CategorySpendSlice]

    # Nutrition Analytics section
    daily_calorie_target: int
    logged_totals: Dict[str, Any]
    logged_daily_average: Dict[str, Any]
    has_nutrition_logs: bool
    sugar_data_available: bool
    macro_distribution: List[MacroSlice]
    weekly_calorie_trend: List[DailyExpensePoint]
    nutrient_progress: List[NutrientProgressItem]
    vitamins_summary: List[NutrientProgressItem]
    minerals_summary: List[NutrientProgressItem]

    # Category-Based Dashboard
    categories_catalog: List[CategoryMetadata]
    active_category_info: CategoryMetadata
    category_recommended_foods: List[Dict[str, Any]]
    category_suggested_meals: List[SuggestedMealSlot]

    # Smart Food Insights & Recent Activity
    smart_insights: List[InsightItem]
    recent_activity: List[ActivityFeedItem]
    notifications: List[NotificationItem]
    food_logs: List[FoodLogResponse]
    saved_plans_count: int
    saved_foods_count: int

