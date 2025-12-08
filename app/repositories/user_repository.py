# app/repositories/user_repository.py
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate
from app.utils.hashing import hash_password


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user_in: UserCreate) -> User:
        user = User(
            username=user_in.username,
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hash_password(user_in.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
