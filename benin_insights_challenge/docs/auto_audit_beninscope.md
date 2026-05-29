# AUTO-AUDIT — BeninScope / TERROIR
## Audit critique du projet · BeninScope · 29 mai 2026

---

> **Méthode :** audit réalisé après lecture complète du code source (FastAPI, Vue.js, Streamlit, poller GDELT, STT, reporting, data_loader, routers). Les observations sont basées sur ce qui existe réellement dans le repo, pas sur ce qui est décrit.

---

## 1. Est-ce que le projet est utile ?

### Oui, et pour de vraies raisons

- Le Bénin fait face à une pression sécuritaire croissante au nord (Borgou, Alibori, Atacora). Le projet couvre une vraie zone de tension réelle, documentée, d'actualité.
- Il n'existe **aucun outil gratuit, open-source et en temps quasi-réel** pour la veille sécuritaire sub-nationale au Bénin. ACLED existe mais coûte cher et n'a pas de scoring territorial automatisé.
- Le workflow complet — GDELT → filtre → enrichissement → API → carte → scoring — tient en un seul déploiement local. Un opérateur sur le terrain peut l'utiliser avec une connexion internet basique.
- Le formulaire de signalement citoyen avec GPS, statut non-vérifié / validé, et playbook de réponse est **directement utilisable** par une ONG ou une préfecture.

### Non, ou pas encore, pour ces raisons

- La fenêtre de données live est pour l'instant d'**1 événement** (28 mai 2026). La carte est vide en pratique.
- Le STT calculé sur des données 2025 avec une référence temporelle en mai 2026 produit **des scores tous à 0** (voir section 7). La fonctionnalité principale est silencieusement cassée.
- Sans réseau de signalants terrain, le formulaire citoyen reste vide. La boucle GDELT + citoyen n'existe que sur le papier pour l'instant.

### Qui l'utiliserait vraiment

| Profil | Intérêt | Condition |
|---|---|---|
| ONG humanitaire présente au nord-Bénin | Fort | Si le STT est fiable et les données à jour |
| Journaliste d'investigation | Moyen | Pour croiser avec ses sources terrain |
| Coordinateur sécurité entreprise | Fort | Pour les zones Borgou / Atacora / Alibori |
| Préfecture ou collectivité locale | Possible | Seulement si validé par une autorité |
| Grand public | Faible | Interface trop technique, pas de contexte narratif |

---

## 2. Est-ce que ça ressemble encore à un dashboard académique ?

### Ce qui évite l'effet étudiant

- **L'application web est propre.** Vue 3 + Bootstrap 5 + Leaflet rendu correctement, sans Streamlit visible. L'interface ressemble à un vrai produit.
- **Le playbook de réponse** (Normal / Précaution / Alerte → actions recommandées) est un élément de produit mature. Un jury voit ça et comprend que quelqu'un a pensé à l'utilisateur final.
- **Le panneau de statut GDELT** (world_events_read, benin_events_found, benin_events_added, coord_quality) est de la transparence opérationnelle réelle. Pas un graphe de plus.
- **L'explication honnête du score** dans le frontend ("le score ne prédit pas une crise") évite le piège du discours prédictif infondé.
- **L'architecture à deux couches** (GDELT macro + signalements micro) est un vrai choix de design produit, pas un notebook enrichi.

### Ce qui y ressemble encore

- Il y a **deux interfaces** (FastAPI Vue + Streamlit). C'est le signe classique d'un projet qui a changé de direction en cours de route sans nettoyer.
- Le lien `http://localhost:8501` dans le footer du site est resté. En démo, c'est un lien mort.
- La vue "Analyse 2025" dans le frontend est peu interactive — juste KPI et timeline. Ça ressemble à un slide de présentation mis en page web.
- **Le STT est recalculé à chaque requête** sans cache HTTP. Dans un vrai produit, ce score serait précalculé toutes les 15 min et servi en lecture seule.

---

## 3. Ce qui impressionnera probablement le jury

**Par ordre d'impact probable :**

1. **L'architecture live réelle** — un poller GDELT qui tourne, qui filtre le Bénin, qui enrichit, qui déduplique, qui stocke. Ce n'est pas simulé. Le panneau de statut GDELT le prouve en temps réel.

