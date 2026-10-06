from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Optional

class EvidenceCreate(BaseModel):
    case_id: str = Field(min_length=1, max_length=100)
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=5_000_000)
    source: Optional[str] = Field(default="manual", max_length=100)
    notes: Optional[str] = Field(default=None, max_length=2000)

class Evidence(BaseModel):
    id: str
    case_id: str
    filename: str
    sha256: str
    source: str
    notes: Optional[str] = None
    created_at: str

def create_evidence(payload: EvidenceCreate) -> Evidence:
    digest = sha256(payload.content.encode("utf-8")).hexdigest()
    return Evidence(
        id=str(uuid4()),
        case_id=payload.case_id,
        filename=payload.filename,
        sha256=digest,
        source=payload.source or "manual",
        notes=payload.notes,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
