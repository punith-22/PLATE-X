from fastapi import APIRouter, HTTPException
from app.services.plate import normalize_plate, validate_plate, state_code

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/{registration}")
def lookup_vehicle(registration: str):
    try:
        plate = normalize_plate(registration)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "registration": plate,
        "valid_format": validate_plate(plate),
        "state_code": state_code(plate),
        "owner_data": "not_available",
        "data_sources": [],
        "message": "Sensitive owner data requires an authorized provider.",
    }
