"""
gdelt_live_snippet.py
=====================
Snippets à copier-coller dans app.py pour intégrer le live.
NE PAS exécuter ce fichier directement.
"""

# ── 1. DANS LES IMPORTS DE app.py ─────────────────────────────────────────────

from backend.services.gdelt_live_poller import (
    start_background_poller,
    load_live_events,
    get_live_stats,
)

# ── 2. DÉMARRAGE DU THREAD (une seule fois au lancement de l'app) ─────────────
# À placer AVANT st.title(), en haut du script, hors de tout cache/session.

import streamlit as st

if "poller_started" not in st.session_state:
    start_background_poller()
    st.session_state["poller_started"] = True

# ── 3. CHARGEMENT DES DONNÉES (avec cache 15 min) ─────────────────────────────

@st.cache_data(ttl=900)
def load_historique():
    import pandas as pd
    return pd.read_parquet("data/processed/benin_enrichi.parquet")

@st.cache_data(ttl=900)
def load_live():
    return load_live_events()   # vide si aucune donnée live encore

df_hist = load_historique()
df_live = load_live()

# Dataset complet = historique + live (sans doublons)
import pandas as pd
if not df_live.empty:
    df_all = pd.concat([df_hist, df_live], ignore_index=True).drop_duplicates("GLOBALEVENTID")
else:
    df_all = df_hist

# ── 4. INDICATEURS LIVE DANS LA SIDEBAR ───────────────────────────────────────

stats = get_live_stats()

with st.sidebar:
    st.markdown("---")
    st.markdown("**GDELT Live**")

    if stats["n_events"] == 0:
        st.info("En attente du premier cycle (max 15 min)")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Évts live", stats["n_events"])
        col2.metric("Màj", stats["last_update"])

    if st.button("Forcer une actualisation"):
        from backend.services.gdelt_live_poller import run_one_cycle
        with st.spinner("Interrogation GDELT en cours..."):
            result = run_one_cycle()
        if result["n_new"] > 0:
            st.success(f"{result['n_new']} nouvelle(s) ligne(s) ajoutée(s)")
            st.cache_data.clear()
            st.rerun()
        elif result["status"] == "no_benin_events":
            st.info("Aucun événement Bénin dans ce cycle.")
        elif result["status"] == "skipped":
            st.info("Fichier déjà traité. Prochain cycle dans 15 min.")
        else:
            st.warning(f"Statut : {result['status']}")

# ── 5. BANDEAU LIVE EN HAUT DU DASHBOARD ──────────────────────────────────────

if not df_live.empty:
    last_date = pd.to_datetime(df_live["SQLDATE"]).max()
    st.success(
        f"**Données à jour** — Dernier événement : {last_date.strftime('%d %b %Y')} "
        f"· {stats['n_events']} événements live · Refresh auto toutes les 15 min"
    )
else:
    st.warning(
        "**Mode historique** — Données live en cours de chargement "
        "(premier cycle dans les 15 prochaines minutes)"
    )

# ── 6. UTILISATION DE df_all DANS LE RESTE DU DASHBOARD ──────────────────────
# Remplacer simplement df par df_all dans tous les graphes existants.
# Exemple :
#
#   daily = df_all.groupby(df_all['SQLDATE'].dt.date).agg(...)
#   nss   = compute_nss(df_all)
#   stt   = compute_stt(df_all, baseline=df_hist)
#
# La baseline STT reste df_hist (2025 uniquement).
# Le signal courant se calcule sur df_live (ou df_all[-14j]).
