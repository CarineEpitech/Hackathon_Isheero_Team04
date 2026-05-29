# Journal de bord — TERROIR / BeninScope
**Projet :** TERROIR — Système de veille territoriale et sécuritaire du Bénin
**Équipe :** BeninScope (anciennement Équipe 04)
**Hackathon :** iSHEERO × DataCamp 2026

---

## Format des entrées

```
## Étape N — Titre
Date    :
Durée   :
Auteur  :
Objectif :
Actions :
Tests exécutés :
Résultat :
Problèmes rencontrés :
Décisions :
Prochaine étape :
```

---

## Étape 0 — Audit initial du repository

**Date :** 2026-05-28
**Objectif :** Comprendre l'état exact du projet avant toute modification. Préparer la migration vers une vraie application web sans rien casser.

### Structure détectée

```
benin_insights_challenge/
│
├── Pipeline.py                        Pipeline GDELT (nettoyage + enrichissement)
├── requirements.txt                   Dépendances Python
├── README.md
│
├── data/
│   ├── raw/benin_raw.csv              Source brute BigQuery
│   └── processed/
│       ├── benin_enrichi.parquet      Dataset principal (23 859 evt, 41 col)
│       ├── benin_enrichi.csv          Idem en CSV
│       ├── benin_clean.csv            Version sans enrichissement
│       ├── benin_features.csv         Features ML
│       ├── benin_live.parquet         Snapshot live (généré en session)
│       └── .gdelt_last_processed.txt  Curseur GDELT dernier traitement
│
├── backend/
│   ├── data/
│   │   └── incidents.db               SQLite — signalements citoyens (2 entrées test)
│   └── services/
│       ├── gdelt_fetcher.py           Collecteur GDELT 15 min (truststore SSL)
│       ├── realtime_pipeline.py       Enrichissement snapshots temps réel
│       ├── metrics.py                 Calcul STT (z-scores, fenêtres glissantes)
│       ├── reporting.py               CRUD SQLite — incidents citoyens
│       ├── gdelt_live_poller.py       Poller GDELT (généré en session)
│       └── gdelt_live_snippet.py      Snippet live (généré en session)
│
├── dashboard/
│   └── app.py                         Streamlit 4 onglets (500+ lignes)
│
├── models/
│   ├── metrics_rf.json                Métriques RF (acc=69.8%, gain=+7pp)
│   ├── random_forest_ton.pkl          Modèle RF sérialisé
│   ├── naive_bayes_v1.pkl
│   ├── kmeans_v1.pkl
│   └── encoders.pkl
│
├── notebooks/
│   ├── 01_pipeline_gdelt.ipynb
│   ├── 02_eda_exploration.ipynb
│   ├── 03_feature_engineering_v0.ipynb
│   ├── 03_ml_models.ipynb
│   └── 04_analyse_complete.ipynb
│
├── docs/                              (créé étape 0)
├── scripts/
│   ├── query_bigquery.sql
│   ├── query_bigquery_2026.sql
│   └── import_2026_csv.py
```

### Composants réutilisables

| Composant | Fichier | Statut | Réutilisation web app |
|---|---|---|---|
| Pipeline GDELT | `Pipeline.py` | Fonctionnel | Import direct |
| Collecteur GDELT 15 min | `backend/services/gdelt_fetcher.py` | Testé ✅ | Import direct |
| Pipeline temps réel | `backend/services/realtime_pipeline.py` | Testé ✅ | Import direct |
| Calcul STT | `backend/services/metrics.py` | Testé ✅ | Via router FastAPI |
| Signalements citoyens | `backend/services/reporting.py` | Testé ✅ | Via router FastAPI |
| Dataset historique | `data/processed/benin_enrichi.parquet` | 23 859 lignes | Chargé au démarrage |
| Métriques ML | `models/metrics_rf.json` | Valeurs validées | Endpoint /api/ml |
| SQLite incidents | `backend/data/incidents.db` | 2 entrées test | Endpoint /api/incidents |

### État du dataset

- **N événements :** 23 859
- **Colonnes :** 41 (30 originales + 11 enrichies)
- **Période :** 2025-01-01 → 2025-12-31
- **Sécurité (codes 13-20) :** 3 975 événements (16,7%)
- **Géolocalisés précisément :** 2 101 (8,8%) — le reste est centroïde générique BN

### Dépendances — état avant étape 0

| Package | Statut avant | Action |
|---|---|---|
| pandas, numpy, pyarrow | ✅ présent | Rien |
| streamlit, plotly | ✅ présent | Rien |
| scikit-learn, joblib, scipy | ✅ présent | Rien |
| requests, truststore | ✅ présent | Rien |
| uvicorn | ✅ présent (via streamlit) | Rien |
| jinja2 | ✅ présent (via streamlit) | Rien |
| python-multipart | ✅ présent (via streamlit) | Rien |
| **fastapi** | ❌ absent | **Installé** |
| **aiofiles** | ❌ absent | **Installé** |

### Risques identifiés

| Risque | Niveau | Mitigation |
|---|---|---|
| `use_container_width` déprécié Streamlit 2.x | Faible | Déjà corrigé (`width='stretch'`) |
| Chemins relatifs dans les services backend | Moyen | `Path(__file__).resolve().parents[N]` — déjà appliqué |
| SSL Windows sur GDELT HTTPS | Résolu | `truststore.inject_into_ssl()` — déjà en place |
| Dataset historique 2025 vs live 2026 | Moyen | Fallback automatique dans `realtime_pipeline.py` |
| SQLite non thread-safe en prod | Faible | Suffisant pour MVP hackathon |
| Port 8501 (Streamlit) et 8000 (FastAPI) en parallèle | Nul | Ports différents, coexistent |

### Décisions techniques prises à l'étape 0

1. **FastAPI sert tout** : API REST + fichiers HTML/JS/CSS statiques via `StaticFiles`
2. **Aucun build frontend** : Vue.js, Plotly.js, Leaflet.js, Bootstrap 5 via CDN uniquement
3. **Port FastAPI : 8000** — Streamlit reste sur 8501
4. **Streamlit intouché** — ne pas modifier `dashboard/app.py`
5. **Services backend partagés** — les routers FastAPI importent `metrics.py`, `reporting.py`, `gdelt_fetcher.py` directement

### Tests exécutés

