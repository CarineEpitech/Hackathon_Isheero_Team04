# backend/routers/stt.py
from typing import Optional
from datetime import datetime
import pandas as pd
from fastapi import APIRouter, Query
from backend.services.data_loader import load_historical_data, load_live_data

router = APIRouter(prefix="/api", tags=["STT"])


def _load_combined() -> pd.DataFrame:
    """
    Historique 2025 + données live (benin_live.parquet).
    Déduplication par GLOBALEVENTID.
    Le STT est ainsi calculé sur la fenêtre courante RÉELLE (aujourd'hui - 14j).
    """
    df_hist = load_historical_data()
    df_live = load_live_data()

    if df_live.empty:
        return df_hist

    if df_hist.empty:
        return df_live

    df = pd.concat([df_hist, df_live], ignore_index=True)
    df = df.drop_duplicates(subset=["GLOBALEVENTID"])
    return df


@router.get("/stt")
def stt_scores(ref_date: Optional[str] = Query(None, description="Date de référence YYYY-MM-DD")):
    from backend.services.metrics import compute_all_departments

    df = _load_combined()

    # ref_date explicite → l'utiliser (utile pour replay historique)
    # Sinon → maintenant (système live)
    if ref_date:
        ref = pd.Timestamp(ref_date)
    else:
        ref = datetime.utcnow()

    scores = compute_all_departments(df, ref_date=ref)

    return {
        "scores": scores,
        "count": len(scores),
        "ref_date": ref.isoformat(timespec="seconds"),
        "n_events_total": len(df),
    }
