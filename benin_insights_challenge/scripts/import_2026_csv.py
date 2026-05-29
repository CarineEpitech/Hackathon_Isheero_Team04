"""
import_2026_csv.py
==================
Importe le CSV exporté depuis BigQuery (benin_2026.csv),
applique l'enrichissement TERROIR, et ajoute les lignes dans
benin_live.parquet (sans doublons).

Usage :
    python scripts/import_2026_csv.py
    python scripts/import_2026_csv.py --csv data/raw/mon_fichier.csv

Prérequis :
    - Avoir exécuté scripts/query_bigquery_2026.sql dans la console BigQuery
    - Avoir sauvegardé le résultat en CSV dans data/raw/benin_2026.csv
"""

import sys
import argparse
import pandas as pd
from pathlib import Path

# ── Chemins ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parents[1]   # benin_insights_challenge/
CSV_PATH   = BASE_DIR / "data" / "raw" / "benin_2026.csv"
LIVE_PATH  = BASE_DIR / "data" / "processed" / "benin_live.parquet"

# Ajouter backend/services au path pour importer _enrich depuis le poller
sys.path.insert(0, str(BASE_DIR / "backend" / "services"))
from gdelt_live_poller import _enrich   # réutilise exactement la même logique


# ── Colonnes attendues (mêmes que query_bigquery_2026.sql) ────────────────────
EXPECTED_COLS = [
    "GLOBALEVENTID", "SQLDATE", "MONTHYEAR", "YEAR", "FractionDate",
    "IsRootEvent", "ActionGeo_CountryCode", "ActionGeo_FullName",
    "ActionGeo_ADM1Code", "ActionGeo_Lat", "ActionGeo_Long",
    "Actor1Geo_CountryCode", "Actor2Geo_CountryCode",
    "Actor1CountryCode", "Actor2CountryCode",
    "Actor1Name", "Actor2Name",
    "Actor1Type1Code", "Actor2Type1Code",
    "Actor1KnownGroupCode", "Actor2KnownGroupCode",
    "EventRootCode", "EventBaseCode", "EventCode",
    "QuadClass", "GoldsteinScale", "NumMentions",
    "NumSources", "NumArticles", "AvgTone", "SOURCEURL",
]


def load_csv(csv_path: Path) -> pd.DataFrame:
    """Charge le CSV BigQuery (avec ou sans header)."""
    print(f"Lecture CSV : {csv_path}")
    df = pd.read_csv(csv_path, dtype=str, low_memory=False)

    # BigQuery exporte avec header → vérifier que les colonnes existent
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Colonnes manquantes dans le CSV : {missing}\n"
            "Vérifiez que vous avez utilisé query_bigquery_2026.sql sans modification."
        )

    return df[EXPECTED_COLS].copy()


def load_live() -> pd.DataFrame:
    """Charge benin_live.parquet existant (vide si inexistant)."""
    if LIVE_PATH.exists():
        return pd.read_parquet(LIVE_PATH)
    return pd.DataFrame()


def append_to_live(df_new: pd.DataFrame) -> int:
    """
    Déduplique par GLOBALEVENTID, enrichit, et ajoute à benin_live.parquet.
    Retourne le nombre de lignes vraiment ajoutées.
    """
    df_existing = load_live()

    existing_ids = (
        set(df_existing["GLOBALEVENTID"].astype(str))
        if not df_existing.empty else set()
    )

    df_new["GLOBALEVENTID"] = df_new["GLOBALEVENTID"].astype(str)
    df_really_new = df_new[~df_new["GLOBALEVENTID"].isin(existing_ids)].copy()

    if df_really_new.empty:
        print("Toutes les lignes sont déjà dans benin_live.parquet — rien à ajouter.")
        return 0

    print(f"Enrichissement de {len(df_really_new)} nouvelles lignes...")
    df_enriched = _enrich(df_really_new)

    LIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_combined = pd.concat([df_existing, df_enriched], ignore_index=True)
    df_combined.to_parquet(LIVE_PATH, index=False)

    return len(df_enriched)


def main():
    parser = argparse.ArgumentParser(description="Import CSV BigQuery 2026 → benin_live.parquet")
    parser.add_argument(
        "--csv", type=Path, default=CSV_PATH,
        help=f"Chemin du CSV exporté depuis BigQuery (défaut : {CSV_PATH})"
    )
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"\n ERREUR : fichier introuvable → {args.csv}")
        print("\n Marche à suivre :")
        print("  1. Ouvrir https://console.cloud.google.com/bigquery")
        print("  2. Coller et exécuter scripts/query_bigquery_2026.sql")
        print("  3. Résultats > Enregistrer > CSV (fichier local)")
        print(f"  4. Déplacer le fichier téléchargé vers : {args.csv}")
        print("  5. Relancer ce script")
        sys.exit(1)

    df_raw = load_csv(args.csv)
    print(f"  {len(df_raw)} lignes lues dans le CSV")

    n_added = append_to_live(df_raw)

    if n_added > 0:
        # Afficher un résumé rapide
        df_check = pd.read_parquet(LIVE_PATH)
        df_check["SQLDATE"] = pd.to_datetime(df_check["SQLDATE"], errors="coerce")
        yr_2026 = df_check[df_check["SQLDATE"].dt.year == 2026]
        print(f"\n  {n_added} lignes 2026 ajoutées dans benin_live.parquet")
        print(f"  Total lignes 2026  : {len(yr_2026)}")
        print(f"  Jours couverts     : {yr_2026['SQLDATE'].dt.date.nunique()}")
        print(f"  Période            : {yr_2026['SQLDATE'].min().date()} → {yr_2026['SQLDATE'].max().date()}")
        print(f"  Total benin_live   : {len(df_check)} lignes")
        print("\n  Lance le dashboard pour voir les données 2026 :")
        print("  streamlit run dashboard/app.py")
    else:
        print("Aucune modification apportée à benin_live.parquet.")


if __name__ == "__main__":
    main()
