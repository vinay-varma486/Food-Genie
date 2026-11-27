from typing import List, Optional
from sqlalchemy.orm import Session
from model_recommendation import Recommendation, DietPlan

def record_recommendation(
    db: Session,
    query: str,
    summary: str,
    intent: str,
    language: str = "en",
    user_id: Optional[int] = None,
    recommended_foods: Optional[list] = None,
    foods_to_avoid: Optional[list] = None,
    cautions: Optional[str] = None
) -> Recommendation:
    rec = Recommendation(
        user_id=user_id,
        query=query,
        summary=summary,
        intent=intent,
        language=language,
        recommended_foods=recommended_foods or [],
        foods_to_avoid=foods_to_avoid or [],
        cautions=cautions
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_recommendations_by_user(db: Session, user_id: int, limit: int = 20) -> List[Recommendation]:
    return db.query(Recommendation).filter(Recommendation.user_id == user_id).order_by(Recommendation.created_at.desc()).limit(limit).all()

def save_diet_plan(
    db: Session,
    title: str,
    duration_type: str,
    budget_tier: str,
    estimated_cost_inr: float,
    target_calories: int,
    meals_data: dict,
    grocery_checklist: list,
    language: str = "en",
    user_id: Optional[int] = None
) -> DietPlan:
    plan = DietPlan(
        user_id=user_id,
        title=title,
        duration_type=duration_type,
        budget_tier=budget_tier,
        estimated_cost_inr=estimated_cost_inr,
        target_calories_daily=target_calories,
        meals_plan_data=meals_data,
        grocery_checklist=grocery_checklist,
        language=language
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

def get_diet_plans_by_user(db: Session, user_id: int) -> List[DietPlan]:
    return db.query(DietPlan).filter(DietPlan.user_id == user_id).order_by(DietPlan.created_at.desc()).all()

def delete_diet_plan(db: Session, plan_id: int, user_id: int) -> bool:
    plan = db.query(DietPlan).filter(DietPlan.id == plan_id, DietPlan.user_id == user_id).first()
    if not plan:
        return False
    db.delete(plan)
    db.commit()
    return True

def update_diet_plan(
    db: Session,
    plan_id: int,
    user_id: int,
    title: Optional[str] = None,
    estimated_cost_inr: Optional[float] = None,
    target_calories_daily: Optional[int] = None,
    meals_plan_data: Optional[object] = None,
    grocery_checklist: Optional[object] = None,
) -> Optional[DietPlan]:
    plan = db.query(DietPlan).filter(DietPlan.id == plan_id, DietPlan.user_id == user_id).first()
    if not plan:
        return None
    if title is not None:
        plan.title = title
    if estimated_cost_inr is not None:
        plan.estimated_cost_inr = estimated_cost_inr
    if target_calories_daily is not None:
        plan.target_calories_daily = target_calories_daily
    if meals_plan_data is not None:
        plan.meals_plan_data = meals_plan_data
    if grocery_checklist is not None:
        plan.grocery_checklist = grocery_checklist
    db.commit()
    db.refresh(plan)
    return plan

