# app/utils/hashing.py
from passlib.context import CryptContext

# Using pbkdf2_sha256 to avoid bcrypt issues on macOS + Python 3.13
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain password safely."""
    if isinstance(password, bytes):
        password = password.decode("utf-8")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if isinstance(plain_password, bytes):
        plain_password = plain_password.decode("utf-8")
    return pwd_context.verify(plain_password, hashed_password)
