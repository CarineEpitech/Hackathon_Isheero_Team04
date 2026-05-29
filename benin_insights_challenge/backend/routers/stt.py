# backend/routers/stt.py
from typing import Optional
import pandas as pd
from fastapi import APIRouter, Query
from backend.services.data_loader import load_historical_data

router = APIRouter(prefix="/api", tags=["STT"])


@router.get("/stt")
def stt_scores(ref_date: Optional[str] = Query(None, description="Date de référence YYYY-MM-DD")):
    from backend.services.metrics import compute_all_departments
    df = load_historical_data()

    # Résolution de la date de référence.
    # Si aucune date fournie → dernière date du dataset (pas datetime.utcnow()).
    # Raison : le dataset historique s'arrête en déc 2025 ; une ref_date en 2026
    # produirait une fenêtre 14j vide → tous les scores à 0.
    if ref_date:
        ref = pd.Timestamp(ref_date)
    elif not df.empty and "SQLDATE" in df.columns:
        ref = pd.Timestamp(df["SQLDATE"].max())
    else:
        ref = None

    scores = compute_all_departments(df, ref_date=ref)
    return {"scores": scores, "count": len(scores)}
