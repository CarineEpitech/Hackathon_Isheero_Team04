"""
gdelt_live_poller.py
====================
Polling GDELT v2 toutes les 15 minutes.
- Si aucun nouvel événement Bénin → rien ne se passe.
- Si nouveaux événements → lignes ajoutées à benin_live.parquet.

Usage standalone :
    python gdelt_live_poller.py

Usage dans FastAPI (lifespan) :
    from backend.services.gdelt_live_poller import start_background_poller
    start_background_poller()
"""

import io
import json
import time
import logging
import threading
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────

BASE_DIR     = Path(__file__).resolve().parents[2]
LIVE_PATH    = BASE_DIR / "data"    / "processed" / "benin_live.parquet"
STATE_PATH   = BASE_DIR / "data"    / "processed" / ".gdelt_last_processed.txt"
STATUS_PATH  = BASE_DIR / "backend" / "data"      / "gdelt_status.json"
POLL_SECONDS = 900

LASTUPDATE_URL = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [GDELT-LIVE] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("gdelt_live")

# ── MAPPING CSV GDELT v2 (61 colonnes, 0-indexé) ─────────────────────────────
#
# Blocs géo : 8 colonnes chacun (Type, FullName, CountryCode, ADM1Code,
# ADM2Code, Lat, Long, FeatureID).
#   Actor1Geo : 35-42  — CC=37, Lat=40, Long=41
#   Actor2Geo : 43-50  — CC=45, Lat=48, Long=49
#   ActionGeo : 51-58  — FullName=52, CC=53, ADM1=54, Lat=56, Long=57
#   SOURCEURL : 60
#
GDELT_COL_INDICES = {
    0:  "GLOBALEVENTID",
    1:  "SQLDATE",
    2:  "MONTHYEAR",
    3:  "YEAR",
    4:  "FractionDate",
    6:  "Actor1Name",
    7:  "Actor1CountryCode",
    8:  "Actor1KnownGroupCode",
    12: "Actor1Type1Code",
    16: "Actor2Name",
    17: "Actor2CountryCode",
    18: "Actor2KnownGroupCode",
    22: "Actor2Type1Code",
    25: "IsRootEvent",
    26: "EventCode",
    27: "EventBaseCode",
    28: "EventRootCode",
    29: "QuadClass",
    30: "GoldsteinScale",
    31: "NumMentions",
    32: "NumSources",
    33: "NumArticles",
    34: "AvgTone",
    37: "Actor1Geo_CountryCode",
    40: "Actor1Geo_Lat",
    41: "Actor1Geo_Long",
    45: "Actor2Geo_CountryCode",
    48: "Actor2Geo_Lat",
    49: "Actor2Geo_Long",
    52: "ActionGeo_FullName",
    53: "ActionGeo_CountryCode",
    54: "ActionGeo_ADM1Code",
    56: "ActionGeo_Lat",
    57: "ActionGeo_Long",
    60: "SOURCEURL",
}

USECOLS   = sorted(GDELT_COL_INDICES.keys())
COL_NAMES = [GDELT_COL_INDICES[i] for i in USECOLS]

# ── ENRICHISSEMENT ────────────────────────────────────────────────────────────

DEPARTEMENTS_NORD = {
    "Banikoara", "Gogounou", "Kandi", "Karimama", "Malanville", "Segbana",
    "Boukoumbe", "Cobly", "Kerou", "Kouande", "Materi", "Natitingou",
    "Pehunco", "Tanguieta", "Toucountouna",
    "Bassila", "Copargo", "Djougou", "Ouake",
    "Bembereke", "Kalale", "N'Dali", "Nikki", "Parakou",
    "Perere", "Sinende", "Tchaourou",
}

QUAD_MAP = {
    1: "cooperation_verbale",
    2: "cooperation_materielle",
    3: "conflit_verbal",
    4: "conflit_materiel",
}

