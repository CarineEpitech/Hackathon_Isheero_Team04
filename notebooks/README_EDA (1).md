# README — Notebook EDA Bénin Insights Challenge

## `notebooks/02_eda_benin.ipynb`

**Hackathon iSHEERO × DataCamp 2026**  
**Rôle :** Data Analyst  
**Auteur :** Équipe Bénin Insights  
**Date :** Mai 2026

---

## Objectif

Ce notebook réalise l'**analyse exploratoire des données (EDA)** sur le dataset GDELT filtré
pour le Bénin (2025). Il produit les **5 visualisations obligatoires** du cahier des charges
et prépare les observations analytiques transmises au Data Scientist pour la rédaction des insights finaux.

---

## Données source

| Paramètre | Valeur |
|---|---|
| **Fichier** | `data/processed/benin_clean.csv` |
| **Lignes** | 10 722 événements |
| **Colonnes** | 41 variables |
| **Périmètre** | Bénin (`ActionGeo_CountryCode = 'BN'`) |
| **Période** | 1er janvier 2025 → 31 décembre 2025 |
| **Source originale** | GDELT Project — BigQuery `gdelt-bq.gdeltv2.events` |

---

## Prérequis

### Environnement Python

```
python >= 3.9
```

### Installation des dépendances

```bash
pip install -r requirements.txt
```

Contenu minimal de `requirements.txt` :

```
pandas>=1.5
numpy>=1.23
matplotlib>=3.6
seaborn>=0.12
scipy>=1.9
jupyter>=1.0
nbformat>=5.7
```

### Structure du répertoire attendue

```
benin-insights-challenge/
├── data/
│   └── processed/
│       └── benin_clean.csv         ← fichier requis
├── notebooks/
│   └── 02_eda_benin.ipynb          ← ce notebook
├── outputs/                         ← créé automatiquement
│   ├── viz1_evolution_temporelle.png
│   ├── viz2_tone_par_type.png
│   ├── viz3_top_pays_source.png
│   ├── viz4_carte_benin.png
│   ├── viz5_goldstein.png
│   ├── viz6_quadclass.png
│   ├── viz7_nord_sud.png
│   └── viz8_anomalies.png
└── requirements.txt
```

---

## Exécution

### Depuis le terminal

```bash
# Se placer à la racine du projet
cd benin-insights-challenge

# Lancer Jupyter
jupyter notebook notebooks/02_eda_benin.ipynb

# OU exécuter sans interface (reproductibilité)
jupyter nbconvert --to notebook --execute notebooks/02_eda_benin.ipynb \
    --output notebooks/02_eda_benin_executed.ipynb
```

### Depuis Google Colab

```python
# Uploader benin_clean.csv dans /content/data/processed/
# Exécuter toutes les cellules (Runtime > Run all)
```

---

## Structure du notebook

Le notebook est découpé en **9 sections** :

| Section | Contenu | Colonnes mobilisées |
|---|---|---|
| **0 — Dictionnaire** | Description détaillée des 41 colonnes | — |
| **1 — Chargement** | Import, aperçu, statistiques descriptives | Toutes |
| **2 — Qualité** | Valeurs manquantes, doublons, complétude temporelle | Toutes |
| **3 — Viz 1** | Évolution mensuelle du nombre d'événements | `mois`, `GLOBALEVENTID` |
| **4 — Viz 2** | Distribution AvgTone par type d'événement | `EventRootCode`, `AvgTone` |
| **5 — Viz 3** | Top 15 pays sources | `Actor1CountryCode`, `AvgTone` |
| **6 — Viz 4** | Carte géographique des événements | `ActionGeo_Lat/Long`, `zone_benin` |
| **7 — Viz 5** | Score de Goldstein dans le temps | `mois`, `GoldsteinScale` |
| **8 — Analyses complémentaires** | QuadClass, comparaison nord/sud, signaux Z-score | `quadclass_label`, `zone_benin`, `NumMentions` |
| **9 — Synthèse** | Tableau récapitulatif des observations par question analytique | — |

---

## Les 5 visualisations obligatoires

| # | Visualisation | Type | Fichier de sortie |
|---|---|---|---|
| Viz 1 | Évolution mensuelle des événements | Lineplot avec zone ombrée | `viz1_evolution_temporelle.png` |
| Viz 2 | Distribution AvgTone par type CAMEO | Boxplot | `viz2_tone_par_type.png` |
| Viz 3 | Top 15 pays source | Barplot horizontal | `viz3_top_pays_source.png` |
| Viz 4 | Carte des événements geolocalisés | Scatter + barplot zone | `viz4_carte_benin.png` |
| Viz 5 | Score de Goldstein dans le temps | Lineplot lissé | `viz5_goldstein.png` |

