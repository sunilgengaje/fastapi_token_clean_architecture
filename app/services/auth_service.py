# app/services/auth_service.py
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate, UserRead, Token, TokenData
from app.utils.hashing import verify_password
from app.utils.jwt_utils import create_access_token, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.user_repo = UserRepository(self.db)

    def register_user(self, user_in: UserCreate) -> UserRead:
        if self.user_repo.get_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        if self.user_repo.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = self.user_repo.create(user_in)
        return UserRead.model_validate(user)

    def authenticate_user(self, username: str, password: str) -> Optional[UserRead]:
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return UserRead.model_validate(user)

    def create_login_token(self, user: UserRead) -> Token:
        access_token = create_access_token({"sub": user.username})
        return Token(access_token=access_token, token_type="bearer")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserRead:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data: TokenData = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    user = UserRepository(db).get_by_username(token_data.username)
    if not user:
        raise credentials_exception

    return UserRead.model_validate(user)


def get_current_active_user(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
