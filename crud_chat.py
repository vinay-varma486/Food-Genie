from typing import List, Optional
from sqlalchemy.orm import Session
from model_chat import ChatHistory

def record_chat_message(
    db: Session,
    user_query: str,
    genie_response: str,
    language_code: str = "en",
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    is_voice_input: bool = False,
    is_voice_output: bool = False,
    detected_language: Optional[str] = None,
    intent: Optional[str] = None
) -> ChatHistory:
    record = ChatHistory(
        user_id=user_id,
        session_id=session_id,
        user_query=user_query,
        genie_response=genie_response,
        language_code=language_code,
        detected_language=detected_language,
        is_voice_input=is_voice_input,
        is_voice_output=is_voice_output,
        intent=intent
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_chat_history(
    db: Session,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    order: str = "desc"
) -> List[ChatHistory]:
    # Never expose other users' records when unauthenticated without a session_id
    if user_id is None and not session_id:
        return []

    q = db.query(ChatHistory)
    if user_id is not None:
        q = q.filter(ChatHistory.user_id == user_id)
    else:
        q = q.filter(ChatHistory.user_id.is_(None))

    if session_id:
        q = q.filter(ChatHistory.session_id == session_id)

    if order == "asc":
        return q.order_by(ChatHistory.created_at.asc(), ChatHistory.id.asc()).offset(skip).limit(limit).all()
    return q.order_by(ChatHistory.created_at.desc(), ChatHistory.id.desc()).offset(skip).limit(limit).all()

def get_user_conversations(db: Session, user_id: Optional[int] = None) -> List[dict]:
    """
    Returns list of distinct chat sessions/conversations for a user,
    with automatic titles derived from the first user query, message counts, and timestamps.
    """
    if not user_id:
        return []

    from sqlalchemy import func
    rows = db.query(
        ChatHistory.session_id,
        func.min(ChatHistory.created_at).label("started_at"),
        func.max(ChatHistory.created_at).label("last_active"),
        func.count(ChatHistory.id).label("message_count")
    ).filter(
        ChatHistory.user_id == user_id,
        ChatHistory.session_id.isnot(None)
    ).group_by(ChatHistory.session_id).order_by(func.max(ChatHistory.created_at).desc()).all()

    conversations = []
    for r in rows:
        session_id = r.session_id
        first_msg = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id,
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.asc(), ChatHistory.id.asc()).first()

        raw_title = first_msg.user_query if first_msg else "Nutrition Chat"
        title = raw_title[:45] + ("..." if len(raw_title) > 45 else "")
        conversations.append({
            "session_id": session_id,
            "title": title,
            "started_at": r.started_at,
            "last_active": r.last_active,
            "message_count": r.message_count,
            "last_message": first_msg.genie_response[:80] + "..." if first_msg and first_msg.genie_response else ""
        })
    return conversations

def delete_conversation_by_session(
    db: Session,
    session_id: str,
    user_id: Optional[int] = None
) -> int:
    q = db.query(ChatHistory).filter(ChatHistory.session_id == session_id)
    if user_id is not None:
        q = q.filter(ChatHistory.user_id == user_id)
    else:
        q = q.filter(ChatHistory.user_id.is_(None))
    deleted = q.delete(synchronize_session=False)
    db.commit()
    return deleted

def delete_chat_history(
    db: Session,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None
) -> int:
    if user_id is None and not session_id:
        return 0
    q = db.query(ChatHistory)
    if user_id is not None:
        q = q.filter(ChatHistory.user_id == user_id)
        if session_id:
            q = q.filter(ChatHistory.session_id == session_id)
    else:
        q = q.filter(ChatHistory.user_id.is_(None), ChatHistory.session_id == session_id)
    deleted = q.delete(synchronize_session=False)
    db.commit()
    return deleted
