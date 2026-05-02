# pipeline.py
# Usage : python pipeline.py
# Ce script extrait, nettoie et enrichit les données GDELT du Bénin en une seule commande

import pandas as pd          # Manipulation des données
import numpy as np           # Calculs numériques
import os                    # Gestion des fichiers et dossiers
from pathlib import Path     # Gestion des chemins de fichiers

# Chemin racine du projet (2 niveaux au-dessus de ce fichier)
ROOT_DIR = Path(__file__).resolve().parent.parent

def run_pipeline(input_path=None, output_dir=None):
    # Fonction principale qui enchaîne toutes les étapes du pipeline

    # Définir les chemins par défaut si non fournis
    if input_path is None:
        input_path = ROOT_DIR / "data/raw/benin_raw.csv"
        # Chemin vers le CSV brut extrait de BigQuery
    if output_dir is None:
        output_dir = ROOT_DIR / "data/processed"
        # Dossier de sortie pour les fichiers nettoyés

    print("=" * 55)
    print("🇧🇯 PIPELINE GDELT — BÉNIN INSIGHTS CHALLENGE")
    print("=" * 55)
    print(f" Source      : {input_path}")
    print(f" Destination : {output_dir}")

    # ════════════════════════════════════════════════════
    # ÉTAPE 1 : CHARGEMENT
    # ════════════════════════════════════════════════════
    print("\n Chargement des données brutes...")
    df = pd.read_csv(input_path, low_memory=False)
    # Charger le CSV brut depuis le chemin fourni en paramètre
    # low_memory=False évite les avertissements sur les colonnes avec types mixtes
    print(f"    {len(df):,} lignes chargées · {df.shape[1]} colonnes")

    # ════════════════════════════════════════════════════
    # ÉTAPE 2 : SÉLECTION DES COLONNES
    # ════════════════════════════════════════════════════
    print("\n  Sélection des colonnes utiles...")
    colonnes_cles = [
        # Identification & dates
        'GLOBALEVENTID',        # Identifiant unique de l'événement
        'SQLDATE',              # Date au format YYYYMMDD
        'MONTHYEAR',            # Mois + année au format YYYYMM
        'YEAR',                 # Année seule
        'FractionDate',         # Date décimale pour séries temporelles fines
        'IsRootEvent',          # 1=Bénin sujet principal, 0=mention secondaire

        # Géographie
        'ActionGeo_CountryCode', # Code FIPS du pays (BN pour Bénin)
        'ActionGeo_FullName',    # Nom complet du lieu (ex: "Cotonou, Benin")
        'ActionGeo_ADM1Code',    # Code département béninois
        'ActionGeo_Lat',         # Latitude GPS
        'ActionGeo_Long',        # Longitude GPS

        # Acteurs — localisation
        'Actor1Geo_CountryCode', # Pays de localisation de l'acteur 1
        'Actor2Geo_CountryCode', # Pays de localisation de l'acteur 2

        # Acteurs — nationalité & identité
        'Actor1CountryCode',     # Nationalité acteur 1 (code FIPS)
        'Actor2CountryCode',     # Nationalité acteur 2
        'Actor1Name',            # Nom de l'acteur 1
        'Actor2Name',            # Nom de l'acteur 2
        'Actor1Type1Code',       # Type CAMEO acteur 1 (GOV/MIL/NGO/CVL...)
        'Actor2Type1Code',       # Type CAMEO acteur 2
        'Actor1KnownGroupCode',  # Groupe connu acteur 1 (ISWAP, ECOWAS...)
        'Actor2KnownGroupCode',  # Groupe connu acteur 2

        # Événement & classification
        'EventRootCode',         # Code CAMEO racine (1-20)
        'EventBaseCode',         # Code CAMEO intermédiaire
        'EventCode',             # Code CAMEO précis
        'QuadClass',             # 1=Coop verbale · 2=Coop matérielle
                                 # 3=Conflit verbal · 4=Conflit matériel

        # Stabilité & volume
        'GoldsteinScale',        # Score stabilité (-10 à +10)
        'NumMentions',           # Nombre de mentions
        'NumSources',            # Nombre de sources distinctes
        'NumArticles',           # Nombre d'articles

        # Ton & sentiment
        'AvgTone',               # Ton médiatique moyen

        # Source
        'SOURCEURL'              # URL de l'article source
    ]

    colonnes_presentes = [c for c in colonnes_cles if c in df.columns]
    # Garder seulement les colonnes qui existent dans le fichier
    # (évite une erreur si une colonne attendue est absente)

    colonnes_absentes = [c for c in colonnes_cles if c not in df.columns]
    # Identifier les colonnes manquantes pour les signaler

    df = df[colonnes_presentes]
    # Réduire le DataFrame aux colonnes utiles

    print(f"    {len(colonnes_presentes)} colonnes conservées")
    if colonnes_absentes:
        print(f"     Colonnes absentes du CSV : {colonnes_absentes}")
        # Signaler les colonnes manquantes sans planter

    # ════════════════════════════════════════════════════
    # ÉTAPE 3 : CORRECTION DES TYPES
    # ════════════════════════════════════════════════════
    print("\n Correction des types de données...")

    df['SQLDATE'] = pd.to_datetime(
        df['SQLDATE'].astype(str),
        format='%Y%m%d',
        errors='coerce'
    )
    # Convertir SQLDATE en datetime Python
    # format='%Y%m%d' : date au format YYYYMMDD (ex: 20250427)
    # errors='coerce' : dates invalides → NaT au lieu de planter

    for col in ['FractionDate', 'GoldsteinScale', 'AvgTone',
                'ActionGeo_Lat', 'ActionGeo_Long',
                'NumMentions', 'NumSources', 'NumArticles']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Convertir chaque colonne numérique en float
            # errors='coerce' : valeurs non numériques → NaN

    for col in ['IsRootEvent', 'QuadClass']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Convertir IsRootEvent et QuadClass en entier (0/1 et 1/2/3/4)

    print(f"    Types corrigés")

    # ════════════════════════════════════════════════════
    # ÉTAPE 4 : NETTOYAGE
    # ════════════════════════════════════════════════════
    print("\n🧹 Nettoyage des données...")

    nb_avant = len(df)
    df = df.drop_duplicates(subset=['GLOBALEVENTID'])
    # Supprimer les événements en double sur l'identifiant unique
    nb_doublons = nb_avant - len(df)

    nb_avant = len(df)
    df = df.dropna(subset=['SQLDATE'])
    # Supprimer les lignes sans date valide (inutilisables pour l'analyse temporelle)
    nb_dates = nb_avant - len(df)

    print(f"    {nb_doublons:,} doublons supprimés")
    print(f"    {nb_dates:,} lignes sans date supprimées")
    print(f"    {len(df):,} lignes restantes")

    # ════════════════════════════════════════════════════
    # ÉTAPE 5 : ENRICHISSEMENT
    # ════════════════════════════════════════════════════
    print("\n Enrichissement des données...")

    # ── Colonnes temporelles ──────────────────────────
    df['mois'] = df['SQLDATE'].dt.month
    # Extraire le numéro du mois (1 à 12)

    df['trimestre'] = df['SQLDATE'].dt.quarter
    # Extraire le trimestre (1 à 4)

    df['annee'] = df['SQLDATE'].dt.year
    # Extraire l'année

    df['mois_annee'] = df['SQLDATE'].dt.to_period('M').astype(str)
    # Créer une colonne "YYYY-MM" (ex: "2025-03") pour les graphiques temporels

    df['jour_semaine'] = df['SQLDATE'].dt.dayofweek
    # Extraire le jour de la semaine (0=Lundi, 6=Dimanche)

    # ── Ton médiatique ────────────────────────────────
    def categoriser_ton(tone):
        # Catégoriser le ton médiatique en 5 niveaux
        if pd.isna(tone):
            return 'inconnu'
        elif tone > 3:
            return 'tres_positif'   # Couverture très favorable
        elif tone > 1:
            return 'positif'        # Couverture favorable
        elif tone < -3:
            return 'tres_negatif'   # Couverture très défavorable
        elif tone < -1:
            return 'negatif'        # Couverture défavorable
        else:
            return 'neutre'         # Couverture neutre

    df['ton_categorie'] = df['AvgTone'].apply(categoriser_ton)
    # Appliquer la catégorisation du ton à chaque ligne

    # ── Score Goldstein ───────────────────────────────
    def categoriser_goldstein(score):
        # Catégoriser le score de stabilité en 5 niveaux
        if pd.isna(score):
            return 'inconnu'
        elif score >= 5:
            return 'tres_cooperatif'    # Événement très stabilisateur
        elif score > 0:
            return 'cooperatif'         # Événement positif
        elif score == 0:
            return 'neutre'             # Événement neutre
        elif score >= -5:
            return 'conflictuel'        # Événement déstabilisateur
        else:
            return 'tres_conflictuel'   # Événement très déstabilisateur

    df['goldstein_categorie'] = df['GoldsteinScale'].apply(categoriser_goldstein)
    # Appliquer la catégorisation Goldstein à chaque ligne

    # ── QuadClass lisible ─────────────────────────────
    quadclass_labels = {
        1: 'cooperation_verbale',    # Déclarations de soutien, promesses
        2: 'cooperation_materielle', # Aide concrète, accords signés
        3: 'conflit_verbal',         # Accusations, critiques, menaces
        4: 'conflit_materiel'        # Violence, attaques, arrestations
    }
    if 'QuadClass' in df.columns:
        df['quadclass_label'] = df['QuadClass'].map(quadclass_labels)
        # Remplacer les codes 1/2/3/4 par des labels lisibles

    # ── Classification zone géographique ─────────────
    
    departements_nord = [# Alibori
    "Banikoara", "Gogounou", "Kandi", "Karimama", "Malanville", "Segbana", "Alassane", "Gbeke", "Alibori", "Kantoro", "Mehrou", "Toura"

    # Atacora
    "Boukoumbé", "Cobly", "Kerou", "Kouandé", "Matéri", "Natitingou", "Péhunco", "Tanguieta", "Toucountouna", "Akoko", "Kayode", "Atakora", "Porga", "Taiakou", "Tanougou", "Tobre"

    # Donga
    "Bassila", "Copargo", "Djougou", "Ouaké", "Donga"

    # Borgou
    "Bembereke", "Kalale", "Ndali", "Nikki", "Parakou", "Pèrèrè", "Sinendé", "Tchaourou", "Babariba", "Bouca", "Gokana", "Gourou", "Kika" "Borgou", "Sekere"]
    # BN01=Alibori · BN02=Atacora · BN06=Borgou — zone exposée jihadiste

    departements_centre = [
    # Zou
    "Abomey", "Agbangnizoun", "Bohicon", "Cové", "Djidja",
    "Ouinhi", "Kpota", "Zagnanado", "Zogbodomey", "Dosso", "Zou"

    # Collines
    "Bantè", "Dassa-Zoume", "Glazoue", "Ouèssè", "Savalou", "Savè", "Alafia", "Kokou", "Collines", "Ogou", "Okio"
    ]
    # Départements du centre — Zou et Collines

    # Le sud = Atlantique, Littoral (Cotonou), Ouémé, Plateau, Mono, Couffo

    def classifier_zone(nom_lieu):
        # Classifier un lieu béninois en nord, centre ou sud
        if pd.isna(nom_lieu):
            return 'inconnu'
            # Valeur manquante → inconnu

        nom_lieu_str = str(nom_lieu).lower()
        # Convertir en minuscules pour ignorer la casse
        # Ex : "KANDI, BENIN" → "kandi, benin"

        if any(ville.lower() in nom_lieu_str for ville in departements_nord):
            return 'nord'
            # Ex : "Kandi, Alibori, Benin" contient "kandi" → nord

        elif any(ville.lower() in nom_lieu_str for ville in departements_centre):
            return 'centre'
            # Ex : "Bohicon, Zou, Benin" contient "bohicon" → centre

        elif pd.notna(nom_lieu):
            return 'sud'
            # Lieu connu mais pas dans nord ni centre → sud
            # Ex : "Cotonou, Littoral, Benin" → sud

        else:
            return 'inconnu'

    if 'ActionGeo_FullName' in df.columns:
        df['zone_benin'] = df['ActionGeo_FullName'].apply(classifier_zone)
        # Appliquer la classification à chaque ligne de ActionGeo_FullName

    # ── Extraction domaine source ─────────────────────
    def extraire_domaine(url):
        # Extraire le domaine depuis l'URL pour identifier le média et sa langue
        if pd.isna(url):
            return 'inconnu'
        try:
            domaine = str(url).split('/')[2]
            # Prendre la 3ème partie de l'URL (ex: "www.rfi.fr")
            domaine = domaine.replace('www.', '')
            # Supprimer le préfixe "www."
            return domaine
        except:
            return 'inconnu'

    if 'SOURCEURL' in df.columns:
        df['source_domaine'] = df['SOURCEURL'].apply(extraire_domaine)
        # Extraire le domaine de chaque URL pour identifier le média

    print(f"    Colonnes enrichies ajoutées")

    # ════════════════════════════════════════════════════
    # ÉTAPE 6 : ASSERTIONS QUALITÉ
    # ════════════════════════════════════════════════════
    print("\n  Vérification de la qualité...")

    assert len(df) > 100, f" Trop peu d'événements : {len(df)}"
    # Vérifier qu'on a suffisamment de données

    assert df['GLOBALEVENTID'].duplicated().sum() == 0, " Doublons détectés !"
    # Vérifier l'absence totale de doublons

    assert df['SQLDATE'].isna().sum() == 0, " Dates manquantes !"
    # Vérifier que toutes les dates sont valides

    assert df['SQLDATE'].min().year >= 2025, " Données avant 2025 détectées !"
    # Vérifier que les données respectent le filtre temporel

    if 'ActionGeo_Lat' in df.columns:
        lat_valides = df['ActionGeo_Lat'].dropna()
        if len(lat_valides) > 0:
            assert lat_valides.between(-90, 90).all(), " Latitudes hors limites !"
            # Vérifier que les latitudes sont dans l'intervalle valide

    print(f"    Toutes les assertions passées")

    # ════════════════════════════════════════════════════
    # ÉTAPE 7 : SAUVEGARDE
    # ════════════════════════════════════════════════════
    print("\n Sauvegarde des fichiers...")

    os.makedirs(output_dir, exist_ok=True)
    # Créer le dossier de sortie s'il n'existe pas
    # exist_ok=True évite une erreur si le dossier existe déjà

    df.to_csv(f"{output_dir}/benin_clean.csv", index=False)
    # Sauvegarder le fichier CSV propre (index=False = pas d'index pandas)

    df.to_csv(f"{output_dir}/benin_enrichi.csv", index=False)
    # Sauvegarder le fichier CSV enrichi avec toutes les colonnes calculées

    df.to_parquet(f"{output_dir}/benin_enrichi.parquet", index=False)
    # Sauvegarder en Parquet — plus compact et plus rapide que CSV

    taille_csv = os.path.getsize(f"{output_dir}/benin_enrichi.csv") / 1024
    taille_parquet = os.path.getsize(f"{output_dir}/benin_enrichi.parquet") / 1024
    # Calculer la taille des fichiers en kilooctets

    print(f"    benin_clean.csv      ({taille_csv:.0f} KB)")
    print(f"    benin_enrichi.csv    ({taille_csv:.0f} KB)")
    print(f"    benin_enrichi.parquet ({taille_parquet:.0f} KB)")
    print(f"    Dossier : {output_dir}")

    # ════════════════════════════════════════════════════
    # RAPPORT FINAL
    # ════════════════════════════════════════════════════
    print("\n" + "=" * 55)
    print(" RAPPORT QUALITÉ FINAL")
    print("=" * 55)
    print(f"Événements traités     : {len(df):,}")
    print(f"Période couverte       : {df['SQLDATE'].min().date()} → {df['SQLDATE'].max().date()}")
    print(f"Colonnes totales       : {df.shape[1]}")
    print(f"  dont originales      : {len(colonnes_presentes)}")
    print(f"  dont enrichies       : {df.shape[1] - len(colonnes_presentes)}")

    print(f"\n Valeurs manquantes clés :")
    for col in ['GoldsteinScale', 'AvgTone', 'ActionGeo_Lat',
                'Actor1Name', 'ActionGeo_ADM1Code']:
        if col in df.columns:
            n = df[col].isna().sum()
            pct = (n / len(df) * 100).round(1)
            print(f"   {col:<25} : {n:,} ({pct}%)")

    print(f"\n🎭 Ton médiatique :")
    print(df['ton_categorie'].value_counts().to_string())

    print(f"\n⚖️  Goldstein :")
    print(df['goldstein_categorie'].value_counts().to_string())

    if 'zone_benin' in df.columns:
        print(f"\n Zone géographique :")
        print(df['zone_benin'].value_counts().to_string())

    if 'quadclass_label' in df.columns:
        print(f"\n  QuadClass :")
        print(df['quadclass_label'].value_counts().to_string())

    print("=" * 55)
    print(" Pipeline terminé avec succès !")
    print("=" * 55)

    return df
    # Retourner le DataFrame pour pouvoir l'utiliser dans d'autres scripts


if __name__ == "__main__":
    # Ce bloc s'exécute uniquement quand on lance "python pipeline.py"
    # Il ne s'exécute PAS si le fichier est importé depuis un autre script
    run_pipeline()