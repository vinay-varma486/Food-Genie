from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from deps import get_db, get_optional_user, get_current_user
from model_user import User
from schema_chat import ChatMessageCreate, ChatMessageResponse, ChatHistoryList, ConversationSummary
from genie_service import process_genie_query
from crud_chat import (
    get_chat_history, delete_chat_history,
    get_user_conversations, delete_conversation_by_session
)

router = APIRouter(prefix="/chat", tags=["Genie Chat History"])

@router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="Send message to Genie and receive AI answer",
    description="Processes interactive text query with Genie, stores conversation into PostgreSQL, and responds in active language."
)
def send_chat_message(
    msg_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    user_id = current_user.id if isinstance(current_user, User) else None
    preferred_lang = current_user.profile.preferred_language if (isinstance(current_user, User) and current_user.profile) else msg_in.language
    
    rec_response = process_genie_query(
        db=db,
        query=msg_in.query,
        user_id=user_id,
        preferred_language=preferred_lang,
        session_id=msg_in.session_id,
        is_voice=msg_in.is_voice_input
    )

    # Return latest recorded chat item
    chats = get_chat_history(db, user_id=user_id, session_id=msg_in.session_id, limit=1)
    if chats:
        return chats[0]
    
    from datetime import datetime
    return ChatMessageResponse(
        id=rec_response.id or 1,
        user_query=msg_in.query,
        genie_response=rec_response.summary,
        language_code=rec_response.language,
        detected_language=rec_response.language,
        intent=rec_response.intent,
        is_voice_input=msg_in.is_voice_input,
        is_voice_output=False,
        created_at=datetime.utcnow()
    )

@router.get(
    "/history",
    response_model=List[ChatMessageResponse],
    summary="Retrieve chat history for authenticated user or guest session"
)
def get_user_chat_history(
    session_id: Optional[str] = None,
    order: str = "desc",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    clean_session = str(session_id) if (session_id and not hasattr(session_id, 'default')) else None
    user_id = current_user.id if current_user else None
    return get_chat_history(db, user_id=user_id, session_id=clean_session, skip=skip, limit=limit, order=order)

@router.get(
    "/conversations",
    response_model=List[ConversationSummary],
    summary="Get list of all conversations/sessions for the user"
)
def list_user_conversations(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    user_id = current_user.id if current_user else None
    return get_user_conversations(db, user_id=user_id)

@router.delete(
    "/conversations/{session_id}",
    summary="Delete a single conversation thread by session ID"
)
def remove_conversation(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    user_id = current_user.id if current_user else None
    deleted = delete_conversation_by_session(db, session_id=session_id, user_id=user_id)
    return {"status": "deleted", "session_id": session_id, "deleted_messages": deleted}

@router.delete(
    "/history",
    summary="Delete chat history for authenticated user or guest session",
    description="Deletes all recorded Genie chat messages for the current user or guest session."
)
def clear_user_chat_history(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    clean_session = str(session_id) if (session_id and not hasattr(session_id, 'default')) else None
    user_id = current_user.id if current_user else None
    deleted_count = delete_chat_history(db, user_id=user_id, session_id=clean_session)
    return {"status": "cleared", "deleted_messages": deleted_count}
