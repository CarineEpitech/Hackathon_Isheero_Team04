"""
Couche 2 — Signalement communautaire terrain.
SQLite : stockage, lecture et validation des incidents citoyens.
"""
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "backend" / "data" / "incidents.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

INCIDENT_TYPES = [
    "Agression", "Vol / Cambriolage", "Conflit armé",
    "Manifestation", "Tension", "Enlèvement",
    "Attentat / Explosion", "Autre",
]

SOURCES = ["citoyen", "ong", "journaliste", "prefecturee", "autre"]


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents_citoyens (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    NOT NULL,
                type        TEXT    NOT NULL,
                description TEXT,
                lat         REAL    NOT NULL,
                lon         REAL    NOT NULL,
                source      TEXT    DEFAULT 'citoyen',
                pseudo      TEXT,
                validated   INTEGER DEFAULT 0,
                adm1_code   TEXT,
                departement TEXT
            )
        """)
        conn.commit()


def submit(type_: str, description: str, lat: float, lon: float,
           source: str = "citoyen", pseudo: str = None) -> int:
    """Enregistre un signalement. Retourne son id."""
    adm1, dept = _reverse_geocode(lat, lon)
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """INSERT INTO incidents_citoyens
               (timestamp, type, description, lat, lon, source, pseudo, validated, adm1_code, departement)
               VALUES (?,?,?,?,?,?,?,0,?,?)""",
            (datetime.utcnow().isoformat(), type_, description, lat, lon, source, pseudo, adm1, dept)
        )
        conn.commit()
        return cur.lastrowid


def load_all(validated_only: bool = False) -> pd.DataFrame:
    """Charge tous les signalements (ou uniquement les validés)."""
    init_db()
    query = "SELECT * FROM incidents_citoyens"
    if validated_only:
        query += " WHERE validated = 1"
    query += " ORDER BY timestamp DESC"
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def load_recent(hours: int = 48) -> pd.DataFrame:
    """Signalements des dernières N heures."""
    df = load_all()
    if df.empty:
        return df
    cutoff = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(hours=hours)
    return df[df["timestamp"] >= cutoff]


def validate(incident_id: int):
    """Marque un signalement comme validé."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE incidents_citoyens SET validated=1 WHERE id=?", (incident_id,))
        conn.commit()


def auto_validate_with_gdelt(df_gdelt: pd.DataFrame, radius_km: float = 50, hours: int = 24):
    """
    Valide automatiquement les signalements citoyens qui ont un événement GDELT
    de même type dans un rayon radius_km dans les dernières `hours` heures.
    """
    unvalidated = load_all()
    unvalidated = unvalidated[unvalidated["validated"] == 0]
    if unvalidated.empty or df_gdelt.empty:
        return 0

    validated_count = 0
    cutoff = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(hours=hours)
    recent_gdelt = df_gdelt[
        (df_gdelt["SQLDATE"] >= cutoff) & (df_gdelt["is_security"] == 1)
    ] if "is_security" in df_gdelt.columns else df_gdelt

    for _, row in unvalidated.iterrows():
        if pd.isna(row["lat"]) or pd.isna(row["lon"]):
            continue
        nearby = recent_gdelt[
            (recent_gdelt["ActionGeo_Lat"].notna()) &
            (recent_gdelt["ActionGeo_Long"].notna()) &
            (_haversine(row["lat"], row["lon"],
                        recent_gdelt["ActionGeo_Lat"],
                        recent_gdelt["ActionGeo_Long"]) <= radius_km)
        ]
        if not nearby.empty:
            validate(row["id"])
            validated_count += 1

    return validated_count


def _haversine(lat1, lon1, lat2_series, lon2_series):
    """Distance Haversine vectorisée (km)."""
    R = 6371
    d_lat = np.radians(lat2_series - lat1)
    d_lon = np.radians(lon2_series - lon1)
    a = (np.sin(d_lat / 2) ** 2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2_series)) *
         np.sin(d_lon / 2) ** 2)
    return R * 2 * np.arcsin(np.sqrt(a))


def _reverse_geocode(lat: float, lon: float) -> tuple[str, str]:
    """
    Attribution département Bénin par coordonnées (bounding boxes approx.).
    Retourne (adm1_code, departement_label).
    """
    # Bounding boxes approximatives des départements Bénin
    BBOX = [
        ("BN01", "Alibori",    11.5, 15.0,  2.5,  3.9),
        ("BN02", "Atacora",     9.8, 11.5,  0.8,  2.0),
        ("BN04", "Borgou",      9.2, 12.5,  2.0,  3.6),
        ("BN03", "Donga",       9.0, 10.2,  1.5,  2.0),
        ("BN05", "Collines",    7.8,  9.5,  1.8,  3.0),
        ("BN06", "Atlantique",  6.2,  7.2,  1.9,  2.8),
        ("BN07", "Littoral",    6.3,  6.5,  2.3,  2.5),
        ("BN08", "Ouémé",       6.3,  7.3,  2.4,  3.0),
        ("BN09", "Couffo",      6.8,  7.8,  1.5,  2.0),
        ("BN10", "Zou",         7.0,  8.3,  2.0,  2.8),
        ("BN11", "Plateau",     6.7,  8.0,  2.7,  3.3),
        ("BN12", "Mono",        6.2,  7.2,  1.2,  1.8),
    ]
    for code, label, lat_min, lat_max, lon_min, lon_max in BBOX:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return code, label
    return "BN00", "Bénin (non localisé)"


# Import numpy ici pour _haversine
import numpy as np

init_db()


if __name__ == "__main__":
    print("Test signalement citoyen...")

    # Soumettre un incident test (coordonnées Cotonou)
    id1 = submit("Agression", "Test agression Cotonou", lat=6.366, lon=2.418, pseudo="Test")
    print(f"  Signalement #{id1} créé")

    # Incident nord (Borgou, Parakou)
    id2 = submit("Conflit armé", "Test tension nord Parakou", lat=9.337, lon=2.628, source="ong")
    print(f"  Signalement #{id2} créé")

    df = load_all()
    print(f"\n  Total en base : {len(df)} signalement(s)")
    print(df[["id", "timestamp", "type", "departement", "validated"]].to_string(index=False))