2. **La transparence géographique** — afficher explicitement "91% de centroïdes génériques" et expliquer comment les signalements citoyens compensent ce déficit. C'est honnête et différenciant. La plupart des projets GDELT cachent ça.

3. **Le formulaire citoyen avec GPS** — bouton "Ma position actuelle", validation en temps réel des coordonnées, affichage sur la carte avec statut non-vérifié / validé. C'est concret.

4. **Le STT avec playbook** — si le bug de la ref_date est corrigé (voir section 7), montrer un score vivant par département avec des recommandations d'action claires impressionne. C'est ce que les outils concurrents ne font pas.

5. **Le workflow décrit en une phrase** — "GDELT → filtre → enrichissement → API → carte → STT → recommandation → signalement citoyen". C'est lisible, propre, défendable.

---

## 4. Ce qui peut faire perdre des points

### Critique

| Problème | Impact |
|---|---|
| **STT scores tous à 0** (bug ref_date) | Le cœur du produit semble ne pas fonctionner |
| **`_read_status` absent du poller** | `ImportError` au démarrage → crash du router `/api/gdelt` |
| **Carte vide** avec filtre 24h et 1 événement live | Premier écran = rien à voir |

### Important

| Problème | Impact |
|---|---|
| Lien `localhost:8501` dans le footer | Lien mort en démo = manque de finition |
| Deux frontends (Vue + Streamlit) | Confusion, double maintenance, signal "prototype" |
| Pas d'authentification sur l'API | N'importe qui peut inonder `/api/incidents` de faux signalements |
| Aucune donnée jan–mai 2026 dans le live | Gap de 5 mois = crédibilité temporelle fragile |

### Visible mais acceptable

| Problème | Contexte |
|---|---|
| Bounding boxes approximatives pour la géolocalisation inverse | Connu, documenté, compensé par les signalements |
| SQLite sans WAL ni backup | Hackathon, pas de production |
| Cache mémoire sans TTL dans `data_loader.py` | Ne pose problème qu'après plusieurs heures de serveur |
| Deux fonctions d'enrichissement légèrement différentes | Dette technique, pas un crash |

---

## 5. Ce qui semble "hackathon"

- **`init_db()` appelé à l'import du module** (`reporting.py`, ligne 163). En production, une connexion DB ne s'ouvre pas au chargement du module.
- **Cache mémoire global** (`_cache: dict = {}` dans `data_loader.py`) sans invalidation, sans TTL. Ça fonctionne mais c'est un raccourci visible.
- **Deux systèmes d'enrichissement** coexistent : `_enrich()` dans le poller et `enrich()` dans `realtime_pipeline.py`. Ils ont des seuils de tonalité légèrement différents. C'est le signe qu'il y a eu deux personnes sur le même problème.
- **`POLL_SECONDS = 900` hardcodé** sans variable d'environnement ni configuration externe.
- **Pas de logs persistants**. Le poller log en console, pas dans un fichier. En production, on ne peut pas déboguer après coup.
- **Vue.js chargé depuis CDN** avec 4 scripts séparés. Ce n'est pas une critique sur le fond, mais un jury technique le remarquera.
- **`auto_validate_with_gdelt()`** existe dans `reporting.py` mais n'est appelée **nulle part** dans les routes. La feature de validation automatique est dans le code mais morte.
- **`_read_status` importée mais inexistante** — quelqu'un a planifié une feature, a écrit l'import, mais n'a pas livré la fonction.

---

## 6. Ce qui semble "startup crédible"

- **Le workflow complet tient** : de la source GDELT au signalement citoyen, en passant par le scoring et la carte. C'est rare pour un hackathon. La plupart s'arrêtent à "on a des données et un graphe".
- **Le playbook de réponse** est directement exploitable par une équipe sécurité. Ce n'est pas de la cosmétique — c'est une aide à la décision.
- **La gestion de la transparence géographique** (affichage du `coord_source`, pourcentage exact de centroïdes) est le genre de détail qu'une ONG ou un bailleur regarde. Ça montre que l'équipe comprend les limites de ses données.
- **L'architecture FastAPI + fichiers parquet** est déployable sur n'importe quelle machine sous Linux sans dépendance cloud. C'est adapté à des contextes à ressources limitées (Afrique de l'Ouest, contraintes budgétaires ONG).
- **La portée géographique est réaliste** : Bénin uniquement, 12 départements, focus nord. Ce n'est pas "l'Afrique entière en temps réel" — c'est un périmètre défendable.

