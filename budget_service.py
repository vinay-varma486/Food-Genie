from typing import Dict, Any, List
from schema_budget import BudgetPlanRequest, BudgetPlanResponse, BudgetCategoryAllocation

def generate_budget_plan(request: BudgetPlanRequest) -> BudgetPlanResponse:
    budget = max(request.monthly_budget_inr, 1500.0)
    family = max(request.family_members, 1)
    
    per_person_month = budget / family
    per_person_day = round(per_person_month / 30.0, 2)
    
    if per_person_day < 80.0:
        tier = "Cost Saver (High Nutrition Staples)"
    elif per_person_day <= 180.0:
        tier = "Balanced Vitality (Wholesome Variety)"
    else:
        tier = "Premium Wellness (Diverse & Organic Options)"

    categories = [
        BudgetCategoryAllocation(
            category="Grains & Millets (30%)",
            allocated_inr=round(budget * 0.30, 2),
            percentage=30.0,
            recommended_staples=["Ragi (Finger Millet)", "Jowar Flour", "Brown / Sona Masoori Rice", "Whole Wheat Atta"]
        ),
        BudgetCategoryAllocation(
            category="Pulses, Legumes & Proteins (28%)",
            allocated_inr=round(budget * 0.28, 2),
            percentage=28.0,
            recommended_staples=["Green Moong Dal", "Toor Dal", "Black Chickpeas (Kala Chana)", "Rajma", "Soy Chunks"]
        ),
        BudgetCategoryAllocation(
            category="Fresh Greens & Seasonal Vegetables (22%)",
            allocated_inr=round(budget * 0.22, 2),
            percentage=22.0,
            recommended_staples=["Spinach / Amaranth", "Bottle Gourd / Lauki", "Tomatoes", "Onions", "Carrots"]
        ),
        BudgetCategoryAllocation(
            category="Dairy / Plant Milk & Curd (12%)",
            allocated_inr=round(budget * 0.12, 2),
            percentage=12.0,
            recommended_staples=["Home-set Fresh Curd", "Toned Milk", "Homemade Paneer / Tofu"]
        ),
        BudgetCategoryAllocation(
            category="Seeds, Nuts & Cooking Oils (8%)",
            allocated_inr=round(budget * 0.08, 2),
            percentage=8.0,
            recommended_staples=["Roasted Peanuts", "Flaxseeds", "Mustard / Groundnut Oil", "Sesame Seeds"]
        )
    ]

    hacks = [
        "Swap expensive almonds with raw/roasted peanuts: save 75% on cost while getting identical protein and healthy fats.",
        "Buy whole millets (Ragi, Jowar) in 5kg bags from wholesale mandis rather than branded retail packs.",
        "Sprout green gram (moong) and chickpeas at home — sprouting triples Vitamin C and boosts amino acid availability at zero extra cost.",
        "Visit local Rythu Bazars / Sabzi Mandis in the evening when seasonal leafy greens sell at 30-50% discounts."
    ]

    weekly_breakdown = {
        "week_1_staples_bulk": round(budget * 0.40, 2),
        "week_2_fresh_produce": round(budget * 0.20, 2),
        "week_3_fresh_produce": round(budget * 0.20, 2),
        "week_4_fresh_produce": round(budget * 0.20, 2)
    }

    return BudgetPlanResponse(
        monthly_budget_inr=budget,
        per_person_day_inr=per_person_day,
        dietary_preference=request.dietary_preference,
        tier=tier,
        categories=categories,
        money_saving_hacks=hacks,
        sample_weekly_cost_breakdown=weekly_breakdown,
        language=request.language
    )

