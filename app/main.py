# app/main.py
from fastapi import FastAPI

from app.database import Base, engine
# import model modules so they register with Base
from app.models.user import User  # noqa: F401
from app.models.item import Item  # noqa: F401
from app.models import logs  # noqa: F401  (ensures UserSession & AccessLog are registered)

from app.routers.auth_router import router as auth_router
from app.routers.item_router import router as item_router

# Create tables (dev only; use Alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clean Architecture JWT Demo - with logging",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)

# register logging middleware BEFORE routers
from app.middleware.logging_middleware import session_logging_middleware
app.middleware("http")(session_logging_middleware)

app.include_router(auth_router)
app.include_router(item_router)

@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}
