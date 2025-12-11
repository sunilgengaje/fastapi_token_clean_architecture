# app/main.py
import os, base64
from fastapi import FastAPI

from app.database import Base, engine
# import model modules so they register with Base
from app.models.user import User  # noqa: F401
from app.models.item import Item  # noqa: F401
from app.models import logs  # noqa: F401

from app.routers.auth_router import router as auth_router
from app.routers.item_router import router as item_router

import os, base64
from pathlib import Path
from dotenv import load_dotenv
import warnings

# -------------------------
# Deterministic .env load
# -------------------------
# assume .env is at repo root (one level above app/)
project_root = Path(__file__).resolve().parents[1]
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=str(dotenv_path))

# Read AES key env (same names client uses)
key_b64 = os.environ.get("AESGCM_KEY") or os.environ.get("AES_KEY_B64")
if not key_b64:
    warnings.warn("AES env var not found: AESGCM_KEY or AES_KEY_B64 is not set.")
else:
    try:
        key_bytes = base64.b64decode(key_b64)
        # Print only length and a short masked prefix for verification
        masked_prefix = key_b64[:6] + "..." + key_b64[-4:]
        print(f"SERVER: AES env found. decoded length={len(key_bytes)} bytes, key_b64_mask={masked_prefix}")
    except Exception as e:
        warnings.warn(f"Failed to decode AES key on startup: {e}")


Base.metadata.create_all(bind=engine)

app = FastAPI(title="AES-GCM Demo", docs_url="/docs", redoc_url=None, openapi_url="/openapi.json")

# your existing logging middleware (if any)
from app.middleware.logging_middleware import session_logging_middleware
app.middleware("http")(session_logging_middleware)

# AES middleware wiring
try:
    from app.middleware.aes_gcm_middleware import AESGCMMiddleware
    from app.deps import get_aes_key
    aes_key = get_aes_key()
    app.add_middleware(AESGCMMiddleware, aes_key=aes_key, secure_prefix="/secure")
except Exception as e:
    import warnings
    warnings.warn(f"AES middleware not attached: {e}")

# include routers normally (plain JSON)
app.include_router(auth_router)
app.include_router(item_router)

# include same routers under /secure so middleware will handle them
app.include_router(auth_router, prefix="/secure")
app.include_router(item_router, prefix="/secure")

@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}
