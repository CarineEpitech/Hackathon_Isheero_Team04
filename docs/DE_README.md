# PROMPT DE REPRISE DE CONTEXTE — DATA ENGINEER
## Hackathon iSHEERO × DataCamp 2026 — Bénin Insights Challenge
## QUI JE SUIS
Je suis le **Data Engineer** d'une équipe de 4 personnes participant au
**Hackathon iSHEERO × DataCamp 2026**, défi **Bénin Insights Challenge**.
Mon rôle dans l'équipe :
•	Extraction des données GDELT via Google BigQuery
•	Nettoyage et enrichissement des données (`benin_clean.csv`, `benin_enrichi.csv`)
•	Documentation du pipeline (`01_pipeline_nettoyage.ipynb`)
•	Création et gel des dépendances (`requirements.txt`)
•	Vérification de la reproductibilité from scratch
•	Fourniture du `pipeline.py` standalone

Je ne touche jamais : `docs/*` · `app/*` · `models/*` · `notebooks/02_*` ·
`notebooks/03_*` · `notebooks/04_*`
---
## L'ÉQUIPE
| Rôle | Responsabilités principales |
|---|---|
| Data Engineer (DE) — MOI | Pipeline GDELT · nettoyage · `benin_clean.csv` · `benin_enrichi.csv` · `requirements.txt` · `pipeline.py` |
| Data Analyst (DA) | EDA · 5 visualisations · dashboard Streamlit · `streamlit_app.py` |
| ML Engineer (ML) | Feature engineering · modèle ML · détection d'anomalies · `model_final.pkl` |
| Data Scientist (DS) | Insights · résumé · scripts pitch · Q&A · coordination soumission |
---
## LE PROJET
**Compétition :** Hackathon iSHEERO × DataCamp 2026
**Défi :** Bénin Insights Challenge
**Période :** 27 avril → 5 mai 2026 (Phase 1) · Demo Day 9 mai 2026
**Source de données :** GDELT Project (`gdelt-bq.gdeltv2.events`)
**Filtre principal :** `ActionGeo_CountryCode = 'BN'` · période 01/01/2025–31/12/2025

>  **Correction critique** : Les documents officiels iSHEERO indiquent
> `ActionGeo_CountryCode = 'BC'` mais ce code correspond à la
> **Colombie-Britannique** (Canada). Le vrai code FIPS du Bénin est **`'BN'`**.
> Toutes nos requêtes utilisent `'BN'`.

**Livrable final :** Dashboard Streamlit interactif + pitch vidéo 3 min +
résumé d'une page + 5 insights actionnables
---
## MES LIVRABLES PAR JOUR
| Jour | Ce que je crée | Ce que je finalise | Dépendances sortantes |
|---|---|---|---|
| J1 | `README.md` v1 · `data/raw/benin_raw.csv` | `benin_raw.csv`(fait) | DA + ML + DS attendent mon CSV |
| J2 | `01_pipeline_nettoyage.ipynb` · `benin_clean.csv` · `benin_enrichi.csv` · `benin_enrichi.parquet` | `benin_clean.csv`(fait)  · `benin_enrichi.csv`(fait)  | DA commence EDA · ML commence features |
| J3 | `pipeline.py` standalone · Pipeline v2 (assertions qualité · zone_benin · enrichissement complet) | `01_pipeline_nettoyage.ipynb`(fait)  · `pipeline.py`(fait)  | ML peut avoir besoin de colonnes supplémentaires |
| J4 | `requirements.txt` · test reproductibilité from scratch | `requirements.txt`(fait)  | DA + ML doivent pouvoir relancer sans moi |
| J5 | — | `README.md`  (relecture finale)(fait) | Support soumission pour toute l'équipe |

**Règle d'or :** Une fois `benin_clean.csv` livré en J2, ne plus modifier
`data/processed/` — les autres construisent dessus.

