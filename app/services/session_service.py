# app/services/session_service.py
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.logs import UserSession

def create_session(db: Session, user_id: int, ip: str, user_agent: str) -> str:
    session_id = uuid.uuid4().hex
    session = UserSession(id=session_id, user_id=user_id, ip=ip, user_agent=user_agent)
    db.add(session)
    db.commit()
    return session_id

def end_session(db: Session, session_id: str):
    sess = db.query(UserSession).filter(UserSession.id == session_id, UserSession.active == True).first()
    if sess:
        sess.active = False
        sess.ended_at = datetime.utcnow()
        db.add(sess)
        db.commit()
