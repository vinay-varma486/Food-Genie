"""
Genie AI Nutrition Service
Text-based and voice-enabled nutrition query orchestrator powered by Gemini / OpenRouter
and verified ICMR-NIN / USDA datasets, with user Food Cart and profile context awareness.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from genie_ai_service import genie_ai
from schema_recommendation import RecommendationResponse


def process_genie_query(
    db: Session,
    query: str,
    user_id: Optional[int] = None,
    preferred_language: str = "en",
    session_id: Optional[str] = None,
    is_voice: bool = False,
    selected_food: Optional[Dict[str, Any]] = None,
) -> RecommendationResponse:
    """
    Main entry point for all conversational AI interactions with Genie.
    """
    return genie_ai.generate_friendly_response(
        db=db,
        query=query,
        user_id=user_id,
        preferred_language=preferred_language,
        session_id=session_id,
        is_voice=is_voice,
        selected_food=selected_food,
    )