---
## STRUCTURE DU REPO GITHUB
Hackathon_Isheero_Team04/ ├── README.md ← je maintiens ├── requirements.txt ← je crée en J4 ├── pipeline.py ← script standalone · python pipeline.py ├── .gitignore ← exclut data/raw/ · *.csv · *.parquet ├── data/ │ ├── raw/ │ │ └── benin_raw.csv ← extraction GDELT brute  figé après J1 │ └── processed/ │ ├── benin_clean.csv ←  figé après J2 │ ├── benin_enrichi.csv ←  figé après J2 │ └── benin_enrichi.parquet ←  format compressé pour dashboard ├── notebooks/ │ ├── 00_schema_exploration.ipynb ← ML Engineer · je ne touche pas │ └── 01_pipeline_nettoyage.ipynb ← MON seul notebook ├── app/ ← DA gère · je ne touche pas │ └── streamlit_app.py ├── models/ ← ML gère · je ne touche pas ├── docs/ ← DS gère · je ne touche pas └── submission/ ← créé en J5
---
## EXTRACTION GDELT — REQUÊTE DE RÉFÉRENCE
```sql
-- ============================================================
-- REQUÊTE GDELT BÉNIN — VERSION FINALE COMPLÈTE
-- * Toujours filtrer YEAR en premier (économise le quota 1TB)
-- * Tester avec LIMIT 100 avant de lancer LIMIT 10000
-- * Code FIPS Bénin = 'BN' (pas 'BC' comme dans les docs iSHEERO)
-- ============================================================
SELECT
    -- Identification & dates
    GLOBALEVENTID,          -- Clé primaire · déduplication
    SQLDATE,                -- Date YYYYMMDD
    MONTHYEAR,              -- Agrégation mensuelle YYYYMM
    YEAR,                   -- Filtre quota BigQuery — toujours en premier
    FractionDate,           -- Date décimale · séries temporelles fines
    IsRootEvent,            -- 1=Bénin sujet principal · 0=mention secondaire

    -- Géographie événement
    ActionGeo_CountryCode,  -- Code FIPS · valeur Bénin = 'BN'
    ActionGeo_FullName,     -- Nom complet lieu ex: "Cotonou, Littoral, Benin"
    ActionGeo_ADM1Code,     -- Département béninois
    ActionGeo_Lat,          -- Latitude GPS
    ActionGeo_Long,         -- Longitude GPS

    -- Acteurs — localisation
    Actor1Geo_CountryCode,  -- Pays localisation acteur 1
    Actor2Geo_CountryCode,  -- Pays localisation acteur 2

    -- Acteurs — nationalité & identité
    Actor1CountryCode,      -- Nationalité acteur 1 · valeur béninoise = 'BEN'
    Actor2CountryCode,      -- Nationalité acteur 2
    Actor1Name,             -- Nom acteur 1 · ex: "PATRICE TALON"
    Actor2Name,             -- Nom acteur 2
    Actor1Type1Code,        -- Type CAMEO · GOV/MIL/NGO/CVL/BUS/MED/REB
    Actor2Type1Code,        -- Type CAMEO acteur 2
    Actor1KnownGroupCode,   -- Groupe connu · ISWAP · ECOWAS · AQ
    Actor2KnownGroupCode,   -- Groupe connu acteur 2

    -- Événement & classification
    EventRootCode,          -- Code CAMEO racine 1-20
    EventBaseCode,          -- Code CAMEO intermédiaire
    EventCode,              -- Code CAMEO précis 3-4 chiffres
    QuadClass,              -- 1=Coop verbale · 2=Coop matérielle
                            -- 3=Conflit verbal · 4=Conflit matériel

    -- Stabilité & volume
    GoldsteinScale,         -- Score stabilité -10 à +10
    NumMentions,            -- Nombre de mentions
    NumSources,             -- Nombre de sources distinctes
    NumArticles,            -- Nombre d'articles

    -- Ton & sentiment
    AvgTone,                -- Ton médiatique moyen

    -- Source
    SOURCEURL               -- URL article · identifier média et langue

FROM `gdelt-bq.gdeltv2.events`

WHERE YEAR = 2025
  AND ActionGeo_CountryCode = 'BN'       -- Événement physiquement au Bénin (FIPS)
  AND (
      Actor1Geo_CountryCode = 'BN'    -- Acteur 1 localisé au Bénin
      OR Actor2Geo_CountryCode = 'BN'    -- Acteur 2 localisé au Bénin
  )
  AND (
      Actor1CountryCode = 'BEN'       -- Acteur 1 de nationalité béninoise (ISO)
      OR Actor2CountryCode = 'BEN'       -- Acteur 2 de nationalité béninoise (ISO)
  )
  AND LOWER(ActionGeo_FullName) LIKE '%benin%'
```

**Projet BigQuery :** `gdelt-bq`
**Table :** `gdeltv2.events`
**Volume extrait :** ~10 722 lignes · 31 colonnes
**Fichier produit :** `data/raw/benin_raw.csv`
---
## COLONNES CLÉS ET LEUR RÔLE

