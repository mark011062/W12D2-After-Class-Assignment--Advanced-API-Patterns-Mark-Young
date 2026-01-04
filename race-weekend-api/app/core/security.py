from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import hashlib

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.exceptions.handlers import AppError

# Base passlib context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _bcrypt_safe_input(password: str) -> str:
    """
    bcrypt hard-limits input to 72 BYTES.

    To make password hashing robust (even if some code accidentally calls
    pwd_context.hash() directly), we convert the password into a fixed-length,
    bcrypt-safe string via SHA-256 (64 hex chars).

    Optional: supports a server-side pepper if settings.PASSWORD_PEPPER exists.
    """
    pepper = getattr(settings, "PASSWORD_PEPPER", "")
    raw = f"{password}{pepper}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()  # always 64 chars


# -------------------------------------------------------------------
# HARDENING: wrap the CryptContext methods so *all* hashing/verifying
# goes through _bcrypt_safe_input, even if someone calls pwd_context.hash()
# directly in another module.
# -------------------------------------------------------------------
_original_hash = pwd_context.hash
_original_verify = pwd_context.verify


def _safe_hash(secret: str, *args, **kwargs) -> str:
    safe = _bcrypt_safe_input(secret)
    return _original_hash(safe, *args, **kwargs)


def _safe_verify(secret: str, hashed: str, *args, **kwargs) -> bool:
    safe = _bcrypt_safe_input(secret)
    return _original_verify(safe, hashed, *args, **kwargs)


# Monkeypatch the instance methods (instance-level override)
pwd_context.hash = _safe_hash  # type: ignore[assignment]
pwd_context.verify = _safe_verify  # type: ignore[assignment]


def hash_password(password: str) -> str:
    """
    Hash a password for storage.
    """
    # uses wrapped pwd_context.hash() which pre-hashes safely
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its stored hash.
    """
    # uses wrapped pwd_context.verify() which pre-hashes safely
    return pwd_context.verify(password, hashed)


def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise AppError("unauthorized", "Token expired.", 401)
    except Exception:
        raise AppError("unauthorized", "Invalid token.", 401)
