# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from app.config import settings

DATABASE_URL = settings.DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()   # <-- THIS MUST EXIST


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
