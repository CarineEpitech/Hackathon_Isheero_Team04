"""
fill_gap_2026.py
================
Comble le gap entre la derniere date de benin_enrichi.parquet et la veille
en telechargeant les fichiers historiques GDELT v2 (15 min) depuis
masterfilelist.txt et en les integrant dans benin_enrichi.parquet.

Pourquoi benin_enrichi.parquet et non benin_live.parquet ?
  - benin_live.parquet est ecrase par le poller live avec un cutoff 30 jours.
  - benin_enrichi.parquet est le baseline stable lu par load_historical_data().

Usage :
    python scripts/fill_gap_2026.py
    python scripts/fill_gap_2026.py --start 20260418 --end 20260527
    python scripts/fill_gap_2026.py --dry-run   # compte les fichiers sans telecharger
    python scripts/fill_gap_2026.py --reset      # recommence depuis zero (ignore checkpoint)

Duree estimee : 20-45 min (6 downloads en parallele).
Resume automatique si interrompu (checkpoint JSON).
"""

import sys
import io
import json
import time
import argparse
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Chemins ────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parents[1]
ENRICHI     = BASE_DIR / "data" / "processed" / "benin_enrichi.parquet"
CHECKPOINT  = BASE_DIR / "data" / "processed" / "fill_gap_checkpoint.json"

sys.path.insert(0, str(BASE_DIR / "backend" / "services"))
from gdelt_live_poller import _enrich, USECOLS, COL_NAMES

# ── Constantes ─────────────────────────────────────────────────────────────────
MASTER_URL  = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
MAX_WORKERS = 6    # downloads en parallele (respecte les serveurs GDELT)
BATCH_SIZE  = 192  # ecriture parquet toutes les 2 jours (~192 fichiers 15-min)


# ── Calcul automatique du gap ───────────────────────────────────────────────────

def compute_gap() -> tuple[str, str]:
    """
    Retourne (start_yyyymmdd, end_yyyymmdd) du gap a combler.
    start = lendemain du dernier jour dans benin_enrichi.parquet
    end   = hier (CURRENT_DATE - 1)
    """
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y%m%d")

    if not ENRICHI.exists():
        return "20260418", yesterday

    try:
        df = pd.read_parquet(ENRICHI, columns=["SQLDATE"])
        df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], errors="coerce")
        max_date = df["SQLDATE"].max()
        if pd.isna(max_date):
            return "20260418", yesterday
        start = (max_date + timedelta(days=1)).strftime("%Y%m%d")
        return start, yesterday
    except Exception:
        return "20260418", yesterday


# ── masterfilelist ─────────────────────────────────────────────────────────────

def load_master_urls(start: str, end: str) -> list:
    """
    Telecharge masterfilelist.txt et retourne les URLs export.CSV.zip
    dont la date (8 premiers chiffres du nom de fichier) est dans [start, end].
    """
    print("Telechargement de masterfilelist.txt (peut prendre 30s)...")
    r = requests.get(MASTER_URL, timeout=120)
    r.raise_for_status()

    urls = []
    for line in r.text.strip().splitlines():
        parts = line.split()
        if len(parts) != 3:
            continue
        url = parts[2]
        if "export.CSV.zip" not in url:
            continue
        filename = url.split("/")[-1]   # ex: 20260418120000.export.CSV.zip
        date_str = filename[:8]         # ex: 20260418
        if start <= date_str <= end:
            urls.append(url)

    return sorted(urls)


# ── Download + filtre ──────────────────────────────────────────────────────────

def download_and_filter(url: str) -> tuple:
    """
    Telecharge un fichier 15-min GDELT, filtre pour le Benin.
    Retourne (df_benin, world_count, url).
    df_benin peut etre vide si aucun evenement BN ou erreur.
    """
    try:
        r = requests.get(url, timeout=45)
        r.raise_for_status()

        df = pd.read_csv(
            io.BytesIO(r.content),
            compression="zip",
            sep="\t",
            header=None,
            usecols=USECOLS,
            names=COL_NAMES,
            low_memory=False,
            dtype=str,
        )
        world_count = len(df)

        # Filtre geographique strict : action au Benin (FIPS BN)
        cc_mask = df["ActionGeo_CountryCode"].str.upper() == "BN"

        # Bounding box Benin (elimine les erreurs de geocodage ex. Benin City Nigeria)
        lat_col = pd.to_numeric(df["ActionGeo_Lat"], errors="coerce")
        lon_col = pd.to_numeric(df["ActionGeo_Long"], errors="coerce")
        has_coords = lat_col.notna() & lon_col.notna()
        coords_in_benin = lat_col.between(5.5, 13.0) & lon_col.between(0.5, 4.0)
        coord_ok = ~has_coords | coords_in_benin

        df_benin = df[cc_mask & coord_ok].copy()
        return df_benin, world_count, url

    except Exception as e:
        return pd.DataFrame(), 0, url


