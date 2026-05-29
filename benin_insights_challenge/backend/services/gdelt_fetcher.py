import ssl
import requests
import zipfile
import io
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

RAW_DIR = Path("data/raw/realtime")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# GDELT 2.0 Event files are published every 15 minutes
GDELT_LASTUPDATE = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
GDELT_MASTER_URL = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"

BENIN_COUNTRY_CODES = {"BN"}   # ActionGeo uniquement (FIPS Bénin = code pays, pas nationalité acteur)


def check_gdelt_connection() -> dict:
    response = requests.get("http://data.gdeltproject.org/", timeout=20)
    response.raise_for_status()
    return {
        "status": "ok",
        "checked_at": datetime.utcnow().isoformat(),
        "status_code": response.status_code,
    }


def get_latest_gdelt_file_url() -> str:
    """Return the CSV.zip URL of the most recently published GDELT 2.0 event file."""
    resp = requests.get(GDELT_LASTUPDATE, timeout=20)
    resp.raise_for_status()
    # Each line: "<size> <md5> <url>"  — first line is the events file
    for line in resp.text.strip().splitlines():
        parts = line.split()
        if len(parts) == 3 and "export.CSV.zip" in parts[2]:
            return parts[2]
    raise ValueError("Could not parse lastupdate.txt")


def fetch_latest_events(filter_benin: bool = True) -> pd.DataFrame:
    """
    Download the latest GDELT 2.0 15-minute update and return it as a DataFrame.
    If filter_benin=True, keep only rows where ActionGeo_CountryCode == 'BN'.
    """
    url = get_latest_gdelt_file_url()
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        csv_name = z.namelist()[0]
        with z.open(csv_name) as f:
            df = pd.read_csv(
                f,
                sep="\t",
                header=None,
                low_memory=False,
                on_bad_lines="skip",
            )

    df.columns = _gdelt_columns()

    if filter_benin:
        mask = (
            df["ActionGeo_CountryCode"].isin(BENIN_COUNTRY_CODES)
            | df["Actor1Geo_CountryCode"].isin(BENIN_COUNTRY_CODES)
            | df["Actor2Geo_CountryCode"].isin(BENIN_COUNTRY_CODES)
        )
        df = df[mask].copy()

    df["fetched_at"] = datetime.utcnow().isoformat()
    return df


def save_snapshot(df: pd.DataFrame) -> Path:
    """Persist a 15-min snapshot to parquet in RAW_DIR."""
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    out = RAW_DIR / f"gdelt_benin_{ts}.parquet"
    df.to_parquet(out, index=False)
    return out


def _gdelt_columns() -> list:
    return [
        "GlobalEventID", "Day", "MonthYear", "Year", "FractionDate",
        "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode",
        "Actor1EthnicCode", "Actor1Religion1Code", "Actor1Religion2Code",
        "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
        "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode",
        "Actor2EthnicCode", "Actor2Religion1Code", "Actor2Religion2Code",
        "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
        "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode",
        "QuadClass", "GoldsteinScale", "NumMentions", "NumSources",
        "NumArticles", "AvgTone",
        "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
        "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code",
        "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",
        "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
        "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code",
        "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID",
        "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
        "ActionGeo_ADM1Code", "ActionGeo_ADM2Code",
        "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID",
        "DATEADDED", "SOURCEURL",
    ]


if __name__ == "__main__":
    print("Vérification connexion GDELT...")
    print(check_gdelt_connection())

    print("\nTéléchargement dernière mise à jour (15 min)...")
    df = fetch_latest_events(filter_benin=True)
    print(f"  {len(df)} événements Bénin trouvés")

    if not df.empty:
        path = save_snapshot(df)
        print(f"  Sauvegardé : {path}")
        print(df[["Day", "EventRootCode", "GoldsteinScale", "AvgTone", "ActionGeo_FullName"]].head(10).to_string())
    else:
        print("  Aucun événement Bénin dans cette mise à jour (normal entre deux pics).")
