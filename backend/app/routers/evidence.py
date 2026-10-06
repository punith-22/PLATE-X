from fastapi import APIRouter, HTTPException
from app.models import Case
from app.services.evidence import Evidence, EvidenceCreate, create_evidence

router = APIRouter(prefix="/evidence", tags=["evidence"])
_evidence: dict[str, Evidence] = {}

@router.post("", response_model=Evidence)
def add_evidence(payload: EvidenceCreate):
    evidence = create_evidence(payload)
    _evidence[evidence.id] = evidence
    return evidence

@router.get("", response_model=list[Evidence])
def list_evidence(case_id: str | None = None):
    items = list(_evidence.values())
    if case_id:
        items = [item for item in items if item.case_id == case_id]
    return items

@router.get("/{evidence_id}", response_model=Evidence)
def get_evidence(evidence_id: str):
    evidence = _evidence.get(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence
