# pipeline.py
# Usage : python pipeline.py
# Ce script extrait, nettoie et enrichit les données GDELT du Bénin en une seule commande

import pandas as pd          # Manipulation des données
import numpy as np           # Calculs numériques
import os                    # Gestion des fichiers et dossiers
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def run_pipeline(input_path= ROOT_DIR /"data/raw/donnees_benin.csv",
                 output_dir= ROOT_DIR /"data/processed"):
    # Fonction principale qui enchaîne toutes les étapes du pipeline

    print(" Démarrage du pipeline GDELT Bénin...")

    # --- ÉTAPE 1 : Chargement ---
    print("\n Chargement des données brutes...")
    df = pd.read_csv(input_path, low_memory=False)
    # Charger le CSV brut depuis le chemin fourni en paramètre
    print(f"  {len(df):,} lignes chargées")

    # --- ÉTAPE 2 : Sélection des colonnes ---
    print("\n  Sélection des colonnes utiles...")
    colonnes_cles = [
        'GLOBALEVENTID', 'SQLDATE', 'MONTHYEAR', 'YEAR',
        'Actor1CountryCode', 'Actor2CountryCode',
        'EventRootCode', 'EventBaseCode',
        'GoldsteinScale', 'NumMentions', 'NumSources',
        'NumArticles', 'AvgTone',
        'ActionGeo_CountryCode', 'ActionGeo_Lat', 'ActionGeo_Long',
        'SOURCEURL'
    ]
    colonnes_presentes = [c for c in colonnes_cles if c in df.columns]
    # Garder seulement les colonnes qui existent dans le fichier
    df = df[colonnes_presentes]
    print(f"   {len(colonnes_presentes)} colonnes conservées")

    # --- ÉTAPE 3 : Correction des types ---
    print("\n Correction des types de données...")
    df['SQLDATE'] = pd.to_datetime(df['SQLDATE'], format='%Y%m%d', errors='coerce')
    # Convertir la date en format datetime
    df['GoldsteinScale'] = pd.to_numeric(df['GoldsteinScale'], errors='coerce')
    # Convertir le score Goldstein en nombre
    df['AvgTone'] = pd.to_numeric(df['AvgTone'], errors='coerce')
    # Convertir le ton moyen en nombre
    df['ActionGeo_Lat'] = pd.to_numeric(df['ActionGeo_Lat'], errors='coerce')
    # Convertir la latitude en nombre
    df['ActionGeo_Long'] = pd.to_numeric(df['ActionGeo_Long'], errors='coerce')
    # Convertir la longitude en nombre
    print(f"    Types corrigés")

    # --- ÉTAPE 4 : Nettoyage ---
    print("\n Nettoyage des données...")
    nb_avant = len(df)
    df = df.drop_duplicates(subset=['GLOBALEVENTID'])
    # Supprimer les événements en double
    df = df.dropna(subset=['SQLDATE'])
    # Supprimer les lignes sans date valide
    print(f"   {nb_avant - len(df)} lignes supprimées (doublons + dates invalides)")

    # --- ÉTAPE 5 : Enrichissement ---
    print("\n Enrichissement des données...")
    df['mois'] = df['SQLDATE'].dt.month
    # Extraire le numéro du mois
    df['trimestre'] = df['SQLDATE'].dt.quarter
    # Extraire le trimestre
    df['annee'] = df['SQLDATE'].dt.year
    # Extraire l'année
    df['mois_annee'] = df['SQLDATE'].dt.to_period('M').astype(str)
    # Créer une colonne "YYYY-MM" pour les graphiques temporels

    df['ton_categorie'] = df['AvgTone'].apply(
        lambda x: 'inconnu' if pd.isna(x) else ('positif' if x > 1 else ('negatif' if x < -1 else 'neutre'))
    )
    # Catégoriser le ton médiatique

    df['type_event'] = df['GoldsteinScale'].apply(
        lambda x: 'inconnu' if pd.isna(x) else ('cooperatif' if x > 3 else ('conflictuel' if x < -3 else 'neutre'))
    )
    # Catégoriser le type d'événement
    print(f"   Colonnes enrichies ajoutées")

    # --- ÉTAPE 6 : Assertions qualité ---
    print("\n  Vérification de la qualité...")
    assert len(df) > 100, f" Trop peu d'événements : {len(df)}"
    # Vérifier qu'on a suffisamment de données
    assert df['GLOBALEVENTID'].duplicated().sum() == 0, " Doublons détectés !"
    # Vérifier l'absence de doublons
    assert df['SQLDATE'].isna().sum() == 0, " Dates manquantes !"
    # Vérifier que toutes les dates sont valides
    print(f"    Toutes les assertions passées")

    # --- ÉTAPE 7 : Sauvegarde ---
    print("\n Sauvegarde des fichiers...")
    os.makedirs(output_dir, exist_ok=True)
    # Créer le dossier de sortie s'il n'existe pas
    df.to_csv(f"{output_dir}/benin_clean.csv", index=False)
    # Sauvegarder le fichier CSV propre
    df.to_csv(f"{output_dir}/benin_enrichi.csv", index=False)
    # Sauvegarder le fichier CSV enrichi
    df.to_parquet(f"{output_dir}/benin_enrichi.parquet", index=False)
    # Sauvegarder en Parquet pour un accès plus rapide
    print(f"    Fichiers sauvegardés dans {output_dir}/")

    # --- RAPPORT FINAL ---
    print("\n" + "=" * 50)
    print(" RAPPORT QUALITÉ FINAL")
    print("=" * 50)
    print(f"Événements traités  : {len(df):,}")
    print(f"Période couverte    : {df['SQLDATE'].min().date()} → {df['SQLDATE'].max().date()}")
    print(f"Colonnes            : {df.shape[1]}")
    print(f"Nulls GoldsteinScale: {df['GoldsteinScale'].isna().sum()}")
    print(f"Nulls AvgTone       : {df['AvgTone'].isna().sum()}")
    print(f"\nTon médiatique :")
    print(df['ton_categorie'].value_counts().to_string())
    print(f"\nType d'événement :")
    print(df['type_event'].value_counts().to_string())
    print("=" * 50)
    print(" Pipeline terminé avec succès !")

    return df
    # Retourner le DataFrame pour pouvoir l'utiliser dans d'autres scripts


if __name__ == "__main__":
    # Ce bloc s'exécute uniquement quand on fait "python pipeline.py"
    # Il ne s'exécute PAS si le fichier est importé depuis un autre script
    run_pipeline()