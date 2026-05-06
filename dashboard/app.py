# dashboard/app.py
# Dashboard Streamlit — Bénin Insights Challenge
# Lancement : streamlit run dashboard/app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path

st.set_page_config(
    page_title="Bénin Insights 2025",
    page_icon="🇧🇯",
    layout="wide",
)

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

LABELS_TRIM = {
    1: "T1 — Jan / Fév / Mar",
    2: "T2 — Avr / Mai / Jun",
    3: "T3 — Jul / Aoû / Sep",
    4: "T4 — Oct / Nov / Déc",
}

LABELS_ZONES = {"nord": "Nord", "centre": "Centre", "sud": "Sud"}

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

# Dates anormales identifiées dans le notebook (Z-score + MAD + fenêtre glissante)
DATES_ANOMALIES = {
    "2025-01-10",
    "2025-04-17",
    "2025-12-07",
    "2025-12-08",
    "2025-12-09",
    "2025-12-10",
    "2025-12-11",
    "2025-12-12",
}

# Descriptions neutres — événements réels non confirmés dans les données
DESCRIPTIONS_ANOMALIES = {
    "2025-01-10": "Pic médiatique à contextualiser",
    "2025-04-17": "Pic médiatique à contextualiser",
    "2025-12-07": "Séquence décembre — pic médiatique majeur",
    "2025-12-08": "Séquence décembre — pic médiatique majeur",
    "2025-12-09": "Séquence décembre — pic médiatique majeur",
    "2025-12-10": "Séquence décembre — pic médiatique majeur",
    "2025-12-11": "Séquence décembre — pic médiatique majeur",
    "2025-12-12": "Séquence décembre — pic médiatique majeur",
}


# ── CHARGEMENT DES DONNÉES ────────────────────────────────────────────────────

@st.cache_data
def charger_donnees():
    ROOT_DIR = Path(__file__).resolve().parent.parent
    chemin_parquet = ROOT_DIR / "data/processed/benin_enrichi.parquet"
    chemin_csv = ROOT_DIR / "data/processed/benin_enrichi.csv"
    if os.path.exists(chemin_parquet):
        return pd.read_parquet(chemin_parquet)
    elif os.path.exists(chemin_csv):
        return pd.read_csv(chemin_csv)
    else:
        st.error("Fichier de données introuvable. Lancez d'abord Pipeline.py")
        return None


# ── EN-TÊTE ───────────────────────────────────────────────────────────────────

st.title("🇧🇯 Bénin Insights 2025")
st.markdown(
    "**iSHEERO × DataCamp Hackathon 2026** — Couverture médiatique internationale du Bénin"
)
st.divider()

df = charger_donnees()

