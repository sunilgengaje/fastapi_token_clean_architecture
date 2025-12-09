# app/utils/logging_utils.py
from pathlib import Path
from fastapi import Request
from openpyxl import Workbook, load_workbook
from typing import List
import os

LOG_BASE = Path("logs")
SESSION_DIR = LOG_BASE / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

def ensure_session_folder():
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    return SESSION_DIR

def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    client = getattr(request, "client", None)
    if client:
        return client.host
    return "unknown"

def session_log_path(session_id: str, ext: str = "txt") -> Path:
    ensure_session_folder()
    filename = f"session_{session_id}.{ext}"
    return SESSION_DIR / filename

def append_text_log(session_id: str, line: str):
    p = session_log_path(session_id, "txt")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")

def append_xlsx_log(session_id: str, row: List):
    p = session_log_path(session_id, "xlsx")
    if not p.exists():
        wb = Workbook()
        ws = wb.active
        ws.append(["timestamp", "method", "path", "status", "ip", "user_agent", "extra"])
        ws.append(row)
        wb.save(p)
    else:
        wb = load_workbook(p)
        ws = wb.active
        ws.append(row)
        wb.save(p)
