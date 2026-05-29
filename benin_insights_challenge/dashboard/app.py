# dashboard/app.py — BeninScope / TERROIR Phase 2
# Lancement : streamlit run dashboard/app.py

import json
import sys
import time
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date, datetime

ROOT_DIR   = Path(__file__).resolve().parent.parent
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
sys.path.insert(0, str(ROOT_DIR / "backend" / "services"))

from gdelt_live_poller import (
    start_background_poller,
    load_live_events,
    get_live_stats,
    run_one_cycle,
)

st.set_page_config(
    page_title="BeninScope — TERROIR",
    page_icon="🇧🇯",
    layout="wide",
)

# ── GDELT LIVE — démarrage thread daemon (une seule fois par session) ─────────
if "poller_started" not in st.session_state:
    start_background_poller()
    st.session_state["poller_started"] = True

# ── CONSTANTES ────────────────────────────────────────────────────────────────

LABELS_TON = {
    "tres_negatif": "Très négatif", "negatif": "Négatif", "neutre": "Neutre",
    "positif": "Positif", "tres_positif": "Très positif",
}
LABELS_QUAD = {
    "cooperation_verbale": "Coopération (verbale)",
    "cooperation_materielle": "Coopération (matérielle)",
    "conflit_verbal": "Conflit (verbal)",
    "conflit_materiel": "Conflit (matériel)",
}
LABELS_ZONES  = {"nord": "Nord", "centre": "Centre", "sud": "Sud", "inconnu": "Inconnu"}
NOMS_PAYS = {
    "NGA": "Nigeria", "AFR": "Afrique (générique)", "FRA": "France",
    "WAF": "Afrique de l'Ouest", "NER": "Niger", "BFA": "Burkina Faso",
    "TGO": "Togo", "GBR": "Royaume-Uni", "CHN": "Chine", "USA": "États-Unis",
    "SEN": "Sénégal", "GHA": "Ghana", "CIV": "Côte d'Ivoire", "CMR": "Cameroun",
}
DATE_MIN = date(2025, 1, 1)
DATE_MAX = date(2025, 12, 31)
MOIS_LABELS = {
    0: "Toute l'année", 1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Aoû", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc",
}
DATES_ANOMALIES = {
    "2025-01-10", "2025-04-17",
    "2025-12-07", "2025-12-08", "2025-12-09",
    "2025-12-10", "2025-12-11", "2025-12-12",
}
DESCRIPTIONS_ANOMALIES = {
    "2025-01-10": "Fête nationale du Vodoun — Vodun Days à Ouidah",
    "2025-04-17": "Attaque JNIM (Al-Qaïda) dans le parc W — 54 militaires tués",
    "2025-12-07": "Tentative de coup d'État — Lt.-Col. Pascal Tigri",
    "2025-12-08": "Putschistes en fuite — aide militaire du Nigeria",
    "2025-12-09": "Traque des mutins — soutien français confirmé",
    "2025-12-10": "Couverture internationale soutenue",
    "2025-12-11": "Premières arrestations — Tigri en cavale",
    "2025-12-12": "Bilan judiciaire — une trentaine écrouée",
}
INCIDENT_TYPES = [
    "Agression", "Vol / Cambriolage", "Conflit armé",
    "Manifestation", "Tension", "Enlèvement",
    "Attentat / Explosion", "Autre",
]
BENIN_LAT  = (5.5, 12.5)
BENIN_LON  = (0.5, 3.8)
MAP_MAX_POINTS = 2000
LEVEL_COLORS = {0: "#4caf50", 1: "#ff9800", 2: "#f44336"}
LEVEL_LABELS = {0: "Normal", 1: "Précaution", 2: "Alerte"}

# ── CHARGEMENT DONNÉES ────────────────────────────────────────────────────────

@st.cache_data(ttl=900)
def charger_donnees_historiques():
    chemin = ROOT_DIR / "data/processed/benin_enrichi.parquet"
    if chemin.exists():
        df = pd.read_parquet(chemin)
        df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], errors="coerce")
        return df
    return pd.DataFrame()


