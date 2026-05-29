# backend/routers/gdelt.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import pandas as pd

from backend.services.gdelt_live_poller import (
    run_one_cycle, _read_status, LIVE_PATH,
)

router = APIRouter(prefix="/api/gdelt", tags=["GDELT Live"])


def _coord_quality() -> dict:
    """Lit benin_live.parquet et compte les coord_source."""
    base = {"action_geo": 0, "actor1_geo": 0, "actor2_geo": 0,
            "centroid_adm1": 0, "centroid_country": 0}
    if not LIVE_PATH.exists():
        return base
    try:
        df = pd.read_parquet(LIVE_PATH)
        if "coord_source" not in df.columns:
            return base
        for k, v in df["coord_source"].value_counts().items():
            if k in base:
                base[k] = int(v)
    except Exception:
        pass
    return base


@router.get("/status")
def gdelt_status():
    """Retourne le dernier statut connu du poller GDELT + qualité des coordonnées."""
    status = _read_status()
    status["coord_quality"] = _coord_quality()
    return status


@router.post("/refresh")
def gdelt_refresh():
    """Lance un cycle GDELT immédiatement. Tolère les erreurs réseau sans crasher."""
    try:
        result = run_one_cycle()
        return {
            "status":              result.get("status", "ok"),
            "message":             result.get("message", "Cycle terminé."),
            "world_events_read":   result.get("world_events_read", 0),
            "benin_events_found":  result.get("benin_events_found", 0),
            "benin_events_added":  result.get("benin_events_added", 0),
            "live_total_events":   result.get("live_total_events", 0),
        }
    except Exception as exc:
        return JSONResponse(status_code=200, content={
            "status":             "error",
            "message":            f"Erreur lors du rafraîchissement : {str(exc)[:120]}",
            "world_events_read":  0,
            "benin_events_found": 0,
            "benin_events_added": 0,
            "live_total_events":  0,
        })
