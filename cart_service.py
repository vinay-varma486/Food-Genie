from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from model_user import User
from model_cart import UserCart, UserCartItem
from model_nutrition import FoodItem, FoodNutrient
from crud_diet import save_diet_plan
from dashboard_service import record_activity_event
from nutrition_service import NutritionRAGRetriever
from schema_cart import (
    CartItemAddRequest,
    CartItemUpdateRequest,
    CartItemResponse,
    CartTotalsSummary,
    CartSaveRequest,
    CartResponse,
)

MEAL_SLOTS_ORDER = ["Breakfast", "Morning Snack", "Lunch", "Evening Snacks", "Dinner"]


def normalize_meal_category(raw: Optional[str]) -> str:
    val = (raw or "").strip().lower()
    if "breakfast" in val:
        return "Breakfast"
    if "morning" in val:
        return "Morning Snack"
    if "evening" in val or "snack" in val:
        return "Evening Snacks"
    if "dinner" in val or "night" in val:
        return "Dinner"
    return "Lunch"


def get_or_create_user_cart(db: Session, user_id: int) -> UserCart:
    cart = db.query(UserCart).filter(UserCart.user_id == user_id).first()
    if not cart:
        cart = UserCart(user_id=user_id, title="My Food Cart")
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _to_item_response(item: UserCartItem) -> CartItemResponse:
    qty = float(item.quantity or 1.0)
    return CartItemResponse(
        id=item.id,
        food_id=item.food_id,
        food_name=item.food_name,
        image_url=item.image_url,
        meal_category=item.meal_category,
        quantity=round(qty, 2),
        serving_size=item.serving_size or "1 serving",
        calories_per_unit=round(item.calories_per_unit or 0.0, 1),
        protein_per_unit=round(item.protein_per_unit or 0.0, 1),
        carbs_per_unit=round(item.carbs_per_unit or 0.0, 1),
        fat_per_unit=round(item.fat_per_unit or 0.0, 1),
        fiber_per_unit=round(item.fiber_per_unit or 0.0, 1),
        estimated_price_inr_per_unit=round(item.estimated_price_inr_per_unit or 0.0, 2),
        price_type=item.price_type or "estimated_market_price",
        total_calories=round((item.calories_per_unit or 0.0) * qty, 1),
        total_protein_g=round((item.protein_per_unit or 0.0) * qty, 1),
        total_carbs_g=round((item.carbs_per_unit or 0.0) * qty, 1),
        total_fat_g=round((item.fat_per_unit or 0.0) * qty, 1),
        total_fiber_g=round((item.fiber_per_unit or 0.0) * qty, 1),
        total_estimated_cost_inr=round((item.estimated_price_inr_per_unit or 0.0) * qty, 2),
        vitamins_summary=list(item.vitamins_summary or []),
        minerals_summary=list(item.minerals_summary or []),
        health_benefits=item.health_benefits,
        notes=item.notes,
        created_at=item.created_at,
    )


def build_cart_response(db: Session, user: User) -> CartResponse:
    cart = get_or_create_user_cart(db, user.id)
    item_resps = [_to_item_response(it) for it in cart.items]

    grouped: Dict[str, List[CartItemResponse]] = {slot: [] for slot in MEAL_SLOTS_ORDER}
    for ir in item_resps:
        slot = normalize_meal_category(ir.meal_category)
        grouped.setdefault(slot, []).append(ir)

    total_cals = round(sum(i.total_calories for i in item_resps), 1)
    total_prot = round(sum(i.total_protein_g for i in item_resps), 1)
    total_carbs = round(sum(i.total_carbs_g for i in item_resps), 1)
    total_fat = round(sum(i.total_fat_g for i in item_resps), 1)
    total_fiber = round(sum(i.total_fiber_g for i in item_resps), 1)
    total_cost = round(sum(i.total_estimated_cost_inr for i in item_resps), 2)
    total_units = round(sum(i.quantity for i in item_resps), 2)

    profile = user.profile
    daily_cal_target = int(profile.daily_calorie_target or 2000) if profile else 2000
    daily_budget = round(float(profile.monthly_food_budget or 5000.0) / 30.0, 2) if profile else 166.67

    totals = CartTotalsSummary(
        total_items=len(item_resps),
        total_units=total_units,
        total_calories=total_cals,
        total_protein_g=total_prot,
        total_carbs_g=total_carbs,
        total_fat_g=total_fat,
        total_fiber_g=total_fiber,
        total_estimated_cost_inr=total_cost,
        daily_calorie_target=daily_cal_target,
        daily_budget_inr=daily_budget,
        calorie_target_percent=round((total_cals / daily_cal_target) * 100.0, 1) if daily_cal_target > 0 else 0.0,
    )

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        title=cart.title,
        notes=cart.notes,
        updated_at=cart.updated_at or datetime.utcnow(),
        items=item_resps,
        grouped_meals=grouped,
        totals=totals,
    )


