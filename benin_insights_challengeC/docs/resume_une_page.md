# Bénin Insights 2025 — Résumé d'une page

**Hackathon iSHEERO × DataCamp 2026 · Team 04**
**Bénin Insights Challenge · 9 mai 2026**

---

## Le projet en deux phrases

Nous avons analysé **10 722 événements médiatiques** publiés sur le Bénin dans le monde entier pendant toute l'année 2025, à partir de la base GDELT. Notre objectif : comprendre comment le Bénin est perçu dans les médias internationaux, et identifier les facteurs qui façonnent cette perception.

---

## Cinq insights clés

### 1. Le ton médiatique sur le Bénin est globalement négatif

Sur 12 mois de couverture, **11 affichent un ton moyen négatif**. Le ton moyen annuel est de **−1,22** sur l'échelle GDELT (qui va de −100 à +100). Décembre est le mois le plus dur (−2,46), octobre est le seul mois légèrement positif (+0,23). Paradoxe : le score Goldstein, qui mesure l'intensité géopolitique réelle des événements, est lui légèrement **positif** (+0,56). Autrement dit, les médias durcissent le ton sur des événements qui sont, dans les faits, plutôt coopératifs.

### 2. La couverture est concentrée au sud, mais le nord pèse plus lourd qu'il n'y paraît

**93,7 % des événements** géolocalisés sont au sud du pays (Cotonou, Porto-Novo). Le centre représente 1,4 % et est la seule zone à ton positif (+0,58). Le **nord ne pèse que 4,9 % du volume**, mais y affiche un **ton près de 4 fois plus négatif que le sud** (−4,29 contre −1,09). Une asymétrie nette : peu d'événements au nord, mais quand il y en a, ils tirent fortement la perception nationale vers le négatif.

### 3. Les conflits font le ton, même quand la coopération fait le volume

La coopération (verbale + matérielle) représente **74,4 %** des événements, contre **25,5 % de conflits**. Pourtant ce sont les conflits qui orientent le ton négatif global. Un quart d'événements suffit donc à structurer la perception médiatique du pays.

### 4. Trois moments-clés ont structuré l'année

L'analyse des anomalies (Z-score, MAD, fenêtre glissante) a fait ressortir **trois pics** :
- **10 janvier** — pic isolé à très forte tonalité négative (88 événements, ton −3,48)
- **17 avril** — seul pic *positif* de l'année (77 événements, ton +0,81)
- **7-12 décembre** — séquence de 6 jours, **1 272 événements en une semaine**, +131 % au-dessus de la médiane mensuelle

Décembre concentre à lui seul **18,2 % du volume annuel**.

### 5. Le Nigeria est au centre de la couverture du Bénin

L'analyse des acteurs montre que **696 événements impliquent le Nigeria**, soit **5 fois plus que la France**, le premier pays non-africain. Niger, Burkina Faso, Togo et Côte d'Ivoire suivent. **L'image internationale du Bénin se construit d'abord à l'échelle ouest-africaine**, pas occidentale.

---

## Le modèle de classification

Nous avons entraîné un **Random Forest** capable de prédire si un article sur le Bénin sera classé positif ou négatif. Le modèle atteint **72 % de précision** sur le jeu de test. Les trois variables les plus influentes :

| Rang | Variable | Importance | Lecture |
|------|----------|-----------:|---------|
| 1 | **mois** | 0,36 | effet saisonnier — décembre très influent |
| 2 | **GoldsteinScale** | 0,24 | intensité géopolitique de l'événement |
| 3 | **EventRootCode** | 0,12 | type d'événement (CAMEO) |

Lecture simple : **la temporalité et le type d'événement pèsent plus que la géographie**. Le « quand » et le « quoi » comptent davantage que le « où ».

---

## Pour qui c'est utile

- **Décideurs publics** : surveiller en temps réel la réputation internationale du pays et anticiper les fenêtres de communication.
- **Journalistes** : repérer les angles sous-couverts et le décalage entre faits et tonalité.
- **Chercheurs** : disposer d'une base solide pour des analyses plus fines (sentiment par source, biais linguistique, etc.).

---

## Comment on a travaillé

| Données | Méthodes | Outils |
|---|---|---|
| 10 722 événements GDELT (2025) | Analyse exploratoire | Python · Pandas |
| 349 jours couverts sur 365 | Détection d'anomalies (Z-score, MAD) | Plotly · Streamlit |
| 82 points uniques géolocalisés | Random Forest (100 arbres) | Scikit-learn |
| Sources internationales | Importance des variables | BigQuery · GDELT |

---

## Limites assumées

La segmentation nord / centre / sud repose sur des seuils de latitude approximatifs. La détection de signaux *précurseurs* aux pics n'a pas été implémentée — seuls les pics au moment où ils surviennent sont détectés. Les événements réels associés aux pics (10 janvier, 17 avril, séquence décembre) n'ont pas été identifiés formellement depuis les données. L'analyse du biais francophone / anglophone reste à mener.

---

**Dashboard live** : benin-insights-2025.streamlit.app
**Dépôt complet** : github.com/CarineEpitech/Hackathon_Isheero_Team04