ADM1_CENTROIDS = {
    "BN01": (11.500,  2.800),
    "BN02": (10.500,  1.500),
    "BN03": ( 9.800,  1.700),
    "BN04": ( 9.800,  2.800),
    "BN05": ( 8.500,  2.200),
    "BN06": ( 6.600,  2.200),
    "BN07": ( 6.370,  2.420),
    "BN08": ( 6.700,  2.600),
    "BN09": ( 7.000,  1.900),
    "BN10": ( 7.500,  2.300),
    "BN11": ( 7.200,  2.900),
    "BN12": ( 6.900,  1.600),
    "BN18": ( 9.337,  2.628),
}

BENIN_CENTER = (9.30, 2.30)
JITTER_SCALE = 0.06


def _categoriser_ton(t):
    if pd.isna(t):  return "inconnu"
    if t > 3:       return "tres_positif"
    if t > 1:       return "positif"
    if t < -3:      return "tres_negatif"
    if t < -1:      return "negatif"
    return "neutre"


def _categoriser_goldstein(s):
    if pd.isna(s):  return "inconnu"
    if s >= 5:      return "tres_cooperatif"
    if s > 0:       return "cooperatif"
    if s == 0:      return "neutre"
    if s >= -5:     return "conflictuel"
    return "tres_conflictuel"


def _extraire_domaine(url):
    if pd.isna(url): return "inconnu"
    try:
        return url.split("/")[2].replace("www.", "")
    except Exception:
        return "inconnu"


def _jitter(event_ids: pd.Series, axis: int) -> pd.Series:
    primes = [997, 1009]
    ids = pd.to_numeric(event_ids, errors="coerce").fillna(0).astype(int)
    return ((ids % primes[axis]) / primes[axis] - 0.5) * (JITTER_SCALE * 2)


