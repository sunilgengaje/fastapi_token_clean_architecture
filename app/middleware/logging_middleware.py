# app/middleware/logging_middleware.py
from fastapi import Request
from starlette.responses import Response
from sqlalchemy.orm import Session
import traceback
from app.database import SessionLocal
from app.models.logs import AccessLog, UserSession
from app.utils.logging_utils import get_client_ip, append_text_log, append_xlsx_log
from datetime import datetime

async def session_logging_middleware(request: Request, call_next):
    db: Session = SessionLocal()
    try:
        response: Response = await call_next(request)
        status = response.status_code

        session_id = request.cookies.get("session_id")
        ip = get_client_ip(request)
        ua = request.headers.get("user-agent", "unknown")

        session_row = None
        if session_id:
            session_row = db.query(UserSession).filter(UserSession.id == session_id, UserSession.active == True).first()

        access = AccessLog(
            session_id = session_id if session_row else None,
            user_id = session_row.user_id if session_row else None,
            path = request.url.path,
            method = request.method,
            status_code = status,
            ip = ip,
            user_agent = ua,
            extra = None
        )
        db.add(access)
        db.commit()

        if session_row:
            ts = datetime.utcnow().isoformat()
            line = f"[{ts}] {request.method} {request.url.path} status={status} ip={ip} ua={ua}"
            try:
                append_text_log(session_id, line)
                append_xlsx_log(session_id, [ts, request.method, request.url.path, status, ip, ua, ""])
            except Exception:
                traceback.print_exc()

        return response
    except Exception:
        traceback.print_exc()
        return Response("Internal server error in logging middleware", status_code=500)
    finally:
        db.close()