@st.cache_data(ttl=900)
def charger_donnees_live():
    """
    Retourne les données combinées (benin_enrichi + benin_live) filtrées
    sur les 30 derniers jours — source unique pour la carte et les métriques live.
    Fallback sur le dataset historique complet si la fenêtre est vide.
    """
    sys.path.insert(0, str(ROOT_DIR / "backend" / "services"))
    from data_loader import load_combined_data
    df = load_combined_data()
    if df.empty:
        df_h = charger_donnees_historiques()
        return df_h, "historique (fallback)"
    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], errors="coerce")
    cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=30)
    df_30 = df[df["SQLDATE"] >= cutoff].copy()
    if df_30.empty:
        return df, f"combiné complet ({len(df):,} évts)"
    return df_30, f"combiné 30j ({len(df_30):,} évts)"


def charger_incidents():
    try:
        from reporting import load_recent
        return load_recent(hours=72)
    except Exception:
        return pd.DataFrame()


def charger_stt():
    try:
        from metrics import compute_all_departments
        from data_loader import load_combined_data
        df = load_combined_data()
        if df.empty:
            return []
        df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], errors="coerce")
        ref = pd.Timestamp.now()   # ancrage sur aujourd'hui, pas sur max(SQLDATE)
        return compute_all_departments(df, ref_date=ref)
    except Exception as e:
        st.warning(f"Calcul STT indisponible : {e}")
        return []


def _plotly_map(df_points, color_col, title, color_scale="RdYlGn", mid=0, rng=(-6, 6)):
    kwargs = dict(
        lat="lat", lon="lon", color=color_col,
        color_continuous_scale=color_scale,
        color_continuous_midpoint=mid,
        range_color=list(rng),
        hover_name="label",
        hover_data={"lat": False, "lon": False},
        zoom=5.5,
        center={"lat": 9.3, "lon": 2.3},
        title=title,
    )
    if hasattr(px, "scatter_map"):
        try:
            return px.scatter_map(df_points, map_style="carto-positron", **kwargs)
        except Exception:
            pass
    try:
        return px.scatter_mapbox(df_points, mapbox_style="open-street-map", **kwargs)
    except Exception:
        pass
    return px.scatter_geo(
        df_points, lat="lat", lon="lon", color=color_col,
        color_continuous_scale=color_scale, color_continuous_midpoint=mid,
        range_color=list(rng), hover_name="label",
        title=title, scope="africa", fitbounds="locations",
    )


# ── EN-TÊTE ───────────────────────────────────────────────────────────────────

_armoiries = ASSETS_DIR / "armoiries_benin.png"
col_logo, col_titre = st.columns([1, 11])
with col_logo:
    if _armoiries.exists():
        st.image(str(_armoiries), width=72)
with col_titre:
    st.markdown("## BeninScope — TERROIR")
    st.markdown(
        "**Veille territoriale & signalement citoyen — Bénin** · "
        "iSHEERO × DataCamp Hackathon 2026 · Source : GDELT + terrain"
    )

st.divider()

df_hist = charger_donnees_historiques()
if df_hist.empty:
    st.error("Dataset introuvable. Exécutez Pipeline.py pour générer benin_enrichi.parquet.")
    st.stop()

# ── ONGLETS ───────────────────────────────────────────────────────────────────

tab_live, tab_signal, tab_terroir, tab_analyse = st.tabs([
    "Carte Live",
    "Signaler un incident",
    "TERROIR — Scoring",
    "Analyse 2025",
])

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — CARTE LIVE
# ══════════════════════════════════════════════════════════════════════════════

