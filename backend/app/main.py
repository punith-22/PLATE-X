import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.health import router as health_router
from app.routers.vehicles import router as vehicles_router
from app.routers.cases import router as cases_router
from app.routers.evidence import router as evidence_router
from app.routers.auth import router as auth_router
from app.routers.audit import router as audit_router
from app.routers.users import router as users_router
from app.services.auth import hash_password
from app.services.store import create_user, get_user, init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if not get_user(os.getenv("PLATE_X_ADMIN_USERNAME", "admin")):
        create_user(os.getenv("PLATE_X_ADMIN_USERNAME", "admin"), hash_password(os.getenv("PLATE_X_ADMIN_PASSWORD", "ChangeMe-Immediately-123!")), "admin")
    yield

origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",") if x.strip()]

app = FastAPI(title="PLATE-X API", description="Privacy-first vehicle investigation and intelligence API.", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(vehicles_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(evidence_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"name":"PLATE-X","version":"1.0.0","status":"operational","storage":"sqlite","owner_data_lookup":"disabled_by_default"}
