# app/middleware/logging_middleware.py
from fastapi import Request
from starlette.responses import Response
from sqlalchemy.orm import Session
import traceback
from app.database import SessionLocal
from app.models.logs import AccessLog, UserSession
from app.utils.logging_utils import (
    append_rotating_log,
    append_session_text,
    append_session_xlsx,
)
from datetime import datetime

async def session_logging_middleware(request: Request, call_next):
    db: Session = SessionLocal()
    try:
        # call downstream handlers
        response: Response = await call_next(request)
        status = response.status_code

        # gather info (safe ip extraction)
        xff = request.headers.get("x-forwarded-for")
        if xff:
            ip = xff.split(",")[0].strip()
        else:
            client = getattr(request, "client", None)
            ip = client.host if client else "unknown"
        ua = request.headers.get("user-agent", "unknown")
        session_id = request.cookies.get("session_id")

        # find active session row and derive username/user_id
        session_row = None
        username = None
        user_id = None
        if session_id:
            session_row = db.query(UserSession).filter(
                UserSession.id == session_id,
                UserSession.active == True
            ).first()
            if session_row and hasattr(session_row, "user") and session_row.user is not None:
                user = session_row.user
                user_id = getattr(user, "id", None)
                username = getattr(user, "username", None)

        # write DB access log (with username)
        access = AccessLog(
            session_id = session_id if session_row else None,
            user_id = user_id,
            username = username,
            path = request.url.path,
            method = request.method,
            status_code = status,
            ip = ip,
            user_agent = ua,
            extra = None
        )
        db.add(access)
        db.commit()

        # append per-session files (if session exists)
        if session_row:
            ts = datetime.utcnow().isoformat()
            line = (
                f"[{ts}] user={username} user_id={user_id} "
                f"method={request.method} path={request.url.path} "
                f"status={status} ip={ip} ua={ua}"
            )
            try:
                append_session_text(session_id, line)
                append_session_xlsx(session_id, [ts, username, user_id, request.method, request.url.path, status, ip, ua, ""])
            except Exception:
                traceback.print_exc()

        # append to global rotating log (include username in extra)
        try:
            extra = f"user={username} user_id={user_id}" if username or user_id else None
            append_rotating_log(
                method=request.method,
                path=request.url.path,
                status=status,
                ip=ip,
                ua=ua,
                session_id=session_id,
                extra=extra
            )
        except Exception:
            traceback.print_exc()

        return response
    except Exception:
        traceback.print_exc()
        return Response("Internal server error in logging middleware", status_code=500)
    finally:
        db.close()
