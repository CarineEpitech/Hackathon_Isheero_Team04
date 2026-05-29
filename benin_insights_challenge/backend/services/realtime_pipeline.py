"""
Pipeline temps réel : transforme un snapshot GDELT brut (15 min)
en parquet enrichi identique au schéma benin_enrichi.parquet.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "realtime"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ADM1Code → zone géographique Bénin
ADM1_ZONE = {
    # Nord (Borgou, Alibori, Atacora, Donga)
    "BN04": "nord", "BN01": "nord", "BN02": "nord", "BN03": "nord",
    # Centre (Collines, Zou, Plateau, Couffo)
    "BN05": "centre", "BN11": "centre", "BN10": "centre", "BN09": "centre",
    # Sud (Atlantique, Littoral, Ouémé, Mono, Donga-Sud)
    "BN06": "sud",  "BN07": "sud",  "BN08": "sud",  "BN12": "sud",
    "BN13": "sud",  "BN14": "sud",  "BN15": "sud",  "BN16": "sud",
    "BN17": "sud",  "BN18": "sud",
    "BN00": "sud",  # générique pays → défaut sud (biais couverture)
    "BN": "sud",
}

ADM1_LABEL = {
    "BN01": "Alibori",   "BN02": "Atacora",  "BN03": "Donga",
    "BN04": "Borgou",    "BN05": "Collines", "BN06": "Atlantique",
    "BN07": "Littoral",  "BN08": "Ouémé",    "BN09": "Couffo",
    "BN10": "Zou",       "BN11": "Plateau",  "BN12": "Mono",
    "BN13": "Atacora-2", "BN14": "Donga-2",  "BN15": "Borgou-2",
    "BN16": "Alibori-2", "BN17": "Natitingou","BN18": "Parakou",
    "BN00": "Bénin (générique)", "BN": "Bénin (générique)",
}

QUADCLASS_LABEL = {
    1: "cooperation_verbale",
    2: "cooperation_materielle",
    3: "conflit_verbal",
    4: "conflit_materiel",
}

# Codes CAMEO sécurité — utilisés pour le scoring STT
SECURITY_ROOT_CODES = {13, 14, 15, 17, 18, 19, 20}
SECURITY_BASE_CODES = {173, 172, 145, 154, 181, 182, 186, 190, 192, 193}


def _categorize_tone(tone: float) -> str:
    if tone <= -5:   return "tres_negatif"
    if tone <= -1:   return "negatif"
    if tone < 1:     return "neutre"
    if tone < 5:     return "positif"
    return "tres_positif"


def _categorize_goldstein(gs: float) -> str:
    if gs <= -7:    return "tres_conflictuel"
    if gs <= -2:    return "conflictuel"
    if gs < 2:      return "neutre"
    if gs < 7:      return "cooperatif"
    return "tres_cooperatif"


def _extract_domain(url: str) -> str:
    if not url or pd.isna(url):
        return "inconnu"
    try:
        host = url.split("/")[2].lower()
        return host.replace("www.", "")
    except Exception:
        return "inconnu"


def enrich(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Applique le même enrichissement que le pipeline historique.
    Entrée  : DataFrame brut sorti de gdelt_fetcher.fetch_latest_events()
    Sortie  : DataFrame au schéma benin_enrichi.parquet
    """
    if df_raw.empty:
        return pd.DataFrame()

    df = df_raw.copy()

    # ── Normalisation colonnes ────────────────────────────────
    col_map = {
        "GlobalEventID": "GLOBALEVENTID",
        "Day":           "SQLDATE",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # SQLDATE : int YYYYMMDD → datetime
    if "SQLDATE" in df.columns and df["SQLDATE"].dtype != "datetime64[us]":
        df["SQLDATE"] = pd.to_datetime(df["SQLDATE"].astype(str), format="%Y%m%d", errors="coerce")

    # ── Features temporelles ──────────────────────────────────
    df["mois"]        = df["SQLDATE"].dt.month.astype("int32")
    df["trimestre"]   = df["SQLDATE"].dt.quarter.astype("int32")
    df["annee"]       = df["SQLDATE"].dt.year.astype("int32")
    df["mois_annee"]  = df["SQLDATE"].dt.strftime("%Y-%m")
    df["jour_semaine"]= df["SQLDATE"].dt.dayofweek.astype("int32")

    # ── Features qualitatives ────────────────────────────────
    df["ton_categorie"]      = df["AvgTone"].apply(_categorize_tone)
    df["goldstein_categorie"]= df["GoldsteinScale"].apply(_categorize_goldstein)
    df["quadclass_label"]    = df["QuadClass"].map(QUADCLASS_LABEL).fillna("inconnu")

    # ── Géographie ───────────────────────────────────────────
    adm1 = df.get("ActionGeo_ADM1Code", pd.Series(["BN"] * len(df)))
    df["zone_benin"]     = adm1.map(ADM1_ZONE).fillna("sud")
    df["departement"]    = adm1.map(ADM1_LABEL).fillna("Bénin (générique)")

    # ── Source ───────────────────────────────────────────────
    df["source_domaine"] = df["SOURCEURL"].apply(_extract_domain)

    # ── Flag sécurité ────────────────────────────────────────
    df["is_security"] = (
        df["EventRootCode"].isin(SECURITY_ROOT_CODES) |
        df["EventBaseCode"].isin(SECURITY_BASE_CODES)
    ).astype(int)

    # ── Nettoyage types ──────────────────────────────────────
    for col in ["EventRootCode", "EventBaseCode", "EventCode",
                "QuadClass", "NumMentions", "NumSources", "NumArticles"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    for col in ["GoldsteinScale", "AvgTone", "ActionGeo_Lat", "ActionGeo_Long"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def run(df_raw: pd.DataFrame) -> Path:
    """Enrichit et sauvegarde un snapshot. Retourne le chemin du fichier."""
    df = enrich(df_raw)
    if df.empty:
        return None
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    out = PROCESSED_DIR / f"gdelt_benin_enriched_{ts}.parquet"
    df.to_parquet(out, index=False)
    return out


def load_latest_enriched() -> pd.DataFrame:
    """Charge le snapshot enrichi le plus récent (ou le historique si rien de récent)."""
    files = sorted(PROCESSED_DIR.glob("gdelt_benin_enriched_*.parquet"), reverse=True)
    if files:
        return pd.read_parquet(files[0])
    # Fallback sur le dataset historique
    hist = PROJECT_ROOT / "data" / "processed" / "benin_enrichi.parquet"
    if hist.exists():
        return pd.read_parquet(hist)
    return pd.DataFrame()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from gdelt_fetcher import fetch_latest_events
    print("Téléchargement snapshot GDELT...")
    raw = fetch_latest_events(filter_benin=True)
    print(f"  {len(raw)} événements bruts")

    if raw.empty:
        print("  Snapshot vide — test sur 5 lignes du dataset historique")
        raw = pd.read_parquet(PROJECT_ROOT / "data" / "processed" / "benin_enrichi.parquet").head(5)
        raw = raw.rename(columns={"GLOBALEVENTID": "GlobalEventID"})

    df_enriched = enrich(raw)
    print(f"  {len(df_enriched)} lignes enrichies")
    print(f"  Colonnes : {df_enriched.columns.tolist()}")
    print(df_enriched[["SQLDATE", "EventRootCode", "GoldsteinScale",
                        "zone_benin", "departement", "is_security"]].head(5).to_string())
