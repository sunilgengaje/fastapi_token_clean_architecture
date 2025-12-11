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