def add_item_to_cart(db: Session, user: User, req: CartItemAddRequest) -> CartResponse:
    cart = get_or_create_user_cart(db, user.id)
    meal_slot = normalize_meal_category(req.meal_category)
    guide = NutritionRAGRetriever.FOOD_PRICE_CONSUMPTION_GUIDE

    food_obj: Optional[FoodItem] = None
    if req.food_id:
        food_obj = db.query(FoodItem).filter(FoodItem.id == req.food_id).first()

    if food_obj:
        sw = food_obj.serving_weight_g or 100.0
        scale = sw / 100.0
        info = guide.get(food_obj.name, {})
        food_name = food_obj.name
        image_url = req.image_url or food_obj.image_url
        serving_size = req.serving_size or food_obj.serving_size or info.get("qty") or "1 serving"
        cals = req.calories_per_unit if req.calories_per_unit is not None else round((food_obj.calories_kcal or 0.0) * scale, 1)
        prot = req.protein_per_unit if req.protein_per_unit is not None else round((food_obj.protein_g or 0.0) * scale, 1)
        carbs = req.carbs_per_unit if req.carbs_per_unit is not None else round((food_obj.carbs_g or 0.0) * scale, 1)
        fat = req.fat_per_unit if req.fat_per_unit is not None else round((food_obj.fat_g or 0.0) * scale, 1)
        fiber = req.fiber_per_unit if req.fiber_per_unit is not None else round((food_obj.fiber_g or 0.0) * scale, 1)
        price = req.estimated_price_inr_per_unit if req.estimated_price_inr_per_unit is not None else float(info.get("price", 15.0))
        benefits = req.health_benefits or food_obj.benefits_summary or "Nutritious wholefood."

        vits, mins = [], []
        fns = db.query(FoodNutrient).filter(FoodNutrient.food_id == food_obj.id).all()
        for fn in fns:
            if not fn.nutrient:
                continue
            label = f"{fn.nutrient.name} ({round(fn.amount_per_100g * scale, 1)}{fn.unit})"
            if fn.nutrient.category == "vitamin":
                vits.append(label)
            else:
                mins.append(label)
        if req.vitamins_summary:
            vits = req.vitamins_summary
        if req.minerals_summary:
            mins = req.minerals_summary
    else:
        if not (req.food_name and req.food_name.strip()):
            raise HTTPException(status_code=400, detail="Either food_id or food_name must be provided.")
        food_name = req.food_name.strip()
        image_url = req.image_url
        serving_size = req.serving_size or "1 serving"
        cals = float(req.calories_per_unit or 0.0)
        prot = float(req.protein_per_unit or 0.0)
        carbs = float(req.carbs_per_unit or 0.0)
        fat = float(req.fat_per_unit or 0.0)
        fiber = float(req.fiber_per_unit or 0.0)
        price = float(req.estimated_price_inr_per_unit or 0.0)
        benefits = req.health_benefits or "Added to personal Food Cart."
        vits = list(req.vitamins_summary or [])
        mins = list(req.minerals_summary or [])

    # Deduplicate: if exact same food + meal slot already exists, increment quantity
    existing: Optional[UserCartItem] = None
    for it in cart.items:
        same_id = food_obj is not None and it.food_id == food_obj.id
        same_name = it.food_name.strip().lower() == food_name.lower()
        if (same_id or same_name) and normalize_meal_category(it.meal_category) == meal_slot:
            existing = it
            break

    if existing:
        existing.quantity = round(min(50.0, float(existing.quantity or 1.0) + float(req.quantity)), 2)
        if req.notes:
            existing.notes = req.notes
        existing.updated_at = datetime.utcnow()
    else:
        db.add(
            UserCartItem(
                cart_id=cart.id,
                food_id=food_obj.id if food_obj else None,
                food_name=food_name,
                image_url=image_url,
                meal_category=meal_slot,
                quantity=float(req.quantity),
                serving_size=serving_size,
                calories_per_unit=cals,
                protein_per_unit=prot,
                carbs_per_unit=carbs,
                fat_per_unit=fat,
                fiber_per_unit=fiber,
                estimated_price_inr_per_unit=price,
                price_type=req.price_type or "estimated_market_price",
                vitamins_summary=vits,
                minerals_summary=mins,
                health_benefits=benefits,
                notes=req.notes,
            )
        )

    cart.updated_at = datetime.utcnow()
    db.commit()
    record_activity_event(
        db=db,
        activity_type="cart_updated",
        title=f"Added {food_name} to Food Cart",
        subtitle=f"{meal_slot} • Qty {req.quantity}",
        amount_inr=round(price * req.quantity, 2),
        calories_kcal=round(cals * req.quantity, 1),
        status="completed",
        user_id=user.id,
    )
    return build_cart_response(db, user)


