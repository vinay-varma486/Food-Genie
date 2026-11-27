from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

from model_user import User, UserProfile
from model_nutrition import FoodItem, Nutrient, FoodNutrient, SavedFood
from model_recommendation import DietPlan, Recommendation
from model_grocery import GroceryItem
from model_dashboard import FoodLog, DashboardActivity
from nutrition_service import NutritionRAGRetriever
from ai_budget_planner import ai_budget_planner
from schema_diet_planner import AIDietPlanRequest
from schema_dashboard import (
    FoodLogCreate,
    SummaryCardMetric,
    BudgetPoint,
    DailyExpensePoint,
    CategorySpendSlice,
    NutrientProgressItem,
    MacroSlice,
    CategoryMetadata,
    SuggestedMealSlot,
    InsightItem,
    ActivityFeedItem,
    NotificationItem,
    DashboardOverviewResponse,
)

# Category specifications matching Requirement 6 (All Categories + 9 specific categories)
CATEGORY_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "id": "all",
        "label": "All Categories",
        "description": "Complete view across all foods, logged meals, and balanced daily nutrition.",
        "calorie_delta": 0,
        "protein_ratio": 0.20,
        "carbs_ratio": 0.52,
        "fat_ratio": 0.28,
        "fiber_goal": 30.0,
        "diet_pref": None,
        "budget_goal": "maintain_weight",
        "focus_nutrients": ["Iron", "Calcium", "Vitamin C", "Vitamin B12"],
        "informational_guidance": "General wellness overview using ICMR-NIN and USDA reference tables.",
        "recommend_professional_advice": False,
        "food_topic": "general_nutrition",
        "exclude_categories": [],
        "allocation_weights": {
            "Grains & Millets": 0.30,
            "Pulses & Proteins": 0.28,
            "Leafy Greens & Vegetables": 0.22,
            "Dairy & Eggs": 0.12,
            "Seeds, Nuts & Fruits": 0.08,
        },
    },
    {
        "id": "weight_loss",
        "label": "Weight Loss",
        "description": "High-fiber, high-satiety wholefoods calibrated for a moderate calorie deficit.",
        "calorie_delta": -400,
        "protein_ratio": 0.26,
        "carbs_ratio": 0.46,
        "fat_ratio": 0.28,
        "fiber_goal": 35.0,
        "diet_pref": None,
        "budget_goal": "weight_loss",
        "focus_nutrients": ["Protein", "Fiber", "Iron", "Potassium", "Magnesium"],
        "informational_guidance": "General informational guide prioritizing whole grains, legumes, and non-starchy greens. Consult a registered dietitian or physician before starting an aggressive calorie deficit.",
        "recommend_professional_advice": True,
        "food_topic": "healthy_eating",
        "exclude_categories": [],
        "allocation_weights": {
            "Leafy Greens & Vegetables": 0.30,
            "Pulses & Proteins": 0.30,
            "Grains & Millets": 0.22,
            "Fruits": 0.10,
            "Dairy & Seeds": 0.08,
        },
    },
    {
        "id": "weight_gain",
        "label": "Weight Gain",
        "description": "Calorie-dense, nutrient-rich wholefoods supporting steady, healthy weight gain.",
        "calorie_delta": 400,
        "protein_ratio": 0.22,
        "carbs_ratio": 0.50,
        "fat_ratio": 0.28,
        "fiber_goal": 30.0,
        "diet_pref": None,
        "budget_goal": "weight_gain",
        "focus_nutrients": ["Calories", "Protein", "Calcium", "Iron", "Zinc"],
        "informational_guidance": "Supports gradual calorie surplus using wholefood carbs, dairy/legumes, nuts, and seeds. Seek clinical medical advice if underweight due to an underlying condition.",
        "recommend_professional_advice": True,
        "food_topic": "protein_rich",
        "exclude_categories": [],
        "allocation_weights": {
            "Grains & Millets": 0.28,
            "Pulses & Proteins": 0.28,
            "Dairy & Eggs": 0.20,
            "Seeds & Nuts": 0.14,
            "Vegetables & Fruits": 0.10,
        },
    },
    {
        "id": "muscle_building",
        "label": "Muscle Building",
        "description": "High bioavailable protein with slow-release carbohydrates and essential minerals.",
        "calorie_delta": 250,
        "protein_ratio": 0.30,
        "carbs_ratio": 0.45,
        "fat_ratio": 0.25,
        "fiber_goal": 32.0,
        "diet_pref": None,
        "budget_goal": "weight_gain",
        "focus_nutrients": ["Protein", "Magnesium", "Zinc", "Calcium", "Iron"],
        "informational_guidance": "Prioritizes complete amino acids across meals. For competitive sports or kidney conditions, verify higher protein targets with a certified sports nutritionist or doctor.",
        "recommend_professional_advice": True,
        "food_topic": "protein_rich",
        "exclude_categories": [],
        "allocation_weights": {
            "Pulses & Proteins": 0.36,
            "Dairy & Eggs": 0.22,
            "Grains & Millets": 0.22,
            "Seeds & Nuts": 0.10,
            "Greens & Vegetables": 0.10,
        },
    },
    {
        "id": "healthy_diet",
        "label": "Healthy Diet",
        "description": "Balanced micronutrient-rich daily eating focused on greens, millets, fruits, and probiotics.",
        "calorie_delta": 0,
        "protein_ratio": 0.20,
        "carbs_ratio": 0.52,
        "fat_ratio": 0.28,
        "fiber_goal": 32.0,
        "diet_pref": None,
        "budget_goal": "maintain_weight",
        "focus_nutrients": ["Vitamin C", "Folate (Vitamin B9)", "Vitamin A (Beta-Carotene)", "Potassium"],
        "informational_guidance": "Follows balanced wholefood diversity across leafy greens, seasonal fruits, millets, and fermented curd.",
        "recommend_professional_advice": False,
        "food_topic": "healthy_eating",
        "exclude_categories": [],
        "allocation_weights": {
            "Leafy Greens & Vegetables": 0.28,
            "Grains & Millets": 0.26,
            "Pulses & Proteins": 0.24,
            "Fruits": 0.12,
            "Dairy & Seeds": 0.10,
        },
    },
    {
        "id": "low_budget",
        "label": "Low Budget Meals",
        "description": "Maximum nutrition per rupee using local staples like ragi, green moong, chana, peanuts, and greens.",
        "calorie_delta": 0,
        "protein_ratio": 0.22,
        "carbs_ratio": 0.54,
        "fat_ratio": 0.24,
        "fiber_goal": 30.0,
        "diet_pref": "vegetarian",
        "budget_goal": "maintain_weight",
        "focus_nutrients": ["Iron", "Calcium", "Protein", "Biotin (Vitamin B7)"],
        "informational_guidance": "Highlights cost-effective ICMR staples paired with seasonal mandi pricing benchmarks to stretch your food budget without losing nutrition.",
        "recommend_professional_advice": False,
        "food_topic": "budget_diet",
        "exclude_categories": [],
        "allocation_weights": {
            "Grains & Millets": 0.34,
            "Pulses & Legumes": 0.32,
            "Leafy Greens & Vegetables": 0.20,
            "Seeds & Peanuts": 0.08,
            "Fruits": 0.06,
        },
    },
    {
        "id": "high_protein",
        "label": "High Protein Diet",
        "description": "Ranked by protein density per serving across lentils, soya chunks, paneer, eggs, and seeds.",
        "calorie_delta": 100,
        "protein_ratio": 0.32,
        "carbs_ratio": 0.42,
        "fat_ratio": 0.26,
        "fiber_goal": 30.0,
        "diet_pref": None,
        "budget_goal": "maintain_weight",
        "focus_nutrients": ["Protein", "Zinc", "Iron", "Vitamin B12", "Calcium"],
        "informational_guidance": "Increases dietary protein share across meals. Individuals with reduced kidney function should consult their physician before increasing protein intake.",
        "recommend_professional_advice": True,
        "food_topic": "protein_rich",
        "exclude_categories": [],
        "allocation_weights": {
            "Pulses & Proteins": 0.38,
            "Dairy & Eggs": 0.22,
            "Grains & Millets": 0.20,
            "Seeds & Nuts": 0.12,
            "Vegetables & Greens": 0.08,
        },
    },
    {
        "id": "vegetarian",
        "label": "Vegetarian",
        "description": "Plant-and-dairy nutrition pairing pulses, millets, greens, seeds, paneer, and curd.",
        "calorie_delta": 0,
        "protein_ratio": 0.20,
        "carbs_ratio": 0.53,
        "fat_ratio": 0.27,
        "fiber_goal": 32.0,
        "diet_pref": "vegetarian",
        "budget_goal": "maintain_weight",
        "focus_nutrients": ["Vitamin B12", "Iron", "Zinc", "Calcium", "Plant Omega-3 (ALA)"],
        "informational_guidance": "Pairs Vitamin C (amla/lemon) with plant iron sources and monitors Vitamin B12 intake from dairy/fortified options. Consider medical B12 screening periodically.",
        "recommend_professional_advice": True,
        "food_topic": "general_nutrition",
        "exclude_categories": ["poultry"],
        "allocation_weights": {
            "Pulses & Legumes": 0.30,
            "Grains & Millets": 0.28,
            "Leafy Greens & Vegetables": 0.22,
            "Dairy & Curd": 0.12,
            "Seeds & Nuts": 0.08,
        },
    },
    {
        "id": "non_vegetarian",
        "label": "Non-Vegetarian",
        "description": "Combines eggs/lean poultry with high-fiber grains, dal, and seasonal vegetables.",
        "calorie_delta": 0,
        "protein_ratio": 0.26,
        "carbs_ratio": 0.46,
        "fat_ratio": 0.28,
        "fiber_goal": 28.0,
        "diet_pref": "non-vegetarian",
        "budget_goal": "maintain_weight",
        "focus_nutrients": ["Vitamin B12", "Iron", "Zinc", "Protein"],
        "informational_guidance": "Balances bioavailable animal protein and Vitamin B12 with adequate dietary fiber from whole grains and vegetables.",
        "recommend_professional_advice": False,
        "food_topic": "protein_rich",
        "exclude_categories": [],
        "allocation_weights": {
            "Eggs & Lean Poultry": 0.30,
            "Grains & Millets": 0.26,
            "Pulses & Legumes": 0.18,
            "Greens & Vegetables": 0.18,
            "Dairy & Seeds": 0.08,
        },
    },
    {
        "id": "general_nutrition",
        "label": "General Nutrition",
        "description": "Well-rounded daily nutrition targeting all 11 essential vitamins & minerals in ICMR/USDA.",
        "calorie_delta": 0,
        "protein_ratio": 0.20,
        "carbs_ratio": 0.52,
        "fat_ratio": 0.28,
        "fiber_goal": 30.0,
        "diet_pref": None,
        "budget_goal": "maintain_weight",
        "focus_nutrients": ["Iron", "Calcium", "Vitamin C", "Vitamin A (Beta-Carotene)", "Folate (Vitamin B9)"],
        "informational_guidance": "Balanced everyday nutrition benchmark for healthy adults based on ICMR-NIN Recommended Dietary Allowances.",
        "recommend_professional_advice": False,
        "food_topic": "general_nutrition",
        "exclude_categories": [],
        "allocation_weights": {
            "Grains & Millets": 0.30,
            "Pulses & Proteins": 0.26,
            "Leafy Greens & Vegetables": 0.22,
            "Fruits & Dairy": 0.14,
            "Seeds & Nuts": 0.08,
        },
    },
]

