# Audit repo — BeninScope / TERROIR
# Avant push GitHub final

---

## 1. Structure recommandée finale

```
Hackathon_Isheero_Team04/
├── README.md                          ✓ (V2 déjà en place)
├── .gitignore                         ✓
│
└── benin_insights_challenge/
    ├── README.md                      ✓ (V2 déjà en place)
    ├── Pipeline.py                    ✓
    ├── requirements.txt               ✓ (voir note dépendances)
    ├── railway.toml                   ✓
    ├── Procfile                       ✓
    ├── runtime.txt                    ✓
    ├── .gitignore                     ✓ (à compléter)
    │
    ├── backend/
    │   ├── main.py                    ✓
    │   ├── routers/                   ✓ (tous actifs)
    │   ├── services/
    │   │   ├── gdelt_live_poller.py   ✓ ACTIF
    │   │   ├── data_loader.py         ✓ ACTIF
    │   │   ├── metrics.py             ✓ ACTIF
    │   │   ├── reporting.py           ✓ ACTIF
    │   │   ├── gdelt_fetcher.py       ⚠ orphelin (voir section 5)
    │   │   ├── gdelt_live_snippet.py  ✗ à supprimer du repo
    │   │   ├── realtime_pipeline.py   ⚠ orphelin (voir section 5)
    │   │   └── storage.py             ⚠ orphelin (voir section 5)
    │   ├── static/                    ✓ (frontend complet)
    │   └── data/
    │       └── gdelt_status.json      ✓ (auto-généré, ok)
    │
    ├── data/
    │   ├── raw/
    │   │   └── benin_raw.csv          ✓ GARDER (source BigQuery)
    │   └── processed/
    │       └── benin_enrichi.parquet  ✓ GARDER (1,5 MB, utilisé par l'app)
    │       [benin_clean.csv]          ✗ SUPPRIMER du repo
    │       [benin_enrichi.csv]        ✗ SUPPRIMER du repo
    │       [benin_features.csv]       ✗ SUPPRIMER du repo
    │
    ├── models/
    │   └── metrics_rf.json            ✓ GARDER (3 Ko, résultats Phase 1)
    │   [*.pkl]                        ✗ UNTRACKER (déjà dans .gitignore)
    │
    ├── notebooks/
    │   ├── 01_pipeline_gdelt.ipynb    ✓
    │   ├── 02_eda_exploration.ipynb   ✓
    │   ├── 03_feature_engineering_v0  ✓
    │   ├── 03_ml_models.ipynb         ✓
    │   ├── 04_analyse_complete.ipynb  ✓
    │   ├── outputs/                   ✓ (visuels Phase 1)
    │   ├── archive/                   ✓ (brouillons isolés)
    │   └── models/scaler_standard.pkl ✗ UNTRACKER
    │
    ├── scripts/
    │   ├── fill_gap_2026.py           ✓ ACTIF (rattrapage GDELT)
    │   ├── import_2026_csv.py         ✓ ACTIF (import BigQuery CSV)
    │   ├── query_bigquery.sql         ✓ GARDER (documente la source)
    │   ├── query_bigquery_2026.sql    ✓ GARDER
    │   └── patch_terroir_v4.py        ✗ DÉPLACER (chemin absolu local)
    │
    ├── docs/
    │   ├── resume_une_page.md         ✓ GARDER
    │   ├── insights.md                ✓ GARDER
    │   └── questions_jury_beninscope.md ✓ GARDER
    │   [autres docs internes]         ✗ DÉPLACER vers docsphase2
    │
    └── dashboard/
        └── app.py                     ✓ GARDER (Phase 1, contexte)
        [README_dashboard.md]          ✗ DÉPLACER (doc interne Streamlit)
```

---

## 2. Fichiers à déplacer vers OneDrive/Downloads/docsphase2

Ces fichiers ne doivent pas être dans le repo public. Ils sont des documents de travail internes, audits, journaux ou prompts de sessions.

