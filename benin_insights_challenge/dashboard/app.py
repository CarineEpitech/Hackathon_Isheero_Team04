# dashboard/app.py
# Dashboard Streamlit — Bénin Insights Challenge
# Lancement : streamlit run dashboard/app.py

import json
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path
from datetime import date

st.set_page_config(
    page_title="Bénin Insights 2025",
    page_icon="🇧🇯",
    layout="wide",
)

# ── CHEMINS ───────────────────────────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
OUTPUTS_DIR = ROOT_DIR / "outputs"

# ── CONSTANTES ────────────────────────────────────────────────────────────────

LABELS_TON = {
    "tres_negatif": "Très négatif",
    "negatif": "Négatif",
    "neutre": "Neutre",
    "positif": "Positif",
    "tres_positif": "Très positif",
}

LABELS_QUAD = {
    "cooperation_verbale": "Coopération (verbale)",
    "cooperation_materielle": "Coopération (matérielle)",
    "conflit_verbal": "Conflit (verbal)",
    "conflit_materiel": "Conflit (matériel)",
}

LABELS_ZONES = {"nord": "Nord", "centre": "Centre", "sud": "Sud", "inconnu": "Inconnu"}

NOMS_PAYS = {
    "NGA": "Nigeria",
    "AFR": "Afrique (générique)",
    "FRA": "France",
    "WAF": "Afrique de l'Ouest",
    "NER": "Niger",
    "BFA": "Burkina Faso",
    "TGO": "Togo",
    "GBR": "Royaume-Uni",
    "CHN": "Chine",
    "USA": "États-Unis",
    "SEN": "Sénégal",
    "GHA": "Ghana",
    "MDG": "Madagascar",
    "CIV": "Côte d'Ivoire",
    "CMR": "Cameroun",
    "RUS": "Russie",
    "EU": "Union européenne",
    "EGY": "Égypte",
    "ZAF": "Afrique du Sud",
    "MAR": "Maroc",
}

DATE_MIN = date(2025, 1, 1)
DATE_MAX = date(2025, 12, 31)

MOIS_LABELS = {
    0: "Toute l'année",
    1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Aoû",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc",
}

# Dates anormales identifiées par approche multi-méthodes (Z-score + MAD + fenêtre glissante)
DATES_ANOMALIES = {
    "2025-01-10",
    "2025-04-17",
    "2025-12-07", "2025-12-08", "2025-12-09",
    "2025-12-10", "2025-12-11", "2025-12-12",
}

# Sources vérifiées :
# 2025-01-10 : Fête nationale du Vodoun (10 janv.) + Vodun Days à Ouidah
# — AFP, Global Voices, Africanews (janv. 2025)
# 2025-04-17 : Attaque JNIM/GSIM dans le parc W (Bénin / Niger / Burkina Faso)
# — France 24 (23 avr. 2025), Euronews, OPEX360
# 2025-12-07+ : Tentative de coup d'État (Lt.-Col. Pascal Tigri contre Patrice Talon)
# — France 24, Wikipedia FR/EN, Jeune Afrique, CBS News, Euronews
DESCRIPTIONS_ANOMALIES = {
    "2025-01-10": (
        "Fête nationale du Vodoun et Vodun Days à Ouidah — ""célébration de 3 jours, +300 000 visiteurs attendus"),
    "2025-04-17": (
        "Attaque du JNIM (Al-Qaïda) dans le parc W — ""54 militaires béninois tués, plus grande perte de l'armée béninoise"),
    "2025-12-07": (
        "Tentative de coup d'État — Lt.-Col. Pascal Tigri attaque ""la résidence de Talon, déjouée par la Garde républicaine"),
    "2025-12-08": (
        "Lendemain du coup — putschistes en fuite, aide militaire du Nigeria, ""réactions France / CEDEAO / UA"),
    "2025-12-09": (
        "Traque des mutins — déclarations CEDEAO, soutien français ""en renseignement confirmé par Macron"),
    "2025-12-10": (
        "Couverture internationale soutenue — ""crise institutionnelle et sécuritaire au Bénin"),
    "2025-12-11": (
        "Arrestations — premières personnes écrouées, ""Tigri toujours en cavale, enquête judiciaire ouverte"),
    "2025-12-12": (
        "Bilan judiciaire — une trentaine de personnes écrouées ""(majorité militaires), mutins recherchés"),
}