CATEGORY_MAP: Dict[str, Dict[str, Any]] = {c["id"]: c for c in CATEGORY_DEFINITIONS}

CATEGORY_ALIASES = {
    "all categories": "all",
    "weight loss": "weight_loss",
    "weight gain": "weight_gain",
    "muscle building": "muscle_building",
    "healthy diet": "healthy_diet",
    "low budget": "low_budget",
    "low budget meals": "low_budget",
    "high protein": "high_protein",
    "high protein diet": "high_protein",
    "vegetarian": "vegetarian",
    "non-vegetarian": "non_vegetarian",
    "non vegetarian": "non_vegetarian",
    "general nutrition": "general_nutrition",
}


def normalize_category(raw: Optional[str]) -> str:
    if not raw:
        return "all"
    key = raw.strip().lower()
    if key in CATEGORY_MAP:
        return key
    return CATEGORY_ALIASES.get(key, "all")


def _period_windows(date_range: str, now: Optional[datetime] = None) -> Tuple[str, datetime, datetime, datetime, int]:
    now = now or datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    rng = (date_range or "weekly").lower().strip()
    if rng == "daily":
        start = today_start
        prev_start = start - timedelta(days=1)
        return "daily", start, prev_start, now, 1
    if rng == "monthly":
        start = today_start - timedelta(days=29)
        prev_start = start - timedelta(days=30)
        return "monthly", start, prev_start, now, 30
    start = today_start - timedelta(days=6)
    prev_start = start - timedelta(days=7)
    return "weekly", start, prev_start, now, 7


def _normalize_food_category_label(cat: Optional[str]) -> str:
    if not cat:
        return "General Foods"
    c = cat.lower()
    if "leafy" in c or "vegetable" in c or "tuber" in c:
        return "Greens & Vegetables"
    if "millet" in c or "grain" in c:
        return "Grains & Millets"
    if "pulse" in c or "plant_protein" in c or "legume" in c:
        return "Pulses & Proteins"
    if "dairy" in c or "poultry" in c or "egg" in c:
        return "Dairy & Eggs"
    if "fruit" in c:
        return "Fruits"
    if "seed" in c or "nut" in c:
        return "Seeds & Nuts"
    return cat.replace("_", " ").title()


