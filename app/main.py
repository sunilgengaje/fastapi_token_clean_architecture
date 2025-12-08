# app/main.py
from fastapi import FastAPI

from app.database import Base, engine
from app.models.user import User  # noqa: F401
from app.models.item import Item  # noqa: F401
from app.routers.auth_router import router as auth_router
from app.routers.item_router import router as item_router

# Create tables (for demo; use Alembic in real apps)
Base.metadata.create_all(bind=engine)



app = FastAPI(
    title="Clean Architecture JWT Demo",
    docs_url="/docs",          # 👈 NOT /docs
    redoc_url=None,
    openapi_url="/openapi.json",
)



app.include_router(auth_router)
app.include_router(item_router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}
