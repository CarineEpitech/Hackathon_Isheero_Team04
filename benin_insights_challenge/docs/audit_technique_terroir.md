# Audit technique — TERROIR / BeninScope
**Date :** 2026-05-28
**Contexte :** Préparation migration vers application web professionnelle (FastAPI + Vue.js)

---

## 1. Structure actuelle du projet

```
benin_insights_challenge/
├── Pipeline.py              Pipeline de nettoyage + enrichissement GDELT
├── data/processed/          Dataset principal (parquet + CSV)
├── backend/services/        Modules Python backend (fetcher, pipeline, metrics, reporting)
├── backend/data/            Base SQLite des signalements citoyens
├── dashboard/app.py         Dashboard Streamlit (Phase 1 + Phase 2 en tabs)
├── models/                  Modèles ML sérialisés + métriques
├── notebooks/               5 notebooks d'analyse (Phase 1)
└── docs/                    Documentation projet
```

---

## 2. Forces réutilisables

### 2.1 Pipeline de données — solide
`Pipeline.py` est propre, testé, documenté. Il produit un parquet de 23 859 événements
avec 41 colonnes enrichies. Il peut être importé directement par FastAPI sans modification.

### 2.2 Backend services — déjà construits
Les 4 modules backend sont fonctionnels et testés :

| Module | Fonction | Tests |
|---|---|---|
| `gdelt_fetcher.py` | Collecte GDELT 15 min (HTTP, truststore SSL) | ✅ connexion OK |
| `realtime_pipeline.py` | Enrichissement identique au pipeline historique | ✅ 5 lignes test OK |
| `metrics.py` | STT par département (z-scores, 14j vs 90j) | ✅ 13 départements scorés |
| `reporting.py` | SQLite CRUD signalements citoyens + géoloc Bénin | ✅ 2 entrées test OK |

Ces modules constituent le cœur métier. Les routers FastAPI seront des adaptateurs minces
par-dessus eux — aucune logique à réécrire.

### 2.3 Dataset — production-ready
- 23 859 événements, 41 colonnes, couverture 2025 complète
- 3 975 événements sécuritaires (codes CAMEO 13-20)
- 2 101 événements précisément géolocalisés (utilisables pour la carte)
- Métriques ML validées (RF acc=69,8%, gain +7pp vs baseline)

### 2.4 Dépendances FastAPI — présentes à 80%
uvicorn, jinja2, python-multipart étaient déjà installés via Streamlit.
Seuls fastapi et aiofiles ont été ajoutés à l'étape 0.

---

## 3. Limites actuelles

### 3.1 Limites des données GDELT
- **91,2% de géolocalisation générique** (centroïde pays BN) : la carte live n'affichera
  que les 8,8% d'événements avec ville précise. Documenté et assumé.
- **Couverture médiatique ≠ réalité terrain** : 22% des articles viennent de médias nigérians.
  La couche citoyenne corrige partiellement ce biais.
- **Codes CAMEO : 15-30% d'erreur estimée** : agrégation sur EventRootCode (codes larges)
  plutôt que EventCode (codes fins) pour limiter le bruit.

### 3.2 Limites techniques
- **SQLite non thread-safe** sous forte concurrence : suffisant pour hackathon,
  à remplacer par PostgreSQL en production.
- **Pas de WebSocket** : le "live" est simulé par polling toutes les 30 secondes.
  Acceptable pour la démo.
- **Scheduler GDELT** : le poller 15 min n'est pas encore intégré à FastAPI.
  À brancher en Étape 2 via `asyncio` background task ou APScheduler.

---

## 4. Ce qui sera conservé

| Composant | Conservé | Note |
|---|---|---|
| `Pipeline.py` | ✅ intouché | Utilisé pour régénérer le dataset |
| `dashboard/app.py` (Streamlit) | ✅ intouché | Coexiste avec FastAPI sur port 8501 |
| Tous les notebooks | ✅ intouché | Phase 1, référence analytique |
| `data/processed/benin_enrichi.parquet` | ✅ source unique | Chargé par FastAPI au démarrage |
| `models/metrics_rf.json` | ✅ | Exposé via `/api/ml/metrics` |
| `backend/services/*.py` | ✅ | Importés directement par les routers |
| `backend/data/incidents.db` | ✅ | Base citoyenne existante |

---

## 5. Ce qui sera ajouté

### Backend
```
backend/
├── main.py                    FastAPI app — point d'entrée unique
└── routers/
    ├── events.py              /api/events/* — données GDELT
    ├── stt.py                 /api/stt — scores STT
    ├── incidents.py           /api/incidents — signalements citoyens
    └── ml.py                  /api/ml — métriques Random Forest
```

