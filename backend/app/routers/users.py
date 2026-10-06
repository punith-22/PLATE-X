from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.services.auth import hash_password, require_roles
from app.services.store import create_user, get_user, list_users

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9._-]+$")
    password: str = Field(min_length=12, max_length=200)
    role: str = Field(pattern=r"^(admin|investigator|viewer)$")

@router.get("", dependencies=[Depends(require_roles("admin"))])
def users():
    return list_users()

@router.post("", dependencies=[Depends(require_roles("admin"))])
def add_user(payload: UserCreate):
    if get_user(payload.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    create_user(payload.username, hash_password(payload.password), payload.role)
    return {"username": payload.username, "role": payload.role}