| Colonne | Type | Rôle analytique | Critique ? |
|---|---|---|---|
| `GLOBALEVENTID` | INT | Clé primaire · déduplication |  Oui |
| `SQLDATE` | INT (YYYYMMDD) | Horodatage précis |  Oui |
| `MONTHYEAR` | INT (YYYYMM) | Agrégation mensuelle |  Oui |
| `FractionDate` | FLOAT | Séries temporelles journalières |  Oui |
| `IsRootEvent` | INT (0/1) | Filtrer les vraies actualités béninoises |  Oui |
| `AvgTone` | FLOAT | Tonalité couverture (négatif = mauvais) |  Oui |
| `GoldsteinScale` | FLOAT | Impact stabilisateur/déstabilisateur (−10 à +10) |  Oui |
| `NumMentions` | INT | Volume de couverture |  Oui |
| `NumArticles` | INT | Nombre d'articles distincts |  Oui |
| `EventRootCode` | STRING | Famille d'événement CAMEO (1-20) |  Oui |
| `EventCode` | STRING | Type précis d'événement CAMEO (3-4 chiffres) |  Oui |
| `QuadClass` | INT | 4 grandes catégories conflit/coopération |  Oui |
| `ActionGeo_FullName` | STRING | Nom lieu · classification zone nord/centre/sud |  Oui |
| `ActionGeo_ADM1Code` | STRING | Département béninois |  Oui |
| `ActionGeo_Lat/Long` | FLOAT | Géolocalisation précise · cartographie |  Oui |
| `SOURCEURL` | STRING | Domaine source → pays et langue éditeur |  Oui |
| `Actor1CountryCode` | STRING | Pays acteur principal |  Souvent null |
| `Actor1Name` | STRING | Nom acteur principal |  Souvent null |
| `Actor1KnownGroupCode` | STRING | Groupes armés connus (ISWAP...) |  Souvent null |
---
## TRANSFORMATIONS DANS `benin_enrichi.csv`
Colonnes calculées ajoutées dans le pipeline pour le DA et le ML :
```python
# ── Temporelles ───────────────────────────────────────────
df['SQLDATE'] = pd.to_datetime(df['SQLDATE'].astype(str), format='%Y%m%d')
df['mois']       = df['SQLDATE'].dt.month
df['trimestre']  = df['SQLDATE'].dt.quarter
df['annee']      = df['SQLDATE'].dt.year
df['mois_annee'] = df['SQLDATE'].dt.to_period('M').astype(str)  # ex: "2025-06"
df['jour_semaine'] = df['SQLDATE'].dt.dayofweek                 # 0=Lundi

# ── Ton médiatique (5 niveaux) ────────────────────────────
# tres_negatif · negatif · neutre · positif · tres_positif
df['ton_categorie'] = df['AvgTone'].apply(categoriser_ton)

# ── Goldstein (5 niveaux) ─────────────────────────────────
# tres_conflictuel · conflictuel · neutre · cooperatif · tres_cooperatif
df['goldstein_categorie'] = df['GoldsteinScale'].apply(categoriser_goldstein)

# ── QuadClass lisible ─────────────────────────────────────
# cooperation_verbale · cooperation_materielle
# conflit_verbal · conflit_materiel
df['quadclass_label'] = df['QuadClass'].map(quadclass_labels)

# ── Zone géographique Bénin ───────────────────────────────
# Recherche par any() + .lower() pour matcher
# "Kandi, Alibori, Benin" → 'nord' 
# "Bohicon, Zou, Benin"   → 'centre' 
# "Cotonou, Benin"        → 'sud' 
df['zone_benin'] = df['ActionGeo_FullName'].apply(classifier_zone)

# Nord    : Alibori · Atacora · Donga · Borgou
# Centre  : Zou · Collines
# Sud     : Atlantique · Littoral · Ouémé · Plateau · Mono · Couffo

# ── Domaine source ────────────────────────────────────────
# ex: "www.rfi.fr" → "rfi.fr"
df['source_domaine'] = df['SOURCEURL'].apply(extraire_domaine)

# ── Score intensité composite ─────────────────────────────
df['intensite'] = df['NumMentions'] * abs(df['GoldsteinScale'].fillna(0))
```
---
## ASSERTIONS QUALITÉ PIPELINE
```python
# Volume suffisant
assert len(df) > 1000, \
    f" Dataset trop petit ({len(df)} lignes) — vérifier le filtre GDELT"

# Aucun doublon
assert df['GLOBALEVENTID'].duplicated().sum() == 0, \
    " Doublons détectés sur GLOBALEVENTID"

# Aucune date invalide
assert df['SQLDATE'].isna().sum() == 0, \
    " Dates manquantes après nettoyage"

# Période correcte
assert df['SQLDATE'].min().year >= 2025, \
    " Données avant 2025 détectées"

# AvgTone majoritairement renseigné
assert df['AvgTone'].notna().mean() > 0.95, \
    f" Trop de nulls AvgTone ({df['AvgTone'].isna().mean():.1%})"

# GoldsteinScale dans les bornes
assert df['GoldsteinScale'].dropna().between(-10, 10).all(), \
    " GoldsteinScale hors plage [-10, 10]"

# Latitudes valides
assert df['ActionGeo_Lat'].dropna().between(-90, 90).all(), \
    " Latitudes hors limites"

# Colonnes critiques présentes
for col in ['GLOBALEVENTID', 'SQLDATE', 'AvgTone',
            'GoldsteinScale', 'ActionGeo_CountryCode']:
    assert col in df.columns, f" Colonne manquante : {col}"

print(f" Pipeline validé — {len(df):,} événements · "
      f"{df['mois_annee'].nunique()} mois · "
      f"{df['source_domaine'].nunique():,} domaines sources")
```
---

