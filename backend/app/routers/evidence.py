from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import require_roles
from app.services.audit import audit
from app.services.evidence import Evidence, EvidenceCreate, create_evidence
from app.services.store import insert, row, rows

router = APIRouter(prefix="/evidence", tags=["evidence"])

@router.post("", response_model=Evidence)
def add_evidence(payload: EvidenceCreate, user=Depends(require_roles("admin", "investigator"))):
    evidence = create_evidence(payload)
    if not row("cases", evidence.case_id):
        raise HTTPException(status_code=404, detail="Case not found")
    insert("evidence", evidence.model_dump())
    audit(user, "create", "evidence", evidence.id, {"case_id": evidence.case_id, "filename": evidence.filename, "source": evidence.source})
    return evidence

@router.get("", response_model=list[Evidence])
def list_evidence(case_id: str | None = None, user=Depends(require_roles("admin", "investigator", "viewer"))):
    items = rows("evidence")
    if case_id:
        items = [item for item in items if item["case_id"] == case_id]
    return [Evidence(**item) for item in items]

@router.get("/{evidence_id}", response_model=Evidence)
def get_evidence(evidence_id: str, user=Depends(require_roles("admin", "investigator", "viewer"))):
    item = row("evidence", evidence_id)
    if not item:
        raise HTTPException(status_code=404, detail="Evidence not found")
    audit(user, "read", "evidence", evidence_id)
    return Evidence(**item)
