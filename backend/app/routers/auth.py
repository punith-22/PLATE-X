import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.auth import create_token, hash_password, verify_password
from app.services.store import get_user

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=200)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = get_user(payload.username)
    if not user or not user["active"] or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    ttl = int(os.getenv("PLATE_X_TOKEN_TTL", "3600"))
    return TokenResponse(access_token=create_token(user["username"], user["role"]), expires_in=ttl)

@router.get("/me")
def me(user=__import__("fastapi").Depends(__import__("app.services.auth", fromlist=["current_user"]).current_user)):
    return {"username": user["sub"], "role": user["role"], "expires_at": user["exp"]}