---

## 7. Ce qu'il faut ABSOLUMENT stabiliser avant le jury

### 🔴 Critique — sans correction, la démo échoue

**Bug 1 — STT scores tous à zéro**

Le router `/api/stt` appelle `compute_all_departments(df, ref_date=None)` → `ref_date = datetime.utcnow()` (mai 2026) → fenêtre 14j et baseline 90j sont **entièrement hors des données 2025** → tous les scores = 0 → la page TERROIR affiche "Situation normale sur l'ensemble du territoire" en permanence.

**Correction :**
```python
# Dans backend/routers/stt.py
@router.get("/stt")
def stt_scores(ref_date: Optional[str] = Query(None)):
    from backend.services.metrics import compute_all_departments
    df = load_historical_data()
    # Si pas de ref_date fournie, utiliser la date max du dataset
    if ref_date is None:
        ref = df["SQLDATE"].max() if not df.empty else None
    else:
        ref = pd.Timestamp(ref_date)
    scores = compute_all_departments(df, ref_date=ref)
    return {"scores": scores, "count": len(scores)}
```

---

**Bug 2 — `_read_status` n'existe pas dans le poller**

```python
# gdelt.py ligne 7 — import qui crashe au démarrage
from backend.services.gdelt_live_poller import (
    run_one_cycle, _read_status, LIVE_PATH,   # ← _read_status inexistant
)
```

**Correction :**
```python
from backend.services.gdelt_live_poller import (
    run_one_cycle, get_live_stats, LIVE_PATH,
)
# Puis remplacer _read_status() par get_live_stats() dans gdelt_status()
```

---

**Bug 3 — Carte vide en démo**

Le filtre par défaut est `hours=24`. Avec 1 événement live (28 mai), la carte est vide si on démarre. Solution : passer le filtre par défaut à `720` (30 jours) pour la démo, ou charger les données historiques 2025 quand la fenêtre est vide.

---

### 🟡 Important — fragilise la crédibilité

- **Supprimer le lien `localhost:8501`** dans le footer (ou le remplacer par un lien relatif si Streamlit tourne sur le même serveur)
- **Combler le gap jan–mai 2026** via le script BigQuery (`import_2026_csv.py`) avant la démo
- **Activer `auto_validate_with_gdelt()`** quelque part — au moins dans le cycle du poller — sinon la feature de cross-validation est invisible

### 🔵 Optionnel — finition

- Supprimer ou masquer l'interface Streamlit du frontend public (garder pour usage interne)
- Ajouter un minimum de rate-limiting sur `POST /api/incidents`

---

## 8. Ce qu'il ne faut plus toucher

| Composant | Raison |
|---|---|
| **`gdelt_live_poller.py`** (sauf le bug `_read_status`) | Fonctionne, testé, en production. Chaque modification risque de casser le cycle. |
| **`metrics.py` (formule STT)** | La formule est défendable, documentée, cohérente. Ne pas changer les poids ni les seuils. |
| **`index.html` + `style.css`** | Le design est propre. Ajouter des features visuelles maintenant = risque de régression. |
| **`reporting.py` (SQLite)**| Le schéma fonctionne. Ne pas migrer vers PostgreSQL ou autre maintenant. |
| **`Pipeline.py` et `benin_enrichi.parquet`** | Dataset historique stable. Ne pas re-générer sauf si nécessaire. |
| **La structure des routers FastAPI** | L'API est cohérente et documentée. Les ajouter est risqué, les modifier aussi. |

---

## 9. La vraie proposition de valeur

**En une phrase :**
> BeninScope est le seul système qui combine la couverture médiatique internationale GDELT et les signalements citoyens terrain pour produire un score d'alerte territorial en temps quasi-réel pour le Bénin.

**Version jury :**
> "Là où les autres outils surveillent les médias OU le terrain, nous surveillons les deux simultanément et mesurons l'écart entre eux."

