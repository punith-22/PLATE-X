from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from app.models import Case, CaseCreate
from app.services.store import insert, row, rows

router = APIRouter(prefix="/cases", tags=["cases"])

@router.post("", response_model=Case)
def create_case(payload: CaseCreate):
    case = Case(id=str(uuid4()), **payload.model_dump())
    insert("cases", {
        "id": case.id,
        "title": case.title,
        "description": case.description,
        "registration": case.registration,
        "status": case.status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return case

@router.get("", response_model=list[Case])
def list_cases():
    return [Case(**item) for item in rows("cases")]

@router.get("/{case_id}", response_model=Case)
def get_case(case_id: str):
    item = row("cases", case_id)
    if not item:
        raise HTTPException(status_code=404, detail="Case not found")
    return Case(**item)
