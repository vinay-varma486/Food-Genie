from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

class ChatMessageCreate(BaseModel):
    query: str
    language: str = "en"
    session_id: Optional[str] = None
    is_voice_input: bool = False

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

class ChatMessageResponse(BaseModel):
    id: int
    user_query: str
    genie_response: str
    language_code: str
    detected_language: Optional[str] = None
    intent: Optional[str] = None
    is_voice_input: bool
    is_voice_output: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatHistoryList(BaseModel):
    total: int
    messages: List[ChatMessageResponse]

class ConversationSummary(BaseModel):
    session_id: str
    title: str
    started_at: datetime
    last_active: datetime
    message_count: int
    last_message: Optional[str] = None