---

## Correspondance Questions analytiques ↔ Visualisations

| Question | Visualisations directes | Analyses complémentaires |
|---|---|---|
| Q1 — Image médiatique | Viz 1, Viz 2, Viz 3 | — |
| Q2 — Narratifs dominants | Viz 2 | QuadClass (Section 8.1) |
| Q3 — Impact sécuritaire nord | Viz 4 | Nord/Sud (Section 8.2) |
| Q4 — Signaux faibles | Viz 5 | Z-score hebdo (Section 8.3) |
| Q5 — Périodes marquantes | Viz 1, Viz 5 | — |

---

## Variables clés — Rappel rapide

| Variable | Plage de valeurs | Interprétation |
|---|---|---|
| `AvgTone` | Négatif à positif (centré ~0) | Très négatif = médias hostiles, très positif = médias favorables |
| `GoldsteinScale` | -10 à +10 | Négatif = événement déstabilisant, positif = stabilisant |
| `NumMentions` | 1 à plusieurs centaines | Plus une valeur est haute, plus l'événement est médiatiquement amplifié |
| `EventRootCode` | 1 à 19 | Code CAMEO : 1-8 = coopération, 9-19 = conflit/confrontation |
| `QuadClass` | 1 à 4 | 1=Coop.Verbale, 2=Coop.Matérielle, 3=Conflit Verbal, 4=Conflit Matériel |
| `zone_benin` | nord / centre / sud | Variable enrichie par le Data Engineer à partir des codes ADM1 |

---

## Conventions de style du notebook

- **Pas d'emojis** dans les cellules de code ou les titres
- **Titres en gras** via `##` et `###` Markdown
- **Espaces** entre chaque section pour la lisibilité
- **Blocs `>`** (blockquotes Markdown) utilisés pour les encadrés analytiques :
  - Choix de méthode avec 2e et 3e alternatives expliquées
  - Observations post-graphique
- **Langue** : français, vocabulaire accessible, sans jargon technique superflu
- **Couleurs** définies en constantes en tête de notebook (modifiables en un point unique)

---

## Choix techniques documentés

Chaque cellule de visualisation est suivie d'un encadré qui documente :

1. **Choix retenu** avec justification
2. **Alternative 2** : quel autre type de graphique aurait pu convenir, et pourquoi il a été écarté
3. **Alternative 3** : idem pour un troisième candidat

Cette documentation facilite :
- La compréhension par un jury non-technique
- La reprise du notebook par un autre membre de l'équipe
- L'adaptation rapide si le cahier des charges évolue en Phase 2

---

## Outputs produits

Tous les graphiques sont sauvegardés en **PNG (150 dpi)** dans le dossier `outputs/`.  
Ces fichiers sont utilisables directement pour :
- Le dashboard Streamlit (`st.image()` si Plotly n'est pas disponible)
- Le résumé d'une page (copier-coller dans Word ou Google Docs)
- Le README GitHub (captures d'écran de présentation)

---

## Limitations connues

| Limitation | Impact | Contournement |
|---|---|---|
| Pas de fond de carte pour Viz 4 | Carte moins lisible sans frontières tracées | Recommander Plotly Mapbox pour le dashboard |
| Biais géographique du dataset | 93% des événements localisés dans le sud | Interpréter les chiffres nord avec précaution (volume faible) |
| Biais linguistique (médias nigérians) | Sur-représentation de la couverture anglophone | Mentionner explicitement dans les insights finaux |
| Valeurs manquantes sur les acteurs | ~26% de `Actor1CountryCode` vides | Analyses sur les acteurs doublées sur `source_domaine` |

---

## Auteurs et usage de l'IA

> Ce notebook a été développé dans le cadre du hackathon iSHEERO × DataCamp 2026.  
> L'usage d'outils d'intelligence artificielle a été mobilisé pour accélérer la rédaction  
> des commentaires analytiques et des structures de code. Tous les résultats et interprétations  
> ont été vérifiés par l'équipe.  
> Conformément aux règles du hackathon, cet usage est mentionné explicitement ici.

---

*Dernière mise à jour : Mai 2026*
