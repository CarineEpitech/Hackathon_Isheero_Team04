# BeninScope

Plateforme de veille territoriale et d'alerte précoce au Bénin, développée lors du Hackathon iSHEERO × DataCamp 2026.

**Démo en ligne :** [terroir.up.railway.app](https://terroir.up.railway.app)

---

## TERROIR

TERROIR est une application web qui surveille en continu les signaux d'instabilité territoriale au Bénin. Elle agrège toutes les 15 minutes les nouvelles internationales issues de GDELT, les combine avec les signalements de terrain, et produit pour chaque département un score de tension actualisé.

L'objectif est simple : donner à une ONG, une mairie ou une préfecture une vision claire de la situation — sans avoir à croiser soi-même des dizaines de sources.

---

## Le problème

Le Bénin dispose de très peu d'outils pour suivre en temps quasi réel les signaux d'instabilité territoriale.

Les informations existent, mais elles sont dispersées : articles de presse internationale, rapports terrain, données statistiques. Les acteurs locaux n'ont pas toujours les moyens de les agréger, de les filtrer et de les interpréter rapidement.

Résultat : les signaux faibles passent souvent inaperçus jusqu'à ce qu'ils deviennent des crises visibles.

TERROIR cherche à combler cet écart — pas en remplaçant l'expertise humaine, mais en la rendant plus rapide à mobiliser.

---

## Comment ça fonctionne

```
Flux GDELT (toutes les 15 min)          Signalements terrain (citoyens)
            +                                        +
      Filtre géographique                    Validation manuelle
      (18 départements Bénin)
                    |
                    v
         Score de Tension Territorial
         (fenêtre 14 jours vs. baseline 90 jours)
                    |
                    v
        Carte interactive en direct
                    |
                    v
     Alertes par département (Normal / Précaution / Alerte)
```

GDELT publie toutes les 15 minutes un fichier contenant l'ensemble des événements mondiaux extraits de la presse. TERROIR télécharge ces fichiers, filtre les événements localisés au Bénin, et met à jour automatiquement la carte et les scores.

---

## Fonctionnalités principales

**Carte Live**
Visualisation en temps quasi réel des événements GDELT géolocalisés au Bénin. Chaque point représente un article de presse, coloré selon la gravité (ton négatif, code CAMEO sécuritaire). Filtre par type d'événement et par fenêtre temporelle (24h, 48h, 7 jours).

**Scoring territorial (STT)**
Le Score de Tension Territorial compare l'activité des 14 derniers jours à la baseline des 90 jours précédents pour chaque département. Trois niveaux : Normal, Précaution, Alerte. Le calcul pondère le ton moyen, le volume d'événements, les codes sécuritaires et le nombre de sources.

**Signalements citoyens**
Un formulaire simple permet à toute personne présente sur le terrain de signaler une situation. Les signalements sont visibles sur la carte (en attente de validation) et comptabilisés comme signal complémentaire.

**Indicateur de dépendance nigériane (IDN)**
22 % des articles GDELT sur le Bénin proviennent de médias nigérians. Le bouton "Inclure / Exclure Nigéria" permet de voir l'effet de cette surreprésentation sur la carte.

**Analyse historique**
Graphiques sur la période janvier 2025 – mai 2026 : évolution du ton médiatique, répartition des types d'événements, distribution géographique par département.

---

## Exemple concret

Une ONG opérant dans l'Atacora reçoit une alerte "Précaution" sur le tableau de bord TERROIR un lundi matin.

En cliquant sur le département, elle voit que 4 articles de presse internationale ont mentionné la zone au cours des 3 derniers jours, avec un ton significativement plus négatif que la moyenne des 3 mois précédents. Un signalement terrain non validé apparaît également sur la carte.

L'ONG contacte son équipe locale pour vérifier. Ce n'est pas une crise — mais c'est un signal qui mérite attention, qu'elle n'aurait peut-être pas repéré sans TERROIR.

Autres utilisations possibles :

- Une préfecture qui souhaite prioriser ses visites de terrain sur les zones à tension récente
- Un journaliste qui cherche quelles zones ont connu un regain d'activité médiatique cette semaine
- Une mairie qui veut objectiver une demande de moyens supplémentaires auprès d'un bailleur

---

## Architecture

```
Frontend (navigateur)
  Vue 3 · Leaflet · Plotly · Bootstrap 5
  Fichiers statiques servis par FastAPI

Backend (Python)
  FastAPI  —  API REST  (/api/events, /api/stt, /api/incidents, ...)
  Poller GDELT  —  thread en arrière-plan, cycle 15 min
  Calcul STT  —  fenêtre glissante, z-scores par département

Données
  benin_enrichi.parquet  —  31 529 événements, janv. 2025 → mai 2026
  benin_live.parquet     —  fenêtre mobile 30 jours (mise à jour automatique)
  incidents.csv          —  signalements citoyens

Déploiement
  Railway  —  conteneur Docker, redémarrage automatique
```

Il n'y a pas de base de données externe. Tout fonctionne avec des fichiers parquet locaux, ce qui simplifie le déploiement et garantit la disponibilité même en cas de coupure réseau partielle.

---

## Structure du projet

```
benin_insights_challenge/
├── backend/
│   ├── main.py                     # Point d'entrée FastAPI
│   ├── routers/
│   │   ├── events.py               # /api/events — carte et filtres
│   │   ├── stt.py                  # /api/stt — scores départements
│   │   ├── incidents.py            # /api/incidents — signalements
│   │   ├── gdelt.py                # /api/gdelt — statut du poller
│   │   └── stats.py                # /api/stats — métriques globales
│   ├── services/
│   │   ├── gdelt_live_poller.py    # Collecte GDELT toutes les 15 min
│   │   ├── data_loader.py          # Chargement historique + live
│   │   ├── metrics.py              # Calcul STT par département
│   │   └── reporting.py            # Gestion des signalements
│   └── static/                     # Frontend (HTML/CSS/JS)
│
├── data/
│   ├── raw/benin_raw.csv           # Export BigQuery (source)
│   └── processed/
│       ├── benin_enrichi.parquet   # Données enrichies (31 529 événements)
│       └── benin_live.parquet      # Événements live (30 derniers jours)
│
├── scripts/
│   ├── Pipeline.py                 # Traitement du CSV brut → parquet enrichi
│   └── fill_gap_2026.py            # Rattrapage historique GDELT manquant
│
├── notebooks/                      # Analyse exploratoire Phase 1
├── models/                         # Random Forest entraîné (Phase 1)
├── Dockerfile
└── requirements.txt
```

---

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/CarineEpitech/Hackathon_Isheero_Team04.git
cd Hackathon_Isheero_Team04

# Créer l'environnement Python
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# ou : .venv\Scripts\activate    # Windows

# Installer les dépendances
pip install -r benin_insights_challenge/requirements.txt
```

---

## Lancer l'application

```bash
# Depuis la racine du dépôt
cd benin_insights_challenge
uvicorn backend.main:app --reload --port 8000
```

L'interface est accessible sur **http://localhost:8000**

La documentation de l'API est disponible sur **http://localhost:8000/api/docs**

Au démarrage, le poller GDELT s'active automatiquement et commence à collecter les données live en arrière-plan.

---

## Limites

**Dépendance GDELT**
GDELT mesure la couverture médiatique internationale, pas les événements réels. Un incident non couvert par la presse n'apparaît pas dans TERROIR. Inversement, un événement très médiatisé peut produire un score élevé sans correspondre à une menace concrète sur le terrain.

**Géolocalisation approximative**
Environ 91 % des événements GDELT sont localisés au centroïde du pays, faute de données géographiques précises dans les articles sources. La carte indique le niveau de précision de chaque point (position exacte, département estimé, ou pays approximatif).

**Sources nigérianes**
22 % des articles proviennent de médias nigérians, ce qui peut amplifier la perception des zones frontalières. Le bouton IDN permet d'isoler cet effet.

**Signalements non validés**
Les signalements citoyens sont affichés dès leur soumission et marqués "en attente de validation". Ils ne déclenchent pas d'alerte automatique et nécessitent une vérification humaine avant toute action.

---

## Perspectives

Quelques directions pour une version production :

- Connecter une base de données persistante (PostgreSQL) pour les signalements
- Mettre en place des alertes par e-mail ou SMS pour les opérateurs terrain
- Affiner le scoring STT avec des données complémentaires (météo, marché, présence humanitaire)
- Ouvrir une API pour permettre à d'autres acteurs d'intégrer les scores TERROIR dans leurs propres outils

---

## Équipe

**BeninScope** — Hackathon iSHEERO × DataCamp 2026