## `requirements.txt` — CONTENU ATTENDU (J4)
pandas>=2.2.0 numpy>=1.26.0 google-cloud-bigquery>=3.17.0 db-dtypes>=1.2.0 pyarrow>=15.0.0 polars>=0.20.0 scikit-learn>=1.4.0 matplotlib>=3.8.0 seaborn>=0.13.0 plotly>=5.19.0 folium>=0.15.0 streamlit>=1.31.0 streamlit-folium>=0.18.0 textblob>=0.18.0 transformers>=4.38.0 scipy>=1.12.0 tqdm>=4.66.0 python-dotenv>=1.0.0 jupyter>=1.0.0 ipykernel>=6.29.0
---

## `README.md` — SECTIONS À MAINTENIR

```markdown
# 🇧🇯 Bénin Insights Challenge — Hackathon iSHEERO × DataCamp 2026

## Équipe
| Rôle | Membre |
|------|--------|
| Data Engineer | [Ton nom] |
| Data Analyst | [Nom] |
| ML Engineer | [Nom] |
| Data Scientist | [Nom] |

## Objectif
Extraire, analyser et visualiser la couverture médiatique mondiale du Bénin
(01/01/2025-31/12/2025) via la base GDELT pour produire des insights actionnables
à destination de journalistes, chercheurs et décideurs publics.

## Installation
pip install -r requirements.txt

## Reproduire le pipeline
1. Placer `benin_raw.csv` dans `data/raw/`
   → Télécharger depuis Google Drive : [lien]
2. Exécuter `notebooks/01_pipeline_nettoyage.ipynb`
   → Produit `benin_clean.csv` et `benin_enrichi.csv`
3. Exécuter `notebooks/02_eda_exploration.ipynb`
4. Exécuter `notebooks/03_feature_engineering.ipynb`
5. Exécuter `notebooks/04_modele_ml_final.ipynb`
6. Lancer `streamlit run app/streamlit_app.py`

Ou en une seule commande :
python pipeline.py

## Dashboard
[URL Streamlit Cloud — à compléter]

## Données
Source : GDELT Project — gdelt-bq.gdeltv2.events
Filtre : ActionGeo_CountryCode = 'BN' · Période : 2025–2026
Volume : ~10 722 événements · 31 colonnes
CSV brut commité → data/raw/benin_raw 

## Usage IA
Claude (Anthropic) utilisé pour la génération et le debug du pipeline.
Mentionné conformément aux règles du hackathon iSHEERO 2026.
```
---

## ÉTAT D'AVANCEMENT

| Jour | Statut | Ce qui est livré |
|---|---|---|
| J1 | Fait | `donnees_benin.csv` (31 col · ~11 000 lignes · code BN) · `README.md` v1 · repo structuré |
| J2 | Fait | `benin_clean.csv` · `benin_enrichi.csv` · `benin_enrichi.parquet` · `01_pipeline_nettoyage.ipynb` v1 |
| J3 | Fait | `pipeline.py` standalone · Pipeline v2 (assertions · zone nord/centre/sud · enrichissement complet) |
| J4 | En cours | `requirements.txt` · test reproductibilité from scratch |
| J5 | En cours | Relecture `README.md` · support soumission |
---
## CE QUI RESTE À FAIRE

**J4 :**
1. Créer `requirements.txt` propre et versionné
2. Tester reproductibilité dans un environnement vierge :
```bash
   git clone https://github.com/[org]/benin-insights-challenge.git
   cd benin-insights-challenge
   pip install -r requirements.txt
   python pipeline.py
   streamlit run app/streamlit_app.py
```
3. Vérifier que `benin_clean.csv` et `benin_enrichi.csv` sont accessibles
   par le DA et le ML sans intervention de ma part
4. Mettre à jour `README.md` avec l'URL du dashboard une fois déployé
**J5 :**
1. Relire `README.md` — vérifier tous les liens et instructions
2. S'assurer que tous les notebooks s'exécutent dans l'ordre sans erreur
3. Être disponible pour débloquer tout problème technique de dernière minute

---

## POINTS D'ATTENTION CRITIQUES
 Code pays : utiliser 'BN' (Bénin) et NON 'BC' (Colombie-Britannique)  Nationalité acteurs : utiliser 'BEN' (ISO 3 lettres) et NON 'BN'  Ne jamais modifier data/processed/ après J2  Quota BigQuery : toujours filtrer YEAR en premier · tester LIMIT 100 avant LIMIT 10000  zone_benin : utiliser any() + .lower() pour matcher "Kandi, Benin" → nord
---.