def _base_calorie_target(profile: Optional[UserProfile]) -> int:
    if profile and profile.daily_calorie_target and profile.daily_calorie_target >= 1000:
        return int(profile.daily_calorie_target)
    if profile and profile.weight_kg and profile.height_cm and profile.age:
        s = -161 if (profile.gender or "").lower() == "female" else 5
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + s
        mult = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}.get(
            (profile.activity_level or "moderate").lower(), 1.55
        )
        return max(1200, int(round(bmr * mult)))
    return 2000


def _build_category_metadata(
    cat_def: Dict[str, Any],
    base_cals: int,
    period_budget_inr: float,
) -> CategoryMetadata:
    target_cals = max(1200, int(base_cals + cat_def["calorie_delta"]))
    protein_g = round((target_cals * cat_def["protein_ratio"]) / 4.0, 1)
    carbs_g = round((target_cals * cat_def["carbs_ratio"]) / 4.0, 1)
    fat_g = round((target_cals * cat_def["fat_ratio"]) / 9.0, 1)
    alloc = {
        k: round(period_budget_inr * w, 2)
        for k, w in cat_def["allocation_weights"].items()
    }
    return CategoryMetadata(
        id=cat_def["id"],
        label=cat_def["label"],
        description=cat_def["description"],
        daily_calorie_target=target_cals,
        protein_goal_g=protein_g,
        carbs_goal_g=carbs_g,
        fat_goal_g=fat_g,
        fiber_goal_g=cat_def["fiber_goal"],
        focus_nutrients=cat_def["focus_nutrients"],
        informational_guidance=cat_def["informational_guidance"],
        recommend_professional_advice=cat_def["recommend_professional_advice"],
        budget_allocation=alloc,
    )


def _rank_category_foods(
    db: Session,
    cat_def: Dict[str, Any],
    search: Optional[str] = None,
    limit: int = 8,
) -> List[Dict[str, Any]]:
    all_items = db.query(FoodItem).all()
    if not all_items:
        return []

    excluded = set(cat_def.get("exclude_categories") or [])
    items = [it for it in all_items if (it.category or "").lower() not in excluded]

    if search and search.strip():
        q = search.strip().lower()
        items = [
            it for it in items
            if q in (it.name or "").lower()
            or q in (it.category or "").lower()
            or q in (it.benefits_summary or "").lower()
            or q in (it.name_te or "").lower()
            or q in (it.name_hi or "").lower()
        ]

    cat_id = cat_def["id"]
    guide = NutritionRAGRetriever.FOOD_PRICE_CONSUMPTION_GUIDE

    def score_item(it: FoodItem) -> Tuple[float, str]:
        price = guide.get(it.name, {}).get("price", 15.0)
        if cat_id in ("high_protein", "muscle_building"):
            return (-(it.protein_g or 0.0), it.name)
        if cat_id == "weight_loss":
            fiber_score = (it.fiber_g or 0.0) * 8.0 + (it.protein_g or 0.0) * 3.0 - (it.calories_kcal or 0.0) * 0.25
            return (-fiber_score, it.name)
        if cat_id == "weight_gain":
            return (-((it.calories_kcal or 0.0) + (it.protein_g or 0.0) * 5.0), it.name)
        if cat_id == "low_budget":
            nut_density = ((it.protein_g or 1.0) * 4.0 + (it.fiber_g or 1.0) * 2.0 + (it.calories_kcal or 50.0) * 0.1)
            return (-(nut_density / max(price, 4.0)), it.name)
        if cat_id == "non_vegetarian":
            bonus = 100.0 if (it.category or "").lower() in ("poultry", "dairy") else 0.0
            return (-(bonus + (it.protein_g or 0.0)), it.name)
        if cat_id == "healthy_diet":
            bonus = 20.0 if (it.category or "").lower() in ("leafy green", "fruit", "millet") else 0.0
            return (-(bonus + (it.fiber_g or 0.0)), it.name)
        topic_names = NutritionRAGRetriever.TOPIC_FOOD_MAP.get(cat_def.get("food_topic", "general_nutrition"), [])
        idx = topic_names.index(it.name) if it.name in topic_names else 999
        return (idx, it.name)

    items.sort(key=score_item)
    selected = items[:limit]

    enriched: List[Dict[str, Any]] = []
    for it in selected:
        sw = it.serving_weight_g or 100.0
        scale = sw / 100.0
        info = guide.get(it.name, {})
        fns = db.query(FoodNutrient).filter(FoodNutrient.food_id == it.id).all()
        vits, mins = [], []
        for fn in fns:
            if not fn.nutrient:
                continue
            entry = {
                "name": fn.nutrient.name,
                "category": fn.nutrient.category,
                "amount_per_100g": round(fn.amount_per_100g, 2),
                "amount_per_serving": round(fn.amount_per_100g * scale, 2),
                "unit": fn.unit,
                "percent_daily_value": fn.percent_daily_value,
            }
            if fn.nutrient.category == "vitamin":
                vits.append(entry)
            else:
                mins.append(entry)

        enriched.append({
            "id": it.id,
            "name": it.name,
            "name_te": it.name_te,
            "name_hi": it.name_hi,
            "category": it.category,
            "meal_category": info.get("meal_cat", "Lunch"),
            "serving_size": it.serving_size or "100g",
            "serving_weight_g": sw,
            "estimated_price_inr": info.get("price", 15.0),
            "price_type": "estimated_market_price",
            "how_to_consume": info.get("how") or it.preparation_methods,
            "preparation_methods": it.preparation_methods,
            "benefit": it.benefits_summary or "Verified nutrient-dense wholefood.",
            "benefits_summary": it.benefits_summary,
            "cautions": it.cautions,
            "verified_source": it.verified_source,
            "calories_kcal": round((it.calories_kcal or 0.0) * scale, 1),
            "protein_g": round((it.protein_g or 0.0) * scale, 1),
            "carbs_g": round((it.carbs_g or 0.0) * scale, 1),
            "fat_g": round((it.fat_g or 0.0) * scale, 1),
            "fiber_g": round((it.fiber_g or 0.0) * scale, 1),
            "nutrients_per_100g": {
                "calories_kcal": round(it.calories_kcal or 0.0, 1),
                "protein_g": round(it.protein_g or 0.0, 1),
                "carbs_g": round(it.carbs_g or 0.0, 1),
                "fat_g": round(it.fat_g or 0.0, 1),
                "fiber_g": round(it.fiber_g or 0.0, 1),
            },
            "nutrients_per_serving": {
                "calories_kcal": round((it.calories_kcal or 0.0) * scale, 1),
                "protein_g": round((it.protein_g or 0.0) * scale, 1),
                "carbs_g": round((it.carbs_g or 0.0) * scale, 1),
                "fat_g": round((it.fat_g or 0.0) * scale, 1),
                "fiber_g": round((it.fiber_g or 0.0) * scale, 1),
            },
            "vitamins": vits,
            "minerals": mins,
        })
    return enriched


