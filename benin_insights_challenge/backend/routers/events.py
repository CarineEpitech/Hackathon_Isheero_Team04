# backend/routers/events.py
from typing import Optional
import math
from datetime import datetime, timedelta
from fastapi import APIRouter, Query
import pandas as pd
from backend.services.data_loader import load_best_data, safe_column

router = APIRouter(prefix="/api/events", tags=["Événements"])

SECURITY_ROOTS = {13, 14, 15, 17, 18, 19, 20}

CAMEO_LABELS = {
    "01": "Déclaration verbale", "02": "Appel", "03": "Expression d'intention",
    "04": "Consultation", "05": "Engagement", "06": "Coopération",
    "07": "Fourniture d'aide", "08": "Entente", "09": "Enquête",
    "10": "Demande", "11": "Désapprobation", "12": "Rejet",
    "13": "Menace", "14": "Protestation", "15": "Force militaire",
    "16": "Réduction des relations", "17": "Coercition", "18": "Agression",
    "19": "Violence", "20": "Conflit armé",
}


def _is_security(root_code) -> bool:
    try:
        return int(float(str(root_code))) in SECURITY_ROOTS
    except (ValueError, TypeError):
        return False


def _row_to_event(row) -> dict:
    lat = row.get("ActionGeo_Lat")
    lon = row.get("ActionGeo_Long")
    root = str(row.get("EventRootCode", ""))
    return {
        "id": int(row.get("GLOBALEVENTID", 0)),
        "date": str(row.get("SQLDATE", "")),
        "lat": float(lat) if lat and not math.isnan(float(lat)) else None,
        "lon": float(lon) if lon and not math.isnan(float(lon)) else None,
        "adm1": str(row.get("ActionGeo_ADM1Code", "")),
        "location": str(row.get("ActionGeo_FullName", "")),
        "event_root_code": root,
        "event_code": str(row.get("EventCode", "")),
        "event_label": CAMEO_LABELS.get(root.zfill(2), root),
        "goldstein": float(row.get("GoldsteinScale", 0) or 0),
        "tone": float(row.get("AvgTone", 0) or 0),
        "mentions": int(row.get("NumMentions", 0) or 0),
        "sources": int(row.get("NumSources", 0) or 0),
        "actor1": str(row.get("Actor1Name", "") or ""),
        "actor2": str(row.get("Actor2Name", "") or ""),
        "url": str(row.get("SOURCEURL", "") or ""),
        "is_security": _is_security(root),
        "zone": str(row.get("zone_benin", "") or ""),
        "quadclass": str(row.get("quadclass_label", "") or ""),
        "coord_source": str(row.get("coord_source", "") or ""),
    }


def _is_nigeria_source(url: str) -> bool:
    u = (url or "").lower()
    return ".ng/" in u or ".ng\"" in u or "nigeria" in u or "naij.com" in u


@router.get("/map")
def events_map(
    security_only: bool = Query(False, description="Filtrer uniquement les événements sécuritaires"),
    limit: int = Query(500, ge=1, le=5000),
    adm1: Optional[str] = Query(None, description="Code département BN01-BN18"),
    hours: Optional[int] = Query(None, ge=1, le=8760, description="Fenêtre temporelle en heures"),
    exclude_nigeria: bool = Query(False, description="Exclure les sources médiatiques nigérianes (IDN)"),
):
    df = load_best_data()

    lat_col = safe_column(df, "ActionGeo_Lat", None)
    lon_col = safe_column(df, "ActionGeo_Long", None)
    mask = lat_col.notna() & lon_col.notna()

    if security_only:
        root_col = safe_column(df, "EventRootCode", 0)
        sec_mask = root_col.apply(_is_security)
        mask = mask & sec_mask

    if adm1:
        adm1_col = safe_column(df, "ActionGeo_ADM1Code", "")
        mask = mask & (adm1_col == adm1)

    if hours is not None:
        date_col = safe_column(df, "SQLDATE", None)
        if date_col is not None:
            try:
                dt_col    = pd.to_datetime(date_col, errors="coerce")
                max_dt    = dt_col.max()
                if pd.notna(max_dt):
                    cutoff_dt = max_dt - timedelta(hours=hours)
                    mask = mask & (dt_col >= cutoff_dt)
            except Exception:
                pass

    # IDN : compter les sources nigérianes sur le sous-ensemble filtré (avant exclusion)
    sub_all = df[mask]
    url_col  = safe_column(sub_all, "SOURCEURL", "")
    ng_mask  = url_col.apply(_is_nigeria_source)
    n_total_pre = len(sub_all)
    n_nigeria   = int(ng_mask.sum())
    idn_pct = round(n_nigeria / n_total_pre * 100, 1) if n_total_pre else 0.0

    if exclude_nigeria:
        mask = mask & ~safe_column(df, "SOURCEURL", "").apply(_is_nigeria_source)

    sub    = df[mask].tail(limit)
    events = [_row_to_event(row) for _, row in sub.iterrows()]
    return {
        "count":   len(events),
        "events":  events,
        "idn_pct": idn_pct,
        "nigeria_excluded": exclude_nigeria,
    }


@router.get("/security")
def events_security(limit: int = Query(200, ge=1, le=2000)):
    df = load_best_data()
    root_col = safe_column(df, "EventRootCode", 0)
    mask = root_col.apply(_is_security)
    sub = df[mask].tail(limit)
    events = [_row_to_event(row) for _, row in sub.iterrows()]
    return {"count": len(events), "events": events}


@router.get("/timeline")
def events_timeline():
    df = load_best_data()
    date_col = safe_column(df, "SQLDATE", None)
    root_col = safe_column(df, "EventRootCode", 0)

    if date_col is None:
        return {"timeline": []}

    df2 = df.copy()
    df2["_date"] = date_col.astype(str).str[:10]
    df2["_sec"] = root_col.apply(_is_security)

    by_date = df2.groupby("_date").agg(
        total=("_date", "count"),
        security=("_sec", "sum"),
    ).reset_index()

    timeline = [
        {
            "date": row["_date"],
            "total": int(row["total"]),
            "security": int(row["security"]),
        }
        for _, row in by_date.iterrows()
    ]
    timeline.sort(key=lambda x: x["date"])
    return {"timeline": timeline}