def _apply_coord_priority(df: pd.DataFrame) -> pd.DataFrame:
    act_lat = pd.to_numeric(df.get("ActionGeo_Lat",  pd.Series(dtype=float)), errors="coerce")
    act_lon = pd.to_numeric(df.get("ActionGeo_Long", pd.Series(dtype=float)), errors="coerce")

    lat = act_lat.copy()
    lon = act_lon.copy()
    src = pd.Series([""] * len(df), index=df.index, dtype=str)
    src[act_lat.notna() & act_lon.notna()] = "action_geo"

    need = lat.isna() | lon.isna()

    if need.any():
        j_lat = _jitter(df["GLOBALEVENTID"], 0)
        j_lon = _jitter(df["GLOBALEVENTID"], 1)

        if "Actor1Geo_Lat" in df.columns and "Actor1Geo_Long" in df.columns:
            a1_lat = pd.to_numeric(df["Actor1Geo_Lat"], errors="coerce")
            a1_lon = pd.to_numeric(df["Actor1Geo_Long"], errors="coerce")
            a1_cc  = df.get("Actor1Geo_CountryCode", pd.Series(dtype=str)).astype(str).str.upper()
            mask2  = need & a1_lat.notna() & a1_lon.notna() & (a1_cc == "BN")
            lat[mask2] = a1_lat[mask2]; lon[mask2] = a1_lon[mask2]; src[mask2] = "actor1_geo"
            need = need & ~mask2

        if need.any() and "Actor2Geo_Lat" in df.columns and "Actor2Geo_Long" in df.columns:
            a2_lat = pd.to_numeric(df["Actor2Geo_Lat"], errors="coerce")
            a2_lon = pd.to_numeric(df["Actor2Geo_Long"], errors="coerce")
            a2_cc  = df.get("Actor2Geo_CountryCode", pd.Series(dtype=str)).astype(str).str.upper()
            mask3  = need & a2_lat.notna() & a2_lon.notna() & (a2_cc == "BN")
            lat[mask3] = a2_lat[mask3]; lon[mask3] = a2_lon[mask3]; src[mask3] = "actor2_geo"
            need = need & ~mask3

        if need.any():
            adm1 = df.get("ActionGeo_ADM1Code", pd.Series(dtype=str)).astype(str).str.strip().str.upper()
            for code, (clat, clon) in ADM1_CENTROIDS.items():
                mask4 = need & (adm1 == code)
                if mask4.any():
                    lat[mask4] = clat + j_lat[mask4]; lon[mask4] = clon + j_lon[mask4]
                    src[mask4] = "centroid_adm1"; need = need & ~mask4
                    if not need.any():
                        break

        if need.any():
            lat[need] = BENIN_CENTER[0] + j_lat[need]
            lon[need] = BENIN_CENTER[1] + j_lon[need]
            src[need] = "centroid_country"

    df["ActionGeo_Lat"]  = lat
    df["ActionGeo_Long"] = lon
    df["coord_source"]   = src
    return df


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    df["SQLDATE"]        = pd.to_datetime(df["SQLDATE"].astype(str), format="%Y%m%d", errors="coerce")
    df["FractionDate"]   = pd.to_numeric(df["FractionDate"],   errors="coerce")
    df["GoldsteinScale"] = pd.to_numeric(df["GoldsteinScale"], errors="coerce")
    df["AvgTone"]        = pd.to_numeric(df["AvgTone"],        errors="coerce")
    df["ActionGeo_Lat"]  = pd.to_numeric(df["ActionGeo_Lat"],  errors="coerce")
    df["ActionGeo_Long"] = pd.to_numeric(df["ActionGeo_Long"], errors="coerce")
    df["NumMentions"]    = pd.to_numeric(df["NumMentions"],    errors="coerce")
    df["NumSources"]     = pd.to_numeric(df["NumSources"],     errors="coerce")
    df["NumArticles"]    = pd.to_numeric(df["NumArticles"],    errors="coerce")
    df["IsRootEvent"]    = pd.to_numeric(df["IsRootEvent"],    errors="coerce")
    df["QuadClass"]      = pd.to_numeric(df["QuadClass"],      errors="coerce")

    df = df.drop_duplicates(subset=["GLOBALEVENTID"])
    df = df.dropna(subset=["SQLDATE"])

    df = _apply_coord_priority(df)

    df["mois"]         = df["SQLDATE"].dt.month
    df["trimestre"]    = df["SQLDATE"].dt.quarter
    df["annee"]        = df["SQLDATE"].dt.year
    df["mois_annee"]   = df["SQLDATE"].dt.to_period("M").astype(str)
    df["jour_semaine"] = df["SQLDATE"].dt.dayofweek

    df["ton_categorie"]       = df["AvgTone"].apply(_categoriser_ton)
    df["goldstein_categorie"] = df["GoldsteinScale"].apply(_categoriser_goldstein)
    df["quadclass_label"]     = df["QuadClass"].map(QUAD_MAP)

    df["zone_benin"] = df["ActionGeo_FullName"].apply(
        lambda x: "nord" if x in DEPARTEMENTS_NORD else ("sud" if pd.notna(x) else "inconnu")
    )
    df["source_domaine"] = df["SOURCEURL"].apply(_extraire_domaine)
    return df


# ── STATUT ────────────────────────────────────────────────────────────────────

_STATUS_DEFAULT = {
    "status": "pending",
    "last_checked_at": None,
    "last_processed_file": None,
    "last_gdelt_url": None,
    "world_events_read": 0,
    "benin_events_found": 0,
    "benin_events_added": 0,
    "live_total_events": 0,
    "last_error": None,
    "message": "En attente du premier cycle de polling GDELT.",
}


def _write_status(d: dict):
    try:
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATUS_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    except Exception as exc:
        log.warning(f"Impossible d'écrire gdelt_status.json : {exc}")


def _read_status() -> dict:
    try:
        if STATUS_PATH.exists():
            return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return dict(_STATUS_DEFAULT)


def _get_live_count() -> int:
    if LIVE_PATH.exists():
        try:
            return len(pd.read_parquet(LIVE_PATH, columns=["GLOBALEVENTID"]))
        except Exception:
            pass
    return 0


