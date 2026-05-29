# backend/routers/stt.py
from typing import Optional
from fastapi import APIRouter, Query
from backend.services.data_loader import load_historical_data

router = APIRouter(prefix="/api", tags=["STT"])


@router.get("/stt")
def stt_scores(ref_date: Optional[str] = Query(None, description="Date de référence YYYY-MM-DD")):
    from backend.services.metrics import compute_all_departments
    df = load_historical_data()
    scores = compute_all_departments(df, ref_date=ref_date)
    return {"scores": scores, "count": len(scores)}
