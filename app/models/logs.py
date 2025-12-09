# app/models/logs.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(String(64), primary_key=True, index=True)  # UUID hex string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip = Column(String(50))
    user_agent = Column(String(400))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True)

    user = relationship("User")

class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("user_sessions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(255), nullable=True)   # <-- ADDED
    path = Column(String(1000))
    method = Column(String(10))
    status_code = Column(Integer)
    ip = Column(String(50))
    user_agent = Column(String(400))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    extra = Column(Text, nullable=True)

    session = relationship("UserSession", foreign_keys=[session_id])