# Bounding box Bénin pour filtrage géographique (lat/lon)
BENIN_LAT = (5.5, 12.5)
BENIN_LON = (0.5, 3.8)
MAP_MAX_POINTS = 2000


# ── CHARGEMENT DES DONNÉES ────────────────────────────────────────────────────

@st.cache_data
def charger_donnees():
    chemin_parquet = ROOT_DIR / "data/processed/benin_enrichi.parquet"
    chemin_csv = ROOT_DIR / "data/processed/benin_enrichi.csv"
    df = None
    if chemin_parquet.exists():
        try:
            df = pd.read_parquet(chemin_parquet)
        except Exception:
            df = None
    if df is None and chemin_csv.exists():
        try:
            df = pd.read_csv(chemin_csv, low_memory=False)
        except Exception:
            return None
    if df is None:
        return None
    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], errors="coerce")
    return df


# ── EN-TÊTE ───────────────────────────────────────────────────────────────────

_armoiries = ASSETS_DIR / "armoiries_benin.png"
col_logo, col_titre = st.columns([1, 11])
with col_logo:
    if _armoiries.exists():
        try:
            st.image(str(_armoiries), width=72)
        except Exception:
            pass
with col_titre:
    st.markdown("## Bénin Insights 2025")
    st.markdown(
        "**iSHEERO × DataCamp Hackathon 2026** ""— Couverture médiatique internationale du Bénin · Source : GDELT")

st.divider()

df = charger_donnees()

if df is None:
    st.error(
        "Fichier de données introuvable. ""Exécutez d'abord `Pipeline.py` pour générer `data/processed/benin_enrichi.parquet`.")
    st.stop()


# ── FILTRES TEMPORELS HORIZONTAUX ─────────────────────────────────────────────

st.markdown("**Période d'analyse**")
col_mois, col_dates = st.columns([7, 3])

with col_mois:
    mois_sel = st.radio(
        "Mois :",
        options=list(MOIS_LABELS.keys()),
        format_func=lambda x: MOIS_LABELS[x],
        horizontal=True,
        index=0,
        key="mois_radio",
    )

with col_dates:
    if mois_sel == 0:
        periode = st.date_input(
            "Plage de dates :",
            value=(DATE_MIN, DATE_MAX),
            min_value=DATE_MIN,
            max_value=DATE_MAX,
            format="DD/MM/YYYY",
            key="plage_dates",
        )
    else:
        st.caption(f"Filtre actif : **{MOIS_LABELS[mois_sel]} 2025**")
        periode = None

st.divider()

# ── FILTRES THÉMATIQUES (SIDEBAR) ─────────────────────────────────────────────

st.sidebar.header("Filtres thématiques")

tons = sorted(df["ton_categorie"].dropna().unique().tolist()) if "ton_categorie" in df.columns else []
ton_sel = st.sidebar.multiselect(
    "Ton médiatique",
    options=tons,
    format_func=lambda x: LABELS_TON.get(x, x),
    default=tons,
)

