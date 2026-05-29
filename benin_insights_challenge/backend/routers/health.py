# backend/routers/health.py
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Système"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "BeninScope TERROIR API",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
