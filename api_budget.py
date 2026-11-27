from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from deps import get_db, get_optional_user, get_current_user
from model_user import User
from schema_budget import BudgetPlanRequest, BudgetPlanResponse
from schema_diet_planner import AIDietPlanRequest, AIDietPlanResponse, AIDietPlanUpdate
from budget_service import generate_budget_plan
from ai_budget_planner import ai_budget_planner
from crud_diet import save_diet_plan, get_diet_plans_by_user, delete_diet_plan, update_diet_plan

router = APIRouter(prefix="/budget", tags=["Budget Planner"])

@router.post(
    "/ai-plan",
    response_model=AIDietPlanResponse,
    summary="Generate personalized AI budget diet plan with 5 meals/day, grocery lists & auto-recalculation",
    description="Generates daily, weekly, monthly, or custom diet schedules across 5 meals (breakfast, morning snack, lunch, evening snack, dinner) with quantities, costs, macro/micronutrients, weekly/monthly grocery lists, verified live prices, and auto-recalculation."
)
def generate_ai_budget_diet(
    request: AIDietPlanRequest,
    current_user: Optional[User] = Depends(get_optional_user)
):
    # Auto-inherit preferred language or allergies if authenticated
    if isinstance(current_user, User) and current_user.profile:
        if not request.language:
            request.language = current_user.profile.preferred_language or "en"
        if not request.allergies and current_user.profile.allergies:
            request.allergies = [a.allergen_name for a in current_user.profile.allergies]

    return ai_budget_planner.generate_plan(request)

@router.post(
    "/ai-plan/save",
    summary="Save generated AI budget diet plan to user account",
    description="Saves meal plans, grocery checklists, and budget allocations to the user's permanent profile."
)
def save_ai_budget_plan(
    plan: AIDietPlanResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    saved = save_diet_plan(
        db=db,
        title=plan.title,
        duration_type=plan.budget_duration,
        budget_tier=plan.budget_status,
        estimated_cost_inr=plan.total_expenditure_inr,
        target_calories=int(plan.daily_plans[0].daily_calories if plan.daily_plans else 2000),
        meals_data=[p.model_dump() for p in plan.daily_plans],
        grocery_checklist=[g.model_dump() for g in plan.weekly_grocery_list],
        language=plan.language,
        user_id=current_user.id
    )
    return {"status": "saved", "plan_id": saved.id, "title": saved.title}

@router.get(
    "/plans",
    summary="Get saved diet plans for authenticated user",
    description="Returns all previously saved meal plans, budget breakdowns, and grocery checklists."
)
def get_user_saved_diet_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plans = get_diet_plans_by_user(db, current_user.id)
    return [
        {
            "id": p.id,
            "title": p.title,
            "duration_type": p.duration_type,
            "budget_tier": p.budget_tier,
            "estimated_cost_inr": p.estimated_cost_inr,
            "target_calories_daily": p.target_calories_daily,
            "meals_plan_data": p.meals_plan_data,
            "grocery_checklist": p.grocery_checklist,
            "language": p.language,
            "created_at": p.created_at
        }
        for p in plans
    ]

@router.delete(
    "/plans/{plan_id}",
    summary="Delete a saved diet plan",
    description="Removes a saved meal plan from the user's account."
)
def delete_user_diet_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = delete_diet_plan(db, plan_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Diet plan not found")
    return {"status": "deleted", "plan_id": plan_id}

@router.put(
    "/plans/{plan_id}",
    summary="Update a saved diet plan",
    description="Updates title, meal entries, cost, or grocery checklist of a saved plan."
)
def update_user_diet_plan(
    plan_id: int,
    update_in: AIDietPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = update_diet_plan(
        db=db,
        plan_id=plan_id,
        user_id=current_user.id,
        title=update_in.title,
        estimated_cost_inr=update_in.estimated_cost_inr,
        target_calories_daily=update_in.target_calories_daily,
        meals_plan_data=update_in.meals_plan_data,
        grocery_checklist=update_in.grocery_checklist,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Diet plan not found")
    return {"status": "updated", "plan_id": updated.id, "title": updated.title}

@router.post(
    "/plan",
    response_model=BudgetPlanResponse,
    summary="Generate budget-based nutrition & staples distribution",
    description="Takes monthly food budget in INR, computes per-person daily allocations, staples category distribution, and practical money-saving hacks."
)
def compute_budget_diet(request: BudgetPlanRequest):
    return generate_budget_plan(request)

