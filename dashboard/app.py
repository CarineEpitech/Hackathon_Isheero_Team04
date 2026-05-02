# dashboard/app.py
# Dashboard Streamlit — Bénin Insights Challenge
# Lancement : streamlit run dashboard/app.py

import streamlit as st           # Framework dashboard web
import pandas as pd              # Manipulation des données
import plotly.express as px      # Visualisations interactives
import os                        # Gestion des fichiers
from pathlib import Path

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Bénin Insights 2025-2026",  # Titre de l'onglet navigateur
    page_icon="🇧🇯",                         # Icône de l'onglet
    layout="wide"                            # Utiliser toute la largeur de l'écran
)

# --- TITRE PRINCIPAL ---
st.title("🇧🇯 Bénin Insights Challenge")
st.markdown("**iSHEERO × DataCamp Hackathon 2026** — Analyse de la couverture médiatique du Bénin")
st.divider()  # Ligne de séparation visuelle

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data  # Mettre en cache pour ne pas recharger à chaque interaction
def charger_donnees():
    # Essayer de charger le fichier enrichi, sinon le fichier propre
    ROOT_DIR = Path(__file__).resolve().parent.parent
    chemin_parquet = ROOT_DIR / "data/processed/benin_enrichi.parquet"
    chemin_csv = ROOT_DIR/"data/processed/benin_enrichi.csv"
    
    if os.path.exists(chemin_parquet):
        return pd.read_parquet(chemin_parquet)  # Parquet = plus rapide
    elif os.path.exists(chemin_csv):
        return pd.read_csv(chemin_csv)          # CSV = fallback
    else:
        st.error("❌ Fichier de données introuvable. Lancez d'abord pipeline.py")
        return None  # Retourner None si aucun fichier trouvé

df = charger_donnees()  # Charger les données

if df is not None:  # Continuer seulement si les données sont chargées

    # Convertir SQLDATE en datetime si ce n'est pas déjà fait
    df['SQLDATE'] = pd.to_datetime(df['SQLDATE'], errors='coerce')

    # --- FILTRES TEMPORELS DANS LA SIDEBAR ---
    st.sidebar.header("🎛️ Filtres")

    # Filtre par année
    annees = sorted(df['annee'].dropna().unique().tolist())
    # Récupérer la liste des années disponibles
    annee_selectionnee = st.sidebar.multiselect(
        "Année",
        options=annees,
        default=annees  # Toutes les années sélectionnées par défaut
    )

    # Filtre par ton médiatique
    tons = df['ton_categorie'].unique().tolist()
    # Récupérer les catégories de ton disponibles
    ton_selectionne = st.sidebar.multiselect(
        "Ton médiatique",
        options=tons,
        default=tons  # Tous les tons sélectionnés par défaut
    )

    # Filtre par type d'événement
    types = df['type_event'].unique().tolist()
    type_selectionne = st.sidebar.multiselect(
        "Type d'événement",
        options=types,
        default=types
    )

    # Appliquer les filtres au DataFrame
    df_filtre = df[
        (df['annee'].isin(annee_selectionnee)) &
        (df['ton_categorie'].isin(ton_selectionne)) &
        (df['type_event'].isin(type_selectionne))
    ]

    # --- MÉTRIQUES CLÉS EN HAUT ---
    col1, col2, col3, col4 = st.columns(4)
    # Créer 4 colonnes côte à côte pour les métriques

    with col1:
        st.metric("📰 Événements total", f"{len(df_filtre):,}")
        # Afficher le nombre total d'événements filtrés

    with col2:
        ton_moyen = df_filtre['AvgTone'].mean().round(2)
        st.metric("🎭 Ton moyen", ton_moyen)
        # Afficher le ton médiatique moyen

    with col3:
        goldstein_moyen = df_filtre['GoldsteinScale'].mean().round(2)
        st.metric("⚖️ Goldstein moyen", goldstein_moyen)
        # Afficher le score Goldstein moyen

    with col4:
        nb_pays = df_filtre['Actor1CountryCode'].nunique()
        st.metric("🌍 Pays impliqués", nb_pays)
        # Afficher le nombre de pays différents impliqués

    st.divider()

    # --- VISUALISATION 1 : Événements par mois ---
    st.subheader("📈 Évolution des événements par mois")
    events_par_mois = df_filtre.groupby('mois_annee').size().reset_index(name='nb_events')
    # Compter le nombre d'événements par mois
    fig1 = px.line(
        events_par_mois,
        x='mois_annee',       # Axe X : mois
        y='nb_events',        # Axe Y : nombre d'événements
        title="Nombre d'événements médiatiques sur le Bénin par mois",
        labels={'mois_annee': 'Mois', 'nb_events': "Nombre d'événements"},
        markers=True          # Afficher des points sur la courbe
    )
    st.plotly_chart(fig1, use_container_width=True)
    # Afficher le graphique en pleine largeur

    # --- VISUALISATION 2 : Répartition du ton médiatique ---
    st.subheader("🎭 Répartition du ton médiatique")
    ton_counts = df_filtre['ton_categorie'].value_counts().reset_index()
    ton_counts.columns = ['ton', 'count']
    # Compter les occurrences de chaque catégorie de ton
    fig2 = px.pie(
        ton_counts,
        names='ton',          # Catégories
        values='count',       # Valeurs
        title="Répartition positive / négative / neutre",
        color='ton',
        color_discrete_map={  # Couleurs personnalisées par catégorie
            'positif': '#2ecc71',
            'negatif': '#e74c3c',
            'neutre': '#95a5a6',
            'inconnu': '#bdc3c7'
        }
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- VISUALISATION 3 : Top pays qui parlent du Bénin ---
    st.subheader("🌍 Pays qui parlent le plus du Bénin")
    top_pays = (
        df_filtre['Actor1CountryCode']
        .value_counts()
        .head(10)              # Top 10 pays
        .reset_index()
    )
    top_pays.columns = ['pays', 'count']
    fig3 = px.bar(
        top_pays,
        x='count',            # Axe X : nombre d'événements
        y='pays',             # Axe Y : pays
        orientation='h',      # Barres horizontales
        title="Top 10 pays impliqués dans les événements au Bénin",
        labels={'count': "Nombre d'événements", 'pays': 'Pays'}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.caption("Source : GDELT Project · iSHEERO × DataCamp Hackathon 2026")
    # Note de bas de page