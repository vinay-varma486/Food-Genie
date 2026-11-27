import json
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from deps import get_db, get_optional_user, get_current_user
from model_user import User
from schema_recommendation import (
    RecommendationRequest, RecommendationResponse, DietPlanRequest, DietPlanResponse,
    RestrictionAnalysisRequest, RestrictionAnalysisResponse
)
from genie_service import process_genie_query
from restriction_service import restriction_service
from crud_diet import get_recommendations_by_user, get_diet_plans_by_user

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])

@router.post(
    "/restrictions/analyze",
    response_model=RestrictionAnalysisResponse,
    summary="Analyze personalized food restrictions, allergies, and drug-food interactions",
    description="Evaluates food allergies, intolerances, medical conditions (Diabetes, BP, Thyroid, PCOS, Kidney Stones), and drug interactions (Warfarin, Statins, Levothyroxine) in English, Telugu, Hindi, Tamil, and Kannada."
)
def analyze_restrictions(
    req: RestrictionAnalysisRequest,
    current_user: Optional[User] = Depends(get_optional_user)
):
    lang = req.language
    if isinstance(current_user, User) and current_user.profile and not req.language:
        lang = current_user.profile.preferred_language or "en"

    return restriction_service.analyze_restrictions(
        query=req.query,
        allergies=req.allergies,
        intolerances=req.intolerances,
        medical_conditions=req.medical_conditions,
        medications=req.medications,
        dietary_preference=req.dietary_preference,
        language=lang
    )

@router.get(
    "/restrictions/profile",
    response_model=RestrictionAnalysisResponse,
    summary="Get personalized food restrictions from logged-in user profile",
    description="Cross-references the authenticated user's saved allergies, medical conditions, and dietary preferences against evidence-based clinical restrictions."
)
def get_profile_restrictions(
    language: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    prof = current_user.profile
    lang = language or (prof.preferred_language if prof else "en") or "en"
    
    allergies = [a.allergen_name for a in prof.allergies] if (prof and prof.allergies) else []
    conditions = []
    if prof and prof.health_conditions:
        try:
            parsed = json.loads(prof.health_conditions)
            if isinstance(parsed, list):
                conditions = parsed
            else:
                conditions = [str(parsed)]
        except Exception:
            conditions = [c.strip() for c in prof.health_conditions.split(",") if c.strip()]
            
    diet = prof.dietary_preference if prof else None

    return restriction_service.analyze_restrictions(
        allergies=allergies,
        medical_conditions=conditions,
        dietary_preference=diet,
        language=lang
    )

@router.post(
    "/query",
    response_model=RecommendationResponse,
    summary="Generate personalized AI food recommendation via Genie",
    description="Processes nutritional query in user's language (English, Telugu, Hindi) and returns verified foods, benefits, cautions, and dietary guidance."
)
def get_recommendation(
    rec_req: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    user_id = current_user.id if isinstance(current_user, User) else None
    preferred_lang = current_user.profile.preferred_language if (isinstance(current_user, User) and current_user.profile) else rec_req.language
    return process_genie_query(
        db=db,
        query=rec_req.query,
        user_id=user_id,
        preferred_language=preferred_lang,
        session_id=rec_req.session_id,
        is_voice=rec_req.is_voice,
        selected_food=rec_req.selected_food,
    )

@router.get(
    "/history",
    response_model=List[RecommendationResponse],
    summary="Get user's past AI recommendations history"
)
def get_user_recommendations_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recs = get_recommendations_by_user(db, current_user.id, limit=limit)
    return [
        RecommendationResponse(
            id=r.id,
            query=r.query,
            language=r.language,
            intent=r.intent,
            summary=r.summary,
            recommended_foods=r.recommended_foods or [],
            foods_to_avoid=r.foods_to_avoid or [],
            cautions=r.cautions,
            created_at=r.created_at
        )
        for r in recs
    ]