| Fichier | Raison |
|---|---|
| `docs/audit_final_pre_jury_beninscope.md` | Audit interne de travail |
| `docs/audit_technique_terroir.md` | Audit interne |
| `docs/auto_audit_beninscope.md` | Audit interne |
| `docs/benin_insights_questions_analytiques.md` | Planning Phase 1, obsolète |
| `docs/journal_de_bord_terroir.md` | Journal de développement interne |
| `docs/questions_jury.md` | Ancien doc jury Phase 1, remplacé par questions_jury_beninscope.md |
| `dashboard/README_dashboard.md` | Doc interne Streamlit |
| `scripts/patch_terroir_v4.py` | Chemin absolu `C:\Users\carin\` — ne doit jamais être dans un repo public |
| `scripts/create_outputs_v4.py` | Non tracké, chemin absolu `C:\Users\carin\`, génère fichiers vers OneDrive |
| `README_backup_original.md` (racine) | Sauvegarde temporaire, inutile dans le repo |

---

## 3. Fichiers à supprimer du repo (git rm)

Ces fichiers sont actuellement **trackés par git** et ne doivent plus l'être. Ils sont inutiles pour l'application et gonflent le repo.

### Données intermédiaires (22 MB inutiles)

| Fichier | Taille | Raison |
|---|---|---|
| `data/processed/benin_clean.csv` | 6,9 MB | Étape intermédiaire du pipeline, dupliqué dans le parquet |
| `data/processed/benin_enrichi.csv` | 9,2 MB | Exactement les mêmes données que `benin_enrichi.parquet`, format redondant |
| `data/processed/benin_features.csv` | 5,4 MB | Features ML Phase 1, non utilisées par TERROIR |

### Service orphelin évident

| Fichier | Raison |
|---|---|
| `backend/services/gdelt_live_snippet.py` | La doc du fichier dit explicitement "NE PAS exécuter — snippets à copier-coller". Plus utile depuis que le code est intégré. |

---

## 4. Fichiers à untracker (git rm --cached)

Ces fichiers sont dans `.gitignore` mais ont été ajoutés à git **avant** la règle — ils restent donc trackés. Il faut les retirer de l'index sans les supprimer localement.

| Fichier | Taille | Problème |
|---|---|---|
| `models/random_forest_ton.pkl` | **36 MB** | Critique — risque de dépasser les limites GitHub LFS |
| `models/kmeans_v1.pkl` | 96 KB | Inutile pour TERROIR |
| `models/naive_bayes_v1.pkl` | — | Inutile pour TERROIR |
| `models/encoders.pkl` | — | Inutile pour TERROIR |
| `notebooks/models/scaler_standard.pkl` | — | Notebook, pas l'app |

Commande :
```bash
git rm --cached models/random_forest_ton.pkl models/kmeans_v1.pkl models/naive_bayes_v1.pkl models/encoders.pkl notebooks/models/scaler_standard.pkl
```

### Compléter le .gitignore (racine benin_insights_challenge/)

Ajouter :
```
# Données intermédiaires (recréées par Pipeline.py)
data/processed/benin_clean.csv
data/processed/benin_enrichi.csv
data/processed/benin_features.csv

