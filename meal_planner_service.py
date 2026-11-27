from typing import Dict, Any, List
from schema_recommendation import DietPlanRequest, DietPlanResponse

# Scientifically balanced 7-day meal schedules
WEEKLY_MEAL_TEMPLATES = {
    "vegetarian": {
        "monday": {
            "day": "Monday",
            "focus": "High Protein Kickstart",
            "breakfast": "Sprouted Green Moong Salad with lime & grated carrot + 1 glass Warm Lemon Water",
            "breakfast_kcal": 280,
            "lunch": "Brown Rice (1 cup) + Toor Dal + Steamed Spinach / Palak with garlic + Fresh Curd",
            "lunch_kcal": 550,
            "snack": "Roasted Bengal Gram (Chana) + Green Tea or Masala Chai",
            "snack_kcal": 180,
            "dinner": "2 Multigrain Ragi Rotis + Mixed Vegetable Curry (Beans, Carrots, Peas) + Moong Dal",
            "dinner_kcal": 490,
            "daily_calories": 1500,
            "daily_protein_g": 62,
            "daily_cost_inr": 110
        },
        "tuesday": {
            "day": "Tuesday",
            "focus": "Iron & Folate Rich Day",
            "breakfast": "Ragi Malt with crushed peanuts & jaggery + 1 Boiled Apple or Guava",
            "breakfast_kcal": 310,
            "lunch": "Sona Masoori Rice + Amaranth / Thotakura Dal + Cucumber Tomato Salad",
            "lunch_kcal": 520,
            "snack": "Soaked Black Raisins & Dates (5-6) + 1 tbsp Roasted Flaxseeds",
            "snack_kcal": 190,
            "dinner": "Whole Wheat Vegetable Daliya (Cracked Wheat Khichdi) with curd",
            "dinner_kcal": 480,
            "daily_calories": 1500,
            "daily_protein_g": 58,
            "daily_cost_inr": 105
        },
        "wednesday": {
            "day": "Wednesday",
            "focus": "Digestive & Prebiotic Fiber",
            "breakfast": "Vegetable Poha (Flattened rice) with roasted peanuts & green peas",
            "breakfast_kcal": 340,
            "lunch": "Jowar Roti (2) + Chana Masala (Chickpeas) + Buttermilk with roasted cumin",
            "lunch_kcal": 560,
            "snack": "1 Fresh Seasonal Banana or Papaya slices",
            "snack_kcal": 120,
            "dinner": "Bottle Gourd (Lauki) & Moong Dal Soup + 1 Multigrain Phulka",
            "dinner_kcal": 450,
            "daily_calories": 1470,
            "daily_protein_g": 56,
            "daily_cost_inr": 95
        },
        "thursday": {
            "day": "Thursday",
            "focus": "Bone Mineral & Calcium Boost",
            "breakfast": "Ragi Dosa (2) with fresh Coconut & Mint Chutney",
            "breakfast_kcal": 350,
            "lunch": "Rajma (Red Kidney Beans) Curry + Steamed Brown Rice + Beetroot Salad",
            "lunch_kcal": 580,
            "snack": "Roasted Peanuts (30g) + 1 Glass Tender Coconut Water or Buttermilk",
            "snack_kcal": 180,
            "dinner": "Methi (Fenugreek) Thepla or Roti (2) + Paneer Bhurji / Tofu with bell peppers",
            "dinner_kcal": 490,
            "daily_calories": 1600,
            "daily_protein_g": 68,
            "daily_cost_inr": 130
        },
        "friday": {
            "day": "Friday",
            "focus": "Antioxidant & Micronutrient Synergy",
            "breakfast": "Oats or Broken Wheat Upma loaded with carrots, beans, and mustard seeds",
            "breakfast_kcal": 310,
            "lunch": "Moringa Leaves (Munagaku) Dal + Steamed Rice + Grilled Tomato Curry",
            "lunch_kcal": 510,
            "snack": "1 Amla (Indian Gooseberry) fresh or juice + Roasted Sesame Chikki",
            "snack_kcal": 150,
            "dinner": "Paneer & Mixed Vegetable Khichdi + Mint Raita",
            "dinner_kcal": 520,
            "daily_calories": 1490,
            "daily_protein_g": 64,
            "daily_cost_inr": 115
        },
        "saturday": {
            "day": "Saturday",
            "focus": "Lean Energy & Sustained Vitality",
            "breakfast": "Moong Dal Cheela (Lentil crepes) with coriander chutney",
            "breakfast_kcal": 330,
            "lunch": "Vegetable Pulao with Soy Chunks + Mixed Sprouts Raita",
            "lunch_kcal": 570,
            "snack": "Handful of roasted pumpkin & sunflower seeds",
            "snack_kcal": 160,
            "dinner": "2 Whole Wheat Phulkas + Palak Dal + Sliced Onions & Lemon",
            "dinner_kcal": 470,
            "daily_calories": 1530,
            "daily_protein_g": 65,
            "daily_cost_inr": 110
        },
        "sunday": {
            "day": "Sunday",
            "focus": "Comfort Wholesome Celebration",
            "breakfast": "Idli (3) with Sambhar (rich in vegetables & dal) + Tomato Chutney",
            "breakfast_kcal": 360,
            "lunch": "Special Vegetable Dum Biryani (prepared in cold-pressed oil) + Boondi/Cucumber Raita",
            "lunch_kcal": 620,
            "snack": "Spiced Roasted Makhana (Foxnuts) + Ginger Tea",
            "snack_kcal": 140,
            "dinner": "Light Vegetable Clear Soup + 2 Jowar Rotis with Baingan Bharta",
            "dinner_kcal": 440,
            "daily_calories": 1560,
            "daily_protein_g": 55,
            "daily_cost_inr": 125
        }
    }
}

def generate_weekly_meal_schedule(request: DietPlanRequest) -> DietPlanResponse:
    diet_key = "vegetarian" # Fallback/standard
    plan = WEEKLY_MEAL_TEMPLATES.get(diet_key, WEEKLY_MEAL_TEMPLATES["vegetarian"])
    
    total_cost_week = sum(d["daily_cost_inr"] for d in plan.values())
    avg_calories = int(sum(d["daily_calories"] for d in plan.values()) / 7)

    grocery_checklist = [
        "Ragi Flour (1 kg)", "Whole Green Moong (1 kg)", "Toor Dal (1 kg)",
        "Brown or Sona Masoori Rice (2 kg)", "Whole Wheat Atta (2 kg)",
        "Fresh Spinach / Amaranth (3 bunches)", "Moringa leaves (1 bunch)",
        "Paneer or Tofu (500g)", "Fresh Curd (2 L)", "Roasted Peanuts & Chana (500g)",
        "Seasonal Vegetables (Carrots, Beans, Lauki, Tomatoes - 3 kg)",
        "Indian Gooseberry / Amla (500g)"
    ]

    return DietPlanResponse(
        title=f"7-Day Balanced {request.dietary_preference.capitalize()} Meal Plan",
        duration_type="weekly",
        budget_tier=request.budget_tier,
        estimated_cost_inr=float(total_cost_week),
        target_calories_daily=avg_calories,
        meals_plan_data=plan,
        grocery_checklist=grocery_checklist,
        language=request.language
    )

