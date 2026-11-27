from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from deps import get_db, get_optional_user
from model_user import User
from model_dashboard import FoodLog, DashboardActivity
from model_nutrition import FoodItem
from schema_dashboard import (
    DashboardOverviewResponse,
    FoodLogCreate,
    FoodLogResponse,
    ApplyCategoryMealRequest,
)
from dashboard_service import (
    build_dashboard_overview,
    create_food_log,
    normalize_category,
    CATEGORY_MAP,
    _generate_category_suggested_meals,
    record_activity_event,
)

router = APIRouter(prefix="/dashboard", tags=["Analytics Dashboard"])


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    summary="Get complete live dashboard analytics, budget tracking, nutrition metrics, and category view",
)
def get_dashboard_overview(
    date_range: str = Query("weekly", pattern="^(daily|weekly|monthly)$"),
    category: str = "all",
    session_id: Optional[str] = None,
    search: Optional[str] = None,
    budget_override: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    return build_dashboard_overview(
        db=db,
        user=current_user,
        date_range=date_range,
        category=category,
        session_id=session_id,
        search=search,
        budget_override=budget_override,
    )


@router.post(
    "/logs",
    response_model=FoodLogResponse,
    summary="Log consumed meal or food expense backed by verified ICMR/USDA database",
)
def log_meal_or_expense(
    log_in: FoodLogCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    try:
        return create_food_log(db=db, log_in=log_in, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/logs/{log_id}",
    summary="Delete a logged meal or food expense",
)
def delete_food_log(
    log_id: int,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    entry = db.query(FoodLog).filter(FoodLog.id == log_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Log entry not found")

    if current_user:
        if entry.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this entry")
    else:
        if not session_id or entry.user_id is not None or entry.session_id != session_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this entry")

    db.delete(entry)
    db.commit()
    return {"status": "deleted", "log_id": log_id}


@router.post(
    "/apply-plan",
    response_model=List[FoodLogResponse],
    summary="Log suggested category meal plan items into active tracking logs",
)
def apply_category_meals_to_log(
    req: ApplyCategoryMealRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    cat_id = normalize_category(req.diet_category)
    cat_def = CATEGORY_MAP[cat_id]
    profile = current_user.profile if current_user else None
    daily_budget = (
        round(float(req.budget_inr) / 30.0, 2)
        if req.budget_inr and req.budget_inr > 0
        else (round(float(profile.monthly_food_budget) / 30.0, 2) if profile and profile.monthly_food_budget else 150.0)
    )
    suggested = _generate_category_suggested_meals(cat_def, profile, daily_budget)
    target_types = {m.lower() for m in req.meal_types} if req.meal_types else None

    created: List[FoodLog] = []
    for slot in suggested:
        if target_types and slot.meal_type.lower() not in target_types:
            continue
        item = FoodLog(
            user_id=current_user.id if current_user else None,
            session_id=req.session_id,
            food_name=slot.food_name,
            food_category=cat_def["label"],
            diet_category=cat_id,
            meal_type=slot.meal_label,
            entry_type="meal",
            quantity_g=150.0,
            servings=1.0,
            cost_inr=slot.estimated_cost_inr,
            calories_kcal=slot.calories_kcal,
            protein_g=slot.protein_g,
            carbs_g=slot.carbs_g,
            fat_g=slot.fat_g,
            fiber_g=slot.fiber_g,
        )
        db.add(item)
        created.append(item)

    db.commit()
    for it in created:
        db.refresh(it)

    if created:
        total_c = round(sum(i.cost_inr for i in created), 2)
        total_k = round(sum(i.calories_kcal for i in created), 1)
        record_activity_event(
            db=db,
            activity_type="nutrition_goal_update",
            title=f"Logged {len(created)} {cat_def['label']} meal(s)",
            subtitle=f"Total ₹{total_c:,.0f} • {total_k:,.0f} kcal",
            amount_inr=total_c,
            calories_kcal=total_k,
            status="completed",
            user_id=current_user.id if current_user else None,
            session_id=req.session_id,
        )

    return created

