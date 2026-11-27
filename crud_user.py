from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from model_user import User, UserProfile, Allergy
from schema_user import UserCreate, UserProfileUpdate, AllergySchema
from security import get_password_hash

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    clean = (email or "").strip().lower()
    return db.query(User).filter(func.lower(User.email) == clean).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserCreate, is_active: bool = True, commit: bool = True) -> User:
    clean_email = user_in.email.strip().lower()
    hashed_pwd = get_password_hash(user_in.password)
    derived_name = (user_in.full_name or "").strip() or (clean_email.split('@')[0].capitalize() if '@' in clean_email else clean_email)
    db_user = User(
        email=clean_email,
        hashed_password=hashed_pwd,
        full_name=derived_name,
        is_active=is_active,
    )
    db.add(db_user)
    db.flush()

    # Automatically initialize user profile
    db_profile = UserProfile(
        user_id=db_user.id,
        preferred_language=user_in.preferred_language or "en",
        dietary_preference=user_in.dietary_preference or "vegetarian",
        age=user_in.age,
        monthly_food_budget=user_in.monthly_food_budget or 5000.0,
        health_goals=user_in.health_goals,
        health_conditions=user_in.health_conditions
    )
    db.add(db_profile)
    db.flush()

    if user_in.allergies:
        for allergen in user_in.allergies:
            db_allergy = Allergy(
                profile_id=db_profile.id,
                allergen_name=allergen,
                severity="moderate"
            )
            db.add(db_allergy)

    if commit:
        db.commit()
        db.refresh(db_user)
    return db_user

def get_profile_by_user_id(db: Session, user_id: int) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

def update_user_profile(db: Session, user_id: int, profile_in: UserProfileUpdate) -> Optional[UserProfile]:
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    if "full_name" in update_data:
        new_name = update_data.pop("full_name")
        user = get_user_by_id(db, user_id)
        if user and new_name is not None:
            user.full_name = new_name.strip() or user.full_name

    allergies_list = update_data.pop("allergies", None)

    for field, value in update_data.items():
        if hasattr(profile, field):
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    if "monthly_food_budget" in update_data and update_data["monthly_food_budget"] is not None:
        from model_dashboard import DashboardActivity
        db.add(
            DashboardActivity(
                user_id=user_id,
                activity_type="budget_update",
                title="Updated Monthly Food Budget",
                subtitle=f"Monthly allocation set to ₹{float(update_data['monthly_food_budget']):,.0f}",
                amount_inr=float(update_data["monthly_food_budget"]),
                status="updated",
            )
        )
        db.commit()
    elif "daily_calorie_target" in update_data or "health_goals" in update_data:
        from model_dashboard import DashboardActivity
        db.add(
            DashboardActivity(
                user_id=user_id,
                activity_type="nutrition_goal_update",
                title="Updated Nutrition Targets",
                subtitle=f"Goal: {profile.health_goals or 'balanced'} • {profile.daily_calorie_target or 2000} kcal/day",
                calories_kcal=float(profile.daily_calorie_target or 2000),
                status="updated",
            )
        )
        db.commit()

    if allergies_list is not None:
        db.query(Allergy).filter(Allergy.profile_id == profile.id).delete(synchronize_session=False)
        for allergen in allergies_list:
            clean_alg = str(allergen).strip()
            if clean_alg:
                db.add(Allergy(
                    profile_id=profile.id,
                    allergen_name=clean_alg,
                    severity="moderate"
                ))
        db.commit()
        db.refresh(profile)

    return profile

def update_user_language(db: Session, user_id: int, language_code: str) -> Optional[UserProfile]:
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id, preferred_language=language_code)
        db.add(profile)
    else:
        profile.preferred_language = language_code
    db.commit()
    db.refresh(profile)
    return profile

def add_user_allergy(db: Session, profile_id: int, allergy_in: AllergySchema) -> Allergy:
    allergy = Allergy(
        profile_id=profile_id,
        allergen_name=allergy_in.allergen_name,
        severity=allergy_in.severity,
        notes=allergy_in.notes
    )
    db.add(allergy)
    db.commit()
    db.refresh(allergy)
    return allergy

def get_user_allergies(db: Session, profile_id: int) -> List[Allergy]:
    return db.query(Allergy).filter(Allergy.profile_id == profile_id).all()