def update_cart_item(db: Session, user: User, item_id: int, req: CartItemUpdateRequest) -> CartResponse:
    cart = get_or_create_user_cart(db, user.id)
    item = db.query(UserCartItem).filter(UserCartItem.id == item_id, UserCartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found.")

    if req.food_name is not None and req.food_name.strip():
        item.food_name = req.food_name.strip()
    if req.meal_category is not None:
        item.meal_category = normalize_meal_category(req.meal_category)
    if req.quantity is not None:
        item.quantity = float(req.quantity)
    if req.serving_size is not None and req.serving_size.strip():
        item.serving_size = req.serving_size.strip()
    if req.estimated_price_inr_per_unit is not None and req.estimated_price_inr_per_unit >= 0:
        item.estimated_price_inr_per_unit = float(req.estimated_price_inr_per_unit)
    if req.notes is not None:
        item.notes = req.notes

    item.updated_at = datetime.utcnow()
    cart.updated_at = datetime.utcnow()
    db.commit()
    return build_cart_response(db, user)


def remove_cart_item(db: Session, user: User, item_id: int) -> CartResponse:
    cart = get_or_create_user_cart(db, user.id)
    item = db.query(UserCartItem).filter(UserCartItem.id == item_id, UserCartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found.")
    db.delete(item)
    cart.updated_at = datetime.utcnow()
    db.commit()
    return build_cart_response(db, user)


def clear_user_cart(db: Session, user: User) -> CartResponse:
    cart = get_or_create_user_cart(db, user.id)
    db.query(UserCartItem).filter(UserCartItem.cart_id == cart.id).delete(synchronize_session=False)
    cart.updated_at = datetime.utcnow()
    db.commit()
    return build_cart_response(db, user)


def save_user_cart(db: Session, user: User, req: CartSaveRequest) -> Dict[str, object]:
    cart = get_or_create_user_cart(db, user.id)
    if req.title and req.title.strip():
        cart.title = req.title.strip()
    if req.notes is not None:
        cart.notes = req.notes
    cart.updated_at = datetime.utcnow()
    db.commit()

    resp = build_cart_response(db, user)
    saved_plan_id = None
    if req.save_as_meal_plan and resp.items:
        meals_dict = {
            slot.lower().replace(" ", "_"): [
                {
                    "food_name": i.food_name,
                    "quantity": f"{i.quantity} x {i.serving_size}",
                    "calories_kcal": i.total_calories,
                    "protein_g": i.total_protein_g,
                    "estimated_cost_inr": i.total_estimated_cost_inr,
                }
                for i in slot_items
            ]
            for slot, slot_items in resp.grouped_meals.items()
            if slot_items
        }
        plan = save_diet_plan(
            db=db,
            title=cart.title or f"Food Cart Plan ({datetime.utcnow().strftime('%d %b %Y')})",
            duration_type="daily",
            budget_tier="custom_cart",
            estimated_cost_inr=resp.totals.total_estimated_cost_inr,
            target_calories=int(resp.totals.total_calories or resp.totals.daily_calorie_target),
            meals_data=meals_dict,
            grocery_checklist=[
                {
                    "name": i.food_name,
                    "quantity": f"{i.quantity} x {i.serving_size}",
                    "estimated_cost_inr": i.total_estimated_cost_inr,
                }
                for i in resp.items
            ],
            language=user.profile.preferred_language if user.profile else "en",
            user_id=user.id,
        )
        saved_plan_id = plan.id

    record_activity_event(
        db=db,
        activity_type="plan_saved" if saved_plan_id else "cart_updated",
        title=f"Saved Food Cart: {cart.title}",
        subtitle=f"{resp.totals.total_items} items • {resp.totals.total_calories:.0f} kcal",
        amount_inr=resp.totals.total_estimated_cost_inr,
        calories_kcal=resp.totals.total_calories,
        status="saved",
        user_id=user.id,
    )
    return {
        "status": "saved",
        "cart_id": cart.id,
        "saved_plan_id": saved_plan_id,
        "cart": resp,
    }

