"""Security helpers for hashing secrets and minting JWT tokens."""
import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

# Skip bcrypt wrap detection that can raise on some platforms (e.g., musllinux builds).
os.environ.setdefault("PASSLIB_BCRYPT_NO_WRAP_CHECK", "1")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str) -> str:
    """Return a signed JWT encoding the subject and expiration claims."""
    settings = get_settings()
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire_at = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": subject, "exp": expire_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a provided password to its stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Produce a salted hash suitable for persistence."""
    return pwd_context.hash(password)
