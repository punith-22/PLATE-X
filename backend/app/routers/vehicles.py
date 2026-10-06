from fastapi import APIRouter, HTTPException
from app.services.plate import normalize_plate, validate_plate, state_code
from app.services.rto import identify_rto

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/{registration}")
def lookup_vehicle(registration: str):
    try:
        plate = normalize_plate(registration)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    valid = validate_plate(plate)
    return {
        "registration": plate,
        "valid_format": valid,
        "rto": identify_rto(plate) if valid else None,
        "owner_data": "not_available",
        "data_sources": [],
        "message": "Sensitive owner data requires an authorized provider.",
    }
