# Hackathon\_Isheero\_Team04

Bénin Insights Challenge — iSHEERO x DataCamp 2026



\## Mission

Analyser la couverture médiatique du Bénin (janv 2025 - dec 2025) via la base GDELT pour produire des insights actionnables.



\## Équipe

\--------------------------------------

| Rôle           | Membre            |

|----------------|-------------------|

| Data Engineer  | YAOITCHA Rosine   |

| Data Analyst   | GBAGUIDI Adewale  |

| ML Engineer    | HOUNDOFI Jacques  |

| Data Scientist | AGBOTON Carine    |

|\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_|\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_|



\## Stack technique

\*Python

\*BigQuery

\*Pandas

\*Streamlit

\*Scikit-learn



\## Lancer le projet

pip install -r requirements.txt

python pipeline.py



\### Fichiers générés

| Fichier                                | Description                  |

|----------------------------------------|------------------------------|

| `data/processed/benin\_clean.csv`       | Données nettoyées            |

| `data/processed/benin\_enrichi.csv`     | Données + colonnes calculées |

| `data/processed/benin\_enrichi.parquet` | Format compressé rapide      |



\### Qualité des données

\- Période couverte : 2025-01-01 → 2025-12-31

\- Colonnes critiques vérifiées par assertions automatiques

\- Doublons supprimés, types corrigés, dates validées



\## Source des données

GDELT Project — gdeltproject.org

Filtre : ActionGeo\_CountryCode = 'BC', YEAR >= 2025