quadclasses = sorted(df["quadclass_label"].dropna().unique().tolist()) if "quadclass_label" in df.columns else []
quad_sel = st.sidebar.multiselect(
    "Type d'événement",
    options=quadclasses,
    format_func=lambda x: LABELS_QUAD.get(x, x),
    default=quadclasses,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Limites GDELT")
st.sidebar.caption(
    "**Localisation :** 91 % des événements ont une géolocalisation générique (pas de ville précise) \n""**Acteurs :** 49 % des événements sans `Actor1CountryCode` \n""**Sources :** 22 % des articles proviennent de médias nigérians (.ng) \n""**Interprétation :** GDELT mesure la *couverture médiatique*, pas les faits réels"
)

# ── APPLICATION DES FILTRES ───────────────────────────────────────────────────

if mois_sel != 0:
    df_date = df[df["SQLDATE"].dt.month == mois_sel]
else:
    if isinstance(periode, (list, tuple)) and len(periode) == 2:
        d_start = pd.Timestamp(periode[0])
        d_end = pd.Timestamp(periode[1])
    elif isinstance(periode, date):
        d_start = d_end = pd.Timestamp(periode)
    else:
        d_start = pd.Timestamp(DATE_MIN)
        d_end = pd.Timestamp(DATE_MAX)
    df_date = df[(df["SQLDATE"] >= d_start) & (df["SQLDATE"] <= d_end)]

mask = pd.Series(True, index=df_date.index)
if "ton_categorie" in df_date.columns and ton_sel:
    mask &= df_date["ton_categorie"].isin(ton_sel)
if "quadclass_label" in df_date.columns and quad_sel:
    mask &= df_date["quadclass_label"].isin(quad_sel)
df_filtre = df_date[mask]

vide = len(df_filtre) == 0

# ── SECTION 1 — VUE D'ENSEMBLE ────────────────────────────────────────────────

st.subheader("Vue d'ensemble")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Événements", f"{len(df_filtre):,}" if not vide else "—")
with col2:
    val = f"{df_filtre['AvgTone'].mean():.2f}" if not vide else "—"
    st.metric("Ton médiatique moyen", val)
with col3:
    val = f"{df_filtre['GoldsteinScale'].mean():.2f}" if not vide else "—"
    st.metric("Score Goldstein moyen", val)
with col4:
    val = str(df_filtre["SQLDATE"].dt.date.nunique()) if not vide else "—"
    st.metric("Jours couverts", val)

st.caption(
    "Ton : −100 (très négatif) → +100 (très positif) · ""Goldstein : −10 (déstabilisant) → +10 (stabilisant)"
)
st.divider()

# ── SECTION 2 — ÉVOLUTION TEMPORELLE ─────────────────────────────────────────

st.subheader("Évolution temporelle")
col_ton, col_gold = st.columns(2)

with col_ton:
    if not vide and "mois_annee" in df_filtre.columns:
        tone_mensuel = (
            df_filtre.groupby("mois_annee")["AvgTone"]
            .mean().reset_index().sort_values("mois_annee")
            .rename(columns={"mois_annee": "Mois", "AvgTone": "Ton moyen"})
        )
        fig1 = px.line(
            tone_mensuel, x="Mois", y="Ton moyen", markers=True,
            title="Ton médiatique mensuel (AvgTone)",
        )
        fig1.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="0")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

with col_gold:
    if not vide and "mois_annee" in df_filtre.columns:
        gold_mensuel = (
            df_filtre.groupby("mois_annee")["GoldsteinScale"]
            .mean().reset_index().sort_values("mois_annee")
            .rename(columns={"mois_annee": "Mois", "GoldsteinScale": "Goldstein moyen"})
        )
        fig_gold = px.line(
            gold_mensuel, x="Mois", y="Goldstein moyen", markers=True,
            title="Stabilité géopolitique — score Goldstein",
            color_discrete_sequence=["#2ca02c"],
        )
        fig_gold.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="0")
        st.plotly_chart(fig_gold, use_container_width=True)
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

st.divider()

# ── SECTION 3 — MOMENTS MARQUANTS ─────────────────────────────────────────────
# Calculé sur le dataset complet — résultats fixes, indépendants des filtres actifs

st.subheader("Moments marquants de 2025")

