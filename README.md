## Version corrigée et complète

# Bénin Insights Challenge
### Hackathon iSHEERO × DataCamp 2026

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![BigQuery](https://img.shields.io/badge/Google-BigQuery-orange)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)
![Status](https://img.shields.io/badge/Status-En%20cours-yellow)
![IA](https://img.shields.io/badge/IA-Claude%20Anthropic-purple)

> **Mission** : Transformer les données mondiales GDELT en connaissance locale
> sur le Bénin — pour un journaliste, un chercheur, un décideur public.

---

## Équipe — Team 04

| Rôle              | Membre           | Responsabilité                                  |
|-------------------|------------------|-------------------------------------------------|
| Data Engineer     | YAOITCHA Rosine  | Pipeline GDELT · nettoyage · infrastructure     |
| Data Analyst      | GBAGUIDI Adewale | Visualisations · dashboard · executive summary  |
| ML Engineer       | HOUNDOFI Jacques | Classification · sentiment · clustering         |
| Data Scientist    | AGBOTON Carine   | Questions analytiques · insights · pitch        |

---

##  Lancer le projet en 3 commandes

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Générer les données nettoyées
python pipeline.py

# 3. Lancer le dashboard
streamlit run app/streamlit_app.py
```

>  Testé sur Python 3.10+ · Windows · Linux · Mac

---

##  Structure du projet

```
benin-insights-challenge/
├── README.md
├── requirements.txt
├── pipeline.py                        ← script principal du pipeline
├── .gitignore
├── data/
│   ├── raw/                       
│   └── processed/
│       ├── benin_clean.csv
│       ├── benin_enrichi.csv
│       └── benin_enrichi.parquet
├── notebooks/
│   ├── 01_pipeline_nettoyage.ipynb
│   ├── 02_eda_exploration.ipynb
│   ├── 03_feature_engineering.ipynb
│   └── 04_modele_ml_final.ipynb
├── app/
│   └── streamlit_app.py
├── models/
└── docs/
```

---

##  Dashboard interactif

 **[URL Streamlit Cloud — à compléter après déploiement]**

---

##  Source des données

| Paramètre               | Valeur                                                        |
|-------------------------|---------------------------------------------------------------|
| **Source**              | [GDELT Project](https://gdeltproject.org) via Google BigQuery |
| **Table**               | `gdelt-bq.gdeltv2.events`                                     |
| **Filtre géographique** | `ActionGeo_CountryCode = 'BN'`                                |
| **Filtre acteurs**      | `Actor1CountryCode = 'BEN'` OR `Actor2CountryCode = 'BEN'`    |
| **Période**             | 1er Janvier 2025 → 31 Decembre 2025                           |
| **Volume**              | ~10 722 événements · 31 colonnes                              |


Pour régénérer depuis zéro :
```bash
python pipeline.py
```

---

##  Reproduire le pipeline complet

```bash
# Étape 1 — Cloner le projet

# Étape 2 — Installer les dépendances
pip install -r requirements.txt

# Étape 3 — Lancer le pipeline
python pipeline.py
# → Génère benin_clean.csv · benin_enrichi.csv · benin_enrichi.parquet

# Étape 4 — Exécuter les notebooks dans l'ordre
# notebooks/01_pipeline_nettoyage.ipynb
# notebooks/02_eda_exploration.ipynb
# notebooks/03_feature_engineering.ipynb
# notebooks/04_modele_ml_final.ipynb

# Étape 5 — Lancer le dashboard
streamlit run app/streamlit_app.py
```

---
 
##  Stack technique

| Catégorie             | Outils                             |
|-----------------------|------------------------------------|
| **Extraction**        | Google BigQuery                    |
| **Manipulation**      | Python · Pandas · Polars · PyArrow |
| **Visualisation**     | Plotly · Seaborn · Folium          |
| **Machine Learning**  | Scikit-learn                       |
| **NLP / Sentiment**   | TextBlob · HuggingFace             |
| **Dashboard**         | Streamlit                          |
| **Versioning**        | GitHub                             |
| **Stockage données**  | Google Drive                       |

---

##  Qualité des données

- Période couverte : 0125 → 202--30
- 31 colonnes critiques extraites et documentées
- Assertions automatiques à chaque exécution du pipeline
- Doublons supprimés sur `GLOBALEVENTID`
- Types corrigés (datetime · float · int)
- Dates invalides supprimées
- Classification géographique : nord / centre / sud Bénin

---

## 🤖 Usage de l'IA

Conformément aux règles du hackathon iSHEERO 2026 :
- **Claude (Anthropic)** — génération et debug du pipeline · structuration du code
- **GitHub Copilot** — autocomplétion lors du développement

Tout le code a été relu, compris et validé par l'équipe.

---

## 📬 Contact & Support

- 📧 formations@isheero.com
- 🌐 [isheero.com](https://isheero.com)

---

*Bénin Insights Challenge · iSHEERO × DataCamp Donates · 2026*
```

---

Deux choses à compléter avant de pusher :

1. **L'URL du dashboard** Streamlit Cloud une fois déployé par le DA
2. **Le lien Google Drive** des données brutes

Le reste est prêt à pusher. 💪