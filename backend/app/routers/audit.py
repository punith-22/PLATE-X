from fastapi import APIRouter, Depends
from app.services.auth import require_roles
from app.services.store import rows

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("", dependencies=[Depends(require_roles("admin"))])
def list_audit_events():
    return rows("audit_events")
