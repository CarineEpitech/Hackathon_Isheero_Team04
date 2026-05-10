# Bénin Insights Challenge

Analyse exploratoire de la couverture médiatique internationale du Bénin en 2025, à partir de la base GDELT. Ce projet mesure comment les médias mondiaux parlent du Bénin — pas ce qui se passe sur le terrain.

**Hackathon iSHEERO × DataCamp 2026 · Équipe 04**

---

## Données

Source : [GDELT Project](https://www.gdeltproject.org) — table `gdelt-bq.gdeltv2.events` 
Filtre : `ActionGeo_CountryCode = 'BN'`, période 2025-01-01 → 2025-12-31 
Volume final : **23 859 événements** sur 351 jours

---

## Structure du projet

```
benin_insights_challenge/
├── Pipeline.py # Script de traitement des données (extraction → enrichissement)
├── requirements.txt
│
├── data/
│ ├── raw/benin_raw.csv # Export brut BigQuery
│ └── processed/
│ ├── benin_clean.csv # Données nettoyées (doublons supprimés, types corrigés)
│ └── benin_enrichi.parquet # Données enrichies (zones, ton catégorisé, domaine source…)
│
├── notebooks/
│ ├── 01_pipeline_gdelt.ipynb # Pipeline officiel — extraction → nettoyage → enrichissement
│ ├── 02_eda_exploration.ipynb # Analyse exploratoire
│ ├── 03_feature_engineering_v0.ipynb # Préparation des features ML
│ ├── 03_ml_models.ipynb # Entraînement Random Forest
│ ├── 04_analyse_complete.ipynb # Analyse complète + conclusions
│ └── archive/ # Brouillons historiques (ne pas exécuter)
│
├── models/
│ ├── random_forest_ton.pkl # Modèle entraîné sur 23 859 events
│ └── metrics_rf.json # Métriques de performance
│
├── dashboard/
│ ├── app.py # Application Streamlit
│ └── README_dashboard.md # Documentation du dashboard
│
└── docs/
    ├── resume_une_page.md # Résumé et 5 insights principaux
    ├── insights.md # Hypothèses et résultats
    ├── questions_jury.md # Questions probables du jury + réponses
    └── benin_insights_questions_analytiques.md # Document de planning Phase 1
```

---

## Lancer le pipeline

```bash
# Depuis benin_insights_challenge/
python Pipeline.py
```

Produit `data/processed/benin_enrichi.parquet` à partir de `data/raw/benin_raw.csv`.

---

## Lancer le dashboard

**Version déployée :** [https://benin-insights-2025-team04.streamlit.app/](https://benin-insights-2025-team04.streamlit.app/)

```bash
streamlit run dashboard/app.py
```

Ouvre l'application sur `http://localhost:8501`. Le dashboard charge automatiquement `benin_enrichi.parquet`.

---

## Résultats principaux

- Le ton médiatique est négatif sur les 12 mois de 2025 (moyenne annuelle : −1,49)
- Les événements localisés au nord affichent un ton significativement plus négatif (−4,10 vs −1,41 au sud, Mann-Whitney p < 0,001)
- Le Nigeria est l'acteur le plus présent (2 198 événements, 6,6× la France)
- 22 % des articles proviennent de sources nigérianes ; 0,6 % de sources béninoises
- Trois périodes ont structuré la couverture : 10 janvier, 17 avril, 7-12 décembre
- Random Forest : 70 % d'accuracy vs 62,7 % pour un classificateur de référence (+7 pp)

Pour le détail : voir `docs/resume_une_page.md`.

---

## Limites

91 % des événements ont une géolocalisation générique (centroïde pays GDELT, sans ville précise). Les analyses géographiques fines portent sur les 8,8 % d'événements précisément localisés. Les résultats décrivent la couverture médiatique internationale, pas les événements sur le terrain.

---

*Hackathon iSHEERO × DataCamp 2026 · Équipe 04*