df_anom = df[df["SQLDATE"].dt.strftime("%Y-%m-%d").isin(DATES_ANOMALIES)]
if len(df_anom) > 0:
    stats_anom = (
        df_anom.groupby(df_anom["SQLDATE"].dt.strftime("%Y-%m-%d"))
        .agg(
            Événements=("GLOBALEVENTID", "count"),
            Mentions=("NumMentions", "sum"),
            ton_moyen=("AvgTone", "mean"),
            goldstein_moyen=("GoldsteinScale", "mean"),
        )
        .reset_index()
        .rename(columns={"SQLDATE": "Date"})
        .sort_values("Date")
    )
    stats_anom["Ton moyen"] = stats_anom["ton_moyen"].round(2)
    stats_anom["Goldstein moyen"] = stats_anom["goldstein_moyen"].round(2)
    stats_anom["Événement probable"] = stats_anom["Date"].map(DESCRIPTIONS_ANOMALIES)
    stats_anom = stats_anom[[
        "Date", "Événements", "Mentions",
        "Ton moyen", "Goldstein moyen", "Événement probable",
    ]]
    st.dataframe(stats_anom.set_index("Date"), use_container_width=True)

st.caption(
    "Dates détectées par approche multi-méthodes (Z-score + MAD + fenêtre glissante) — ""notebook EDA section 7 · ""Événements : sources AFP, France 24, Euronews, Jeune Afrique (2025)"
)
st.write("")

if not vide:
    volume_quotidien = (
        df_filtre.dropna(subset=["SQLDATE"])
        .groupby(df_filtre["SQLDATE"].dt.date)
        .size().reset_index(name="Événements")
        .rename(columns={"SQLDATE": "Date"})
    )
    volume_quotidien["Date"] = pd.to_datetime(volume_quotidien["Date"])

    fig2 = px.line(
        volume_quotidien, x="Date", y="Événements",
        title="Volume d'événements par jour",
    )
    anomalies_visibles = volume_quotidien[
        volume_quotidien["Date"].dt.strftime("%Y-%m-%d").isin(DATES_ANOMALIES)
    ]
    if len(anomalies_visibles) > 0:
        fig2.add_scatter(
            x=anomalies_visibles["Date"],
            y=anomalies_visibles["Événements"],
            mode="markers",
            marker=dict(color="crimson", size=10, symbol="x"),
            name="Date anormale",
        )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Aucune donnée pour les filtres sélectionnés.")

st.divider()

# ── SECTION 4 — CARTE DES ÉVÉNEMENTS ──────────────────────────────────────────

st.subheader("Carte des événements au Bénin")

df_geo = df_filtre.dropna(subset=["ActionGeo_Lat", "ActionGeo_Long"]).copy()
df_geo = df_geo[
    (df_geo["ActionGeo_Lat"] >= BENIN_LAT[0]) & (df_geo["ActionGeo_Lat"] <= BENIN_LAT[1]) &
    (df_geo["ActionGeo_Long"] >= BENIN_LON[0]) & (df_geo["ActionGeo_Long"] <= BENIN_LON[1])
]
# Exclure les events au centroïde pays générique (ADM1Code = BN, coords 9.5 / 2.25)
# 91 % du dataset a cette localisation non précise — les inclure créerait un empilement de points au même endroit
n_generique = int((df_geo.get("ActionGeo_ADM1Code", "").eq("BN")).sum()) if "ActionGeo_ADM1Code" in df_geo.columns else 0
df_geo = df_geo[df_geo.get("ActionGeo_ADM1Code", "") != "BN"] if "ActionGeo_ADM1Code" in df_geo.columns else df_geo

if vide or len(df_geo) == 0:
    st.info(
        "Aucune localisation précise disponible pour les filtres sélectionnés. ""Les événements sans ville identifiée (localisation générique pays) sont exclus de la carte.")
