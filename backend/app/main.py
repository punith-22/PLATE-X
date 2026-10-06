from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers.health import router as health_router
from app.routers.vehicles import router as vehicles_router
from app.routers.cases import router as cases_router
from app.routers.evidence import router as evidence_router
from app.services.store import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="PLATE-X API",
    description="Privacy-first vehicle investigation and intelligence API.",
    version="0.4.0",
    lifespan=lifespan,
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(vehicles_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(evidence_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "name": "PLATE-X",
        "version": "0.4.0",
        "status": "operational",
        "storage": "sqlite",
        "owner_data_lookup": "disabled_by_default",
    }