if df is not None:
    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], errors="coerce")

    # ── FILTRES SIDEBAR ───────────────────────────────────────────────────────

    st.sidebar.header("Filtres")

    trimestres = sorted(df["trimestre"].dropna().unique().tolist())
    trim_sel = st.sidebar.multiselect(
        "Trimestre",
        options=trimestres,
        format_func=lambda x: LABELS_TRIM.get(x, str(x)),
        default=trimestres,
    )

    tons = sorted(df["ton_categorie"].dropna().unique().tolist())
    ton_sel = st.sidebar.multiselect(
        "Ton médiatique",
        options=tons,
        format_func=lambda x: LABELS_TON.get(x, x),
        default=tons,
    )

    quadclasses = sorted(df["quadclass_label"].dropna().unique().tolist())
    quad_sel = st.sidebar.multiselect(
        "Type d'événement",
        options=quadclasses,
        format_func=lambda x: LABELS_QUAD.get(x, x),
        default=quadclasses,
    )

    df_filtre = df[
        df["trimestre"].isin(trim_sel)
        & df["ton_categorie"].isin(ton_sel)
        & df["quadclass_label"].isin(quad_sel)
    ]

    vide = len(df_filtre) == 0

    # ── SECTION 1 — VUE D'ENSEMBLE ────────────────────────────────────────────

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
        "Ton : −100 (très négatif) → +100 (très positif)   ·   "
        "Goldstein : −10 (déstabilisant) → +10 (stabilisant)"
    )
    st.divider()

    # ── SECTION 2 — ÉVOLUTION TEMPORELLE ─────────────────────────────────────

    st.subheader("Évolution temporelle")

    col_ton, col_gold = st.columns(2)

    with col_ton:
        if not vide:
            tone_mensuel = (
                df_filtre.groupby("mois_annee")["AvgTone"]
                .mean()
                .reset_index()
                .sort_values("mois_annee")
                .rename(columns={"mois_annee": "Mois", "AvgTone": "Ton moyen"})
            )
            fig1 = px.line(
                tone_mensuel,
                x="Mois",
                y="Ton moyen",
                markers=True,
                title="Ton médiatique mensuel (AvgTone)",
                labels={"Ton moyen": "Ton moyen"},
            )
            fig1.add_hline(
                y=0, line_dash="dash", line_color="gray", annotation_text="0"
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Aucune donnée pour les filtres sélectionnés.")

    with col_gold:
        if not vide:
            gold_mensuel = (
                df_filtre.groupby("mois_annee")["GoldsteinScale"]
                .mean()
                .reset_index()
                .sort_values("mois_annee")
                .rename(
                    columns={
                        "mois_annee": "Mois",
                        "GoldsteinScale": "Goldstein moyen",
                    }
                )
            )
            fig_gold = px.line(
                gold_mensuel,
                x="Mois",
                y="Goldstein moyen",
                markers=True,
                title="Stabilité géopolitique — score Goldstein",
                labels={"Goldstein moyen": "Score Goldstein"},
                color_discrete_sequence=["#2ca02c"],
            )
            fig_gold.add_hline(
                y=0, line_dash="dash", line_color="gray", annotation_text="0"
            )
            st.plotly_chart(fig_gold, use_container_width=True)
        else:
            st.info("Aucune donnée pour les filtres sélectionnés.")

    st.divider()

    # ── SECTION 3 — MOMENTS MARQUANTS ─────────────────────────────────────────
    # Calculé sur le dataset complet — résultats fixes issus du notebook EDA

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
        stats_anom["Description"] = stats_anom["Date"].map(DESCRIPTIONS_ANOMALIES)
        stats_anom = stats_anom[
            ["Date", "Événements", "Mentions", "Ton moyen", "Goldstein moyen", "Description"]
        ]
        st.dataframe(stats_anom.set_index("Date"), use_container_width=True)

    st.caption(
        "Dates anormales détectées par approche multi-méthodes (Z-score, MAD, fenêtre glissante) "
        "— source : notebook EDA, section 7"
    )
    st.write("")

    if not vide:
        df_dates = df_filtre.dropna(subset=["SQLDATE"])
        volume_quotidien = (
            df_dates.groupby(df_dates["SQLDATE"].dt.date)
            .size()
            .reset_index(name="Événements")
            .rename(columns={"SQLDATE": "Date"})
        )
        volume_quotidien["Date"] = pd.to_datetime(volume_quotidien["Date"])

        fig2 = px.line(
            volume_quotidien,
            x="Date",
            y="Événements",
            title="Volume d'événements par jour",
        )

        anomalies_presentes = volume_quotidien[
            volume_quotidien["Date"].dt.strftime("%Y-%m-%d").isin(DATES_ANOMALIES)
        ]
        if len(anomalies_presentes) > 0:
            fig2.add_scatter(
                x=anomalies_presentes["Date"],
                y=anomalies_presentes["Événements"],
                mode="markers",
                marker=dict(color="crimson", size=10, symbol="x"),
                name="Date anormale",
            )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

    st.divider()

    # ── SECTION 4 — GÉOGRAPHIE INTERNE ───────────────────────────────────────

    st.subheader("Géographie interne — nord, centre, sud")

    if not vide:
        zones = (
            df_filtre.groupby("zone_benin")
            .agg(
                nb_evenements=("GLOBALEVENTID", "count"),
                ton_moyen=("AvgTone", "mean"),
                goldstein_moyen=("GoldsteinScale", "mean"),
            )
            .reset_index()
        )
        zones["Zone"] = zones["zone_benin"].map(LABELS_ZONES)
        zones["Ton moyen"] = zones["ton_moyen"].round(2)
        zones["Goldstein moyen"] = zones["goldstein_moyen"].round(2)

        fig3 = px.bar(
            zones.sort_values("ton_moyen"),
            x="Ton moyen",
            y="Zone",
            orientation="h",
            title="Ton médiatique moyen par zone",
            color="Ton moyen",
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            text="Ton moyen",
        )
        fig3.add_vline(x=0, line_dash="dash", line_color="gray")
        fig3.update_traces(textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)

        zones_display = zones[
            ["Zone", "nb_evenements", "Ton moyen", "Goldstein moyen"]
        ].copy()
        zones_display.columns = ["Zone", "Nb événements", "Ton moyen", "Goldstein moyen"]
        st.dataframe(zones_display.set_index("Zone"), use_container_width=True)
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

    st.divider()

    # ── SECTION 5 — NARRATIFS ET ACTEURS ─────────────────────────────────────

    st.subheader("Narratifs et acteurs")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Types d'événements**")
        if not vide:
            quad_counts = (
                df_filtre.groupby("quadclass_label")
                .size()
                .reset_index(name="Nb")
                .sort_values("Nb", ascending=False)
            )
            quad_counts["Type"] = (
                quad_counts["quadclass_label"].map(LABELS_QUAD).fillna(quad_counts["quadclass_label"])
            )
            fig4 = px.bar(
                quad_counts,
                x="Nb",
                y="Type",
                orientation="h",
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
                .value_counts()
                .head(10)
                .reset_index()
            )
            top_acteurs.columns = ["Code", "Nb"]
            top_acteurs["Pays"] = (
                top_acteurs["Code"].map(NOMS_PAYS).fillna(top_acteurs["Code"])
            )
            fig5 = px.bar(
                top_acteurs,
                x="Nb",
                y="Pays",
                orientation="h",
                title="Top 10 pays des acteurs impliqués",
                labels={"Nb": "Nb d'événements", "Pays": ""},
            )
            fig5.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig5, use_container_width=True)
            st.caption(
                "Ces pays correspondent aux acteurs des événements, pas aux pays sources des médias."
            )
        else:
            st.info("Aucune donnée.")

    st.divider()
    st.caption("Source : GDELT Project · iSHEERO × DataCamp Hackathon 2026")