### Frontend (HTML/JS/CSS — zéro npm)
```
backend/static/
├── index.html                 SPA — navbar + Vue Router
├── pages/
│   ├── live.html              Carte live (Leaflet + polling GDELT)
│   ├── report.html            Signalement citoyen
│   ├── terroir.html           STT scoring + alertes
│   └── analyse.html           Analyse 2025 (graphiques Plotly.js)
├── js/
│   ├── app.js                 Vue 3 app + routing entre pages
│   ├── map.js                 Leaflet helpers (markers, popups, layers)
│   └── charts.js              Plotly.js helpers (timeline, barres, etc.)
└── css/
    └── style.css              Overrides Bootstrap 5 + styles BeninScope
```

### Documentation
```
docs/
├── journal_de_bord_terroir.md    Journal étape par étape (ce fichier)
└── audit_technique_terroir.md    Présent document
```

---

## 6. Architecture cible

```
                    ┌─────────────────────────────────────┐
                    │        NAVIGATEUR UTILISATEUR        │
                    │  Vue.js + Leaflet + Plotly.js (CDN)  │
                    └──────────────┬──────────────────────┘
                                   │ HTTP / JSON
                    ┌──────────────▼──────────────────────┐
                    │         FastAPI (port 8000)          │
                    │  ┌──────────┐  ┌──────────────────┐ │
                    │  │ /api/*   │  │ /static/*        │ │
                    │  │ routers  │  │ HTML, JS, CSS    │ │
                    │  └────┬─────┘  └──────────────────┘ │
                    │       │                              │
                    │  ┌────▼──────────────────────────┐  │
                    │  │       Backend Services         │  │
                    │  │  metrics.py  reporting.py      │  │
                    │  │  gdelt_fetcher.py  pipeline.py │  │
                    │  └────┬──────────────────────────┘  │
                    └───────│──────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    benin_enrichi.parquet  incidents.db   GDELT API
    (23 859 evt)           (SQLite)       (15 min)


    Streamlit (port 8501) — dashboard analytique — intouché
```

---

## 7. Risques techniques

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Chemin d'import relatif dans les services | Moyen | Bloquant | `sys.path.insert(0, ...)` dans main.py |
| `use_container_width` Streamlit déprécié | Faible | Mineur | Déjà corrigé |
| GDELT live : 0 événements Bénin par slice | Élevé | Mineur | Fallback dataset historique |
| SQLite concurrence sur `/api/incidents POST` | Faible | Mineur | Acceptable hackathon |
| Leaflet CDN offline | Très faible | Critique | Servir Leaflet en local (fallback) |
| Port 8000 occupé | Faible | Bloquant | `--port 8001` en fallback |

---

## 8. Priorités de build

1. `backend/main.py` + route `/health` — vérifier que FastAPI démarre
2. `backend/routers/events.py` — données GDELT (carte live + analyse)
3. `backend/routers/stt.py` — scores STT (TERROIR)
4. `backend/routers/incidents.py` — signalements citoyens (GET + POST)
5. `backend/routers/ml.py` — métriques ML
6. `backend/static/index.html` + navbar + Vue Router
7. Page `live.html` — carte Leaflet interactive
8. Page `terroir.html` — STT scoring
9. Page `report.html` — formulaire signalement
10. Page `analyse.html` — tous les graphiques Plotly.js
11. Polish CSS + responsive
12. Déploiement Railway

---

## 9. Estimation de faisabilité

| Phase | Contenu | Durée estimée |
|---|---|---|
| Backend FastAPI complet | main.py + 4 routers + tous les endpoints | 2h |
| Frontend structure | index.html + navbar + routing Vue | 30min |
| Carte Live | Leaflet + markers + hover/popup + polling | 1h30 |
| TERROIR STT | Cards + barres Plotly.js + alertes | 1h |
| Signalement | Formulaire + POST + retour visuel | 30min |
| Analyse 2025 | 8 graphiques Plotly.js + tableau anomalies | 2h |
| Polish + déploiement | CSS, responsive, Railway | 1h |
| **Total** | | **~8h30** |

**Verdict :** Faisable dans la fenêtre de temps restante. Le backend réutilise 100% du
code déjà écrit. Le frontend est du HTML/JS standard, aucune compilation nécessaire.

---

## 10. Ordre recommandé des prochaines étapes

```
Étape 0  ✅  Audit — TERMINÉ
Étape 1  →   Backend main.py + tous les routers FastAPI
Étape 2  →   Frontend index.html + navigation Vue.js
Étape 3  →   Page Carte Live (Leaflet)
Étape 4  →   Page TERROIR STT
Étape 5  →   Page Signalement citoyen
Étape 6  →   Page Analyse 2025 (graphiques)
Étape 7  →   Polish + déploiement Railway
```
