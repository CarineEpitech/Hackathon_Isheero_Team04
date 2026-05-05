"""
dashboard/app.py
Benin Media Intelligence Dashboard
Hackathon iSHEERO x DataCamp 2026 — Benin Insights Challenge
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Benin Media Intelligence Dashboard",
    page_icon="BJ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------
# STYLE
# ---------------------------------------------------------------
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .metric-label { font-size: 0.85rem; color: #6c757d; }
    h1 { color: #1a3c5e; }
    h2, h3 { color: #1a3c5e; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# CHARGEMENT DES DONNEES
# ---------------------------------------------------------------
@st.cache_data
def charger_donnees():
    df = pd.read_csv("data/processed/benin_clean.csv", parse_dates=["SQLDATE"])
    return df

df = charger_donnees()

MOIS_LABELS = {
    1:"Jan", 2:"Fev", 3:"Mar", 4:"Avr", 5:"Mai", 6:"Jun",
    7:"Jul", 8:"Aou", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"
}
COULEUR_PRINCIPALE = "#1a3c5e"
COULEUR_ACCENT     = "#e63946"
COULEUR_POSITIF    = "#2a9d8f"
COULEUR_NEGATIF    = "#e76f51"

# ---------------------------------------------------------------
# SIDEBAR — FILTRES
# ---------------------------------------------------------------
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/200px-Flag_of_Benin.svg.png",
    width=120
)
st.sidebar.title("Filtres")

# Filtre mois (slider)
mois_min, mois_max = st.sidebar.select_slider(
    "Periode d'analyse",
    options=list(range(1, 13)),
    value=(1, 12),
    format_func=lambda x: MOIS_LABELS[x]
)

# Filtre zone
zones_disponibles = sorted(df["zone_benin"].dropna().unique())
zones_choisies = st.sidebar.multiselect(
    "Zone geographique du Benin",
    options=zones_disponibles,
    default=zones_disponibles
)

# Filtre type d'action
quadclasses_disponibles = sorted(df["quadclass_label"].dropna().unique())
quadclasses_choisies = st.sidebar.multiselect(
    "Type d'action",
    options=quadclasses_disponibles,
    default=quadclasses_disponibles
)

# Application des filtres
df_filtre = df[
    (df["mois"] >= mois_min) &
    (df["mois"] <= mois_max) &
    (df["zone_benin"].isin(zones_choisies)) &
    (df["quadclass_label"].isin(quadclasses_choisies))
].copy()

# ---------------------------------------------------------------
# EN-TETE
# ---------------------------------------------------------------
st.title("Benin Media Intelligence Dashboard")
st.markdown(
    "**Hackathon iSHEERO x DataCamp 2026** — "
    "Analyse de la couverture mediatique internationale du Benin (2025)  \n"
    "Source : GDELT Project · Filtre : `ActionGeo_CountryCode = 'BN'`"
)

st.markdown("---")

# ---------------------------------------------------------------
# METRIQUES CLES
# ---------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Evenements analyses",
    f"{len(df_filtre):,}",
    delta=f"{len(df_filtre) - len(df):,} vs total" if len(df_filtre) != len(df) else None
)
col2.metric(
    "Tonalite moyenne",
    f"{df_filtre['AvgTone'].mean():.2f}",
    help="AvgTone : negatif = presse hostile, positif = presse favorable"
)
col3.metric(
    "Score Goldstein moyen",
    f"{df_filtre['GoldsteinScale'].mean():.2f}",
    help="Goldstein : -10 (tres destabilisant) a +10 (tres stabilisant)"
)
col4.metric(
    "Total mentions medias",
    f"{df_filtre['NumMentions'].sum():,}"
)
col5.metric(
    "Sources distinctes",
    f"{df_filtre['source_domaine'].nunique():,}"
)

st.markdown("---")

# ---------------------------------------------------------------
# VIZ 1 — TIMELINE INTERACTIVE DES EVENEMENTS
# ---------------------------------------------------------------
st.subheader("Viz 1 — Ligne du temps des evenements et de la tonalite mediatique")
st.caption(
    "Nombre d'evenements par mois (barres) superpose a l'evolution de la tonalite moyenne (ligne). "
    "Un mois avec beaucoup d'evenements et une tonalite negative = attention mediatique hostile."
)

mensuel = (
    df_filtre.groupby("mois")
             .agg(
                 nb_evenements=("GLOBALEVENTID", "count"),
                 ton_moyen=("AvgTone", "mean"),
                 goldstein_moyen=("GoldsteinScale", "mean"),
                 mentions=("NumMentions", "sum")
             )
             .reset_index()
)
mensuel["mois_label"] = mensuel["mois"].map(MOIS_LABELS)

fig1 = make_subplots(specs=[[{"secondary_y": True}]])

fig1.add_trace(
    go.Bar(
        x=mensuel["mois_label"],
        y=mensuel["nb_evenements"],
        name="Nombre d'evenements",
        marker_color=COULEUR_PRINCIPALE,
        opacity=0.7,
        hovertemplate="<b>%{x}</b><br>Evenements : %{y:,}<extra></extra>"
    ),
    secondary_y=False
)

fig1.add_trace(
    go.Scatter(
        x=mensuel["mois_label"],
        y=mensuel["ton_moyen"],
        name="Tonalite moyenne (AvgTone)",
        line=dict(color=COULEUR_ACCENT, width=2.5),
        mode="lines+markers",
        marker=dict(size=7, color=COULEUR_ACCENT),
        hovertemplate="<b>%{x}</b><br>AvgTone : %{y:.2f}<extra></extra>"
    ),
    secondary_y=True
)

fig1.add_hline(y=0, line_dash="dash", line_color="grey", line_width=1,
               annotation_text="Neutralite", secondary_y=True)

fig1.update_layout(
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=420,
    margin=dict(l=40, r=40, t=30, b=40),
    plot_bgcolor="white",
    paper_bgcolor="white"
)
fig1.update_yaxes(title_text="Nombre d'evenements", secondary_y=False)
fig1.update_yaxes(title_text="Tonalite (AvgTone)", secondary_y=True)

st.plotly_chart(fig1, use_container_width=True)

with st.expander("Lire l'interpretation"):
    st.markdown(
        """
        **Ce que montre ce graphique**

        Les barres indiquent le volume de couverture mediatique du Benin mois par mois.
        La ligne rouge suit la tonalite : en dessous de zero, les medias parlent du Benin negativement.

        **Point d'attention :** Decembre 2025 concentre 18 % de tous les evenements annuels avec
        la tonalite la plus negative de l'annee (-2.46). Octobre 2025 est le seul mois
        a tonalite positive (+0.23).
        """
    )

st.markdown("---")

# ---------------------------------------------------------------
# VIZ 2 — CARTE DES EVENEMENTS GEOLOCALISES
# ---------------------------------------------------------------
st.subheader("Viz 2 — Carte des evenements geolocalises au Benin")
st.caption(
    "Chaque point represente un evenement. La couleur indique la tonalite (vert = positif, rouge = negatif). "
    "La taille est proportionnelle au nombre de mentions."
)

LAT_MIN, LAT_MAX = 6.0, 12.5
LON_MIN, LON_MAX = 0.8, 3.9

df_carte = df_filtre.dropna(subset=["ActionGeo_Lat", "ActionGeo_Long"]).copy()
df_carte = df_carte[
    (df_carte["ActionGeo_Lat"].between(LAT_MIN, LAT_MAX)) &
    (df_carte["ActionGeo_Long"].between(LON_MIN, LON_MAX))
]

# Echantillon pour performance (max 3000 points)
if len(df_carte) > 3000:
    df_carte = df_carte.sample(3000, random_state=42)

df_carte["taille"] = df_carte["NumMentions"].clip(1, 30)
df_carte["zone_label"] = df_carte["zone_benin"].str.capitalize()

fig2 = px.scatter_mapbox(
    df_carte,
    lat="ActionGeo_Lat",
    lon="ActionGeo_Long",
    color="AvgTone",
    size="taille",
    color_continuous_scale="RdYlGn",
    range_color=[-10, 10],
    hover_data={
        "ActionGeo_FullName": True,
        "AvgTone": ":.2f",
        "GoldsteinScale": ":.2f",
        "NumMentions": True,
        "quadclass_label": True,
        "ActionGeo_Lat": False,
        "ActionGeo_Long": False,
        "taille": False
    },
    mapbox_style="carto-positron",
    zoom=5.2,
    center={"lat": 9.3, "lon": 2.3},
    height=520,
    opacity=0.75,
    labels={"AvgTone": "Tonalite"}
)

fig2.update_layout(
    coloraxis_colorbar=dict(title="Tonalite"),
    margin=dict(l=0, r=0, t=10, b=10)
)

st.plotly_chart(fig2, use_container_width=True)

with st.expander("Lire l'interpretation"):
    st.markdown(
        """
        **Ce que montre cette carte**

        La quasi-totalite des evenements se concentre dans le sud du Benin (Cotonou, Porto-Novo,
        region cotiere). Les points rouges dans le nord correspondent aux evenements de type
        securitaire — rares en nombre, mais couverts tres negativement.

        **Point d'attention :** Le nord du Benin affiche une tonalite moyenne de -4.29,
        soit 3 fois plus negative que le sud (-1.09).
        """
    )

st.markdown("---")

# ---------------------------------------------------------------
# VIZ 3 — EVOLUTION DU SENTIMENT MEDIATIQUE
# ---------------------------------------------------------------
st.subheader("Viz 3 — Evolution du sentiment mediatique par type d'action")
st.caption(
    "Repartition mensuelle des 4 grandes categories d'actions (QuadClass). "
    "Permet de voir si la couverture evolue vers plus de cooperation ou plus de conflit."
)

quad_mensuel = (
    df_filtre.groupby(["mois", "quadclass_label"])
             .size()
             .reset_index(name="nb")
)
quad_mensuel["mois_label"] = quad_mensuel["mois"].map(MOIS_LABELS)
quad_mensuel["pct"] = quad_mensuel.groupby("mois")["nb"].transform(lambda x: x / x.sum() * 100)

COULEURS_QUAD = {
    "cooperation_verbale":    COULEUR_POSITIF,
    "cooperation_materielle": "#52b788",
    "conflit_verbal":         "#f4a261",
    "conflit_materiel":       COULEUR_NEGATIF
}

col_viz3a, col_viz3b = st.columns([2, 1])

with col_viz3a:
    fig3a = px.bar(
        quad_mensuel,
        x="mois_label",
        y="pct",
        color="quadclass_label",
        color_discrete_map=COULEURS_QUAD,
        barmode="stack",
        labels={"pct": "Proportion (%)", "mois_label": "Mois", "quadclass_label": "Type d'action"},
        height=420,
        hover_data={"nb": True}
    )
    fig3a.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=30, b=40)
    )
    st.plotly_chart(fig3a, use_container_width=True)

with col_viz3b:
    # Donut global
    quad_global = df_filtre["quadclass_label"].value_counts().reset_index()
    quad_global.columns = ["type", "nb"]
    quad_global["couleur"] = quad_global["type"].map(COULEURS_QUAD)

    fig3b = px.pie(
        quad_global,
        values="nb",
        names="type",
        color="type",
        color_discrete_map=COULEURS_QUAD,
        hole=0.45,
        height=420
    )
    fig3b.update_traces(textposition="inside", textinfo="percent+label")
    fig3b.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.caption("Repartition globale sur la periode")
    st.plotly_chart(fig3b, use_container_width=True)

with st.expander("Lire l'interpretation"):
    st.markdown(
        """
        **Ce que montre ce graphique**

        La cooperation verbale (declarations, consultations, diplomatie) domine la couverture
        avec 65 % des evenements. Les conflits materiels restent minoritaires (15 %) mais
        generent le plus de mentions par evenement — leur poids mediatique reel est plus important
        que leur nombre.

        **Point d'attention :** Les mois avec une proportion elevee de conflits materiels
        correspondent aux periodes de tonalite la plus negative.
        """
    )

st.markdown("---")

# ---------------------------------------------------------------
# SECTION BONUS — TOP PAYS SOURCE
# ---------------------------------------------------------------
with st.expander("Bonus — D'ou vient la couverture mediatique ?"):
    st.subheader("Pays sources dominant la couverture du Benin")

    PAYS_LABELS = {
        "BEN":"Benin","NGA":"Nigeria","AFR":"Afrique","FRA":"France",
        "WAF":"Afrique de l'Ouest","NER":"Niger","BFA":"Burkina Faso",
        "TGO":"Togo","GBR":"Royaume-Uni","CHN":"Chine","USA":"Etats-Unis",
        "GHA":"Ghana","CIV":"Cote d'Ivoire","MLI":"Mali","SEN":"Senegal"
    }

    top_pays = (
        df_filtre.dropna(subset=["Actor1CountryCode"])
                 .groupby("Actor1CountryCode")
                 .agg(nb=("GLOBALEVENTID","count"), ton=("AvgTone","mean"))
                 .reset_index()
                 .sort_values("nb", ascending=True)
                 .tail(12)
    )
    top_pays["pays_nom"] = top_pays["Actor1CountryCode"].map(PAYS_LABELS).fillna(top_pays["Actor1CountryCode"])
    top_pays["couleur"] = top_pays["ton"].apply(lambda x: COULEUR_POSITIF if x > 0 else COULEUR_NEGATIF)

    fig_pays = px.bar(
        top_pays, x="nb", y="pays_nom", orientation="h",
        color="ton", color_continuous_scale="RdYlGn",
        range_color=[-5, 5],
        labels={"nb": "Nombre d'evenements", "pays_nom": "Pays", "ton": "Ton moyen"},
        height=420
    )
    fig_pays.update_layout(margin=dict(l=10, r=20, t=10, b=40), plot_bgcolor="white")
    st.plotly_chart(fig_pays, use_container_width=True)

# ---------------------------------------------------------------
# PIED DE PAGE
# ---------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; color:#6c757d; font-size:0.85rem;'>
    Hackathon iSHEERO x DataCamp 2026 — Benin Insights Challenge<br>
    Source : GDELT Project · Periode : Janvier–Decembre 2025 · 10 722 evenements analyses
    </div>
    """,
    unsafe_allow_html=True
)
