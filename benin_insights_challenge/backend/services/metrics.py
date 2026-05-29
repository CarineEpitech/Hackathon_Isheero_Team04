"""
Calcul du Score de Tension Territorial (STT) par département.
STT = 0.40×z_cameo + 0.35×z_tone + 0.15×z_volume + 0.10×z_sources
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SECURITY_ROOT_CODES = {13, 14, 15, 17, 18, 19, 20}

STT_WEIGHTS = {"cameo": 0.40, "tone": 0.35, "volume": 0.15, "sources": 0.10}

ALERT_LEVELS = {0: "normal", 1: "precaution", 2: "alerte"}
ALERT_THRESHOLDS = {"precaution": 2.0, "alerte": 3.0}

DEPARTMENTS = {
    "BN01": "Alibori", "BN02": "Atacora", "BN03": "Donga",
    "BN04": "Borgou",  "BN05": "Collines","BN06": "Atlantique",
    "BN07": "Littoral","BN08": "Ouémé",   "BN09": "Couffo",
    "BN10": "Zou",     "BN11": "Plateau", "BN12": "Mono",
    "BN18": "Parakou",
}

PRIORITY_NORTH = {"BN01", "BN02", "BN03", "BN04"}


def _safe_zscore(value: float, baseline: pd.Series) -> float:
    std = baseline.std()
    mean = baseline.mean()
    if std == 0 or np.isnan(std):
        return 0.0
    return float((value - mean) / std)


def compute_stt(df: pd.DataFrame, adm1_code: str, ref_date: datetime = None) -> dict:
    """
    Calcule le STT pour un département sur la fenêtre courante (14j)
    vs la baseline (J-104 à J-15).
    """
    if ref_date is None:
        ref_date = datetime.utcnow()

    window_start  = ref_date - timedelta(days=14)
    baseline_end  = ref_date - timedelta(days=15)
    baseline_start= ref_date - timedelta(days=104)

    dept_df = df[df["ActionGeo_ADM1Code"] == adm1_code].copy()
    if dept_df.empty:
        # Tenter fallback sur zone générique BN
        dept_df = df[df["ActionGeo_ADM1Code"] == "BN"].copy()

    window   = dept_df[dept_df["SQLDATE"] >= pd.Timestamp(window_start)]
    baseline = dept_df[
        (dept_df["SQLDATE"] >= pd.Timestamp(baseline_start)) &
        (dept_df["SQLDATE"] <= pd.Timestamp(baseline_end))
    ]

    if len(window) == 0 and len(baseline) == 0:
        return _empty_stt(adm1_code)

    # ── z_cameo : part d'événements codes négatifs ──────────
    def neg_ratio(d):
        if len(d) == 0: return 0.0
        return len(d[d["EventRootCode"].isin(SECURITY_ROOT_CODES)]) / len(d)

    # Calcul jour par jour sur la baseline pour avoir une distribution
    baseline["_date"] = baseline["SQLDATE"].dt.date
    daily_neg = baseline.groupby("_date").apply(neg_ratio)
    cur_neg   = neg_ratio(window)
    z_cameo   = _safe_zscore(cur_neg, daily_neg)

    # ── z_tone : ton moyen inversé ────────────────────────
    window["_date"]   = window["SQLDATE"].dt.date
    baseline["_date"] = baseline["SQLDATE"].dt.date
    daily_tone   = baseline.groupby("_date")["AvgTone"].mean()
    cur_tone     = window["AvgTone"].mean() if len(window) else 0.0
    z_tone       = _safe_zscore(-cur_tone, -daily_tone)

    # ── z_volume : nb événements par jour ────────────────
    daily_vol = baseline.groupby("_date").size()
    cur_vol   = len(window) / 14
    z_volume  = _safe_zscore(cur_vol, daily_vol)

    # ── z_sources : diversité sources ────────────────────
    daily_src = baseline.groupby("_date")["source_domaine"].nunique()
    cur_src   = window["source_domaine"].nunique()
    z_sources = _safe_zscore(cur_src, daily_src)

    stt = (
        STT_WEIGHTS["cameo"]   * z_cameo +
        STT_WEIGHTS["tone"]    * z_tone  +
        STT_WEIGHTS["volume"]  * z_volume +
        STT_WEIGHTS["sources"] * z_sources
    )
    stt = float(np.clip(stt, -5, 10))

    level = 0
    if stt >= ALERT_THRESHOLDS["alerte"]:     level = 2
    elif stt >= ALERT_THRESHOLDS["precaution"]: level = 1

    return {
        "adm1_code":    adm1_code,
        "departement":  DEPARTMENTS.get(adm1_code, adm1_code),
        "stt":          round(stt, 2),
        "level":        level,
        "level_label":  ALERT_LEVELS[level],
        "z_cameo":      round(z_cameo, 3),
        "z_tone":       round(z_tone, 3),
        "z_volume":     round(z_volume, 3),
        "z_sources":    round(z_sources, 3),
        "n_window":     len(window),
        "n_baseline":   len(baseline),
        "neg_ratio_cur":round(cur_neg, 3),
        "tone_cur":     round(cur_tone, 2),
        "computed_at":  datetime.utcnow().isoformat(),
        "priority":     adm1_code in PRIORITY_NORTH,
    }


def compute_all_departments(df: pd.DataFrame, ref_date: datetime = None) -> list[dict]:
    """Calcule le STT pour tous les départements connus."""
    results = []
    for code in DEPARTMENTS:
        results.append(compute_stt(df, code, ref_date))
    results.sort(key=lambda x: x["stt"], reverse=True)
    return results


def _empty_stt(adm1_code: str) -> dict:
    return {
        "adm1_code": adm1_code,
        "departement": DEPARTMENTS.get(adm1_code, adm1_code),
        "stt": 0.0, "level": 0, "level_label": "normal",
        "z_cameo": 0.0, "z_tone": 0.0, "z_volume": 0.0, "z_sources": 0.0,
        "n_window": 0, "n_baseline": 0,
        "neg_ratio_cur": 0.0, "tone_cur": 0.0,
        "computed_at": datetime.utcnow().isoformat(),
        "priority": adm1_code in PRIORITY_NORTH,
    }


if __name__ == "__main__":
    df = pd.read_parquet(PROJECT_ROOT / "data" / "processed" / "benin_enrichi.parquet")
    print(f"Dataset : {len(df)} événements")
    print(f"Periode : {df['SQLDATE'].min().date()} -> {df['SQLDATE'].max().date()}")

    # Référence = fin du dataset (simulation temps réel sur données 2025)
    ref = pd.Timestamp(df["SQLDATE"].max())
    scores = compute_all_departments(df, ref_date=ref)

    print("\nScore de Tension Territorial — tous départements\n")
    print(f"{'Département':<20} {'STT':>6} {'Niveau':<12} {'z_cameo':>8} {'z_tone':>8} {'N win':>6}")
    print("-" * 70)
    for s in scores:
        flag = "⚠" if s["level"] >= 1 else " "
        print(f"{s['departement']:<20} {s['stt']:>6.2f} {s['level_label']:<12} "
              f"{s['z_cameo']:>8.3f} {s['z_tone']:>8.3f} {s['n_window']:>6}  {flag}")