def _generate_category_suggested_meals(
    cat_def: Dict[str, Any],
    profile: Optional[UserProfile],
    daily_budget_inr: float,
) -> List[SuggestedMealSlot]:
    diet_pref = cat_def.get("diet_pref") or (profile.dietary_preference if profile else "vegetarian")
    if cat_def["id"] == "non_vegetarian":
        diet_pref = "non-vegetarian"
    elif cat_def["id"] == "vegetarian":
        diet_pref = "vegetarian"

    allergies = [a.allergen_name for a in profile.allergies] if profile and profile.allergies else []
    eff_budget = max(100.0, daily_budget_inr if daily_budget_inr > 0 else 150.0)
    plan_req = AIDietPlanRequest(
        budget_inr=eff_budget,
        budget_duration="daily",
        custom_days=1,
        location=(profile.city if profile and profile.city else "Hyderabad"),
        dietary_preference=diet_pref,
        health_goal=cat_def["budget_goal"],
        allergies=allergies,
        number_of_people=1,
        allow_over_budget=eff_budget >= 130.0,
        language=(profile.preferred_language if profile and profile.preferred_language else "en"),
    )
    plan = ai_budget_planner.generate_plan(plan_req)
    slots: List[SuggestedMealSlot] = []
    if plan.daily_plans:
        day_meals = plan.daily_plans[0].meals
        for mk in ["breakfast", "morning_snack", "lunch", "evening_snack", "dinner"]:
            item = day_meals.get(mk)
            if not item:
                continue
            slots.append(
                SuggestedMealSlot(
                    meal_type=item.meal_type,
                    meal_label=item.meal_label,
                    timing=item.timing or "",
                    food_name=item.food_name,
                    quantity=item.quantity,
                    estimated_cost_inr=item.estimated_cost_inr,
                    calories_kcal=item.nutrients.calories_kcal,
                    protein_g=item.nutrients.protein_g,
                    carbs_g=item.nutrients.carbs_g,
                    fat_g=item.nutrients.fat_g,
                    fiber_g=item.nutrients.fiber_g,
                    vitamins_and_minerals=item.nutrients.vitamins_and_minerals,
                )
            )
    return slots


