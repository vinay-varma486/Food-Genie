from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from deps import get_db, get_current_user
from model_user import User
from schema_user import (
    UserProfileResponse, UserProfileUpdate, AllergySchema
)
from crud_user import update_user_profile, add_user_allergy, get_user_allergies

router = APIRouter(prefix="/profile", tags=["User Profiles"])

@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get user profile details",
    description="Returns detailed user profile including diet type, budget mode, calorie target, and allergies."
)
def get_my_profile(current_user: User = Depends(get_current_user)):
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not configured")
    return current_user.profile

@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update user profile details",
    description="Updates user dietary preferences, monthly food budget, weight, height, and target calories."
)
def update_my_profile(
    profile_in: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = update_user_profile(db, current_user.id, profile_in)
    return profile

@router.post(
    "/me/allergies",
    response_model=AllergySchema,
    status_code=status.HTTP_201_CREATED,
    summary="Add an allergy or food sensitivity",
    description="Stores known allergen triggers (e.g. Peanuts, Lactose, Gluten) to personalize Genie safety warnings."
)
def add_allergy(
    allergy_in: AllergySchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.profile:
        raise HTTPException(status_code=400, detail="Profile must be created before adding allergies")
    return add_user_allergy(db, current_user.profile.id, allergy_in)

@router.get(
    "/me/allergies",
    response_model=List[AllergySchema],
    summary="List all recorded user allergies"
)
def list_my_allergies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.profile:
        return []
    return get_user_allergies(db, current_user.profile.id)

@router.delete(
    "/me",
    summary="Delete account and all associated personal data",
    description="Permanently removes the user account, profile, chat history, saved foods, and diet plans."
)
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from model_dashboard import FoodLog, DashboardActivity
    from model_auth import EmailVerification
    from model_cart import UserCart
    db.query(FoodLog).filter(FoodLog.user_id == current_user.id).delete(synchronize_session=False)
    db.query(DashboardActivity).filter(DashboardActivity.user_id == current_user.id).delete(synchronize_session=False)
    db.query(EmailVerification).filter(EmailVerification.user_id == current_user.id).delete(synchronize_session=False)
    cart = db.query(UserCart).filter(UserCart.user_id == current_user.id).first()
    if cart:
        db.delete(cart)
    db.delete(current_user)
    db.commit()
    return {"status": "success", "message": "Account and all associated personal data successfully deleted"}


