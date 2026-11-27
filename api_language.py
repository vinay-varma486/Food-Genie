from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from deps import get_db, get_optional_user
from config import settings
from model_user import User
from schema_user import LanguagePreferenceUpdate
from crud_user import update_user_language

router = APIRouter(prefix="/language", tags=["Language Preferences"])

@router.get(
    "/supported",
    response_model=List[Dict[str, str]],
    summary="List all supported languages with native titles and codes"
)
def get_supported_languages():
    return [
        {"code": "en", "name": "English", "native": "English", "flag": "🇬🇧"},
        {"code": "te", "name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
        {"code": "hi", "name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳"},
        {"code": "ta", "name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
        {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ", "flag": "🇮🇳"}
    ]

@router.post(
    "/preference",
    summary="Update and persist user language preference",
    description="Saves user language in PostgreSQL profile so future voice and text Genie interactions stay in this language."
)
def set_language_preference(
    pref: LanguagePreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    if pref.preferred_language not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{pref.preferred_language}' is not supported. Supported: {settings.SUPPORTED_LANGUAGES}"
        )
    
    if isinstance(current_user, User):
        update_user_language(db, current_user.id, pref.preferred_language)

    return {
        "status": "success",
        "preferred_language": pref.preferred_language,
        "persisted_in_db": isinstance(current_user, User)
    }