# Sauvegarde temporaire
README_backup_original.md
```

---

## 5. Services orphelins — décision

Ces fichiers sont trackés mais **non importés** par aucun module actif de l'application.

| Fichier | Statut | Recommandation |
|---|---|---|
| `backend/services/gdelt_fetcher.py` | Non importé — précurseur du `gdelt_live_poller.py` | Garder (référence historique, pas de risque) |
| `backend/services/realtime_pipeline.py` | Non importé — ancienne architecture | Garder (pas de risque actif) |
| `backend/services/storage.py` | Non importé — utilitaire JSON non utilisé | Garder (3 Ko, inoffensif) |

Ces fichiers ne cassent rien et peuvent être utiles pour comprendre l'évolution du code. Le seul à supprimer est `gdelt_live_snippet.py` car sa propre documentation dit qu'il ne doit pas être exécuté.

---

## 6. Risques de déploiement Railway

### Risque 1 — requirements.txt contient des dépendances inutiles au runtime

```
streamlit>=1.30.0    # Utilisé uniquement par dashboard/app.py (Phase 1)
kaleido==0.2.1       # Export PNG Plotly — non utilisé par TERROIR
matplotlib>=3.7.0    # Non utilisé par TERROIR (notebooks uniquement)
seaborn>=0.12.0      # Non utilisé par TERROIR
scikit-learn>=1.3.0  # Non utilisé par TERROIR à runtime
joblib>=1.3.0        # Idem
scipy>=1.11.0        # Idem
```

Ces packages allongent le build Railway de plusieurs minutes et consomment de la mémoire. Risque faible (le déploiement fonctionne) mais build lent.

### Risque 2 — Les pkl files trackés (36 MB) ralentissent les push et pulls

Tant qu'ils ne dépassent pas 100 MB (limite GitHub LFS), le push passe. Mais les retirer reste recommandé.

### Risque 3 — `backend/data/gdelt_status.json` modifié à chaque cycle

Ce fichier est tracké et est modifié toutes les 15 minutes par le poller. Chaque déploiement Railway part d'un `gdelt_status.json` potentiellement en erreur. Pas bloquant car le poller le réécrit au démarrage.

### Risque 4 — `data/processed/benin_live.parquet` absent au premier démarrage

Il est dans `.gitignore` donc pas dans le repo. Le poller le crée automatiquement. Le `data_loader.py` gère l'absence proprement. Pas de risque.

### Risque 5 — Chemin `data/processed/fill_gap_checkpoint.json`

Créé par `fill_gap_2026.py` si interrompu. Pas tracké, pas de risque.

---

## 7. Risques GitHub (visibilité publique)

| Risque | Fichier | Gravité |
|---|---|---|
| Chemin absolu local | `scripts/patch_terroir_v4.py` (`C:\Users\carin\`) | Moyen — révèle le username local |
| Chemin absolu local | `scripts/create_outputs_v4.py` (non tracké) | Faible — pas encore dans le repo |
| Fichier trop lourd | `models/random_forest_ton.pkl` (36 MB) | Moyen — ralentit tous les clones |
| Données redondantes | `benin_clean.csv` + `benin_enrichi.csv` (16 MB) | Faible — inutile mais pas dangereux |
| Doc interne visible | `docs/journal_de_bord_terroir.md` | Faible — notes de travail exposées |
| Doc interne visible | `docs/audit_*.md` | Faible — audits internes exposés |
| Config IDE | `benin_insights_challenge/.claude/settings.local.json` | Moyen — config locale dans .gitignore ✓ |

Aucun secret (token, clé API, mot de passe) détecté dans les fichiers trackés.

---

## 8. Check-list finale avant push

```
□ git rm --cached models/*.pkl notebooks/models/*.pkl
□ git rm --cached data/processed/benin_clean.csv data/processed/benin_enrichi.csv data/processed/benin_features.csv
□ git rm --cached docs/audit_final_pre_jury_beninscope.md docs/audit_technique_terroir.md docs/auto_audit_beninscope.md docs/benin_insights_questions_analytiques.md docs/journal_de_bord_terroir.md docs/questions_jury.md
□ git rm --cached dashboard/README_dashboard.md
□ git rm --cached backend/services/gdelt_live_snippet.py
□ git rm --cached scripts/patch_terroir_v4.py
□ Déplacer ces fichiers vers OneDrive/Downloads/docsphase2 AVANT le git rm
□ Compléter .gitignore (CSV intermédiaires + README_backup)
□ Supprimer README_backup_original.md de la racine
□ git add + git commit "chore: nettoyage repo final avant jury"
□ git push
□ Vérifier sur GitHub que random_forest_ton.pkl n'apparaît plus
□ Vérifier que terroir.up.railway.app est accessible
□ Vérifier que l'API /api/docs répond
□ Vérifier que la carte Live charge des points
```

---

*BeninScope — Hackathon iSHEERO × DataCamp 2026*
