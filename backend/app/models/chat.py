from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from app.db.base import Base
from datetime import datetime

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    encrypted_chat = Column(Text)
    mood_score = Column(Integer, default=5)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)