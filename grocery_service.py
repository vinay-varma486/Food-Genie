from typing import List
from sqlalchemy.orm import Session
from crud_grocery import get_grocery_items
from schema_grocery import GroceryBasketRequest, GroceryBasketResponse, GroceryItemResponse

def build_grocery_basket(db: Session, request: GroceryBasketRequest) -> GroceryBasketResponse:
    db_items = get_grocery_items(db, limit=30)
    
    # Calculate affordable staples
    total_cost = sum(item.avg_price_inr for item in db_items[:12]) if db_items else 850.0
    
    smart_swaps = [
        {"swap_from": "Imported Almonds (₹950/kg)", "swap_to": "Native Peanuts (₹140/kg)", "savings": "85% cheaper", "benefit": "Equal protein (25g/100g) and rich monounsaturated fats"},
        {"swap_from": "Rolled Oats (₹280/kg)", "swap_to": "Whole Finger Millet / Ragi (₹45/kg)", "savings": "83% cheaper", "benefit": "3x more calcium and superior glycemic control"},
        {"swap_from": "Imported Chia Seeds (₹650/kg)", "swap_to": "Brown Flaxseeds / Alsi (₹110/kg)", "savings": "80% cheaper", "benefit": "Identical plant-based Omega-3 ALA content"},
        {"swap_from": "Packaged Protein Bars (₹120/bar)", "swap_to": "Roasted Bengal Gram / Chana (₹90/kg)", "savings": "90% cheaper", "benefit": "Zero added preservatives or refined sugars"}
    ]

    items_res = [GroceryItemResponse.model_validate(item) for item in db_items]

    return GroceryBasketResponse(
        total_estimated_cost_inr=float(total_cost),
        budget_limit_inr=request.target_budget_inr,
        savings_vs_premium_inr=round(total_cost * 1.8, 2),
        items_count=len(items_res),
        items=items_res,
        smart_swaps=smart_swaps,
        language=request.language
    )

