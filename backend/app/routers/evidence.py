from hashlib import sha256
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.services.auth import require_roles
from app.services.audit import audit
from app.services.evidence import Evidence, EvidenceCreate, create_evidence
from app.services.store import insert, row, rows

router = APIRouter(prefix="/evidence", tags=["evidence"])
MAX_UPLOAD_BYTES = 25 * 1024 * 1024

@router.post("", response_model=Evidence)
def add_evidence(payload: EvidenceCreate, user=Depends(require_roles("admin", "investigator"))):
    evidence = create_evidence(payload)
    if not row("cases", evidence.case_id):
        raise HTTPException(status_code=404, detail="Case not found")
    insert("evidence", evidence.model_dump())
    audit(user, "create", "evidence", evidence.id, {"case_id": evidence.case_id, "filename": evidence.filename, "source": evidence.source})
    return evidence

@router.post("/upload", response_model=Evidence)
async def upload_evidence(
    case_id: str = Form(...),
    source: str = Form("upload"),
    notes: str = Form(""),
    file: UploadFile = File(...),
    user=Depends(require_roles("admin", "investigator")),
):
    if not row("cases", case_id):
        raise HTTPException(status_code=404, detail="Case not found")
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    digest = sha256()
    total = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Evidence file exceeds 25 MiB limit")
        digest.update(chunk)
    evidence = Evidence(
        id=str(uuid4()),
        case_id=case_id,
        filename=file.filename[:255],
        sha256=digest.hexdigest(),
        source=source[:100] or "upload",
        notes=notes[:2000] or None,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    insert("evidence", evidence.model_dump())
    audit(user, "upload", "evidence", evidence.id, {"case_id": case_id, "filename": evidence.filename, "size_bytes": total, "content_type": file.content_type})
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
