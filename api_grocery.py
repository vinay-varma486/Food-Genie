from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from deps import get_db
from schema_grocery import (
    GroceryBasketRequest, GroceryBasketResponse, GroceryItemResponse
)
from crud_grocery import get_grocery_items
from grocery_service import build_grocery_basket

router = APIRouter(prefix="/grocery", tags=["Grocery Planner"])

@router.get(
    "/items",
    response_model=List[GroceryItemResponse],
    summary="List affordable grocery items and staples",
    description="Returns verified regional prices (in INR) for grains, lentils, fresh produce, and budget hero substitutes."
)
def list_grocery_items(
    category: Optional[str] = None,
    budget_hero_only: bool = False,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    clean_category = str(category) if (category and not hasattr(category, 'default')) else None
    clean_query = str(query) if (query and not hasattr(query, 'default')) else None
    items = get_grocery_items(db, category=clean_category, budget_hero_only=budget_hero_only, query=clean_query)
    return items

@router.post(
    "/basket",
    response_model=GroceryBasketResponse,
    summary="Generate cost-optimized grocery basket with smart food swaps",
    description="Optimizes grocery cart to stay under weekly budget while delivering complete amino acids, vitamins, and minerals."
)
def create_grocery_basket(
    basket_req: GroceryBasketRequest,
    db: Session = Depends(get_db)
):
    return build_grocery_basket(db, basket_req)
