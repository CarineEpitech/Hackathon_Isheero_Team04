# Dashboard — Bénin Insights 2025

Application Streamlit de visualisation de la couverture médiatique internationale du Bénin.

---

## Objectif

Permettre d'explorer les données GDELT 2025 filtrées sur le Bénin à travers cinq sections analytiques correspondant aux questions du projet :

- évolution du ton médiatique dans le temps
- stabilité géopolitique (score Goldstein)
- moments marquants et dates anormales
- comparaison géographique nord / centre / sud
- répartition des types d'événements et des acteurs

---

## Données nécessaires

Le dashboard charge automatiquement les données depuis `data/processed/`.

| Fichier | Format | Priorité |
|---------|--------|----------|
| `data/processed/benin_enrichi.parquet` | Parquet | Chargé en premier (plus rapide) |
| `data/processed/benin_enrichi.csv` | CSV | Fallback si le Parquet est absent |

Ces fichiers sont produits par `Pipeline.py`. Si aucun des deux n'existe, un message d'erreur s'affiche au lancement.

### Colonnes requises

| Colonne | Type | Usage |
|---------|------|-------|
| `SQLDATE` | date | Axe temporel |
| `AvgTone` | float | Ton médiatique |
| `GoldsteinScale` | float | Stabilité géopolitique |
| `NumMentions` | int | Volume de mentions |
| `GLOBALEVENTID` | int | Comptage d'événements |
| `trimestre` | int | Filtre trimestre (1–4) |
| `mois_annee` | str | Agrégation mensuelle (ex : "2025-01") |
| `ton_categorie` | str | Filtre ton (negatif, neutre, positif…) |
| `quadclass_label` | str | Type d'événement (cooperation_verbale…) |
| `zone_benin` | str | Zone géographique (nord, centre, sud) |
| `Actor1CountryCode` | str | Code ISO3 du pays de l'acteur |
| `ActionGeo_Lat` | float | Latitude GPS (carte) |
| `ActionGeo_Long` | float | Longitude GPS (carte) |
| `ActionGeo_ADM1Code` | str | Code département GDELT — filtre centroïde générique ("BN") |
| `ActionGeo_FullName` | str | Nom complet du lieu (tooltip carte) |
| `source_domaine` | str | Domaine source extrait de SOURCEURL (section sources médias) |

---

## Lancement en local

```bash
# Depuis la racine du projet benin_insights_challenge/
streamlit run dashboard/app.py
```

Le dashboard s'ouvre dans le navigateur à l'adresse `http://localhost:8501`.

---

## Filtres disponibles

**Filtres temporels** (bandeau horizontal, en-tête de page) :

| Filtre | Type | Valeurs |
|--------|------|---------|
| **Mois** | Radio | Toute l'année, Jan, Fév, …, Déc |
| **Plage de dates** | Date range | Disponible si "Toute l'année" est sélectionné |

**Filtres thématiques** (barre latérale gauche) :

| Filtre | Colonne | Valeurs |
|--------|---------|---------|
| **Ton médiatique** | `ton_categorie` | Très négatif, Négatif, Neutre, Positif, Très positif |
| **Type d'événement** | `quadclass_label` | Coopération (verbale), Coopération (matérielle), Conflit (verbal), Conflit (matériel) |

Les filtres s'appliquent à toutes les visualisations sauf la table des moments marquants, qui est calculée sur le dataset complet (résultats fixes du notebook).

---

## Visualisations présentes

| Section | Visualisation | Question analytique |
|---------|---------------|---------------------|
| Vue d'ensemble | 4 métriques : nb événements, ton moyen, Goldstein moyen, jours couverts | Chiffres-clés |
| Évolution temporelle | Courbe AvgTone mensuel + ligne à 0 | Q1 — Évolution de l'image |
| Évolution temporelle | Courbe Goldstein mensuel + ligne à 0 | Q1 — Stabilité géopolitique |
| Moments marquants | Table des 8 dates anormales (événements, mentions, ton, Goldstein) | Q4 — Détection de pics |
| Moments marquants | Courbe volume quotidien avec marqueurs sur dates anormales | Q5 — Périodes marquantes |
| Carte | Scatter map événements précisément localisés (hors centroïde générique) | Q3 — Localisation |
| Géographie interne | Bar chart nord / centre / sud (ton moyen) + tableau + avertissement biais | Q3 — Asymétrie géographique |
| Modèle prédictif | 4 KPIs ML + graphique importance des variables (Gini) | Composante ML |
| Narratifs | Bar chart des types d'événements (QuadClass) | Q2 — Narratifs dominants |
| Acteurs | Bar chart top 10 pays des acteurs impliqués (hors Bénin) | Contexte acteurs |
| Sources médias | Top domaines sources + part .ng / .bj | Biais de couverture |

---

## Limites connues

- **Pays acteurs ≠ pays sources médias.** `Actor1CountryCode` identifie le pays de l'acteur de l'événement, non le pays d'origine du média qui en parle. Une analyse des sources médiatiques nécessiterait de parser `SOURCEURL`.
- **Dates anormales codées en dur.** Les 8 dates anormales (10 jan, 17 avr, 7–12 déc 2025) sont issues du notebook EDA (approche multi-méthodes). Elles ne sont pas recalculées dynamiquement par le dashboard.
- **Contenu événements non disponible.** GDELT ne contient pas le texte des articles. Les descriptions contextuelles des 8 dates anormales (dans la table "Moments marquants") sont issues de sources externes vérifiées (AFP, France 24, Euronews, Jeune Afrique).
- **Parquet nécessite pyarrow.** Si `pyarrow` n'est pas installé, le dashboard bascule automatiquement sur le CSV.

---

## Source des données

**GDELT Project** — [gdeltproject.org](https://www.gdeltproject.org)

Filtre appliqué : `ActionGeo_CountryCode = 'BN'` · Période : 2025-01-01 → 2025-12-31
Table BigQuery : `gdelt-bq.gdeltv2.events`

---

## Déploiement Streamlit Community Cloud

1. Pousser le dépôt sur GitHub (branche `main`)
2. Se connecter sur [share.streamlit.io](https://share.streamlit.io)
3. Créer une nouvelle app :
   - **Repository** : `<votre-compte>/<nom-repo>`
   - **Branch** : `main`
   - **Main file path** : `benin_insights_challenge/dashboard/app.py`
4. Cliquer sur **Deploy**

> Le fichier `requirements.txt` à la racine est utilisé automatiquement par Streamlit Cloud pour installer les dépendances.

> Les fichiers de données (`data/processed/`) doivent être inclus dans le dépôt ou chargés depuis un stockage externe (Google Drive, S3). Streamlit Cloud ne dispose pas d'accès BigQuery sans configuration des secrets.

---

*Dashboard — Bénin Insights Challenge · iSHEERO × DataCamp 2026*
