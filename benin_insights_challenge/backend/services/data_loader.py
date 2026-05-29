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


def load_combined_data() -> pd.DataFrame:
    """
    Fusion historique (benin_enrichi.parquet) + live (benin_live.parquet).
    Déduplication par GLOBALEVENTID.
    Source unique pour tous les affichages : carte, graphiques, STT.
    """
    df_hist = load_historical_data()
    if not LIVE_PARQUET.exists():
        return df_hist
    try:
        df_live = pd.read_parquet(LIVE_PARQUET)
    except Exception:
        return df_hist
    if df_live.empty:
        return df_hist
    df = pd.concat([df_hist, df_live], ignore_index=True)
    df = df.drop_duplicates(subset=["GLOBALEVENTID"])
    return df


def load_best_data() -> pd.DataFrame:
    """
    Alias vers load_combined_data() — garantit toujours la vue la plus complète
    (historique jan 2025 → hier + live du jour), dédupliquée.
    Remplace l'ancienne logique 'live si coords sinon historique' qui retournait
    un subset trop réduit quand benin_live.parquet ne contenait que quelques lignes.
    """
    return load_combined_data()
