from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from model_nutrition import FoodItem, Nutrient, FoodNutrient, SavedFood

def get_food_items(
    db: Session,
    query: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[FoodItem]:
    q = db.query(FoodItem)
    if query:
        search_term = f"%{query}%"
        q = q.filter(
            or_(
                FoodItem.name.ilike(search_term),
                FoodItem.name_te.ilike(search_term),
                FoodItem.name_hi.ilike(search_term),
                FoodItem.benefits_summary.ilike(search_term)
            )
        )
    if category:
        cats = [c.strip() for c in category.split(",") if c.strip()]
        if len(cats) > 1:
            q = q.filter(FoodItem.category.in_(cats))
        elif cats:
            q = q.filter(FoodItem.category.ilike(cats[0]))
    return q.offset(skip).limit(limit).all()

def get_food_item_by_id(db: Session, food_id: int) -> Optional[FoodItem]:
    return db.query(FoodItem).filter(FoodItem.id == food_id).first()

def get_food_nutrients(db: Session, food_id: int) -> List[FoodNutrient]:
    return db.query(FoodNutrient).filter(FoodNutrient.food_id == food_id).all()

def get_nutrients(db: Session, category: Optional[str] = None) -> List[Nutrient]:
    q = db.query(Nutrient)
    if category:
        q = q.filter(Nutrient.category == category)
    return q.all()

def save_food_for_user(db: Session, user_id: int, food_id: int, notes: Optional[str] = None) -> SavedFood:
    existing = db.query(SavedFood).filter(
        SavedFood.user_id == user_id,
        SavedFood.food_id == food_id
    ).first()
    if existing:
        if notes:
            existing.notes = notes
            db.commit()
            db.refresh(existing)
        return existing
    
    saved = SavedFood(user_id=user_id, food_id=food_id, notes=notes)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved

def get_saved_foods_by_user(db: Session, user_id: int) -> List[SavedFood]:
    return db.query(SavedFood).filter(SavedFood.user_id == user_id).all()

def remove_saved_food(db: Session, user_id: int, food_id: int) -> bool:
    saved = db.query(SavedFood).filter(
        SavedFood.user_id == user_id,
        SavedFood.food_id == food_id
    ).first()
    if saved:
        db.delete(saved)
        db.commit()
        return True
    return False