# ── FONCTIONS GDELT ───────────────────────────────────────────────────────────

def _get_latest_export_url() -> str | None:
    try:
        r = requests.get(LASTUPDATE_URL, timeout=10)
        r.raise_for_status()
        for line in r.text.strip().splitlines():
            if "export.CSV.zip" in line:
                return line.split()[2]
    except Exception as e:
        log.error(f"Impossible de lire lastupdate.txt : {e}")
    return None


def _already_processed(url: str) -> bool:
    if not STATE_PATH.exists():
        return False
    return STATE_PATH.read_text().strip() == url


def _mark_processed(url: str):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(url)


def _download_and_filter(url: str) -> tuple[pd.DataFrame, int]:
    """Retourne (df_benin, world_count). world_count = 0 en cas d'erreur."""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(
            io.BytesIO(r.content),
            compression="zip", sep="\t", header=None,
            usecols=USECOLS, names=COL_NAMES,
            low_memory=False, dtype=str,
        )
        world_count = len(df)

        # Filtre géographique strict : l'ACTION doit se passer au Bénin (pays).
        # On n'utilise PAS les codes nationalité acteur (Actor1/2CountryCode == "BEN")
        # car ils capturent des événements hors-Bénin impliquant des acteurs béninois,
        # et confondent le Bénin-pays avec "Bénin City" au Nigéria.
        cc_mask = df["ActionGeo_CountryCode"].str.upper() == "BN"

        # Double-vérification coordonnées : si GDELT fournit des coords pour une ligne
        # qui passe le filtre CC, elles doivent tomber dans la bounding box Bénin.
        # Cela élimine les erreurs de géocodage GDELT (ex. Bénin City → Nigéria lon > 4°E).
        lat_col = pd.to_numeric(df["ActionGeo_Lat"],  errors="coerce")
        lon_col = pd.to_numeric(df["ActionGeo_Long"], errors="coerce")
        has_coords  = lat_col.notna() & lon_col.notna()
        coords_in_benin = lat_col.between(5.5, 13.0) & lon_col.between(0.5, 4.0)
        coord_ok = ~has_coords | coords_in_benin  # pas de coords → OK (centroïde plus tard)

        mask = cc_mask & coord_ok
        return df[mask].copy(), world_count
    except Exception as e:
        log.error(f"Erreur téléchargement {url} : {e}")
        return pd.DataFrame(), 0


def _load_live() -> pd.DataFrame:
    if LIVE_PATH.exists():
        return pd.read_parquet(LIVE_PATH)
    return pd.DataFrame()


def _append_new_rows(df_new: pd.DataFrame) -> int:
    df_existing = _load_live()

    if not df_existing.empty and "coord_source" not in df_existing.columns:
        log.info("Schéma obsolète détecté → réinitialisation de benin_live.parquet.")
        df_existing = pd.DataFrame()

    existing_ids = set() if df_existing.empty else set(df_existing["GLOBALEVENTID"].astype(str))
    df_new["GLOBALEVENTID"] = df_new["GLOBALEVENTID"].astype(str)
    df_really_new = df_new[~df_new["GLOBALEVENTID"].isin(existing_ids)]

    if df_really_new.empty:
        return 0

    df_really_new = _enrich(df_really_new)

    LIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_combined = pd.concat([df_existing, df_really_new], ignore_index=True)

    if "SQLDATE" in df_combined.columns:
        cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=30)
        df_combined = df_combined[
            pd.to_datetime(df_combined["SQLDATE"], errors="coerce") >= cutoff
        ]

    df_combined.to_parquet(LIVE_PATH, index=False)
    return len(df_really_new)


# ── CYCLE PRINCIPAL ───────────────────────────────────────────────────────────

