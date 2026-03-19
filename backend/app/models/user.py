from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255))
    password_hash = Column(String(255))
    encryption_key = Column(Text)