# ── Checkpoint ────────────────────────────────────────────────────────────────

def load_checkpoint() -> set:
    if CHECKPOINT.exists():
        try:
            data = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
            return set(data.get("done", []))
        except Exception:
            pass
    return set()


def save_checkpoint(done: set):
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(
        json.dumps(
            {"done": sorted(done), "saved_at": datetime.utcnow().isoformat()},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


# ── Ecriture dans benin_enrichi.parquet ───────────────────────────────────────

def append_to_enrichi(frames: list, existing_ids: set) -> int:
    """
    Enrichit et ajoute les DataFrames de 'frames' dans benin_enrichi.parquet.
    Deduplique par GLOBALEVENTID (contre existing_ids et entre les frames).
    Met a jour existing_ids en place.
    Retourne le nombre de lignes ajoutees.
    """
    if not frames:
        return 0

    df_batch = pd.concat(frames, ignore_index=True)
    df_batch["GLOBALEVENTID"] = df_batch["GLOBALEVENTID"].astype(str)

    # Deduplication contre l'existant + interne au batch
    df_batch = df_batch[~df_batch["GLOBALEVENTID"].isin(existing_ids)]
    df_batch = df_batch.drop_duplicates(subset=["GLOBALEVENTID"])

    if df_batch.empty:
        return 0

    df_enriched = _enrich(df_batch)
    n_new = len(df_enriched)

    # Mise a jour du parquet
    ENRICHI.parent.mkdir(parents=True, exist_ok=True)
    if ENRICHI.exists():
        df_existing = pd.read_parquet(ENRICHI)
        df_combined = pd.concat([df_existing, df_enriched], ignore_index=True)
    else:
        df_combined = df_enriched

    # Harmoniser le type de GLOBALEVENTID (int64 dans l'existant, str dans les nouvelles lignes)
    df_combined["GLOBALEVENTID"] = pd.to_numeric(df_combined["GLOBALEVENTID"], errors="coerce")

    df_combined.to_parquet(ENRICHI, index=False)

    # Mise a jour du set d'IDs (pour les batches suivants)
    existing_ids.update(df_enriched["GLOBALEVENTID"].astype(str).tolist())

    return n_new


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Comble le gap GDELT dans benin_enrichi.parquet"
    )
    parser.add_argument(
        "--start", default=None,
        help="Date debut YYYYMMDD (defaut: lendemain du max de benin_enrichi.parquet)"
    )
    parser.add_argument(
        "--end", default=None,
        help="Date fin   YYYYMMDD (defaut: hier)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Compte les fichiers sans rien telecharger"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Ignore le checkpoint et recommence depuis le debut"
    )
    parser.add_argument(
        "--workers", type=int, default=MAX_WORKERS,
        help=f"Nombre de threads paralleles (defaut: {MAX_WORKERS})"
    )
    args = parser.parse_args()

    # 1. Determiner la plage de dates
    auto_start, auto_end = compute_gap()
    start = args.start or auto_start
    end   = args.end   or auto_end

    print(f"Gap a combler : {start[:4]}-{start[4:6]}-{start[6:]} "
          f"=> {end[:4]}-{end[4:6]}-{end[6:]}")

    if start > end:
        print("Aucun gap a combler — benin_enrichi.parquet est deja a jour.")
        return

    # 2. Liste des URLs
    all_urls = load_master_urls(start, end)
    if not all_urls:
        print("Aucun fichier GDELT trouve pour cette periode dans masterfilelist.txt.")
        print("(Le dataset GDELT public peut avoir un delai de quelques heures.)")
        return

    print(f"{len(all_urls)} fichiers GDELT v2 trouves pour la periode.")

    if args.dry_run:
        print("Mode dry-run — rien telecharge.")
        return

    # 3. Checkpoint
    done = set() if args.reset else load_checkpoint()
    todo = [u for u in all_urls if u not in done]
    print(f"Deja traites : {len(done)} | Restants : {len(todo)}")

    if not todo:
        print("Tous les fichiers sont deja traites.")
        if CHECKPOINT.exists():
            CHECKPOINT.unlink()
        return

    # 4. Charger les IDs existants (pour deduplication rapide)
    print("Chargement des IDs existants dans benin_enrichi.parquet...")
    if ENRICHI.exists():
        df_ids = pd.read_parquet(ENRICHI, columns=["GLOBALEVENTID"])
        existing_ids = set(df_ids["GLOBALEVENTID"].astype(str).tolist())
        print(f"  {len(existing_ids):,} evenements deja en base.")
    else:
        existing_ids = set()
        print("  benin_enrichi.parquet absent — creation.")

    # 5. Traitement parallele par batches
    t0          = time.time()
    batch_frames = []
    total_benin  = 0
    total_added  = 0
    errors       = 0
    n_processed  = 0

    print(f"\nDemarrage avec {args.workers} threads paralleles...\n")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download_and_filter, url): url for url in todo}

        for future in as_completed(futures):
            df_benin, world_count, url = future.result()
            filename = url.split("/")[-1].replace(".export.CSV.zip", "")
            n_processed += 1

            if world_count == 0:
                # Erreur de telechargement (ne pas marquer comme done)
                errors += 1
                pct = n_processed / len(todo) * 100
                print(f"  [{n_processed:4d}/{len(todo)}] {filename[:8]} ERREUR ({pct:.0f}%)")
                continue

            done.add(url)
            total_benin += len(df_benin)

            if not df_benin.empty:
                batch_frames.append(df_benin)

            # Progression
            elapsed = time.time() - t0
            eta_s   = (elapsed / n_processed) * (len(todo) - n_processed) if n_processed > 0 else 0
            eta_str = f"{int(eta_s//60):02d}:{int(eta_s%60):02d}"
            pct     = n_processed / len(todo) * 100
            date_s  = filename[:8]

            print(
                f"  [{n_processed:4d}/{len(todo)}] "
                f"{date_s[:4]}-{date_s[4:6]}-{date_s[6:8]} "
                f"{filename[8:10]}:{filename[10:12]} | "
                f"BN={len(df_benin):2d} | total_BN={total_benin:5d} | "
                f"{pct:.0f}% | ETA {eta_str}",
                flush=True,
            )

            # Sauvegarde par batch
            if len(batch_frames) > 0 and (n_processed % BATCH_SIZE == 0 or n_processed == len(todo)):
                n = append_to_enrichi(batch_frames, existing_ids)
                total_added += n
                batch_frames = []
                save_checkpoint(done)
                print(f"  >> SAUVEGARDE : +{n} lignes (total ajoute: {total_added})", flush=True)

    # Flush du dernier batch (si ThreadPoolExecutor a termine avant la sauvegarde)
    if batch_frames:
        n = append_to_enrichi(batch_frames, existing_ids)
        total_added += n
        save_checkpoint(done)
        print(f"  >> SAUVEGARDE FINALE : +{n} lignes (total ajoute: {total_added})")

    # 6. Resume
    elapsed_total = time.time() - t0
    print(f"\n{'='*60}")
    print(f"Termine en {int(elapsed_total//60)} min {int(elapsed_total%60)} sec")
    print(f"  Fichiers traites  : {len(done)}")
    print(f"  Erreurs           : {errors}")
    print(f"  Evenements BN lus : {total_benin}")
    print(f"  Lignes ajoutees   : {total_added}")

    if ENRICHI.exists():
        df_check = pd.read_parquet(ENRICHI, columns=["SQLDATE"])
        df_check["SQLDATE"] = pd.to_datetime(df_check["SQLDATE"], errors="coerce")
        print(f"  benin_enrichi     : {len(df_check):,} lignes")
        print(f"  Periode           : {df_check['SQLDATE'].min().date()} => {df_check['SQLDATE'].max().date()}")

    if errors == 0 and CHECKPOINT.exists():
        CHECKPOINT.unlink()
        print("Checkpoint supprime (tout est OK).")
    elif errors > 0:
        print(f"ATTENTION : {errors} fichier(s) en erreur.")
        print("Relancez le script pour les retenter (resume automatique).")

    print("\nRedemarrez le serveur FastAPI/Streamlit pour voir les nouvelles donnees.")


if __name__ == "__main__":
    main()
