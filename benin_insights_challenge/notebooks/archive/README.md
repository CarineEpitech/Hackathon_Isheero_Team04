# notebooks/archive — Brouillons historiques

Ce dossier contient des notebooks conservés pour l'historique du projet, mais qui **ne font pas partie du pipeline officiel**.

---

## Contenu

### `00_schema_exploration_draft.ipynb`

Notebook d'exploration du schéma GDELT — Jour 1 du hackathon.

- Développé sur Google Colab (chemins `/content/` non reproductibles en local)
- Chargé sur un export BigQuery à ~13 137 événements (ancien dataset)
- Seuils de sentiment différents de l'implémentation finale (±2 au lieu de ±1/±3)
- Codes départementaux `BC` non conformes aux codes GDELT réels (`BN`)
- Rôle : compréhension initiale du schéma et planification des features ML
- **Ne pas exécuter** pour reproduire le projet

### `01_pipeline_nettoyage_draft.ipynb`

Version antérieure et incomplète du pipeline de données.

- Développé en parallèle par un autre membre de l'équipe (export BigQuery à 17 colonnes)
- Produit les mêmes fichiers de sortie que `01_pipeline_gdelt.ipynb` (`benin_enrichi.parquet`) mais avec seulement 23 colonnes au lieu de 41
- Catégorisation du ton à 3 niveaux (au lieu de 5) — incompatible avec le dashboard
- Bug dans la classification géographique : correspondance exacte sur `ActionGeo_FullName` → 100 % des événements classés en zone "sud"
- Manque : `quadclass_label`, `source_domaine`, `ActionGeo_FullName`, `ActionGeo_ADM1Code`, `QuadClass`
- **Ne pas exécuter** : écraserait `benin_enrichi.parquet` avec une version dégradée

---

## Pipeline officiel

Pour reproduire le projet, utiliser dans l'ordre :

| Étape | Fichier | Description |
|-------|---------|-------------|
| Pipeline données | `../01_pipeline_gdelt.ipynb` ou `../../Pipeline.py` | Extraction → nettoyage → enrichissement (41 colonnes) |
| Analyse exploratoire | `../02_eda_exploration.ipynb` | EDA complète, détection d'anomalies |
| Feature engineering | `../03_feature_engineering_v0.ipynb` | Préparation des features ML |
| Modèle ML | `../03_ml_models.ipynb` | Random Forest, évaluation, métriques |
| Synthèse | `../04_analyse_complete.ipynb` | Analyse complète et conclusions |

---

*Bénin Insights Challenge — iSHEERO × DataCamp Hackathon 2026 · Équipe 04*
