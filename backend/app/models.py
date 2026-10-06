from pydantic import BaseModel, Field
from typing import Optional

class CaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    registration: Optional[str] = Field(default=None, max_length=20)

class Case(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    registration: Optional[str] = None
    status: str = "open"
