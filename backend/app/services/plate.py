import re

PLATE_PATTERN = re.compile(r"^[A-Z]{2}\d{1,2}[A-Z]{0,3}\d{1,4}$")

def normalize_plate(value: str) -> str:
    plate = re.sub(r"[^A-Za-z0-9]", "", value).upper()
    if not plate:
        raise ValueError("Registration number cannot be empty.")
    return plate

def validate_plate(value: str) -> bool:
    return bool(PLATE_PATTERN.fullmatch(value))

def state_code(value: str) -> str:
    return normalize_plate(value)[:2]
