# Bénin Insights Challenge

**Hackathon iSHEERO × DataCamp 2026**

Analyse de la couverture médiatique internationale du Bénin en 2025 à partir des données GDELT.

---

## Contexte

Le Bénin fait face à une couverture médiatique internationale contrastée : des événements positifs (culture, diplomatie, développement) coexistent avec une attention croissante portée aux tensions sécuritaires dans le nord du pays.

Ce projet analyse 10 722 événements médiatiques recensés par GDELT sur l'ensemble de l'année 2025, afin de répondre à cinq questions analytiques sur l'image du Bénin dans la presse mondiale.

---

## Question principale

> Comment les médias internationaux ont-ils couvert le Bénin en 2025, et quels moments ou dynamiques ont le plus influencé cette image ?

---

## Données utilisées

| Source | Description |
|--------|-------------|
| **GDELT Project** | Base de données mondiale des événements médiatiques |
| **Filtre appliqué** | `ActionGeo_CountryCode = 'BN'`, année 2025 |
| **Volume** | 10 722 événements · 349 jours sur 365 couverts |
| **Période** | 1er janvier 2025 → 31 décembre 2025 |
| **Accès** | BigQuery — table `gdelt-bq.gdeltv2.events` |

---

## Structure du dépôt

```
Hackathon_Isheero_Team04/
├── Pipeline.py                        # Pipeline d'extraction et nettoyage GDELT
├── requirements.txt                   # Dépendances Python
│
├── data/
│   ├── raw/
│   │   ├── benin_raw.csv              # Données brutes extraites de BigQuery (non committé)
│   │   └── query_bigquery.sql         # Requête SQL pour régénérer benin_raw.csv
│   └── processed/
│       ├── benin_clean.csv            # Données nettoyées (avant colonnes calculées)
│       ├── benin_enrichi.csv          # Données enrichies (colonnes calculées ajoutées)
│       └── benin_enrichi.parquet      # Format compressé (chargement rapide)
│
├── notebooks/
│   ├── 00_schema_exploration_v0.ipynb # Exploration initiale du schéma GDELT
│   ├── 01_pipeline_gdelt.ipynb        # Pipeline BigQuery → CSV
│   ├── 01_pipeline_nettoyage.ipynb    # Nettoyage et enrichissement
│   ├── 02_eda_exploration.ipynb       # EDA principale — 8 sections analytiques
│   ├── 03_feature_engineering_v0.ipynb# Feature engineering pour ML
│   ├── 03_ml_models.ipynb             # Modèles ML
│   └── 04_analyse_complete.ipynb      # Notebook final : pipeline + EDA + ML
│
├── dashboard/
│   ├── app.py                         # Application Streamlit
│   └── README_dashboard.md            # Documentation du dashboard
│
├── docs/
│   ├── resume_une_page.md             # Résumé exécutif (1 page, résultats réels)
│   ├── insights.md                    # Hypothèses et statuts après EDA
│   └── benin_insights_questions_analytiques.md  # Questions analytiques détaillées
│
└── models/
    └── random_forest_ton.pkl          # Random Forest — prédiction du ton médiatique
```

---

## Installation

```bash
# Cloner le dépôt
git clone <url-du-repo>
cd benin_insights_challenge

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / Mac

# Installer les dépendances
pip install -r requirements.txt
```

---

## Reproduire les données

**Étape 1 — Extraire les données brutes depuis BigQuery**

La requête d'extraction est dans `data/raw/query_bigquery.sql`.
Exécuter cette requête dans la console BigQuery (projet `gdelt-bq`) et exporter le résultat en CSV sous `data/raw/benin_raw.csv`.

**Étape 2 — Lancer le pipeline de nettoyage et d'enrichissement**

```bash
python Pipeline.py
```

Fichiers produits dans `data/processed/` :
- `benin_clean.csv` — données nettoyées, sans colonnes calculées
- `benin_enrichi.csv` — données nettoyées + colonnes calculées (ton, zone, quadclass...)
- `benin_enrichi.parquet` — même contenu que enrichi, format compressé

---

## Lancer le notebook EDA

```bash
jupyter notebook notebooks/02_eda_exploration.ipynb
```

Le notebook est auto-suffisant si `data/processed/benin_enrichi.csv` existe.

---

## Lancer le dashboard

```bash
streamlit run dashboard/app.py
```

Voir `dashboard/README_dashboard.md` pour le détail des filtres et visualisations.

---

## Résultats principaux

Issus du notebook `02_eda_exploration.ipynb`, section 8.

| Question | Résultat |
|----------|----------|
| **Ton médiatique** | Négatif sur 11 des 12 mois (moyenne : −1,22). Score Goldstein médiane positive (+1,9) — les deux mesures sont indépendantes : Goldstein reflète la nature des événements, AvgTone reflète le registre linguistique des articles. |
| **Narratifs dominants** | 65 % de coopération verbale (diplomatie, consultations). 25,5 % de conflits (verbal + matériel). |
| **Géographie interne** | Le nord représente 3,8 % des événements mais affiche un ton près de 4× plus négatif que le sud (−4,36 vs −1,13). Test Mann-Whitney : p < 0,001, r = 0,42. Causalité avec l'image nationale non établie. |
| **Pics médiatiques** | 8 dates anormales détectées (Z-score, MAD, fenêtre glissante). Décembre 2025 : séquence de 6 jours consécutifs, +131 % au-dessus de la médiane mensuelle. |
| **Moments marquants** | Décembre 2025 domine l'année (1 954 événements sur 10 722). Deux autres pics isolés : 10 janvier et 17 avril 2025. |

---

## Statut des hypothèses

| Hypothèse | Statut |
|-----------|--------|
| H1 — Ton médiatique négatif sur 2025 | ⚠️ Partiellement confirmée — ton négatif sur 11/12 mois confirmé. La dégradation "depuis mi-2025" n'est pas testable avec les données d'une seule année. |
| H2 — Sujets dominants : sécurité, coopération, culture | ⚠️ Partiellement confirmée |
| H3 — Impact des attaques au nord sur l'image globale | ⚠️ Asymétrie confirmée — causalité non établie |
| H4 — Signaux précurseurs avant crises | ⏳ Non testée — détection de pics uniquement |
| H5 — Moments marquants identifiables | ⚠️ Partiellement confirmée |

---

## Limites

- La segmentation géographique nord/centre/sud repose sur une correspondance textuelle entre `ActionGeo_FullName` et des listes de communes. Les événements non reconnus sont classés en « sud » par défaut.
- L'analyse du biais francophone/anglophone (H1 sous-volet) n'a pas été réalisée dans l'EDA.
- Les pics détectés correspondent aux anomalies au moment où elles surviennent. La détection de signaux *précurseurs* n'a pas été implémentée.
- Les événements réels associés aux pics (10 jan, 17 avr, 7–12 déc) n'ont pas été identifiés formellement depuis les données.
- La détection de signaux *précurseurs* (avant les crises) n'a pas été implémentée.

---

## Équipe

| Rôle | Membre |
|------|--------|
| Data Engineer | YAOITCHA Rosine |
| Data Analyst | GBAGUIDI Adewale |
| ML Engineer | HOUNDOFI Jacques |
| Data Scientist | AGBOTON Carine |

---

## Stack technique

Python · Pandas · Plotly · Streamlit · Scikit-learn · BigQuery · GDELT

---

*Hackathon iSHEERO × DataCamp 2026 — Bénin Insights Challenge*