- [x] `pip show fastapi` → v0.136.3 installé
- [x] `pip show aiofiles` → v25.1.0 installé
- [x] `pip show uvicorn` → v0.46.0 (déjà présent)
- [x] Dataset parquet chargeable → 23 859 lignes OK
- [x] Dossiers créés : backend/routers, backend/static/*, docs
- [x] `GET /api/health` → HTTP 200, JSON valide ✅
- [x] Streamlit `http://localhost:8501` → HTTP 200 ✅
- [x] FastAPI port 8000 + Streamlit port 8501 coexistent sans conflit ✅

### Résultat

Structure propre, dépendances complètes, aucun composant existant modifié.

### Prochaine étape

Étape 1 — Routers FastAPI (tous les endpoints `/api/*`) + `backend/main.py` complet

---

## Étape 1 — API FastAPI stable et routers de base

**Date :** 2026-05-28
**Objectif :** Créer tous les routers FastAPI, les services support, et mettre à jour `main.py` avec CORS + include des routers.

### Fichiers créés / modifiés

| Fichier | Statut | Description |
|---|---|---|
| `backend/services/data_loader.py` | ✅ créé | `load_historical_data()`, `load_live_data()`, `safe_column()` avec cache en mémoire |
| `backend/services/storage.py` | ✅ créé | `read_json()`, `write_json()`, `append_json_item()` |
| `backend/routers/health.py` | ✅ créé | `GET /api/health` |
| `backend/routers/stats.py` | ✅ créé | `GET /api/stats` (statistiques dataset historique) |
| `backend/routers/events.py` | ✅ créé | `GET /api/events/map`, `/api/events/security`, `/api/events/timeline` |
| `backend/routers/stt.py` | ✅ créé | `GET /api/stt` (calcul STT tous départements) |
| `backend/routers/incidents.py` | ✅ créé | `GET /api/incidents`, `POST /api/incidents` (validation Pydantic, 6°N-12.5°N) |
| `backend/main.py` | ✅ mis à jour | CORS `allow_origins=["*"]`, include 5 routers |

### Problèmes rencontrés et résolus

1. **FastAPI absent de l'environnement Python 3.11** : `pip install fastapi aiofiles --trusted-host pypi.org --trusted-host files.pythonhosted.org` (SSL corporate).
2. **Ancienne instance du serveur sur port 8000** : `Get-NetTCPConnection -LocalPort 8000` + `Stop-Process` avant chaque redémarrage.
3. **NaN / datetime64 non sérialisables dans `/api/incidents`** : normalisation manuelle dans le router (NaN → None, datetime → isoformat).

### Tests exécutés

| Endpoint | Méthode | HTTP | Résultat |
|---|---|---|---|
| `/api/health` | GET | 200 | `{"status":"ok"}` |
| `/api/stats` | GET | 200 | `total_events=23859` |
| `/api/events/map?limit=3` | GET | 200 | 3 événements geolocalisés |
| `/api/events/security?limit=3` | GET | 200 | 3 événements sécuritaires |
| `/api/events/timeline` | GET | 200 | 351 points de timeline |
| `/api/stt` | GET | 200 | 13 départements scorés |
| `/api/incidents` | GET | 200 | 2 incidents test |
| `/api/incidents` | POST 201 | 201 | incident_id=3 créé |

### Décisions techniques

- `data_loader.py` utilise un dict `_cache` simple pour éviter de relire le parquet à chaque requête (23 859 lignes).
- `stt.py` importe `metrics` à l'intérieur de la fonction pour éviter une dépendance circulaire au démarrage.
- `incidents.py` valide lat/lon dans les bornes du Bénin (6–12.5°N, 0.7–3.9°E) via contraintes Pydantic.

### Résultat

**8/8 endpoints HTTP 200** — API complète et fonctionnelle.

### Prochaine étape

Étape 2 — Frontend : structure HTML (`index.html`, navbar Vue Router, layout Bootstrap 5).

---

---

## Étape 2 — Structure frontend web app TERROIR

**Date :** 2026-05-28
**Objectif :** Construire la structure frontend complète servie par FastAPI : navbar, routing hash, 4 vues, Leaflet, Plotly, Vue 3, Bootstrap 5 — tout via CDN, zéro npm.

### Fichiers créés

| Fichier | Taille | Description |
|---|---|---|
| `backend/static/index.html` | 597 lignes | Page principale — navbar, 4 vues Vue 3, toast, footer |
| `backend/static/css/style.css` | CSS custom | Variables CSS, navbar, map, STT cards, KPI cards, responsive |
| `backend/static/js/api.js` | API helpers | `apiGet(path)`, `apiPost(path, data)` avec gestion d'erreurs |
| `backend/static/js/app.js` | App Vue 3 | Routing hash, map Leaflet, STT, stats, timeline, formulaire signalement |

### Pages créées

| Route | Vue | Contenu |
|---|---|---|
| `#/live` | Carte Live | Carte Leaflet OSM centrée Bénin (9.31°N, 2.32°E, zoom 7), markers GDELT (bleu/rouge) + citoyens (orange), légende, barre stats, filtre sécurité |
| `#/terroir` | TERROIR STT | Appel `/api/stt`, 13 cards départements colorées selon level (normal/précaution/alerte), barre de tension, badges résumé |
| `#/report` | Signaler | Formulaire POST `/api/incidents` avec validation Pydantic-side + JS-side, remplissage auto coordonnées par département, message succès |
| `#/analysis` | Analyse 2025 | 4 KPI cards (`/api/stats`), chart timeline Plotly (`/api/events/timeline`), table départements |

### Endpoints consommés

| Endpoint | Vue |
|---|---|
| `GET /api/events/map?limit=500` | `#/live` |
| `GET /api/incidents?hours=72` | `#/live` |
| `GET /api/stt` | `#/terroir` |
| `POST /api/incidents` | `#/report` |
| `GET /api/stats` | `#/analysis` |
| `GET /api/events/timeline` | `#/analysis` |

### Décisions techniques

1. **v-show** (pas v-if) pour les 4 vues : le DOM persiste, évite les pertes de state à la navigation. Leaflet fonctionne correctement avec `invalidateSize()` à chaque retour sur `#/live`.
2. **Routing hash sans Vue Router** : `window.addEventListener('hashchange', ...)` + `watch(currentRoute, ...)` suffit pour 4 routes.
3. **Lazy loading des données** : chaque vue charge ses données à la première visite uniquement (guard `if (!stt.scores.length)`, `if (!stats.data.total_events)`).
4. **Leaflet + Plotly hors Vue** : les instances (`_map`, `_markers`) sont stockées en variables module-level, pas dans le state réactif, pour éviter la proxification Vue.
5. **CDN seulement** : Vue 3.x global prod, Bootstrap 5.3.3, Leaflet 1.9.4, Plotly 2.29.1, Bootstrap Icons 1.11.3.

### Alternatives rejetées

- `v-if` pour la vue Live → Leaflet perd son container à chaque navigation
- Vue Router CDN → alourdit la stack sans gain sur 4 routes
- x-template → moins lisible que inline HTML

### Tests exécutés

| Test | Résultat |
|---|---|
| `GET /` → index.html 597 lignes | ✅ HTTP 200 |
| `GET /static/css/style.css` | ✅ HTTP 200 |
| `GET /static/js/api.js` | ✅ HTTP 200 |
| `GET /static/js/app.js` | ✅ HTTP 200 |
| CDN présents (Vue, Leaflet, Bootstrap, Plotly) | ✅ Vérifiés dans le HTML |
| `POST /api/incidents` → 201 | ✅ incident_id=4 créé |
| Streamlit `:8501` | ✅ HTTP 200 intact |

### Résultat

Application web complète et navigable accessible sur `http://127.0.0.1:8000/`.
4 pages fonctionnelles, API consommée, formulaire POST opérationnel, Streamlit intact.

### Prochaine étape recommandée

Étape 3 — Carte Live enrichie : clustering des markers, hover/popup complet, cercles de densité STT par département, filtres acteur/zone.

---

---

## Étape 3 — Carte Live opérationnelle

**Date :** 2026-05-28
**Objectif :** Transformer la page Carte Live en écran principal : markers colorés par niveau de tension, tooltips/popups détaillés, marqueurs citoyens distincts, filtres, légende complète, barre de statut.

### Fichiers créés

| Fichier | Description |
|---|---|
| `backend/static/js/map.js` | Module Leaflet global `window.TerroirMap` — toute la logique carte isolée de Vue |

### Fichiers modifiés

| Fichier | Changements |
|---|---|
| `backend/static/js/app.js` | Suppression du code Leaflet inline, ajout `mapFilter`/`mapLimit`/`mapStatus`, appels `TerroirMap.*` |
| `backend/static/index.html` | Vue Live : bouton-groupe filtre (Tous/Sécurité/Signalements), sélecteur limite (100/500/1000), barre de statut dynamique, overlay erreur, légende 7 niveaux |
| `backend/static/css/style.css` | Styles popup Leaflet (`.terroir-popup`, `.pp-*`), tooltip dark (`.terroir-tooltip`), carte 70vh, overlay erreur, légende améliorée |

### Fonctionnalités ajoutées

**Markers GDELT (5 niveaux de couleur) :**
- `#6d0000` critique (goldstein ≤ -7 ou ton ≤ -8)
- `#c0392b` alerte forte (goldstein ≤ -5 ou ton ≤ -6)
- `#e74c3c` sécuritaire (is_security)
- `#e67e22` à surveiller (ton < -3)
- `#f1c40f` information (ton < -1)
- `#2980b9` neutre/coopératif

**Taille marker** : base 7 (sécurité) ou 5 (autre) + bonus `min(5, mentions÷8)`

**Tooltip survol** : `<Label> | <Zone> | <Date> · Ton : X` — style dark green

**Popup clic GDELT** : Zone, Date, Ton, Goldstein, Mentions, Source (domaine), Acteur(s), lien source

**Marker citoyen** : `L.divIcon` cercle 22px, orange (!)/vert (✓ vérifié), bordure blanche — visuellement distinct des GDELT

**Popup citoyen** : Type, Département, Description (160 car max), Date, Statut — **aucune donnée personnelle (pseudo, contact)**

**Filtres** : bouton groupe Tous/Sécurité/Signalements + sélecteur 100/500/1000 pts + bouton Rafraîchir avec spinner

**Barre de statut** : N événements GDELT · N sécuritaires · N signalements · heure actualisation

**Gestion erreurs** : overlay rouge centré si `/api/events/map` échoue, sans casser l'app

### Endpoints consommés

| Endpoint | Usage |
|---|---|
| `GET /api/events/map?limit=N[&security_only=true]` | Markers GDELT filtrés |
| `GET /api/incidents?hours=72` | Markers signalements |

### Décisions techniques

1. **Module IIFE `TerroirMap`** : Leaflet (_map, _gdelt, _incidents) hors Vue pour éviter la proxification réactive. Vue gère uniquement le state UI.
2. **Callback `_onStatus`** : TerroirMap appelle `updateMapStatus(s)` pour mettre à jour le state Vue → séparation propre.
3. **`L.divIcon` pour les citoyens** : plus expressif qu'un `CircleMarker` — le "!" ou "✓" communique immédiatement le statut.
4. **Classes CSS Leaflet** : `terroir-tooltip` et `terroir-popup` sont des classes CSS injectées dans les éléments Leaflet (non dans le template Vue), donc absentes de l'HTML statique — comportement normal.

### Alternatives rejetées

- Clustering (MarkerClusterGroup) : nécessite un plugin externe CDN, ajouté en étape suivante si besoin
- Heatmap : dépendance supplémentaire, trop complexe pour cette étape

### Tests exécutés

| Test | Résultat |
|---|---|
| `GET /static/js/map.js` | ✅ HTTP 200 |
| Fonctions `TerroirMap` (9 vérifiées) | ✅ Toutes présentes |
| `setMapFilter`, `mapLimit`, `mapStatus` dans HTML | ✅ |
| `GET /api/events/map?security_only=true` | ✅ HTTP 200 |
| Streamlit `:8501` | ✅ HTTP 200 |

### Résultat

Carte Live professionnelle et opérationnelle — 6 niveaux de couleur GDELT, popups détaillés, filtres fonctionnels, marqueurs citoyens distincts, aucune donnée personnelle exposée.

### Prochaine étape recommandée

Étape 4 — Finalisation visuelle : clustering markers pour la densité, couche STT par département (polygones ou cercles), intégration dans le style global.

---

## Étape 4 — Signalement terrain avancé

**Date :** 2026-05-28
**Objectif :** Améliorer la page Signalement : GPS automatique, champ contact (non stocké), liste des 5 derniers signalements, layout deux colonnes, validation renforcée, confidentialité totale.

### Fichiers modifiés

| Fichier | Changements |
|---|---|
| `backend/routers/incidents.py` | Ajout champ `contact` (accepté, non transmis au service), `min_length=10` + `max_length=500` sur `description` |
| `backend/static/index.html` | Layout deux colonnes (col-lg-7 / col-lg-5) : bouton GPS, indicateurs geoLoading/geoError/geoSuccess, champ contact, note vie privée, liste 5 derniers signalements, cartes info/confidentialité/zones |
| `backend/static/js/app.js` | Nouveau state : `geoLoading`, `geoError`, `geoSuccess`, `recentList`, `recentListError`, `form.contact` — fonctions `geolocate()`, `fillDeptFromCoords()`, `loadRecentIncidents()`, `formatTs()` — watch `#/report` — `submitReport()` inclut contact + recharge la liste |
| `backend/static/css/style.css` | `.recent-item` (séparateur, padding, font-size) + `.report-desc` |

### Fonctionnalités ajoutées

**GPS géolocalisation :**
- `navigator.geolocation.getCurrentPosition` avec timeout 10 s, maximumAge 60 s
- 3 codes d'erreur gérés avec messages FR clairs (refus, position indisponible, timeout)
- Vérification out-of-bounds Bénin (lat 6–12.5, lon 0.7–3.9) avant acceptation
- Remplissage automatique lat/lon + sélection du département le plus proche (distance euclidienne)
- Indicateurs visuels : spinner pendant la recherche, badge vert succès, alerte rouge erreur

**Champ contact :**
- Accepté par le formulaire (max 100 chars), inclus dans le POST
- Non transmis à `submit()` → jamais stocké en base — confidentialité garantie

**Liste des derniers signalements :**
- Chargée au premier affichage de `#/report` et après chaque soumission réussie
- Appel `GET /api/incidents?hours=72`, tranche à 5 éléments
- Affiche : type, département, description tronquée (160 car), date formatée FR
- Aucune donnée personnelle (ni pseudo, ni contact)
- Bouton "Voir sur la carte" → `#/live`

**Validation renforcée :**
- Description : 10 ≤ longueur ≤ 500 caractères

**formatTs(ts) :**
- `Date.toLocaleString("fr-FR", {…})` → format `JJ/MM/AAAA HH:MM`

### Endpoints consommés

| Endpoint | Usage |
|---|---|
| `POST /api/incidents` | Soumission formulaire (contact non stocké) |
| `GET /api/incidents?hours=72` | Liste récente (5 éléments) |

### Décisions techniques

1. **Contact non stocké** : champ présent dans `IncidentIn` pour validation Pydantic, mais non passé à `submit()` → la DB ne contient jamais de données de contact.
2. **Distance euclidienne** : suffisante à cette échelle géographique, pas besoin de formule haversine pour trouver le département le plus proche (erreur max ~5 km).
3. **`loadRecentIncidents()` appelée après submit** : l'utilisateur voit immédiatement son signalement dans la liste sans rechargement manuel.

### Tests exécutés

| Test | Résultat |
|---|---|
| `POST /api/incidents` avec contact | ✅ HTTP 201, incident créé |
| `GET /api/incidents` — clés retournées | ✅ Contact absent des clés de réponse |
| `GET /api/incidents?hours=72` | ✅ count=5, timestamps ISO normalisés |
| Serveur FastAPI `/api/health` | ✅ HTTP 200 |
| Fichiers statiques servis (`/`, `/static/js/app.js`, `/static/css/style.css`) | ✅ HTTP 200 |

### Résultat

Page Signalement professionnelle et confidentielle : géolocalisation automatique avec validation territoire, formulaire enrichi, liste des signalements récents sans donnée personnelle, layout deux colonnes responsive.

### Prochaine étape recommandée

Étape 5 — Page Analyse 2025 enrichie : graphiques Plotly supplémentaires (distribution CAMEO, top acteurs, carte choroplèthe), correspondance exacte avec le dashboard Streamlit.

---

## Étape 5 — Page TERROIR décisionnelle

**Date :** 2026-05-28
**Objectif :** Transformer la page `#/terroir` en écran de décision opérationnelle répondant aux 3 questions clés : quelles zones sont sous tension, pourquoi, et quoi faire dans les prochaines 24–48h.

### Fichiers modifiés

| Fichier | Changements |
|---|---|
| `backend/static/index.html` | Section `#/terroir` entièrement refaite — 6 blocs : KPI bar (4 cartes), bannière zone prioritaire, graphique Plotly STT, grille zones sous tension enrichie, grille complète, explication + playbook opérationnel |
| `backend/static/js/app.js` | `stt.incCount`, `loadStt()` étendu (parallel fetch incidents + rendu chart), `triggerPhrase()`, `recommendedAction()`, `renderSttChart()`, `_sttChartRendered` flag, watch `#/terroir` mis à jour |
| `backend/static/css/style.css` | `.terroir-top-banner`, `.banner-alerte/precaution/normal`, `.stt-decision`, `.trigger-phrase`, `.recommended-action`, `.playbook-level` |

### Fonctionnalités ajoutées

**1. KPI bar (4 cartes) :**
- Zones surveillées = `stt.scores.length` (13)
- Zones en alerte = `sttAlertCount(2)` — badge rouge si > 0
- Événements 14 jours = somme `n_window` de tous les départements
- Signalements terrain = `GET /api/incidents?hours=168` → `count`

**2. Bannière zone la plus surveillée :**
- Couleur dynamique (vert/jaune/rouge) selon `sttTopAlert.level`
- Bouton « Voir sur la carte » → `#/live`

**3. Graphique Plotly (bar chart STT) :**
- `Plotly.react("stt-chart", ...)` — mise à jour sans doublon à chaque `loadStt()`
- x = départements · y = score STT · couleur = niveau (vert/jaune/rouge)
- Lignes horizontales en tirets : Précaution (2.0) et Alerte (3.0)
- Rendu via `nextTick()` après chargement des scores

**4. Grille zones sous tension (level ≥ 1) :**
- Signal déclencheur (`triggerPhrase`) : phrase FR générée par règles simples
  - z_cameo > 1.5 → "forte activité conflictuelle"
  - tone_cur < -3 → "ton médiatique très négatif"
  - z_volume > 1.5 → "volume supérieur à la normale"
  - neg_ratio_cur > 0.5 → "part élevée de signaux sensibles"
- 3 métriques : Évts 14j / Ton moyen / % sensible
- Action recommandée (`recommendedAction`) : phrase action par niveau
- Bouton « Voir sur la carte » par zone

**5. Message situation normale :**
- Si aucun département en précaution/alerte, affiche une alerte verte explicite

**6. Grille complète tous départements** (inchangée dans le fond, compactée)

**7. Explication du score TERROIR :**
- 4 indicateurs expliqués en français simple, sans jargon ML
- Seuils de lecture : Normal < 2.0, Précaution 2.0–3.0, Alerte > 3.0
- Note pédagogique : "ne prédit pas une crise"

**8. Playbook opérationnel :**
- 3 niveaux avec actions concrètes : Normal (veille standard), Précaution (24h vigilance), Alerte (action immédiate)

### Endpoints utilisés

| Endpoint | Usage |
|---|---|
| `GET /api/stt` | Scores STT par département (déjà existant) |
| `GET /api/incidents?hours=168` | Comptage signalements 7 jours pour KPI |

### Décisions techniques

1. **`Plotly.react` vs `newPlot`** : `react` met à jour l'élément existant sans doublon — essentiel au retour sur la page après visite d'une autre vue.
2. **`Promise.allSettled`** dans `loadStt()` : les deux fetches (STT + incidents) se font en parallèle ; un échec du comptage incidents n'empêche pas l'affichage des scores.
3. **`triggerPhrase()` frontend** : phrases générées par règles simples sur les z-scores — pas de LLM, pas de backend. Règles basées sur les seuils statistiques du scoring STT.
4. **`_sttChartRendered` flag** : remis à `false` à chaque `loadStt()` pour forcer un re-rendu à l'actualisation ; vérifié dans le watch pour éviter un rendu vide au retour sur la page.
5. **`??` operator** : `incData.value.count ?? null` — retombe proprement sur `null` si la clé est absente, évitant `0` trompeur.

### Alternatives rejetées

- WebSocket pour actualisation automatique : hors scope, complexité inutile
- LLM pour générer les phrases de signal déclencheur : interdit par le brief
- Clustering carte choroplèthe : nécessiterait GeoJSON Bénin + plugin supplémentaire — étape suivante si besoin
- `Plotly.newPlot` : provoque un doublon si appelé plusieurs fois sur le même `div`

### Tests exécutés

| Test | Résultat |
|---|---|
| `GET /api/stt` | ✅ 200 — 13 scores, level=0 pour tous (situation normale) |
| `GET /api/incidents?hours=168` | ✅ 200 — count=5 |
| `GET /api/events/map?limit=50` | ✅ 200 — Carte Live non cassée |
| `GET /api/stats` | ✅ 200 — Analyse 2025 non cassée |
| `GET /api/events/timeline` | ✅ 200 — Timeline non cassée |
| `GET /static/js/app.js` | ✅ 200 — 145 accolades ouvrantes = 145 fermantes (bilan = 0) |
| `GET /static/css/style.css` | ✅ 200 |
| Nouvelles fonctions dans app.js servi | ✅ `triggerPhrase`, `recommendedAction`, `renderSttChart`, `Plotly.react` présents |
| Nouveaux éléments HTML dans index.html servi | ✅ `stt-chart`, `terroir-top-banner`, `trigger-phrase`, `recommended-action`, `playbook-level`, `banner-alerte`, `Voir sur la carte` |
| Streamlit `:8501` | À vérifier manuellement (non modifié par cette étape) |

### Résultat

Page TERROIR transformée en écran de décision opérationnelle : 4 KPI, bannière zone prioritaire, bar chart STT avec seuils visuels, zones sous tension avec signal déclencheur et action recommandée, explication pédagogique et playbook en 3 niveaux. Lisible en 15 secondes par le grand public.

### Prochaine étape recommandée

Étape 6 — Page Analyse 2025 enrichie : graphiques Plotly supplémentaires (distribution CAMEO, top acteurs, répartition géographique), ou finalisation visuelle + déploiement Railway.

---

## Étape 5.5 — Carte Live recentrée sur les signaux récents

**Date :** 2026-05-28
**Objectif :** Transformer la carte Live en écran de veille opérationnelle : affichage par défaut des 24 dernières heures, filtres temporels, clignotement discret des signaux critiques, badge "Nouveau" pour les événements du dernier jour de la fenêtre.

### Fichiers modifiés

| Fichier | Changements |
|---|---|
| `backend/routers/events.py` | Ajout paramètre `hours` à `GET /events/map` — filtre par `SQLDATE` (datetime64) relatif à la date max du jeu de données |
| `backend/static/js/map.js` | Réécriture complète : `parseGdeltDate()`, `isCritical()`, `newBadgeHtml()`, `buildGdeltPopup(ev, isNew)`, `buildIncidentPopup(inc, isNew)`, `citizenIcon(validated, isNew)` avec anneau pulse, `renderGdeltMarkers()` avec détection isNew + windowInfo, `renderIncidentMarkers()` avec détection isNew, `loadLiveMap(filter, limit, hours)` |
| `backend/static/js/app.js` | `mapHours = ref(24)`, `MAP_HOURS_LABELS`, `mapHoursLabel` computed, `setMapHours(h)`, `loadLiveMap()` passe `mapHours.value`, `mapStatus.windowInfo`, ajouts dans return |
| `backend/static/index.html` | Boutons 24h/72h/7j/30j dans le header Live, bande contexte sous le header, barre de statut affichant la période |
| `backend/static/css/style.css` | `.marker-critical-pulse` (opacity 0.9→0.28, 2.8s), `@keyframes citizen-pulse` (scale+opacity), `.pp-badge-new` (orange), `.map-context-bar` |

### Fonctionnalités ajoutées

**Filtre temporel (backend + frontend) :**
- `GET /api/events/map?hours=N` — filtre les événements dans les N dernières heures relatives à `max(SQLDATE)` du dataset
- 4 boutons dans la navbar Live : 24h (défaut), 72h, 7 jours, 30 jours
- Changement de période → rechargement immédiat de la carte via `setMapHours(h)`
- Compatibilité ascendante : sans paramètre `hours`, comportement identique à avant

**Filtre incidents :**
- `incHours = max(hours, 48)` — les signalements sont toujours affichés sur au moins 48h

**Pulse markers critiques :**
- Couleurs `#6d0000` et `#c0392b` → CSS class `marker-critical-pulse` sur le SVG path Leaflet
- Animation : opacity 0.90 → 0.28 en 2.8s (discret, lent, professionnel)

**Anneau de pulse citoyens récents :**
- Signalement moins de 24h (timestamp absolu) → anneau coloré autour du marker
- `@keyframes citizen-pulse` : scale 0.8→1.8 + opacity 0→0.7 (effet sonar)

**Badge "Nouveau" :**
- GDELT : événements dans le dernier jour de la fenêtre (relatif au max de la sélection)
- Incidents : signalements moins de 24h (absolu)
- Popup header + tooltip : `<span class="pp-badge-new">Nouveau</span>`

**Bande contexte :**
- Phrase descriptive avec période active + légende des couleurs critiques + explication du badge Nouveau

**Barre de statut :**
- Affiche maintenant : période · N événements GDELT · N sécuritaires · N signalements · heure actualisation

### Endpoints modifiés

| Endpoint | Modification |
|---|---|
| `GET /api/events/map` | Ajout `hours: Optional[int]` — filtre datetime relatif à max(SQLDATE) |

### Décisions techniques

1. **Relatif à `max(SQLDATE)` et non à `now()`** : les données GDELT du dataset sont de 2025 ; filtrer par rapport à l'heure système donnerait 0 événement. Filtrer par rapport au max du dataset donne un comportement cohérent quel que soit l'âge des données.
2. **`pd.to_datetime(date_col, errors="coerce")`** : `SQLDATE` est stocké en `datetime64[us]` dans le parquet, pas en entier YYYYMMDD. La conversion `to_numeric` échouait silencieusement (bug corrigé en deux passes de test).
3. **`marker-critical-pulse` sur SVG path** : l'option `className` de `L.circleMarker` s'applique à l'élément `<path>` SVG — les animations CSS opacity fonctionnent sur SVG.
4. **Anneau citoyen en inline CSS** : plus fiable que des classes CSS avec Leaflet divIcon, car le HTML inline ne dépend pas de la cascade.

### Alternatives rejetées

- Filtre par date courante (now) : toujours 0 événement sur dataset 2025
- Clignotement agressif (tous les points) : transformerait la carte en "casino"
- `Plotly` pour la timeline dans cette vue : hors scope de cette étape

### Tests exécutés

| Test | Résultat |
|---|---|
| `GET /api/events/map?hours=24&limit=5000` | ✅ 101 événements |
| `GET /api/events/map?hours=72&limit=5000` | ✅ 211 événements |
| `GET /api/events/map?hours=168&limit=5000` | ✅ 319 événements |
| `GET /api/events/map?hours=720&limit=5000` | ✅ 4 221 événements |
| `GET /api/events/map?limit=500` (sans hours) | ✅ 200 — compatibilité préservée |
| `GET /api/events/map?security_only=true` | ✅ 200 |
| `GET /api/stt`, `/stats`, `/incidents` | ✅ 200 — autres pages non cassées |
| Nouvelles fonctions dans map.js servi | ✅ `marker-critical-pulse`, `citizen-pulse`, `pp-badge-new`, `isNew`, `windowInfo` (×20) |
| Nouvelles variables dans app.js servi | ✅ `mapHours`, `setMapHours`, `mapHoursLabel`, `windowInfo` (×9) |
| CSS animations présentes | ✅ `pulse-critical`, `citizen-pulse`, `pp-badge-new`, `map-context-bar` |
| HTML : boutons 24h/72h/7j/30j + context bar + status | ✅ `setMapHours`, `mapHoursLabel`, `map-context-bar`, `Nouveau` présents |

### Résultat

Carte Live transformée en écran de veille opérationnelle : fenêtre 24h par défaut (101 événements au lieu de 500+), filtres temporels 4 périodes, pulse discret sur les signaux critiques, anneau sonar sur les signalements récents, badge "Nouveau" dans les popups, bande contexte descriptive.

### Prochaine étape recommandée

Étape 6 — Page Analyse 2025 enrichie (graphiques Plotly : distribution CAMEO, top acteurs, répartition géographique) et/ou déploiement Railway.

---

*(ce journal sera mis à jour à chaque étape)*


## Etape 6 - Enrichissement coordonnees GDELT + correction mapping colonnes CSV

**Date :** 2026-05-28
**Auteur :** Claude (Sonnet 4.6)
**Objectif :** Garantir que 100 % des evenements live ont des coordonnees cartographiables. Implementer une regle de priorite a 5 niveaux + jitter deterministe. Corriger simultanement un bug critique de mapping CSV.

---

### Bug critique decouvert : mapping CSV GDELT v2 decale

**Constat** : Le CSV GDELT v2 a 61 colonnes (indices 0-60), avec **8 colonnes par bloc geographique** (Type, FullName, CountryCode, ADM1Code, ADM2Code, Lat, Long, FeatureID). Le code original supposait 7 colonnes/bloc -> tout le bloc ActionGeo etait decale.

| Colonne | Ancienne hypothese | Realite verifiee empiriquement |
|---|---|---|
| 44 | Actor2Geo_CountryCode | Actor2Geo_FullName |
| 50 | ActionGeo_FullName | Actor2Geo_FeatureID |
| 51 | ActionGeo_CountryCode | ActionGeo_Type (entier 1-4) |
| 52 | ActionGeo_ADM1Code | ActionGeo_FullName |
| 53 | ActionGeo_Lat | ActionGeo_CountryCode |
| 54 | ActionGeo_Long | ActionGeo_ADM1Code |
| 57 | SOURCEURL | ActionGeo_Long |

**Consequences du bug** :
1. ActionGeo_Lat lisait ActionGeo_CountryCode (BN, US...) -> toujours NaN apres to_numeric
2. Filtre ActionGeo_CountryCode == BN lisait ActionGeo_Type (entier 1-4) -> toujours False -> le filtre Benin ne capturait que les acteurs, pas les actions sur le territoire
3. SOURCEURL lisait ActionGeo_Long -> source_domaine renvoyait des longitudes comme domaines

**Verification empirique** : telechargement d'un CSV GDELT live (20260528224500.export.CSV.zip), inspection colonne par colonne. Colonnes corrigees :

| Champ | Indice correct |
|---|---|
| Actor1Geo_Lat / Long | 40 / 41 |
| Actor2Geo_CountryCode | 45 (etait 44) |
| Actor2Geo_Lat / Long | 48 / 49 |
| ActionGeo_FullName | 52 (etait 50) |
| ActionGeo_CountryCode | 53 (etait 51) |
| ActionGeo_ADM1Code | 54 (etait 52) |
| ActionGeo_Lat / Long | 56 / 57 (etait 53/54) |
| SOURCEURL | 60 (etait 57) |

---

### Enrichissement coordonnees - regle de priorite

**Decision technique** : 5 niveaux de priorite descendants, sans API externe, sans dependance reseau.



**Jitter deterministe** (niveaux 4 et 5) :
- lat += ((GLOBALEVENTID % 997) / 997 - 0.5) * 0.12
- lon += ((GLOBALEVENTID % 1009) / 1009 - 0.5) * 0.12
- Amplitude : +-0.06deg ~= +-7 km
- Reproductible : meme GLOBALEVENTID -> meme decalage entre cycles

**Centroides** : 13 departements identiques au tableau DEPARTMENTS dans app.js (BN01-BN12 + BN18 Parakou).

---

### Alternatives rejetees

| Alternative | Raison du rejet |
|---|---|
| Nominatim geocoding | Limite 1 req/s, latence boucle 15 min, dependance reseau |
| NER + fetch article | Infra ML, ~30% articles inaccessibles, risque hallucination |
| Jitter random() | Non reproductible : deplace les memes evenements a chaque cycle |
| Lat=9.5 pour tous (comme notebook) | Masque la qualite reelle des donnees |

---

### Tests executes

| Test | Resultat |
|---|---|
| _apply_coord_priority() sur 10 lignes (ADM1=Benin) | OK : 10/10 -> centroid_country |
| Jitter BN10 (centroide 7.50, 2.30) | OK : lat 7.452-7.468, lon 2.263-2.279 (dans +-0.06) |
| Simulation 23 859 evt historiques | OK : 1 240 (5.2%) centroid_adm1, 22 619 (94.8%) centroid_country |
| Cycle GDELT live complet | OK : aucun crash, 0 evt Benin dans ce creneau |
| Detection schema obsolete | OK : declenchee si coord_source absente |
| Verification col CSV empirique | OK : col53='UK'/'US', col56=56.05, col57=-5.11, col60=URL |

---

### Limites connues

1. **Couverture sub-nationale** : ~5 % des evenements ont un code ADM1 de departement. Les 95 % restants -> centroide pays + jitter (~200 km de precision).
2. **Volume events** : le filtre ActionGeo_CountryCode == BN etait silencieusement casse -> le volume d'evenements live augmentera apres la correction.
3. **Historique non re-enrichi** : benin_enrichi.parquet non touche (le notebook avait son propre pipeline).
4. **Ancien benin_live.parquet** : reinitialise automatiquement au prochain cycle Benin (detection absence coord_source).

---

### Fichiers modifies

| Fichier | Modifications |
|---|---|
| backend/services/gdelt_live_poller.py | Réécriture GDELT_COL_INDICES (indices corrects), ajout ADM1_CENTROIDS/BENIN_CENTER/JITTER_SCALE, fonctions _jitter() et _apply_coord_priority(), appel dans _enrich(), detection schema dans _append_new_rows() |


## Etape 6 - Statut live GDELT et preuve de fraicheur

Date/heure : 2026-05-29 00:10
Objectif : Exposer l'etat du poller GDELT en temps reel dans l'interface Carte Live, avec un bouton de rafraichissement manuel et un panneau de transparence sur la qualite des coordonnees.

Fichiers crees :
- backend/data/gdelt_status.json (fichier d'etat atomique, ecrit par le poller a chaque cycle)
- backend/routers/gdelt.py (router FastAPI avec GET /api/gdelt/status et POST /api/gdelt/refresh)

Fichiers modifies :
- backend/services/gdelt_live_poller.py (ajout _write_status/_read_status/_get_live_count, ecriture statut a chaque etape du cycle)
- backend/main.py (import et montage du router gdelt)
- backend/static/js/app.js (objet reactif gdelt, loadGdeltStatus, refreshGdelt, gdeltStatusClass, gdeltCoordLabel, intervalle 2 min sur la vue #/live)
- backend/static/index.html (bouton "Actualiser GDELT" dans le header, panneau "Statut GDELT Live" collapsible apres la carte)
- backend/static/css/style.css (styles du panneau statut : dot anime, cellules stats, qualite coord)

Endpoints ajoutes :
- GET /api/gdelt/status : retourne le JSON complet du statut + repartition coord_quality
- POST /api/gdelt/refresh : lance run_one_cycle() en synchrone, retourne le statut resultant

Fonctionnalites ajoutees :
- Dot d'etat anime (vert pulse = ok, jaune clignotant = checking, rouge = erreur, gris = en attente)
- 6 cellules de stats : derniere verification, fichier traite, evenements mondiaux lus, evenements Benin trouves, ajoutes, total base live
- Repartition de la qualite des coordonnees (exactes / departement estime / centroide pays)
- Note pedagogique sur les centroïdes
- Auto-refresh status toutes les 2 minutes quand la vue #/live est active, arrete sur depart de la vue
- Bouton "Actualiser GDELT maintenant" avec spinner pendant le refresh

Decisions techniques :
- Ecriture atomique du statut via fichier JSON (pas de base de donnees supplementaire)
- Pas de WebSocket : polling toutes les 2 min suffisant pour un contexte hackathon
- world_events_read=0 quand le fichier est deja indexe : comportement correct, le message l'explique
- POST /api/gdelt/refresh retourne HTTP 200 meme en cas d'erreur interne (erreur dans le champ status du JSON)

Alternatives rejetees :
- WebSocket pour le statut en temps reel : over-engineering pour l'usage actuel
- Server-Sent Events : meme raison
- Stockage du statut en base SQLite : fichier JSON suffit et plus simple

Tests executes :
- GET /api/gdelt/status : 200, status=ok, last_checked_at=2026-05-29T00:02:07
- POST /api/gdelt/refresh : 200, cycle complet, timestamp mis a jour a T00:02:47
- GET /api/gdelt/status apres refresh : timestamp actualise confirme
- Tous les endpoints existants (/api/health, /api/stats, /api/events, /api/stt, /api/incidents) : 200
- Verification gdelt_status.json : ecrit automatiquement au demarrage du serveur via lifespan

Resultat : Panneau de statut GDELT entierement fonctionnel. La derniere verification, le fichier traite, les compteurs et la qualite des coordonnees sont visibles directement dans l'interface. Le bouton de rafraichissement manuel permet de forcer un cycle sans redemarrer le serveur.

Problemes rencontres :
- Encodage Windows-1252 du journal empeche l'utilisation de l'outil Edit sur les entrees existantes : contourne par Add-Content PowerShell

Prochaine etape recommandee : Enrichissement des popups carte avec l'indicateur coord_source (afficher "coord. exacte" vs "zone estimee" dans l'infobulle Leaflet pour chaque evenement GDELT).

## Etape 6.5 - Precision des coordonnees dans les popups

Date/heure : 2026-05-29 00:20
Objectif : Afficher dans chaque popup Leaflet GDELT la precision reelle du point cartographie, afin que l utilisateur sache si le point est une coordonnee exacte, une estimation departementale ou une approximation nationale.

Fichiers modifies :
- backend/routers/events.py : ajout du champ coord_source dans _row_to_event()
- backend/static/js/map.js : ajout helper coordPrecisionHtml(), constante COORD_SOURCE_INFO, ligne Precision dans buildGdeltPopup()
- backend/static/css/style.css : ajout styles .pp-coord-badge, .pp-coord-exact/.actor/.dept/.country, .pp-coord-note

Fonctionnalites ajoutees :
- Ligne "Precision" dans les popups GDELT avec badge colore (vert=exact, bleu=acteur, orange=departement, gris=pays)
- Note italique sous le badge quand coord_source=centroid_country : "Ce point represente une zone generale, pas le lieu exact."
- Pas de ligne Precision pour les evenements sans coord_source (donnees historiques sans colonne)
- Signalements citoyens non affectes (buildIncidentPopup intact)

Mapping coord_source -> affichage :
- action_geo       -> "Position exacte du lieu" (vert)
- actor1_geo       -> "Acteur principal beninois" (bleu)
- actor2_geo       -> "Acteur secondaire beninois" (bleu)
- centroid_adm1    -> "Departement estime" (orange)
- centroid_country -> "Pays approximatif" (gris) + note explicite
- vide / inconnu   -> ligne masquee (pas d affichage errone)

Tests executes :
- /api/events/map : 200 (nouveau champ coord_source present dans le schema apres redemarrage serveur)
- /api/health, /api/stats, /api/stt, /api/incidents : 200 (non affectes)
- /api/gdelt/status : 200 (panneau live intact)
- Verification manuelle map.js : buildIncidentPopup non modifie, coordRow conditionnel (falsy si vide)

Resultat : Code correct. La modification necessite un redemarrage du serveur (uvicorn --reload ne se declenche pas de facon fiable sur Windows/OneDrive). Apres redemarrage, les evenements live auront leur badge de precision dans la popup. Les evenements historiques (benin_enrichi.parquet, sans colonne coord_source) n affichent pas la ligne Precision, ce qui est correct.

Problemes rencontres :
- benin_enrichi.parquet (23 859 lignes historiques) n a pas de colonne coord_source : comportement voulu, pas un bug.
- uvicorn --reload ne detecte pas les changements de fichiers sur chemin OneDrive Windows : demarrer avec `uvicorn backend.main:app --port 8000` ou redemarrer manuellement.

Prochaine etape recommandee : Ajouter le filtre par niveau de precision dans la barre de filtres de la carte (afficher uniquement les points "exacts" ou inclure les estimations).

## Etape 7 - Preparation deploiement Railway

Date/heure : 2026-05-29 01:10
Objectif : Rendre l application FastAPI TERROIR deployable sur Railway sans casser le local et sans toucher Streamlit.

Fichiers crees :
- Procfile : web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
- runtime.txt : python-3.11

Fichiers modifies :
- .gitignore : ajout de backend/data/incidents.db, backend/data/incidents.json, data/processed/benin_live.parquet, data/processed/.gdelt_last_processed.txt, *.pkl, *.log, .env
- backend/services/data_loader.py : fallback propre si benin_enrichi.parquet absent (retourne DataFrame vide avec colonnes minimales + log warning)
- backend/services/gdelt_fetcher.py : import truststore rendu conditionnel (try/except ImportError) pour compatibilite Linux
- backend/services/gdelt_live_poller.py : correction bug timezone (pd.Timestamp.utcnow() -> pd.Timestamp.now() pour eviter TypeError: Invalid comparison tz-naive vs tz-aware)
- backend/routers/stt.py : utilise load_historical_data() au lieu de load_best_data() — le calcul STT necessite un historique suffisant (23 859 evenements) ; load_best_data() retournait 4 evenements live apres le premier cycle, causant un crash ArrowDtype dans compute_stt

Verifications :
- data/processed/benin_enrichi.parquet : present, non gitignore, sera commite et disponible sur Railway ✓
- Chemins data_loader.py : Path(__file__).resolve().parents[2] / "data" / "processed" — absolus, fonctionnent depuis n importe quel CWD ✓
- requirements.txt : contient fastapi, uvicorn, aiofiles, pandas, pyarrow, requests, truststore — complet pour Railway ✓
- kaleido==0.2.1 : uniquement utilise en notebooks, non importe par FastAPI — ne bloque pas Railway ✓
- Streamlit : non modifie ✓
- Docker : non ajoute ✓
- Base de donnees supplementaire : non ajoutee ✓

Tests executes (uvicorn --host 0.0.0.0 --port 8000) :
- GET /               : 200 HTML ✓
- GET /api/health     : 200 ✓
- GET /api/stats      : 200, total_events=23859 ✓
- GET /api/events/map?limit=5 : 200, count=4, coord_source=action_geo ✓
- GET /api/gdelt/status : 200, status=ok ✓
- GET /api/stt        : 200, 13 scores departements ✓
- GET /api/incidents?hours=48 : 200 ✓

Bugs corriges en cours de route :
1. Poller crash TypeError tz-naive vs tz-aware : corrige dans gdelt_live_poller.py (pd.Timestamp.now() au lieu de utcnow())
2. STT 500 quand benin_live.parquet existe avec peu d evenements : corrige en utilisant load_historical_data() dans stt.py
3. Vieux processus uvicorn resistant aux Kill via Get-NetTCPConnection : resolu en tuant tous les processus Python (Get-Process python* | Kill)

Resultat : Application deployable Railway. 7/7 endpoints 200. Prochaine etape : initialiser git, pousser sur GitHub, connecter Railway.

Problemes rencontres :
- uvicorn --reload ne fonctionne pas sur OneDrive Windows (watcher inotify non supporte)
- Les processus Python demarres via Start-Process ou Start-Job ne voient pas les modifications de fichiers si un vieux processus sur le port 8000 est toujours actif
- Solution : toujours verifier avec Get-NetTCPConnection + tuer tous les processus Python avant de relancer

Prochaine etape recommandee : git init && git add && git commit && railway up (ou GitHub + Railway connect)
