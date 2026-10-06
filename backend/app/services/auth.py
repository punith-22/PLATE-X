import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from fastapi import HTTPException, Request

JWT_SECRET = os.getenv("PLATE_X_JWT_SECRET", "")
TOKEN_TTL = int(os.getenv("PLATE_X_TOKEN_TTL", "3600"))
ALGORITHM = "HS256"

ROLES = {"admin", "investigator", "viewer"}

def _secret() -> bytes:
    if not JWT_SECRET or len(JWT_SECRET) < 32:
        raise RuntimeError("PLATE_X_JWT_SECRET must be set and at least 32 characters")
    return JWT_SECRET.encode()

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000)
    return "pbkdf2_sha256$310000$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, rounds, salt_b64, digest_b64 = encoded.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

def create_token(username: str, role: str) -> str:
    now = int(time.time())
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = {"sub": username, "role": role, "iat": now, "exp": now + TOKEN_TTL}
    signing = _b64(json.dumps(header, separators=(",", ":")).encode()) + "." + _b64(json.dumps(payload, separators=(",", ":")).encode())
    signature = _b64(hmac.new(_secret(), signing.encode(), hashlib.sha256).digest())
    return signing + "." + signature

def decode_token(token: str) -> dict[str, Any]:
    try:
        header_b64, payload_b64, signature = token.split(".")
        signing = header_b64 + "." + payload_b64
        expected = _b64(hmac.new(_secret(), signing.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("bad signature")
        header = json.loads(_unb64(header_b64))
        payload = json.loads(_unb64(payload_b64))
        if header.get("alg") != ALGORITHM or int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired token")
        if payload.get("role") not in ROLES or not payload.get("sub"):
            raise ValueError("invalid claims")
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def current_user(request: Request) -> dict[str, Any]:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    return decode_token(auth[7:].strip())

def require_roles(*roles: str):
    allowed = set(roles)
    def dependency(request: Request):
        user = current_user(request)
        if user["role"] not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency
