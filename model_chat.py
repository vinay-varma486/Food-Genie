from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True) # nullable for guest sessions
    session_id = Column(String(100), index=True, nullable=True)
    
    # Query & Response
    user_query = Column(Text, nullable=False)
    genie_response = Column(Text, nullable=False)
    
    # Multilingual & Audio metadata
    language_code = Column(String(10), default="en", nullable=False) # 'en', 'te', 'hi', etc.
    detected_language = Column(String(20), nullable=True)
    is_voice_input = Column(Boolean, default=False)
    is_voice_output = Column(Boolean, default=False)
    voice_duration_sec = Column(Float, nullable=True)
    
    # AI Metadata
    intent = Column(String(100), nullable=True) # hair_health, iron_rich, budget_diet, doctor_lookup, general
    confidence_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_history")

