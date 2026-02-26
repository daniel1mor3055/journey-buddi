import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()

ALGORITHM = "HS256"


def create_magic_link_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.magic_link_expire_minutes)
    payload = {
        "sub": email,
        "exp": expire,
        "type": "magic_link",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.magic_link_secret, algorithm=ALGORITHM)


def verify_magic_link_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.magic_link_secret, algorithms=[ALGORITHM])
        if payload.get("type") != "magic_link":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.access_token_expire_days)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload.get("sub")
    except JWTError:
        return None
