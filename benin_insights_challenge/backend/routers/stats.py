# backend/routers/stats.py
from fastapi import APIRouter
from backend.services.data_loader import load_historical_data, safe_column

router = APIRouter(prefix="/api", tags=["Statistiques"])

SECURITY_ROOTS = {13, 14, 15, 17, 18, 19, 20}


@router.get("/stats")
def stats():
    df = load_historical_data()

    # Security events
    root_col = safe_column(df, "EventRootCode", 0)
    try:
        security_mask = root_col.astype(str).str.extract(r"(\d+)")[0].astype(float).isin(SECURITY_ROOTS)
    except Exception:
        security_mask = root_col.isin(SECURITY_ROOTS)

    n_total    = len(df)
    n_security = int(security_mask.sum())

    # Geolocated (non-generic centroid)
    lat_col = safe_column(df, "ActionGeo_Lat", None)
    lon_col = safe_column(df, "ActionGeo_Long", None)
    geo_mask = (lat_col.notna()) & (lon_col.notna()) & (lat_col != 9.3077) & (lon_col != 2.3158)
    n_geo = int(geo_mask.sum())

    # Date range
    date_col = safe_column(df, "SQLDATE", None)
    date_min = str(date_col.min()) if date_col is not None else "N/A"
    date_max = str(date_col.max()) if date_col is not None else "N/A"

    # Departments coverage
    adm1_col = safe_column(df, "ActionGeo_ADM1Code", "")
    n_departments = int(adm1_col.str.startswith("BN").sum() > 0)
    departments = sorted(adm1_col[adm1_col.str.startswith("BN", na=False)].unique().tolist())

    return {
        "total_events": n_total,
        "security_events": n_security,
        "security_pct": round(n_security / n_total * 100, 1) if n_total else 0,
        "geolocated_events": n_geo,
        "geolocated_pct": round(n_geo / n_total * 100, 1) if n_total else 0,
        "date_range": {"min": date_min, "max": date_max},
        "departments": departments,
        "columns": list(df.columns),
    }
