# Bénin Insights 2025 — Résumé d'une page

**Hackathon iSHEERO × DataCamp 2026 · Team 04**
**Bénin Insights Challenge · 9 mai 2026**

---

## Le projet en deux phrases

Nous avons analysé **10 722 événements médiatiques** publiés sur le Bénin dans le monde entier pendant toute l'année 2025, à partir de la base GDELT. Notre objectif : comprendre comment le Bénin est perçu dans les médias internationaux, et identifier les facteurs qui façonnent cette perception.

---

## Cinq insights clés

### 1. Le ton médiatique sur le Bénin est globalement négatif

Sur 12 mois de couverture, **11 affichent un ton moyen négatif**. Le ton moyen annuel est de **−1,22** sur l'échelle GDELT (qui va de −100 à +100). Décembre est le mois le plus dur (−2,46), octobre est le seul mois légèrement positif (+0,23). Paradoxe : le score Goldstein, qui mesure l'implication géopolitique des types d'événements, affiche une médiane **positive** (+1,9). Les deux mesures sont indépendantes : le Goldstein reflète la nature des événements, l'AvgTone reflète le registre linguistique des articles.

### 2. La couverture est concentrée au sud, mais le nord pèse plus lourd qu'il n'y paraît

**94,9 % des événements** géolocalisés sont au sud du pays (Cotonou, Porto-Novo). Le centre représente 1,3 % et est la seule zone à ton positif (+0,85). Le **nord ne représente que 3,8 % du volume**, mais affiche un **ton près de 4 fois plus négatif que le sud** (−4,36 contre −1,13). Un test de Mann-Whitney confirme que la différence est statistiquement significative (p < 0,001, effet r = 0,42). La causalité sur l'image nationale n'est pas établie — c'est une asymétrie observée, pas une relation prouvée.

### 3. Les conflits expliquent l'essentiel du ton négatif

La coopération (verbale + matérielle) représente **74,4 %** des événements, contre **25,5 % de conflits**. Le calcul de contribution pondérée montre que les événements de coopération verbale (65 % du volume) ont un ton moyen quasi nul (−0,005), tandis que les conflits matériels (14,5 %) affichent −5,43. Les conflits expliquent ainsi environ **91 % du ton négatif global**, malgré leur part minoritaire dans le volume.

### 4. Trois moments-clés ont structuré l'année

L'analyse des anomalies (Z-score, MAD, fenêtre glissante) a fait ressortir **trois pics** :
- **10 janvier** — pic isolé à très forte tonalité négative (88 événements, ton −3,48)
- **17 avril** — seul pic *positif* de l'année (77 événements, ton +0,81)
- **7-12 décembre** — séquence de 6 jours, **1 272 événements en une semaine**, +131 % au-dessus de la médiane mensuelle

Décembre concentre à lui seul **18,2 % du volume annuel**.

### 5. Le Nigeria est au centre de la couverture du Bénin

L'analyse des acteurs montre que **696 événements ont le Nigeria comme acteur principal** (Actor1CountryCode = NGA), soit **5 fois plus que la France** (128 événements). Par ailleurs, **21,5 % des articles** proviennent de sources à domaine `.ng` (médias nigérians), contre 0,7 % pour les sources béninoises (`.bj`). **L'image internationale du Bénin se construit d'abord à l'échelle ouest-africaine**, principalement à travers les médias nigérians, pas à travers la presse occidentale.

---

## Le modèle de classification

Nous avons entraîné un **Random Forest** pour prédire si un événement médiatique sur le Bénin sera couvert positivement ou négativement. Évaluation sur split stratifié (20 % test, `random_state=42`) :

| Métrique | Valeur |
|----------|--------|
| Baseline DummyClassifier (classe majoritaire) | 60 % |
| **Random Forest (`class_weight=balanced`)** | **71 %** |
| Gain sur baseline | +11 pp |
| F1 Négatif | 0,75 |
| F1 Positif | 0,67 |

Les trois variables les plus influentes :

| Rang | Variable | Importance | Lecture |
|------|----------|-----------:|---------|
| 1 | **mois** | 0,33 | saisonnalité 2025 — décembre très négatif |
| 2 | **GoldsteinScale** | 0,25 | nature géopolitique de l'événement |
| 3 | **EventRootCode** | 0,13 | type d'événement (CAMEO) |

**La temporalité et le type d'événement pèsent plus que la géographie.** Le « quand » et le « quoi » comptent davantage que le « où ». Le gain de 11 pp sur la baseline est réel mais modeste : le modèle capture des tendances structurelles de 2025, pas un prédicteur causal généralisable.

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

**Sur les données.** GDELT mesure la couverture médiatique internationale, pas les événements sur le terrain. Un pays peut avoir une activité réelle sans couverture médiatique, et inversement. Les résultats décrivent comment le Bénin est *perçu* dans la presse, pas ce qui s'y passe.

**Sur la géographie.** La segmentation nord / centre / sud repose sur une correspondance textuelle entre `ActionGeo_FullName` et des listes de communes. Les événements non reconnus tombent en zone « sud » par défaut. Le nord ne représente que 409 événements sur 10 722 — les chiffres régionaux sont robustes statistiquement (Mann-Whitney p < 0,001) mais restent à interpréter avec prudence vu ce faible volume.

**Sur le modèle ML.** Le Random Forest a été entraîné sur les données 2025 uniquement. La performance de 71 % (11 pp au-dessus de la baseline) n'est pas garantie sur 2026 — en particulier si la distribution mensuelle change. Sans pic de décembre comparable, l'accuracy se rapprocherait des 64 % (test sans `mois`).

**Sur la détection de pics.** Les anomalies sont détectées au moment où elles surviennent. Les signaux précurseurs n'ont pas été implémentés. Les événements réels associés aux pics (10 janvier, 17 avril, séquence décembre) n'ont pas été identifiés formellement depuis les données GDELT.

**Sur H1.** L'hypothèse initiale ("image plus négative depuis mi-2025") n'est pas testable avec une seule année de données. Ce qui est démontré : le ton est négatif sur 11 des 12 mois de 2025. Une dégradation tendancielle nécessiterait des données 2023-2024 pour comparaison.

---

**Dashboard live** : benin-insights-2025.streamlit.app
**Dépôt complet** : github.com/CarineEpitech/Hackathon_Isheero_Team04
