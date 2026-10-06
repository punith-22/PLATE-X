from datetime import datetime, timezone
from typing import Any
from app.services.store import insert

def audit(user: dict[str, Any], action: str, resource: str, resource_id: str | None = None, metadata: dict[str, Any] | None = None):
    insert("audit_events", {
        "id": __import__("uuid").uuid4().hex,
        "username": user.get("sub", "unknown"),
        "role": user.get("role", "unknown"),
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "metadata": __import__("json").dumps(metadata or {}, separators=(",", ":")),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
