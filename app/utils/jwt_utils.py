# app/utils/jwt_utils.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError

from app.config import settings
from app.schemas.auth import TokenData

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: Dict[str, Any],
                        expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise JWTError("Token has no subject")
    return TokenData(username=username)
