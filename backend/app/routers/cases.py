from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from app.models import Case, CaseCreate
from app.services.auth import require_roles
from app.services.audit import audit
from app.services.store import insert, row, rows

router = APIRouter(prefix="/cases", tags=["cases"])

@router.post("", response_model=Case)
def create_case(payload: CaseCreate, user=Depends(require_roles("admin", "investigator"))):
    case = Case(id=str(uuid4()), **payload.model_dump())
    insert("cases", {"id": case.id, "title": case.title, "description": case.description, "registration": case.registration, "status": case.status, "created_at": datetime.now(timezone.utc).isoformat()})
    audit(user, "create", "case", case.id, {"registration": case.registration})
    return case

@router.get("", response_model=list[Case])
def list_cases(user=Depends(require_roles("admin", "investigator", "viewer"))):
    return [Case(**item) for item in rows("cases")]

@router.get("/{case_id}", response_model=Case)
def get_case(case_id: str, user=Depends(require_roles("admin", "investigator", "viewer"))):
    item = row("cases", case_id)
    if not item:
        raise HTTPException(status_code=404, detail="Case not found")
    audit(user, "read", "case", case_id)
    return Case(**item)
