import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context using Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates password hash."""
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any], 
    tenant_id: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Creates a JWT access token containing subject, tenant_id, and user role."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "tenant_id": str(tenant_id),
        "role": role,
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_meta_signature(raw_body: bytes, signature_header: str, app_secret: str) -> bool:
    """Verifies the X-Hub-Signature-256 header sent by Meta WhatsApp Cloud API webhooks."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    
    expected_hash = hmac.new(
        key=app_secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    received_hash = signature_header.split("sha256=")[1]
    return hmac.compare_digest(expected_hash, received_hash)
