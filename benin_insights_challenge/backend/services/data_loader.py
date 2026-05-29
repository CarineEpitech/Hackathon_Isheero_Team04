# backend/services/data_loader.py
from pathlib import Path
import pandas as pd

PROJECT_ROOT  = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REALTIME_DIR  = PROCESSED_DIR / "realtime"
HIST_PARQUET  = PROCESSED_DIR / "benin_enrichi.parquet"
LIVE_PARQUET  = PROCESSED_DIR / "benin_live.parquet"   # sortie du poller GDELT live

_cache: dict = {}


def safe_column(df: pd.DataFrame, name: str, default=None) -> pd.Series:
    if name in df.columns:
        return df[name]
    return pd.Series([default] * len(df), index=df.index)


_EMPTY_COLS = [
    "GLOBALEVENTID", "SQLDATE", "EventRootCode", "EventCode", "GoldsteinScale",
    "NumMentions", "NumSources", "AvgTone", "Actor1Name", "Actor2Name",
    "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FullName", "ActionGeo_ADM1Code",
    "SOURCEURL", "zone_benin", "quadclass_label",
]


def load_historical_data() -> pd.DataFrame:
    if "hist" in _cache:
        return _cache["hist"]
    if not HIST_PARQUET.exists():
        import logging
        logging.getLogger("terroir.data_loader").warning(
            "benin_enrichi.parquet introuvable — retour DataFrame vide."
        )
        return pd.DataFrame(columns=_EMPTY_COLS)
    df = pd.read_parquet(HIST_PARQUET)
    _cache["hist"] = df
    return df


def load_live_data() -> pd.DataFrame:
    """Live GDELT Bénin (30j glissants) → snapshots realtime → historique."""
    # 1. Poller live (benin_live.parquet — mis à jour toutes les 15 min)
    if LIVE_PARQUET.exists():
        return pd.read_parquet(LIVE_PARQUET)
    # 2. Snapshots realtime (ancienne logique de secours)
    if REALTIME_DIR.exists():
        snaps = sorted(REALTIME_DIR.glob("benin_live_*.parquet"), reverse=True)
        if snaps:
            return pd.read_parquet(snaps[0])
    # 3. Fallback historique 2025
    return load_historical_data()


def load_best_data() -> pd.DataFrame:
    """
    Live data quand elle contient des événements géolocalisés,
    sinon historique 2025 (qui a 2101 points avec coordonnées).
    Garantit que la carte a toujours des points à afficher.
    """
    if LIVE_PARQUET.exists():
        try:
            live = pd.read_parquet(LIVE_PARQUET)
            lat = live.get("ActionGeo_Lat", pd.Series(dtype=float))
            if lat.notna().sum() > 0:
                return live
        except Exception:
            pass
    return load_historical_data()