def create_food_log(
    db: Session,
    log_in: FoodLogCreate,
    user: Optional[User] = None,
) -> FoodLog:
    """Logs a real meal or food purchase, calculating verified nutrients when linked to FoodItem."""
    user_id = user.id if user else None
    session_id = log_in.session_id if not user_id else log_in.session_id

    food_item: Optional[FoodItem] = None
    if log_in.food_id:
        food_item = db.query(FoodItem).filter(FoodItem.id == log_in.food_id).first()

    if not food_item and not (log_in.food_name and log_in.food_name.strip()):
        raise ValueError("Either food_id or food_name is required.")

    guide = NutritionRAGRetriever.FOOD_PRICE_CONSUMPTION_GUIDE
    qty_g = float(log_in.quantity_g)
    servings = float(log_in.servings)
    micronutrients: Dict[str, Any] = {}

    if food_item:
        base_sw = food_item.serving_weight_g or 100.0
        total_g = qty_g * servings if log_in.quantity_g != 100.0 else base_sw * servings
        scale_100 = total_g / 100.0
        calories = log_in.calories_kcal if log_in.calories_kcal is not None else round((food_item.calories_kcal or 0.0) * scale_100, 1)
        protein = log_in.protein_g if log_in.protein_g is not None else round((food_item.protein_g or 0.0) * scale_100, 1)
        carbs = log_in.carbs_g if log_in.carbs_g is not None else round((food_item.carbs_g or 0.0) * scale_100, 1)
        fat = log_in.fat_g if log_in.fat_g is not None else round((food_item.fat_g or 0.0) * scale_100, 1)
        fiber = log_in.fiber_g if log_in.fiber_g is not None else round((food_item.fiber_g or 0.0) * scale_100, 1)
        default_price = guide.get(food_item.name, {}).get("price", 15.0) * servings
        cost_inr = log_in.cost_inr if log_in.cost_inr is not None else round(default_price, 2)
        food_name = log_in.food_name or food_item.name
        food_cat = _normalize_food_category_label(log_in.food_category or food_item.category)

        fns = db.query(FoodNutrient).filter(FoodNutrient.food_id == food_item.id).all()
        for fn in fns:
            if fn.nutrient:
                micronutrients[fn.nutrient.name] = {
                    "amount": round(fn.amount_per_100g * scale_100, 2),
                    "unit": fn.unit,
                    "category": fn.nutrient.category,
                }
        qty_g = round(total_g, 1)
    else:
        food_name = (log_in.food_name or "").strip()
        food_cat = _normalize_food_category_label(log_in.food_category)
        calories = round(float(log_in.calories_kcal or 0.0), 1)
        protein = round(float(log_in.protein_g or 0.0), 1)
        carbs = round(float(log_in.carbs_g or 0.0), 1)
        fat = round(float(log_in.fat_g or 0.0), 1)
        fiber = round(float(log_in.fiber_g or 0.0), 1)
        cost_inr = round(float(log_in.cost_inr or 0.0), 2)

    sugar = round(float(log_in.sugar_g), 1) if log_in.sugar_g is not None else None
    entry = FoodLog(
        user_id=user_id,
        session_id=session_id,
        food_id=food_item.id if food_item else None,
        food_name=food_name,
        food_category=food_cat,
        diet_category=normalize_category(log_in.diet_category),
        meal_type=log_in.meal_type or "Lunch",
        entry_type=log_in.entry_type or "meal",
        quantity_g=qty_g,
        servings=servings,
        cost_inr=max(0.0, float(cost_inr)),
        calories_kcal=max(0.0, float(calories)),
        protein_g=max(0.0, float(protein)),
        carbs_g=max(0.0, float(carbs)),
        fat_g=max(0.0, float(fat)),
        fiber_g=max(0.0, float(fiber)),
        sugar_g=sugar,
        micronutrients_json=micronutrients or None,
        logged_at=log_in.logged_at or datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    act_type = "food_purchase" if entry.entry_type == "purchase" else "meal_added"
    act_title = f"{'Purchased' if entry.entry_type == 'purchase' else 'Logged'} {entry.food_name}"
    act_sub = f"{entry.meal_type} • {entry.quantity_g:.0f}g"
    db.add(
        DashboardActivity(
            user_id=user_id,
            session_id=session_id,
            activity_type=act_type,
            title=act_title,
            subtitle=act_sub,
            amount_inr=entry.cost_inr,
            calories_kcal=entry.calories_kcal,
            status="completed",
        )
    )
    db.commit()
    return entry


def record_activity_event(
    db: Session,
    activity_type: str,
    title: str,
    subtitle: Optional[str] = None,
    amount_inr: Optional[float] = None,
    calories_kcal: Optional[float] = None,
    status: str = "updated",
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
) -> None:
    try:
        db.add(
            DashboardActivity(
                user_id=user_id,
                session_id=session_id,
                activity_type=activity_type,
                title=title,
                subtitle=subtitle,
                amount_inr=amount_inr,
                calories_kcal=calories_kcal,
                status=status,
            )
        )
        db.commit()
    except Exception:
        db.rollback()


def _query_user_logs(
    db: Session,
    user: Optional[User],
    session_id: Optional[str],
    start_dt: datetime,
    end_dt: datetime,
    category_id: str,
) -> List[FoodLog]:
    q = db.query(FoodLog)
    if user:
        q = q.filter(FoodLog.user_id == user.id)
    elif session_id:
        q = q.filter(FoodLog.user_id.is_(None), FoodLog.session_id == session_id)
    else:
        return []

    rows = q.filter(FoodLog.logged_at >= start_dt, FoodLog.logged_at <= end_dt).order_by(FoodLog.logged_at.desc()).all()
    if category_id != "all":
        if category_id == "vegetarian":
            rows = [r for r in rows if "poultry" not in (r.food_category or "").lower()]
        elif category_id == "non_vegetarian":
            pass
        else:
            # Keep logs tagged with selected diet category or show all if none match specifically
            tagged = [r for r in rows if r.diet_category == category_id]
            if tagged:
                rows = tagged
    return rows


def build_dashboard_overview(
    db: Session,
    user: Optional[User] = None,
    date_range: str = "weekly",
    category: str = "all",
    session_id: Optional[str] = None,
    search: Optional[str] = None,
    budget_override: Optional[float] = None,
) -> DashboardOverviewResponse:
    now = datetime.utcnow()
    rng, start_dt, prev_start_dt, end_dt, days_in_range = _period_windows(date_range, now)
    cat_id = normalize_category(category)
    cat_def = CATEGORY_MAP[cat_id]
    profile: Optional[UserProfile] = user.profile if user else None

    user_name = "Friend"
    if user:
        user_name = (
            (user.full_name or "").strip()
            or (user.email.split("@")[0].replace(".", " ").title() if user.email else "Friend")
        )

    # Monthly budget priority: explicit override > user profile > 0 (unconfigured clean state)
    monthly_budget = 0.0
    budget_configured = False
    if budget_override is not None and budget_override > 0:
        monthly_budget = float(budget_override)
        budget_configured = True
    elif profile and profile.monthly_food_budget and profile.monthly_food_budget > 0:
        monthly_budget = float(profile.monthly_food_budget)
        budget_configured = True

    daily_budget = round(monthly_budget / 30.0, 2)
    weekly_budget = round((monthly_budget / 30.0) * 7.0, 2)
    period_budget = (
        daily_budget if rng == "daily"
        else weekly_budget if rng == "weekly"
        else round(monthly_budget, 2)
    )

    base_cals = _base_calorie_target(profile)
    active_cat_meta = _build_category_metadata(cat_def, base_cals, period_budget)
    period_calorie_target = active_cat_meta.daily_calorie_target * days_in_range

    # Real logs for active period & previous comparison period
    logs = _query_user_logs(db, user, session_id, start_dt, end_dt, cat_id)
    prev_logs = _query_user_logs(db, user, session_id, prev_start_dt, start_dt - timedelta(seconds=1), cat_id)

    total_spent = round(sum(float(l.cost_inr or 0.0) for l in logs), 2)
    prev_spent = round(sum(float(l.cost_inr or 0.0) for l in prev_logs), 2)
    remaining_budget = round(period_budget - total_spent, 2) if budget_configured else 0.0

    total_calories = round(sum(float(l.calories_kcal or 0.0) for l in logs), 1)
    prev_calories = round(sum(float(l.calories_kcal or 0.0) for l in prev_logs), 1)

    utilization_pct = round((total_spent / period_budget) * 100.0, 1) if period_budget > 0 else 0.0
    cal_adherence_pct = round((total_calories / period_calorie_target) * 100.0, 1) if period_calorie_target > 0 and total_calories > 0 else 0.0

    spent_change_pct = (
        round(((total_spent - prev_spent) / prev_spent) * 100.0, 1)
        if prev_spent > 0
        else None
    )
    cal_change_pct = (
        round(((total_calories - prev_calories) / prev_calories) * 100.0, 1)
        if prev_calories > 0
        else None
    )

    total_budget_card = SummaryCardMetric(
        label="Total Budget",
        value=period_budget,
        unit="₹",
        progress_percent=100.0 if budget_configured else 0.0,
        previous_value=None,
        change_percent=None,
        comparison_note=(
            f"₹{daily_budget:,.0f}/day ({rng.capitalize()} target)"
            if budget_configured
            else "Set your monthly budget in Settings or Budget Planner"
        ),
        status="neutral",
    )

    spent_status = "danger" if utilization_pct > 100 else ("warning" if utilization_pct >= 85 else "success")
    total_spent_card = SummaryCardMetric(
        label="Total Amount Spent",
        value=total_spent,
        unit="₹",
        progress_percent=min(100.0, utilization_pct) if budget_configured else 0.0,
        previous_value=prev_spent if prev_spent > 0 else None,
        change_percent=spent_change_pct,
        comparison_note=(
            f"{'+' if (spent_change_pct or 0) > 0 else ''}{spent_change_pct}% vs prior {rng}"
            if spent_change_pct is not None
            else ("No prior period expense logs yet" if logs else "Log meals or purchases to track spend")
        ),
        status=spent_status if logs else "neutral",
    )

    rem_pct = round(max(0.0, (remaining_budget / period_budget) * 100.0), 1) if period_budget > 0 else 0.0
    remaining_budget_card = SummaryCardMetric(
        label="Remaining Budget",
        value=remaining_budget,
        unit="₹",
        progress_percent=rem_pct,
        previous_value=None,
        change_percent=None,
        comparison_note=(
            f"{rem_pct}% of {rng} budget left"
            if budget_configured and remaining_budget >= 0
            else (f"Over budget by ₹{abs(remaining_budget):,.0f}" if budget_configured else "Configure budget to monitor balance")
        ),
        status=("danger" if remaining_budget < 0 else ("warning" if rem_pct < 20 and budget_configured else "success")),
    )

    total_calories_card = SummaryCardMetric(
        label="Total Calories Consumed",
        value=total_calories,
        unit="kcal",
        progress_percent=min(100.0, cal_adherence_pct),
        previous_value=prev_calories if prev_calories > 0 else None,
        change_percent=cal_change_pct,
        comparison_note=(
            f"{cal_adherence_pct}% of {period_calorie_target:,} kcal goal"
            if total_calories > 0
            else f"Target: {active_cat_meta.daily_calorie_target:,} kcal/day"
        ),
        status="success" if 75 <= cal_adherence_pct <= 115 else ("warning" if cal_adherence_pct > 0 else "neutral"),
    )

    # Expense series grouped cleanly by day or meal slot
    daily_expenses_series: List[DailyExpensePoint] = []
    budget_vs_spending: List[BudgetPoint] = []

    if rng == "daily":
        meal_slots = ["Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"]
        slot_budget = round(daily_budget / 5.0, 2) if budget_configured else 0.0
        for slot in meal_slots:
            slot_logs = [l for l in logs if (l.meal_type or "").lower() == slot.lower()]
            s_cost = round(sum(float(l.cost_inr or 0.0) for l in slot_logs), 2)
            s_kcal = round(sum(float(l.calories_kcal or 0.0) for l in slot_logs), 1)
            budget_vs_spending.append(BudgetPoint(label=slot, planned_budget=slot_budget, actual_spent=s_cost))
            daily_expenses_series.append(DailyExpensePoint(date_label=slot, amount_inr=s_cost, calories_kcal=s_kcal, meals_count=len(slot_logs)))
    elif rng == "weekly":
        for offset in range(6, -1, -1):
            d = (now - timedelta(days=offset)).date()
            d_label = d.strftime("%a %d")
            d_logs = [l for l in logs if (l.logged_at or l.created_at).date() == d]
            d_cost = round(sum(float(l.cost_inr or 0.0) for l in d_logs), 2)
            d_kcal = round(sum(float(l.calories_kcal or 0.0) for l in d_logs), 1)
            budget_vs_spending.append(BudgetPoint(label=d_label, planned_budget=daily_budget, actual_spent=d_cost))
            daily_expenses_series.append(DailyExpensePoint(date_label=d_label, amount_inr=d_cost, calories_kcal=d_kcal, meals_count=len(d_logs)))
    else:
        # Monthly: 4 week buckets for budget vs spending + 30-day trend for daily expenses
        week_budget = round(period_budget / 4.0, 2) if budget_configured else 0.0
        for w in range(4):
            w_start = start_dt + timedelta(days=w * 7)
            w_end = start_dt + timedelta(days=(w + 1) * 7 if w < 3 else 30)
            w_logs = [l for l in logs if w_start <= (l.logged_at or l.created_at) < w_end]
            w_cost = round(sum(float(l.cost_inr or 0.0) for l in w_logs), 2)
            budget_vs_spending.append(BudgetPoint(label=f"Week {w + 1}", planned_budget=week_budget, actual_spent=w_cost))
        for offset in range(29, -1, -1):
            d = (now - timedelta(days=offset)).date()
            d_logs = [l for l in logs if (l.logged_at or l.created_at).date() == d]
            d_cost = round(sum(float(l.cost_inr or 0.0) for l in d_logs), 2)
            d_kcal = round(sum(float(l.calories_kcal or 0.0) for l in d_logs), 1)
            daily_expenses_series.append(DailyExpensePoint(date_label=d.strftime("%d %b"), amount_inr=d_cost, calories_kcal=d_kcal, meals_count=len(d_logs)))

    # Weekly 7-day calorie trend (always 7 days up to today for Nutrition Analytics chart)
    seven_days_ago = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_cal_logs = _query_user_logs(db, user, session_id, seven_days_ago, end_dt, cat_id)
    weekly_calorie_trend: List[DailyExpensePoint] = []
    for offset in range(6, -1, -1):
        d = (now - timedelta(days=offset)).date()
        d_logs = [l for l in week_cal_logs if (l.logged_at or l.created_at).date() == d]
        weekly_calorie_trend.append(
            DailyExpensePoint(
                date_label=d.strftime("%a"),
                amount_inr=round(sum(float(l.cost_inr or 0.0) for l in d_logs), 2),
                calories_kcal=round(sum(float(l.calories_kcal or 0.0) for l in d_logs), 1),
                meals_count=len(d_logs),
            )
        )

    # Spending by category (real logged cost per food_category)
    cat_spend_totals: Dict[str, float] = {}
    cat_log_counts: Dict[str, int] = {}
    for l in logs:
        fc = l.food_category or "General Foods"
        cat_spend_totals[fc] = cat_spend_totals.get(fc, 0.0) + float(l.cost_inr or 0.0)
        cat_log_counts[fc] = cat_log_counts.get(fc, 0) + 1

    category_spending = [
        CategorySpendSlice(
            category=k,
            amount_inr=round(v, 2),
            percentage=round((v / total_spent) * 100.0, 1) if total_spent > 0 else 0.0,
        )
        for k, v in sorted(cat_spend_totals.items(), key=lambda x: -x[1])
        if v > 0
    ]

    planned_category_allocation = [
        CategorySpendSlice(
            category=k,
            amount_inr=round(period_budget * w, 2),
            percentage=round(w * 100.0, 1),
        )
        for k, w in cat_def["allocation_weights"].items()
    ]

    active_spending_days = len({(l.logged_at or l.created_at).date() for l in logs if (l.cost_inr or 0.0) > 0})
    avg_daily_spending = round(total_spent / active_spending_days, 2) if active_spending_days > 0 else 0.0

    # Nutrition aggregation
    total_prot = round(sum(float(l.protein_g or 0.0) for l in logs), 1)
    total_carbs = round(sum(float(l.carbs_g or 0.0) for l in logs), 1)
    total_fat = round(sum(float(l.fat_g or 0.0) for l in logs), 1)
    total_fiber = round(sum(float(l.fiber_g or 0.0) for l in logs), 1)
    sugar_entries = [float(l.sugar_g) for l in logs if l.sugar_g is not None]
    sugar_data_available = len(sugar_entries) > 0
    total_sugar = round(sum(sugar_entries), 1) if sugar_data_available else None

    active_nutrition_days = max(1, len({(l.logged_at or l.created_at).date() for l in logs})) if logs else 1
    avg_daily_cals = round(total_calories / active_nutrition_days, 1) if logs else 0.0
    avg_daily_prot = round(total_prot / active_nutrition_days, 1) if logs else 0.0
    avg_daily_carbs = round(total_carbs / active_nutrition_days, 1) if logs else 0.0
    avg_daily_fat = round(total_fat / active_nutrition_days, 1) if logs else 0.0
    avg_daily_fiber = round(total_fiber / active_nutrition_days, 1) if logs else 0.0
    avg_daily_sugar = round(total_sugar / active_nutrition_days, 1) if (logs and total_sugar is not None) else None

    macro_kcal_total = (avg_daily_prot * 4.0) + (avg_daily_carbs * 4.0) + (avg_daily_fat * 9.0)
    if macro_kcal_total > 0:
        macro_distribution = [
            MacroSlice(
                name="Protein",
                grams=avg_daily_prot,
                kcal=round(avg_daily_prot * 4.0, 1),
                percentage=round((avg_daily_prot * 4.0 / macro_kcal_total) * 100.0, 1),
            ),
            MacroSlice(
                name="Carbohydrates",
                grams=avg_daily_carbs,
                kcal=round(avg_daily_carbs * 4.0, 1),
                percentage=round((avg_daily_carbs * 4.0 / macro_kcal_total) * 100.0, 1),
            ),
            MacroSlice(
                name="Fat",
                grams=avg_daily_fat,
                kcal=round(avg_daily_fat * 9.0, 1),
                percentage=round((avg_daily_fat * 9.0 / macro_kcal_total) * 100.0, 1),
            ),
        ]
    else:
        macro_distribution = []

    nutrient_progress = [
        NutrientProgressItem(
            name="Calories",
            category="macro",
            actual=avg_daily_cals,
            goal=float(active_cat_meta.daily_calorie_target),
            unit="kcal",
            percent_achieved=round((avg_daily_cals / active_cat_meta.daily_calorie_target) * 100.0, 1) if active_cat_meta.daily_calorie_target > 0 else 0.0,
            data_available=bool(logs),
        ),
        NutrientProgressItem(
            name="Protein",
            category="macro",
            actual=avg_daily_prot,
            goal=active_cat_meta.protein_goal_g,
            unit="g",
            percent_achieved=round((avg_daily_prot / active_cat_meta.protein_goal_g) * 100.0, 1) if active_cat_meta.protein_goal_g > 0 else 0.0,
            data_available=bool(logs),
        ),
        NutrientProgressItem(
            name="Carbohydrates",
            category="macro",
            actual=avg_daily_carbs,
            goal=active_cat_meta.carbs_goal_g,
            unit="g",
            percent_achieved=round((avg_daily_carbs / active_cat_meta.carbs_goal_g) * 100.0, 1) if active_cat_meta.carbs_goal_g > 0 else 0.0,
            data_available=bool(logs),
        ),
        NutrientProgressItem(
            name="Fat",
            category="macro",
            actual=avg_daily_fat,
            goal=active_cat_meta.fat_goal_g,
            unit="g",
            percent_achieved=round((avg_daily_fat / active_cat_meta.fat_goal_g) * 100.0, 1) if active_cat_meta.fat_goal_g > 0 else 0.0,
            data_available=bool(logs),
        ),
        NutrientProgressItem(
            name="Fiber",
            category="macro",
            actual=avg_daily_fiber,
            goal=active_cat_meta.fiber_goal_g,
            unit="g",
            percent_achieved=round((avg_daily_fiber / active_cat_meta.fiber_goal_g) * 100.0, 1) if active_cat_meta.fiber_goal_g > 0 else 0.0,
            data_available=bool(logs),
        ),
        NutrientProgressItem(
            name="Sugar",
            category="macro",
            actual=avg_daily_sugar,
            goal=30.0,
            unit="g",
            percent_achieved=round((avg_daily_sugar / 30.0) * 100.0, 1) if avg_daily_sugar is not None else None,
            data_available=sugar_data_available,
            note=None if sugar_data_available else "Sugar values not included in ICMR/USDA reference rows; enter when logging custom items.",
        ),
    ]

    # Micronutrients (Vitamins & Minerals) summed from real logged micronutrients vs Nutrient RDA table
    micro_totals: Dict[str, float] = {}
    for l in logs:
        mj = l.micronutrients_json or {}
        if isinstance(mj, dict):
            for n_name, info in mj.items():
                if isinstance(info, dict):
                    micro_totals[n_name] = micro_totals.get(n_name, 0.0) + float(info.get("amount", 0.0))

    db_nutrients = db.query(Nutrient).all()
    vitamins_summary: List[NutrientProgressItem] = []
    minerals_summary: List[NutrientProgressItem] = []
    for n in db_nutrients:
        daily_val = round(micro_totals.get(n.name, 0.0) / active_nutrition_days, 2) if logs else 0.0
        rda = float(n.daily_rda_adult) if n.daily_rda_adult else None
        pct = round((daily_val / rda) * 100.0, 1) if (rda and logs) else 0.0
        item = NutrientProgressItem(
            name=n.name,
            category=n.category,
            actual=daily_val,
            goal=rda,
            unit=n.unit or "mg",
            percent_achieved=pct,
            data_available=bool(logs),
        )
        if n.category == "vitamin":
            vitamins_summary.append(item)
        else:
            minerals_summary.append(item)

    # Category recommendations & suggested meals
    recommended_foods = _rank_category_foods(db, cat_def, search=search, limit=8)
    suggested_meals = _generate_category_suggested_meals(cat_def, profile, daily_budget)

    # Smart Insights computed strictly from real data
    insights: List[InsightItem] = []
    if budget_configured:
        if remaining_budget >= 0:
            insights.append(
                InsightItem(
                    id="budget-remaining",
                    type="budget",
                    severity="info" if utilization_pct < 80 else "warning",
                    title=f"Budget Remaining ({rng.capitalize()})",
                    detail=f"₹{remaining_budget:,.0f} remaining out of ₹{period_budget:,.0f} ({utilization_pct:.1f}% utilized).",
                )
            )
        else:
            insights.append(
                InsightItem(
                    id="budget-exceeded",
                    type="budget",
                    severity="warning",
                    title="Budget Limit Exceeded",
                    detail=f"Spending is ₹{abs(remaining_budget):,.0f} above your ₹{period_budget:,.0f} {rng} budget.",
                )
            )
    else:
        insights.append(
            InsightItem(
                id="budget-unset",
                type="empty",
                severity="info",
                title="Set Your Monthly Budget",
                detail="Configure a monthly budget in Settings or Budget Planner to track spending utilization and savings.",
            )
        )

    if logs:
        below_goals = [
            np for np in nutrient_progress + vitamins_summary + minerals_summary
            if np.data_available and np.percent_achieved is not None and np.percent_achieved < 70.0 and np.name != "Sugar"
        ]
        if below_goals:
            top_gaps = ", ".join(f"{b.name} ({b.percent_achieved:.0f}%)" for b in below_goals[:4])
            insights.append(
                InsightItem(
                    id="nutrient-gaps",
                    type="nutrition",
                    severity="warning",
                    title="Nutrients Below Daily Goal",
                    detail=f"Logged average is below 70% of goal for: {top_gaps}.",
                )
            )
        top_cat = max(cat_log_counts.items(), key=lambda x: x[1])
        insights.append(
            InsightItem(
                id="frequent-category",
                type="category",
                severity="success",
                title="Most Logged Food Category",
                detail=f"{top_cat[0]} appears in {top_cat[1]} logged {'entry' if top_cat[1] == 1 else 'entries'}, averaging ₹{avg_daily_spending:,.0f}/day on active days.",
            )
        )
    else:
        insights.append(
            InsightItem(
                id="no-logs-yet",
                type="empty",
                severity="info",
                title="No Meals Logged in This Period",
                detail="Use 'Log Meal / Expense' or click 'Log Plan Meals' below to populate live calorie, nutrient, and spending trends.",
            )
        )

    affordable_picks = recommended_foods[:3]
    if affordable_picks:
        picks_str = ", ".join(f"{f['name']} (~₹{f['estimated_price_inr']:.0f})" for f in affordable_picks)
        insights.append(
            InsightItem(
                id="affordable-options",
                type="saving",
                severity="success",
                title=f"Top {cat_def['label']} Picks",
                detail=f"Verified affordable options: {picks_str}.",
            )
        )

    # Notifications based strictly on real status
    notifications: List[NotificationItem] = []
    if budget_configured and utilization_pct >= 85.0:
        notifications.append(
            NotificationItem(
                id="notif-budget-high",
                title="Budget Utilization Alert",
                message=f"You have used {utilization_pct:.1f}% of your {rng} food budget (₹{total_spent:,.0f} of ₹{period_budget:,.0f}).",
                severity="warning",
                timestamp=now,
            )
        )
    if logs and cal_adherence_pct < 60.0:
        notifications.append(
            NotificationItem(
                id="notif-low-cals",
                title="Calorie Intake Below Target",
                message=f"Logged calories are at {cal_adherence_pct:.1f}% of your {period_calorie_target:,} kcal {rng} target.",
                severity="info",
                timestamp=now,
            )
        )
    if not notifications:
        notifications.append(
            NotificationItem(
                id="notif-ready",
                title="FoodGenie Analytics Ready",
                message=(
                    f"Showing real {rng} data for {cat_def['label']}."
                    if logs
                    else "Add a meal log or purchase to track live calories, nutrients, and ₹ spending."
                ),
                severity="success" if logs else "info",
                timestamp=now,
            )
        )

    # Recent Activity feed combining real DB events
    recent_activity: List[ActivityFeedItem] = []
    act_q = db.query(DashboardActivity)
    if user:
        act_q = act_q.filter(DashboardActivity.user_id == user.id)
    elif session_id:
        act_q = act_q.filter(DashboardActivity.user_id.is_(None), DashboardActivity.session_id == session_id)
    else:
        act_q = None

    if act_q is not None:
        for a in act_q.order_by(DashboardActivity.created_at.desc()).limit(12).all():
            recent_activity.append(
                ActivityFeedItem(
                    id=f"act-{a.id}",
                    activity_type=a.activity_type,
                    title=a.title,
                    subtitle=a.subtitle,
                    amount_inr=a.amount_inr,
                    calories_kcal=a.calories_kcal,
                    status=a.status,
                    timestamp=a.created_at,
                )
            )

    if user:
        for r in db.query(Recommendation).filter(Recommendation.user_id == user.id).order_by(Recommendation.created_at.desc()).limit(5).all():
            recent_activity.append(
                ActivityFeedItem(
                    id=f"rec-{r.id}",
                    activity_type="recommendation",
                    title=f"Genie Recommendation: {r.query[:55]}",
                    subtitle=f"Intent: {r.intent or 'nutrition'}",
                    status="completed",
                    timestamp=r.created_at,
                )
            )
        for dp in db.query(DietPlan).filter(DietPlan.user_id == user.id).order_by(DietPlan.created_at.desc()).limit(4).all():
            recent_activity.append(
                ActivityFeedItem(
                    id=f"plan-{dp.id}",
                    activity_type="plan_saved",
                    title=f"Saved Plan: {dp.title}",
                    subtitle=f"{dp.duration_type.capitalize()} • {dp.target_calories_daily} kcal/day",
                    amount_inr=dp.estimated_cost_inr,
                    status="saved",
                    timestamp=dp.created_at,
                )
            )

    recent_activity.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activity = recent_activity[:15]

    saved_plans_count = db.query(DietPlan).filter(DietPlan.user_id == user.id).count() if user else 0
    saved_foods_count = db.query(SavedFood).filter(SavedFood.user_id == user.id).count() if user else 0

    all_cat_metas = [_build_category_metadata(c, base_cals, period_budget) for c in CATEGORY_DEFINITIONS]

    return DashboardOverviewResponse(
        user_name=user_name,
        is_authenticated=bool(user),
        budget_configured=budget_configured,
        date_range=rng,
        selected_category=cat_id,
        period_label=f"Last {days_in_range} day{'s' if days_in_range > 1 else ''}" if rng != "daily" else "Today",
        last_updated=now,
        total_budget_card=total_budget_card,
        total_spent_card=total_spent_card,
        remaining_budget_card=remaining_budget_card,
        total_calories_card=total_calories_card,
        daily_budget_inr=daily_budget,
        weekly_budget_inr=weekly_budget,
        monthly_budget_inr=round(monthly_budget, 2),
        total_food_expenses_inr=total_spent,
        remaining_balance_inr=remaining_budget,
        avg_daily_spending_inr=avg_daily_spending,
        budget_utilization_percent=utilization_pct,
        has_expense_logs=any((l.cost_inr or 0.0) > 0 for l in logs),
        budget_vs_spending=budget_vs_spending,
        daily_expenses_series=daily_expenses_series,
        category_spending=category_spending,
        planned_category_allocation=planned_category_allocation,
        daily_calorie_target=active_cat_meta.daily_calorie_target,
        logged_totals={
            "calories_kcal": total_calories,
            "protein_g": total_prot,
            "carbs_g": total_carbs,
            "fat_g": total_fat,
            "fiber_g": total_fiber,
            "sugar_g": total_sugar,
        },
        logged_daily_average={
            "calories_kcal": avg_daily_cals,
            "protein_g": avg_daily_prot,
            "carbs_g": avg_daily_carbs,
            "fat_g": avg_daily_fat,
            "fiber_g": avg_daily_fiber,
            "sugar_g": avg_daily_sugar,
        },
        has_nutrition_logs=bool(logs),
        sugar_data_available=sugar_data_available,
        macro_distribution=macro_distribution,
        weekly_calorie_trend=weekly_calorie_trend,
        nutrient_progress=nutrient_progress,
        vitamins_summary=vitamins_summary,
        minerals_summary=minerals_summary,
        categories_catalog=all_cat_metas,
        active_category_info=active_cat_meta,
        category_recommended_foods=recommended_foods,
        category_suggested_meals=suggested_meals,
        smart_insights=insights,
        recent_activity=recent_activity,
        notifications=notifications,
        food_logs=logs[:30],
        saved_plans_count=saved_plans_count,
        saved_foods_count=saved_foods_count,
    )