with tab_live:
    # ── Bandeau statut live ───────────────────────────────────────────────────
    _stats_live = get_live_stats()
    if _stats_live["n_events"] > 0:
        _last_d = _stats_live["last_date"]
        _last_d_str = (
            pd.Timestamp(_last_d).strftime("%d %b %Y")
            if _last_d is not None else "—"
        )
        st.success(
            f"**Données à jour** — Dernier événement : {_last_d_str} "
            f"· {_stats_live['n_events']} événements live "
            f"· Refresh auto toutes les 15 min"
        )
    else:
        st.warning(
            "**Mode historique** — Données live en cours de chargement "
            "(premier cycle dans les 15 prochaines minutes)"
        )

    col_hdr, col_refresh = st.columns([8, 2])
    with col_hdr:
        st.markdown("### Carte des événements sécuritaires en temps réel")
        st.caption("GDELT mis à jour toutes les 15 min · Signalements citoyens en orange")
    with col_refresh:
        st.write("")
        if st.button("Rafraîchir", key="refresh_live"):
            with st.spinner("Interrogation GDELT en cours..."):
                _result = run_one_cycle()
            if _result["n_new"] > 0:
                st.toast(f"{_result['n_new']} nouvelle(s) ligne(s) ajoutée(s)", icon="✅")
            st.cache_data.clear()
            st.rerun()

    df_live, src_name = charger_donnees_live()
    df_incidents       = charger_incidents()

    # Filtrer événements sécurité GDELT
    SECURITY_ROOTS = {13, 14, 15, 17, 18, 19, 20}
    if "EventRootCode" in df_live.columns:
        df_sec = df_live[df_live["EventRootCode"].isin(SECURITY_ROOTS)].copy()
    elif "is_security" in df_live.columns:
        df_sec = df_live[df_live["is_security"] == 1].copy()
    else:
        df_sec = df_live.copy()

    df_sec = df_sec.dropna(subset=["ActionGeo_Lat", "ActionGeo_Long"])
    df_sec = df_sec[
        (df_sec["ActionGeo_Lat"].between(*BENIN_LAT)) &
        (df_sec["ActionGeo_Long"].between(*BENIN_LON))
        # ADM1 != "BN" retiré : _apply_coord_priority a déjà appliqué un jitter
        # aux centroïdes génériques, ils restent donc utiles sur la carte.
    ]

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Événements sécurité GDELT", f"{len(df_sec):,}")
    with col_m2:
        n_inc = len(df_incidents) if not df_incidents.empty else 0
        st.metric("Signalements citoyens (72h)", f"{n_inc}")
    with col_m3:
        st.metric("Source", src_name[:40])

    # Construire df unifié pour la carte
    points = []

    for _, r in df_sec.iterrows():
        code = int(r.get("EventRootCode", 0))
        label_evt = {
            13: "Menace", 14: "Protestation", 15: "Posture militaire",
            17: "Coercition", 18: "Agression", 19: "Combat", 20: "Violence de masse",
        }.get(code, "Sécurité")
        points.append({
            "lat": r["ActionGeo_Lat"], "lon": r["ActionGeo_Long"],
            "label": f"[GDELT] {label_evt} — {r.get('ActionGeo_FullName','?')}",
            "tone": float(r.get("AvgTone", 0)),
            "source_type": "GDELT",
            "marker_color": float(r.get("AvgTone", 0)),
        })

    if not df_incidents.empty:
        for _, r in df_incidents.iterrows():
            validated_label = "validé" if r.get("validated") == 1 else "non vérifié"
            points.append({
                "lat": float(r["lat"]), "lon": float(r["lon"]),
                "label": f"[CITOYEN — {validated_label}] {r['type']} — {r.get('departement','?')}",
                "tone": 3.0 if r.get("validated") == 1 else -3.0,
                "source_type": "Citoyen",
                "marker_color": -5.0,
            })

    if points:
        df_map = pd.DataFrame(points)
        fig_live = _plotly_map(df_map, "marker_color",
                               f"Incidents sécuritaires — {len(df_map)} points")
        fig_live.update_layout(height=540, margin={"r": 0, "l": 0, "t": 40, "b": 0})
        st.plotly_chart(fig_live, width='stretch')
        st.caption(
            "Rouge = ton négatif (GDELT) · Points orange = signalements citoyens · "
            "Coordonnées issues de GDELT + jitter centroïde · Bénin uniquement"
        )
    else:
        st.info(
            "Aucun événement sécuritaire précisément géolocalisé dans le snapshot actuel. "
            "C'est normal — la couverture GDELT du nord-Bénin est éparse. "
            "Le dataset historique 2025 couvre 1 862 événements sécuritaires internes."
        )

    if not df_incidents.empty:
        st.markdown("#### Derniers signalements citoyens")
        cols_show = ["timestamp", "type", "departement", "description", "source", "validated"]
        cols_show = [c for c in cols_show if c in df_incidents.columns]
        df_show = df_incidents[cols_show].copy()
        df_show["validated"] = df_show["validated"].map({0: "Non vérifié", 1: "Validé"})
        st.dataframe(df_show.head(10), width='stretch')

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — SIGNALEMENT CITOYEN
# ══════════════════════════════════════════════════════════════════════════════