else:
    n_total = len(df_geo)
    if n_total > MAP_MAX_POINTS:
        df_geo = df_geo.sample(MAP_MAX_POINTS, random_state=42)

    df_geo["Zone"] = df_geo["zone_benin"].map(LABELS_ZONES).fillna("Inconnu") if "zone_benin" in df_geo.columns else "Inconnu"
    df_geo["Taille"] = (df_geo["NumMentions"].clip(upper=100).fillna(5) / 10 + 4).round(1)
    df_geo["Lieu"] = df_geo["ActionGeo_FullName"].fillna("Localisation inconnue")

    _map_title = (
        f"Localisation précise — {len(df_geo):,} points"+ (f" (échantillon sur {n_total:,})" if n_total > MAP_MAX_POINTS else "")
    )
    _map_kwargs = dict(
        lat="ActionGeo_Lat",
        lon="ActionGeo_Long",
        color="AvgTone",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        range_color=[-6, 6],
        size="Taille",
        size_max=14,
        hover_name="Lieu",
        hover_data={
            "AvgTone": ":.2f",
            "Zone": True,
            "Taille": False,
            "ActionGeo_Lat": False,
            "ActionGeo_Long": False,
        },
        zoom=5.5,
        center={"lat": 9.3, "lon": 2.3},
        title=_map_title,
        labels={"AvgTone": "Ton"},
    )
    fig_map = None
    # Plotly 5.24+ / 6.x : px.scatter_map (pas de token nécessaire)
    if hasattr(px, "scatter_map"):
        try:
            fig_map = px.scatter_map(df_geo, map_style="carto-positron", **_map_kwargs)
        except Exception:
            fig_map = None
    # Plotly 5.x : px.scatter_mapbox avec tuiles libres
    if fig_map is None:
        try:
            fig_map = px.scatter_mapbox(df_geo, mapbox_style="open-street-map", **_map_kwargs)
        except Exception:
            fig_map = None
    # Fallback universel : carte géographique sans tuiles
    if fig_map is None:
        fig_map = px.scatter_geo(
            df_geo,
            lat="ActionGeo_Lat",
            lon="ActionGeo_Long",
            color="AvgTone",
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            range_color=[-6, 6],
            size="Taille",
            size_max=14,
            hover_name="Lieu",
            title=_map_title,
            labels={"AvgTone": "Ton"},
            scope="africa",
            fitbounds="locations",
        )
    fig_map.update_layout(height=520, margin={"r": 0, "l": 0, "t": 40, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption(
        "Couleur : ton médiatique — rouge = négatif · vert = positif · ""Taille : volume de mentions · ""Coordonnées : ActionGeo_Lat / ActionGeo_Long (GDELT) · "f"Carte : {n_total:,} événements précisément localisés (ville) sur {len(df_filtre):,} au total — "f"les {n_generique:,} événements à localisation pays générique sont exclus de la carte.")

    # Export carte — désactivé (kaleido non disponible sur Streamlit Cloud)
    # with st.expander("Exporter la carte (PNG)"):
    #     if st.button("Exporter"):
    #         import plotly.io as pio, io
    #         img_bytes = pio.to_image(fig_map, format="png", width=1400, height=900, scale=2)
    #         st.download_button("Télécharger carte_benin_pitch.png", img_bytes,
    #                            file_name="carte_benin_pitch.png", mime="image/png")

st.divider()

# ── SECTION 5 — GÉOGRAPHIE INTERNE ───────────────────────────────────────────

st.subheader("Géographie interne — nord, centre, sud")

if not vide and "zone_benin" in df_filtre.columns:
    if "ActionGeo_ADM1Code" in df_filtre.columns:
        _n_gen = int((df_filtre["ActionGeo_ADM1Code"] == "BN").sum())
        _pct_gen = round(_n_gen / len(df_filtre) * 100, 1)
        st.warning(
            f"**Biais de localisation GDELT** — {_n_gen:,} événements ({_pct_gen} % du total sélectionné) ""ont une localisation générique pays (ADM1=BN), comptabilisés dans la zone 'sud' par défaut. ""La barre 'Sud' ne signifie pas que ces événements ont lieu au sud — ""elle signifie principalement 'événement attribué au Bénin sans ville précise'.")

    zones = (
        df_filtre.groupby("zone_benin")
        .agg(
            nb_evenements=("GLOBALEVENTID", "count"),
            ton_moyen=("AvgTone", "mean"),
            goldstein_moyen=("GoldsteinScale", "mean"),
        )
        .reset_index()
    )
    zones["Zone"] = zones["zone_benin"].map(LABELS_ZONES).fillna(zones["zone_benin"])
    zones["Ton moyen"] = zones["ton_moyen"].round(2)
    zones["Goldstein moyen"] = zones["goldstein_moyen"].round(2)

    fig3 = px.bar(
        zones.sort_values("ton_moyen"),
        x="Ton moyen", y="Zone", orientation="h",
        title="Ton médiatique moyen par zone",
        color="Ton moyen",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        text="Ton moyen",
    )
    fig3.add_vline(x=0, line_dash="dash", line_color="gray")
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    zones_display = zones[["Zone", "nb_evenements", "Ton moyen", "Goldstein moyen"]].copy()
    zones_display.columns = ["Zone", "Nb événements", "Ton moyen", "Goldstein moyen"]
    st.dataframe(zones_display.set_index("Zone"), use_container_width=True)
else:
    st.info("Aucune donnée pour les filtres sélectionnés.")

st.divider()

# ── SECTION 6 — MODÈLE PRÉDICTIF ML ──────────────────────────────────────────

st.subheader("Modèle prédictif — Ton médiatique")

_metrics_path = ROOT_DIR / "models/metrics_rf.json"
if _metrics_path.exists():
    try:
        with open(_metrics_path) as _f:
            _m = json.load(_f)
        col_ma, col_mb, col_mc, col_md = st.columns(4)
        with col_ma:
            st.metric("Accuracy Random Forest", f"{_m['acc_rf']*100:.0f} %")
        with col_mb:
            st.metric("Baseline (classe maj.)", f"{_m['acc_dummy']*100:.1f} %")
        with col_mc:
            st.metric("Gain réel", f"+{_m['gain_baseline']*100:.0f} pp")
        with col_md:
            st.metric("CV 5-fold", f"{_m['cv_mean']*100:.1f} % ± {_m['cv_std']*100:.1f} %")

        _fi = _m.get("feature_importance", {})
        if _fi:
            _fi_df = pd.DataFrame({"Variable": list(_fi.keys()), "Importance": list(_fi.values())})
            _fi_df = _fi_df.sort_values("Importance")
            _fig_fi = px.bar(
                _fi_df, x="Importance", y="Variable", orientation="h",
                title="Importance des variables (Gini impurity)",
                color="Importance",
                color_continuous_scale="Blues",
                labels={"Importance": "Importance Gini", "Variable": ""},
            )
            _fig_fi.update_layout(coloraxis_showscale=False)
            st.plotly_chart(_fig_fi, use_container_width=True)

        st.caption(
            "Random Forest · n_estimators=100 · class_weight='balanced' · split stratifié 80/20 · ""random_state=42 · ""La variable `mois` domine (Gini=0,34) — le modèle capture la saisonnalité de 2025. ""Sans `mois` : accuracy ≈ 65 %. · ""Ce modèle ne prédit pas l'avenir et ne se généralise pas automatiquement à 2026.")
    except Exception as _e:
        st.info(f"Métriques ML non chargées : {_e}")
else:
    st.info(
        "Métriques ML non disponibles — exécuter `notebooks/04_analyse_complete.ipynb` ""pour générer `models/metrics_rf.json`.")

st.divider()

# ── SECTION 7 — NARRATIFS ET ACTEURS ─────────────────────────────────────────

st.subheader("Narratifs et acteurs")
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("**Types d'événements**")
    if not vide:
        quad_counts = (
            df_filtre.groupby("quadclass_label")
            .size().reset_index(name="Nb")
            .sort_values("Nb", ascending=False)
        )
        quad_counts["Type"] = (
            quad_counts["quadclass_label"]
            .map(LABELS_QUAD)
            .fillna(quad_counts["quadclass_label"])
        )
        fig4 = px.bar(
            quad_counts, x="Nb", y="Type", orientation="h",
            title="Répartition par type d'événement",
            labels={"Nb": "Nb d'événements", "Type": ""},
        )
        fig4.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_right:
    st.markdown("**Pays impliqués dans les événements (hors Bénin)**")
    if not vide:
        top_acteurs = (
            df_filtre[df_filtre["Actor1CountryCode"] != "BEN"]["Actor1CountryCode"]
            .value_counts().head(10).reset_index()
        )
        top_acteurs.columns = ["Code", "Nb"]
        top_acteurs["Pays"] = (
            top_acteurs["Code"].map(NOMS_PAYS).fillna(top_acteurs["Code"])
        )
        fig5 = px.bar(
            top_acteurs, x="Nb", y="Pays", orientation="h",
            title="Top 10 pays des acteurs impliqués",
            labels={"Nb": "Nb d'événements", "Pays": ""},
        )
        fig5.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig5, use_container_width=True)
        n_actor_null = int(df_filtre["Actor1CountryCode"].isna().sum()) if "Actor1CountryCode" in df_filtre.columns else 0
        n_actor_total = len(df_filtre)
        pct_null = round(n_actor_null / n_actor_total * 100, 1) if n_actor_total > 0 else 0
        st.caption(
            "Ces pays correspondent aux acteurs des événements, pas aux pays sources des médias. · "f"Note : Actor1CountryCode est non renseigné pour {n_actor_null:,} événements sur {n_actor_total:,} ({pct_null} %) — ""seuls les événements avec acteur identifié apparaissent dans ce graphique.")
    else:
        st.info("Aucune donnée.")

st.markdown("**Provenance des sources médias**")
if not vide:
    if "source_domaine" in df_filtre.columns:
        _src_counts = df_filtre["source_domaine"].value_counts().head(15).reset_index()
        _src_counts.columns = ["Domaine", "Articles"]
        _fig_src = px.bar(
            _src_counts, x="Articles", y="Domaine", orientation="h",
            title="Top 15 domaines sources",
            labels={"Articles": "Nb d'articles", "Domaine": ""},
        )
        _fig_src.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(_fig_src, use_container_width=True)
        _n_ng = int(df_filtre["source_domaine"].str.endswith(".ng", na=False).sum())
        _n_bj = int(df_filtre["source_domaine"].str.endswith(".bj", na=False).sum())
        _n_src = len(df_filtre)
        st.caption(
            f"Sources .ng (médias nigérians) : {_n_ng:,} articles ({round(_n_ng/_n_src*100,1) if _n_src>0 else 0} %) · "f"Sources .bj (médias béninois) : {_n_bj:,} articles ({round(_n_bj/_n_src*100,1) if _n_src>0 else 0} %) · ""L'image internationale du Bénin est construite à ~22 % par les médias nigérians.")
    else:
        st.markdown(
            "Estimé sur 23 859 événements (dataset complet) : \n""- **Sources .ng** (médias nigérians) : **22,3 %** des articles \n""- **Sources .bj** (médias béninois) : **0,6 %** des articles \n\n""> L'image internationale du Bénin est construite à plus de 20 % ""par les médias d'Afrique de l'Ouest — en particulier les médias nigérians.")

st.divider()
st.caption(
    "Source : GDELT Project · iSHEERO × DataCamp Hackathon 2026 · Équipe 04 · ""Événements contextuels : AFP, France 24, Euronews, Jeune Afrique"
)
