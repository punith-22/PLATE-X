from fastapi import FastAPI
from app.routers.health import router as health_router
from app.routers.vehicles import router as vehicles_router

app = FastAPI(
    title="PLATE-X API",
    description="Privacy-first vehicle investigation and intelligence API.",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(vehicles_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "name": "PLATE-X",
        "version": "0.1.0",
        "status": "operational",
        "owner_data_lookup": "disabled_by_default",
    }