with tab_signal:
    st.markdown("### Signaler un incident sécuritaire")
    st.info(
        "Tout signalement est enregistré avec le statut **Non vérifié** par défaut. "
        "Il apparaît immédiatement sur la Carte Live et peut être confirmé "
        "par recoupement avec GDELT ou par un modérateur terrain."
    )

    with st.form("form_signalement", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            type_incident = st.selectbox("Type d'incident *", INCIDENT_TYPES)
            source_sig    = st.selectbox("Vous êtes", ["citoyen", "ong", "journaliste", "autre"])
            pseudo        = st.text_input("Nom / pseudo (optionnel)")
        with col_b:
            lat = st.number_input(
                "Latitude *", min_value=5.5, max_value=12.5,
                value=6.366, step=0.001, format="%.4f",
                help="Cotonou : 6.3666 — Parakou : 9.3370",
            )
            lon = st.number_input(
                "Longitude *", min_value=0.5, max_value=3.8,
                value=2.418, step=0.001, format="%.4f",
                help="Cotonou : 2.4182 — Parakou : 2.6280",
            )

        description = st.text_area(
            "Description (optionnel)", max_chars=300,
            placeholder="Décrivez brièvement l'incident observé...",
        )

        submitted = st.form_submit_button("Soumettre le signalement", type="primary")

        if submitted:
            try:
                from reporting import submit as submit_incident
                incident_id = submit_incident(
                    type_=type_incident,
                    description=description,
                    lat=lat, lon=lon,
                    source=source_sig,
                    pseudo=pseudo if pseudo else None,
                )
                st.success(
                    f"Signalement #{incident_id} enregistré — "
                    f"{type_incident} à ({lat:.4f}, {lon:.4f}). "
                    "Visible sur la Carte Live."
                )
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Erreur lors de l'enregistrement : {e}")

    st.divider()
    st.markdown("#### Tous les signalements")
    df_all_inc = charger_incidents()
    if df_all_inc.empty:
        st.info("Aucun signalement pour le moment. Soyez le premier.")
    else:
        df_all_inc["Statut"] = df_all_inc["validated"].map({0: "Non vérifié", 1: "Validé"})
        st.dataframe(
            df_all_inc[["timestamp", "type", "departement", "description", "source", "Statut"]],
            width='stretch',
        )

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — TERROIR SCORING
# ══════════════════════════════════════════════════════════════════════════════

with tab_terroir:
    st.markdown("### TERROIR — Score de Tension Territorial (STT)")
    st.caption(
        "STT = 0.40×z_cameo + 0.35×z_tone + 0.15×z_volume + 0.10×z_sources · "
        "Fenêtre courante : 14 jours · Baseline : 90 jours précédents"
    )

    with st.spinner("Calcul des scores territoriaux..."):
        scores = charger_stt()

    if not scores:
        st.warning("Données STT indisponibles.")
    else:
        # Métriques globales
        n_alerte    = sum(1 for s in scores if s["level"] == 2)
        n_precaution= sum(1 for s in scores if s["level"] == 1)
        n_normal    = sum(1 for s in scores if s["level"] == 0)

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Zones en ALERTE", n_alerte, delta=None)
        with col_s2:
            st.metric("Zones en PRÉCAUTION", n_precaution)
        with col_s3:
            st.metric("Zones normales", n_normal)

        st.divider()

        # Tableau des scores
        df_stt = pd.DataFrame(scores)
        df_stt["Niveau"] = df_stt["level"].map(LEVEL_LABELS)
        df_stt["Priorité"] = df_stt["priority"].map({True: "Nord (prioritaire)", False: ""})

        col_t, col_g = st.columns([3, 2])

        with col_t:
            st.markdown("**Scores par département**")
            df_display = df_stt[[
                "departement", "stt", "Niveau", "z_cameo", "z_tone",
                "n_window", "Priorité"
            ]].copy()
            df_display.columns = [
                "Département", "STT", "Niveau", "z_CAMEO", "z_Ton",
                "N fenêtre", "Zone"
            ]

            def color_level(row):
                colors = {
                    "Alerte":     "background-color: #ffd6d6",
                    "Précaution": "background-color: #fff3cd",
                    "Normal":     "",
                }
                return [colors.get(row["Niveau"], "")] * len(row)

            st.dataframe(
                df_display.style.apply(color_level, axis=1),
                width='stretch', hide_index=True,
            )

        with col_g:
            st.markdown("**Distribution STT**")
            fig_stt = px.bar(
                df_stt.sort_values("stt", ascending=True),
                x="stt", y="departement", orientation="h",
                color="stt",
                color_continuous_scale=["#4caf50", "#ff9800", "#f44336"],
                range_color=[-2, 4],
                labels={"stt": "STT", "departement": ""},
                title="Score de Tension Territorial",
            )
            fig_stt.add_vline(x=2.0, line_dash="dash", line_color="#ff9800",
                              annotation_text="Précaution")
            fig_stt.add_vline(x=3.0, line_dash="dash", line_color="#f44336",
                              annotation_text="Alerte")
            fig_stt.update_layout(height=420, coloraxis_showscale=False)
            st.plotly_chart(fig_stt, width='stretch')

        # Alertes niveau 1 et 2
        alertes = [s for s in scores if s["level"] >= 1]
        if alertes:
            st.divider()
            st.markdown("#### Zones sous surveillance")
            for s in sorted(alertes, key=lambda x: x["stt"], reverse=True):
                color = "#f44336" if s["level"] == 2 else "#ff9800"
                st.markdown(
                    f'<div style="border-left: 4px solid {color}; padding: 8px 12px; '
                    f'margin: 6px 0; background: {"#fff3f3" if s["level"]==2 else "#fffbf0"}">'
                    f'<b>{s["departement"]}</b> — STT {s["stt"]:.2f} '
                    f'[{LEVEL_LABELS[s["level"]].upper()}] · '
                    f'z_cameo={s["z_cameo"]:.2f} · z_ton={s["z_tone"]:.2f} · '
                    f'{s["n_window"]} évts (14j)</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("Toutes les zones sont dans les normes historiques.")

        st.divider()
        st.caption(
            "Note : avec 91,2 % de géolocalisation générique dans GDELT, "
            "les scores départementaux reposent sur les 8,8 % d'événements précisément localisés. "
            "L'intégration ACLED (roadmap Mois 2-3) améliorera la précision géographique."
        )

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 4 — ANALYSE 2025 (contenu existant)
# ══════════════════════════════════════════════════════════════════════════════

with tab_analyse:
    # Filtres temporels
    st.markdown("**Période d'analyse**")
    col_mois, col_dates = st.columns([7, 3])

    with col_mois:
        mois_sel = st.radio(
            "Mois :", options=list(MOIS_LABELS.keys()),
            format_func=lambda x: MOIS_LABELS[x],
            horizontal=True, index=0, key="mois_radio",
        )
    with col_dates:
        if mois_sel == 0:
            periode = st.date_input(
                "Plage de dates :", value=(DATE_MIN, DATE_MAX),
                min_value=DATE_MIN, max_value=DATE_MAX,
                format="DD/MM/YYYY", key="plage_dates",
            )
        else:
            st.caption(f"Filtre actif : **{MOIS_LABELS[mois_sel]} 2025**")
            periode = None

    # ── Sidebar : indicateurs GDELT Live ─────────────────────────────────────
    _sb_stats = get_live_stats()
    with st.sidebar:
        st.markdown("---")
        st.markdown("**GDELT Live**")
        if _sb_stats["n_events"] == 0:
            st.info("En attente du premier cycle (max 15 min)")
        else:
            _sb_c1, _sb_c2 = st.columns(2)
            _sb_c1.metric("Évts live", _sb_stats["n_events"])
            _sb_c2.metric("Màj", _sb_stats["last_update"] or "—")

        if st.button("Forcer actualisation", key="force_poll_sidebar"):
            with st.spinner("Interrogation GDELT..."):
                _res = run_one_cycle()
            if _res["n_new"] > 0:
                st.success(f"{_res['n_new']} ligne(s) ajoutée(s)")
                st.cache_data.clear()
                st.rerun()
            elif _res["status"] == "no_benin_events":
                st.info("Aucun événement Bénin ce cycle.")
            elif _res["status"] in ("skipped", "all_duplicates"):
                st.info("Fichier déjà traité.")
            else:
                st.warning(f"Statut : {_res['status']}")
        st.markdown("---")

    # Filtres sidebar
    st.sidebar.header("Filtres — Analyse 2025")
    tons = sorted(df_hist["ton_categorie"].dropna().unique()) if "ton_categorie" in df_hist.columns else []
    ton_sel = st.sidebar.multiselect(
        "Ton médiatique", options=tons,
        format_func=lambda x: LABELS_TON.get(x, x), default=tons,
    )
    quadclasses = sorted(df_hist["quadclass_label"].dropna().unique()) if "quadclass_label" in df_hist.columns else []
    quad_sel = st.sidebar.multiselect(
        "Type d'événement", options=quadclasses,
        format_func=lambda x: LABELS_QUAD.get(x, x), default=quadclasses,
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Limites GDELT")
    st.sidebar.caption(
        "**Localisation :** 91 % des événements ont une géolocalisation générique\n"
        "**Acteurs :** 49 % sans `Actor1CountryCode`\n"
        "**Sources :** 22 % des articles proviennent de médias nigérians (.ng)\n"
        "**Interprétation :** GDELT mesure la *couverture médiatique*, pas les faits réels"
    )

    # Application des filtres
    if mois_sel != 0:
        df_date = df_hist[df_hist["SQLDATE"].dt.month == mois_sel]
    else:
        if isinstance(periode, (list, tuple)) and len(periode) == 2:
            d_start, d_end = pd.Timestamp(periode[0]), pd.Timestamp(periode[1])
        elif isinstance(periode, date):
            d_start = d_end = pd.Timestamp(periode)
        else:
            d_start, d_end = pd.Timestamp(DATE_MIN), pd.Timestamp(DATE_MAX)
        df_date = df_hist[(df_hist["SQLDATE"] >= d_start) & (df_hist["SQLDATE"] <= d_end)]

    mask = pd.Series(True, index=df_date.index)
    if "ton_categorie" in df_date.columns and ton_sel:
        mask &= df_date["ton_categorie"].isin(ton_sel)
    if "quadclass_label" in df_date.columns and quad_sel:
        mask &= df_date["quadclass_label"].isin(quad_sel)
    df_filtre = df_date[mask]
    vide = len(df_filtre) == 0

    # Vue d'ensemble
    st.divider()
    st.subheader("Vue d'ensemble")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Événements", f"{len(df_filtre):,}" if not vide else "—")
    with col2: st.metric("Ton moyen", f"{df_filtre['AvgTone'].mean():.2f}" if not vide else "—")
    with col3: st.metric("Goldstein moyen", f"{df_filtre['GoldsteinScale'].mean():.2f}" if not vide else "—")
    with col4: st.metric("Jours couverts", str(df_filtre["SQLDATE"].dt.date.nunique()) if not vide else "—")
    st.caption("Ton : −100 (très négatif) → +100 · Goldstein : −10 (déstabilisant) → +10 (stabilisant)")
    st.divider()

    # Évolution temporelle
    st.subheader("Évolution temporelle")
    col_ton, col_gold = st.columns(2)
    with col_ton:
        if not vide and "mois_annee" in df_filtre.columns:
            tone_m = (df_filtre.groupby("mois_annee")["AvgTone"].mean()
                      .reset_index().sort_values("mois_annee")
                      .rename(columns={"mois_annee": "Mois", "AvgTone": "Ton moyen"}))
            fig1 = px.line(tone_m, x="Mois", y="Ton moyen", markers=True,
                           title="Ton médiatique mensuel (AvgTone)")
            fig1.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="0")
            st.plotly_chart(fig1, width='stretch')
        else:
            st.info("Aucune donnée pour les filtres sélectionnés.")
    with col_gold:
        if not vide and "mois_annee" in df_filtre.columns:
            gold_m = (df_filtre.groupby("mois_annee")["GoldsteinScale"].mean()
                      .reset_index().sort_values("mois_annee")
                      .rename(columns={"mois_annee": "Mois", "GoldsteinScale": "Goldstein moyen"}))
            fig_g = px.line(gold_m, x="Mois", y="Goldstein moyen", markers=True,
                            title="Stabilité géopolitique — score Goldstein",
                            color_discrete_sequence=["#2ca02c"])
            fig_g.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="0")
            st.plotly_chart(fig_g, width='stretch')
        else:
            st.info("Aucune donnée pour les filtres sélectionnés.")
    st.divider()

    # Moments marquants
    st.subheader("Moments marquants de 2025")
    df_anom = df_hist[df_hist["SQLDATE"].dt.strftime("%Y-%m-%d").isin(DATES_ANOMALIES)]
    if len(df_anom) > 0:
        stats_anom = (
            df_anom.groupby(df_anom["SQLDATE"].dt.strftime("%Y-%m-%d"))
            .agg(Evenements=("GLOBALEVENTID","count"), Mentions=("NumMentions","sum"),
                 ton_moyen=("AvgTone","mean"), goldstein_moyen=("GoldsteinScale","mean"))
            .reset_index().rename(columns={"SQLDATE": "Date"}).sort_values("Date")
        )
        stats_anom["Ton moyen"]       = stats_anom["ton_moyen"].round(2)
        stats_anom["Goldstein moyen"] = stats_anom["goldstein_moyen"].round(2)
        stats_anom["Evenement probable"] = stats_anom["Date"].map(DESCRIPTIONS_ANOMALIES)
        st.dataframe(
            stats_anom[["Date","Evenements","Mentions","Ton moyen","Goldstein moyen","Evenement probable"]]
            .set_index("Date"), width='stretch',
        )
    if not vide:
        vol_q = (df_filtre.dropna(subset=["SQLDATE"])
                 .groupby(df_filtre["SQLDATE"].dt.date).size()
                 .reset_index(name="Evenements").rename(columns={"SQLDATE":"Date"}))
        vol_q["Date"] = pd.to_datetime(vol_q["Date"])
        fig2 = px.line(vol_q, x="Date", y="Evenements", title="Volume d'événements par jour")
        anom_vis = vol_q[vol_q["Date"].dt.strftime("%Y-%m-%d").isin(DATES_ANOMALIES)]
        if len(anom_vis):
            fig2.add_scatter(x=anom_vis["Date"], y=anom_vis["Evenements"], mode="markers",
                             marker=dict(color="crimson",size=10,symbol="x"), name="Anomalie")
        st.plotly_chart(fig2, width='stretch')
    st.divider()

    # Carte historique
    st.subheader("Carte des événements géolocalisés")
    df_geo = df_filtre.dropna(subset=["ActionGeo_Lat","ActionGeo_Long"]).copy()
    df_geo = df_geo[
        (df_geo["ActionGeo_Lat"].between(*BENIN_LAT)) &
        (df_geo["ActionGeo_Long"].between(*BENIN_LON)) &
        (df_geo.get("ActionGeo_ADM1Code","") != "BN")
    ] if "ActionGeo_ADM1Code" in df_geo.columns else df_geo
    n_gen = int((df_filtre.get("ActionGeo_ADM1Code","") == "BN").sum()) if "ActionGeo_ADM1Code" in df_filtre.columns else 0

    if not vide and len(df_geo) > 0:
        if len(df_geo) > MAP_MAX_POINTS:
            df_geo = df_geo.sample(MAP_MAX_POINTS, random_state=42)
        df_geo["label"]  = df_geo["ActionGeo_FullName"].fillna("Localisation inconnue")
        df_geo["lat"]    = df_geo["ActionGeo_Lat"]
        df_geo["lon"]    = df_geo["ActionGeo_Long"]
        fig_map = _plotly_map(df_geo, "AvgTone", f"Localisation précise — {len(df_geo):,} points")
        fig_map.update_layout(height=520, margin={"r":0,"l":0,"t":40,"b":0})
        st.plotly_chart(fig_map, width='stretch')
        st.caption(f"Couleur : ton médiatique · {n_gen:,} événements à localisation générique exclus")
    else:
        st.info("Aucune localisation précise disponible pour les filtres sélectionnés.")
    st.divider()

    # Géographie interne
    st.subheader("Géographie interne — nord, centre, sud")
    if not vide and "zone_benin" in df_filtre.columns:
        if "ActionGeo_ADM1Code" in df_filtre.columns:
            _n_gen = int((df_filtre["ActionGeo_ADM1Code"]=="BN").sum())
            st.warning(
                f"**Biais de localisation GDELT** — {_n_gen:,} événements "
                f"({round(_n_gen/len(df_filtre)*100,1)} %) géolocalisés au centroïde pays."
            )
        zones = (df_filtre.groupby("zone_benin")
                 .agg(nb=("GLOBALEVENTID","count"), ton=("AvgTone","mean"), gs=("GoldsteinScale","mean"))
                 .reset_index())
        zones["Zone"] = zones["zone_benin"].map(LABELS_ZONES).fillna(zones["zone_benin"])
        fig3 = px.bar(zones.sort_values("ton"), x="ton", y="Zone", orientation="h",
                      title="Ton moyen par zone", color="ton",
                      color_continuous_scale="RdYlGn", color_continuous_midpoint=0, text="ton")
        fig3.add_vline(x=0, line_dash="dash", line_color="gray")
        fig3.update_traces(texttemplate="%{x:.2f}", textposition="outside")
        st.plotly_chart(fig3, width='stretch')
    st.divider()

    # ML
    st.subheader("Modèle prédictif — Ton médiatique")
    _m_path = ROOT_DIR / "models/metrics_rf.json"
    if _m_path.exists():
        try:
            with open(_m_path) as _f: _m = json.load(_f)
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("Accuracy RF", f"{_m['acc_rf']*100:.0f} %")
            with c2: st.metric("Baseline", f"{_m['acc_dummy']*100:.1f} %")
            with c3: st.metric("Gain réel", f"+{_m['gain_baseline']*100:.0f} pp")
            with c4: st.metric("CV 5-fold", f"{_m['cv_mean']*100:.1f} % ± {_m['cv_std']*100:.1f} %")
            _fi = _m.get("feature_importance",{})
            if _fi:
                _fi_df = pd.DataFrame({"Variable":list(_fi.keys()),"Importance":list(_fi.values())}).sort_values("Importance")
                _fig_fi = px.bar(_fi_df, x="Importance", y="Variable", orientation="h",
                                 title="Importance des variables (Gini)",
                                 color="Importance", color_continuous_scale="Blues")
                _fig_fi.update_layout(coloraxis_showscale=False)
                st.plotly_chart(_fig_fi, width='stretch')
        except Exception as _e:
            st.info(f"Métriques ML non chargées : {_e}")
    else:
        st.info("Métriques ML non disponibles.")
    st.divider()

    # Narratifs & acteurs
    st.subheader("Narratifs et acteurs")
    col_left, col_right = st.columns(2)
    with col_left:
        if not vide:
            qc = (df_filtre.groupby("quadclass_label").size().reset_index(name="Nb").sort_values("Nb",ascending=False))
            qc["Type"] = qc["quadclass_label"].map(LABELS_QUAD).fillna(qc["quadclass_label"])
            fig4 = px.bar(qc, x="Nb", y="Type", orientation="h",
                          title="Répartition par type d'événement",
                          labels={"Nb":"Nb","Type":""})
            fig4.update_layout(yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(fig4, width='stretch')
    with col_right:
        if not vide and "Actor1CountryCode" in df_filtre.columns:
            ta = (df_filtre[df_filtre["Actor1CountryCode"]!="BEN"]["Actor1CountryCode"]
                  .value_counts().head(10).reset_index())
            ta.columns = ["Code","Nb"]
            ta["Pays"] = ta["Code"].map(NOMS_PAYS).fillna(ta["Code"])
            fig5 = px.bar(ta, x="Nb", y="Pays", orientation="h",
                          title="Top 10 pays acteurs",
                          labels={"Nb":"Nb","Pays":""})
            fig5.update_layout(yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(fig5, width='stretch')

    st.divider()
    st.caption(
        "Source : GDELT Project · iSHEERO × DataCamp Hackathon 2026 · BeninScope · "
        "Événements contextuels : AFP, France 24, Euronews, Jeune Afrique"
    )