**Version ONG :**
> "Vous recevez une alerte quand un département béninois sort de sa norme historique — pas quand un journaliste en parle."

**Version mairie / préfecture :**
> "Vous voyez ce que les médias rapportent de votre zone, et ce que vos administrés signalent. Les deux en même temps, sur une même carte."

**Version journaliste :**
> "Filtrez les événements sécuritaires Bénin des 7 derniers jours, avec source URL et niveau de tension — en 2 secondes via l'API."

---

## 10. La faiblesse conceptuelle principale

**Le système mesure des signaux médiatiques, pas des faits.**

GDELT capte ce que les journaux disent. Un événement grave non couvert par les médias est invisible. Une information mal géolocalisée par GDELT atterrit sur le mauvais département. Un article sur le Bénin de Edo State (Nigeria) pourrait théoriquement passer le filtre sur des données mal codées.

Ce n'est pas un défaut du projet — c'est une limite fondamentale de GDELT. Mais le jury va l'attaquer. La réponse honnête est : "C'est pour ça que nous avons les signalements citoyens. L'IAN (Indice d'Asymétrie Narrative) mesure exactement l'écart entre médias et terrain."

La faiblesse est que **la couche citoyenne est encore vide**. Le projet repose sur une promesse : si les citoyens signalent, le système devient puissant. Mais pour l'instant, c'est une promesse.

---

## 11. La force conceptuelle principale

**Le workflow est complet et défendable de bout en bout.**

La plupart des projets hackathon ont une idée et un graphe. BeninScope a un pipeline entier :
- source réelle (GDELT, données publiques, gratuites)
- traitement automatique (filtre, enrichissement, déduplication)
- stockage structuré (parquet + SQLite)
- API REST documentée
- interface utilisateur fonctionnelle
- scoring avec playbook de réponse
- couche de signalement terrain

Chaque brique s'emboîte. Le jury peut tracer un chemin de la donnée brute à la recommandation d'action. C'est rare. C'est convaincant.

---

## 12. Si tu étais jury

**Est-ce que ce projet resterait en mémoire ?**

Oui — si la démo fonctionne. Non — si la carte est vide et le STT affiche "Normal" partout.

Le projet a ce qu'il faut pour marquer : une architecture non-triviale, un cas d'usage réel, une interface propre, et un discours honnête sur ses limites. C'est la combinaison qui différencie.

**Comparé à quoi ?**

Sur un hackathon Afrique-données, la majorité des projets sont soit :
- un notebook avec des graphes Plotly mis en page
- un dashboard PowerBI / Metabase sur des données statiques
- un modèle ML "qui prédit" quelque chose avec 80% d'accuracy sur un dataset kaggle

BeninScope est dans une catégorie différente : c'est un système opérationnel sur des données réelles avec une logique produit. Ça se voit.

**Ce qui le différencie vraiment :**

1. **Il fonctionne vraiment** (GDELT poller en live, API REST, SQLite, Vue.js)
2. **Il est honnête** — il dit "91% de centroïdes", il dit "ne prédit pas une crise"
3. **Il a un utilisateur imaginé** — pas "les décideurs" en général, mais un coordinateur sécurité ONG qui a besoin d'une note de situation dans 5 minutes

**Ce qui peut le faire tomber en démo :**
La carte vide. Le STT figé à zéro. Le jury qui clique sur le lien Streamlit et voit `localhost:8501 ne répond pas`.

---

## Synthèse rapide — priorités avant le jury

```
🔴 CRITIQUE (à corriger avant toute démo)
   → Bug STT ref_date → scores tous à 0
   → Bug _read_status → crash router GDELT

🟡 IMPORTANT (fragilise la crédibilité)
   → Carte vide avec filtre 24h par défaut
   → Lien localhost:8501 dans le footer
   → Gap données jan–mai 2026

🟢 SOLIDE (ne pas toucher)
   → Pipeline GDELT live
   → Formule STT
   → Frontend Vue / Bootstrap
   → Formulaire citoyen
   → Transparence coord_source
```

---

*Auto-audit BeninScope / TERROIR · 29 mai 2026 · Basé sur lecture complète du code source*