def run_one_cycle() -> dict:
    """Lance un cycle complet. Met à jour gdelt_status.json à chaque étape."""
    now  = datetime.now().isoformat(timespec="seconds")
    live = _get_live_count()

    status = {
        "status":              "checking",
        "last_checked_at":     now,
        "last_processed_file": None,
        "last_gdelt_url":      None,
        "world_events_read":   0,
        "benin_events_found":  0,
        "benin_events_added":  0,
        "live_total_events":   live,
        "last_error":          None,
        "message":             "Vérification GDELT en cours…",
    }
    _write_status(status)

    # 1. Obtenir l'URL du dernier export
    url = _get_latest_export_url()
    if not url:
        status.update(
            status="error",
            last_error="Impossible de contacter le serveur GDELT (lastupdate.txt).",
            message="Erreur temporaire de connexion GDELT. Les données locales sont conservées.",
        )
        _write_status(status)
        return status

    filename = url.split("/")[-1].replace(".export.CSV.zip", "")
    status["last_processed_file"] = filename
    status["last_gdelt_url"]      = url

    # 2. Déjà traité ?
    if _already_processed(url):
        status.update(
            status="ok",
            live_total_events=_get_live_count(),
            message=f"Fichier déjà indexé ({filename}). Aucune nouvelle donnée.",
        )
        _write_status(status)
        log.info(f"Déjà traité : {filename} — rien à faire.")
        return status

    # 3. Téléchargement + filtre Bénin
    log.info(f"Nouveau fichier : {filename}")
    df_raw, world_count = _download_and_filter(url)
    status["world_events_read"]  = world_count
    status["benin_events_found"] = len(df_raw)

    if world_count == 0:
        # Erreur de téléchargement
        status.update(
            status="error",
            last_error="Échec du téléchargement du fichier CSV GDELT.",
            message="Erreur temporaire lors du téléchargement GDELT. Les données locales sont conservées.",
        )
        _write_status(status)
        return status

    if df_raw.empty:
        _mark_processed(url)
        status.update(
            status="ok",
            live_total_events=_get_live_count(),
            message=(
                f"Dernière vérification réussie. Aucun événement Bénin dans ce fichier "
                f"({world_count} événements mondiaux lus)."
            ),
        )
        _write_status(status)
        log.info(f"Aucun événement Bénin. {world_count} événements mondiaux lus.")
        return status

    # 4. Ajout des nouvelles lignes
    n_new = _append_new_rows(df_raw)
    _mark_processed(url)
    live_total = _get_live_count()
    status["benin_events_added"] = n_new
    status["live_total_events"]  = live_total

    if n_new > 0:
        log.info(f"{n_new} nouvel(s) événement(s) Bénin → {LIVE_PATH.name}")
        status.update(
            status="ok",
            message=f"Connecté. {n_new} nouvel(s) événement(s) Bénin ajouté(s) à la base live.",
        )
    else:
        log.info("Événements Bénin déjà en base (doublons ignorés).")
        status.update(
            status="ok",
            message="Connecté. Événements Bénin présents dans ce fichier, déjà tous indexés.",
        )

    _write_status(status)
    return status


def run_polling_loop():
    log.info(f"Démarrage du polling GDELT live (intervalle : {POLL_SECONDS}s)")
    while True:
        run_one_cycle()
        time.sleep(POLL_SECONDS)


def start_background_poller():
    t = threading.Thread(target=run_polling_loop, daemon=True, name="gdelt-live-poller")
    t.start()
    log.info("Thread GDELT live démarré en arrière-plan.")
    return t


# ── HELPERS DASHBOARD ────────────────────────────────────────────────────────

def load_live_events() -> pd.DataFrame:
    return _load_live()


def get_live_stats() -> dict:
    df = _load_live()
    if df.empty:
        return {"n_events": 0, "last_date": None, "last_update": None}
    return {
        "n_events":    len(df),
        "last_date":   df["SQLDATE"].max() if "SQLDATE" in df.columns else None,
        "last_update": datetime.fromtimestamp(LIVE_PATH.stat().st_mtime).strftime("%H:%M:%S"),
    }


if __name__ == "__main__":
    run_polling_loop()
