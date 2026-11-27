from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from model_grocery import GroceryItem

def get_grocery_items(
    db: Session,
    category: Optional[str] = None,
    budget_hero_only: bool = False,
    query: Optional[str] = None,
    limit: int = 50
) -> List[GroceryItem]:
    q = db.query(GroceryItem)
    if category:
        q = q.filter(GroceryItem.category.ilike(category))
    if budget_hero_only:
        q = q.filter(GroceryItem.is_budget_hero == True)
    if query:
        search_term = f"%{query}%"
        q = q.filter(
            or_(
                GroceryItem.name.ilike(search_term),
                GroceryItem.name_te.ilike(search_term),
                GroceryItem.name_hi.ilike(search_term)
            )
        )
    return q.limit(limit).all()

