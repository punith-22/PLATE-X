from uuid import uuid4
from fastapi import APIRouter, HTTPException
from app.models import Case, CaseCreate

router = APIRouter(prefix="/cases", tags=["cases"])
_cases: dict[str, Case] = {}

@router.post("", response_model=Case)
def create_case(payload: CaseCreate):
    case = Case(id=str(uuid4()), **payload.model_dump())
    _cases[case.id] = case
    return case

@router.get("", response_model=list[Case])
def list_cases():
    return list(_cases.values())

@router.get("/{case_id}", response_model=Case)
def get_case(case_id: str):
    case = _cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
