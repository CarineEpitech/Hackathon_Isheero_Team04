# backend/routers/gdelt.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import pandas as pd

from backend.services.gdelt_live_poller import (
    run_one_cycle, LIVE_PATH, STATUS_PATH,
)

router = APIRouter(prefix="/api/gdelt", tags=["GDELT Live"])


def _read_status() -> dict:
    """
    Lit le fichier JSON de statut persisté par le poller.
    Retourne un dict par défaut si le fichier est absent ou illisible.
    """
    base = {
        "status":              "waiting",
        "message":             "En attente du premier cycle.",
        "last_checked_at":     None,
        "last_processed_file": None,
        "world_events_read":   0,
        "benin_events_found":  0,
        "benin_events_added":  0,
        "live_total_events":   0,
        "last_error":          None,
    }
    if not STATUS_PATH.exists():
        return base
    try:
        import json
        data = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        base.update(data)
    except Exception:
        pass
    return base


def _coord_quality() -> dict:
    """
    Estime la qualité des coordonnées depuis benin_live.parquet
    en analysant ActionGeo_ADM1Code (pas besoin de coord_source).

    Résultat : dict compatible avec gdeltCoordLabel() côté frontend.
      action_geo       → événements précisément géolocalisés (ADM1 ≠ BN/BN00)
      centroid_adm1    → centroïde département (ADM1 = BN00)
      centroid_country → centroïde pays générique (ADM1 = BN ou vide)
    """
    base = {
        "action_geo":        0,
        "actor1_geo":        0,
        "actor2_geo":        0,
        "centroid_adm1":     0,
        "centroid_country":  0,
    }
    if not LIVE_PATH.exists():
        return base
    try:
        df = pd.read_parquet(LIVE_PATH)
        if df.empty:
            return base
        adm1 = (
            df.get("ActionGeo_ADM1Code", pd.Series(dtype=str))
            .astype(str)
            .fillna("BN")
        )
        generic = {"BN", "BN00", "", "nan"}
        base["action_geo"]       = int((adm1.str.startswith("BN") & ~adm1.isin(generic)).sum())
        base["centroid_adm1"]    = int((adm1 == "BN00").sum())
        base["centroid_country"] = int(adm1.isin({"BN", "", "nan"}).sum())
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
            "status":             result.get("status", "ok"),
            "message":            result.get("message", "Cycle terminé."),
            "world_events_read":  result.get("world_events_read", 0),
            "benin_events_found": result.get("benin_events_found", 0),
            "benin_events_added": result.get("benin_events_added", 0),
            "live_total_events":  result.get("live_total_events", 0),
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
