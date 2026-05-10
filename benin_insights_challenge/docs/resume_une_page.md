# Bénin Insights 2025 — Résumé d'une page

**Hackathon iSHEERO × DataCamp 2026 · Team 04**
**Bénin Insights Challenge · 10 mai 2026**

---

## Le projet en deux phrases

Nous avons analysé **23 859 événements médiatiques** publiés sur le Bénin dans le monde entier pendant toute l'année 2025, à partir de la base GDELT. Notre objectif : comprendre comment le Bénin est perçu dans les médias internationaux, et identifier les facteurs qui façonnent cette perception.

---

## Cinq insights clés

### 1. Le ton médiatique sur le Bénin est globalement négatif

Sur 12 mois de couverture, **les 12 affichent un ton moyen négatif**. Le ton moyen annuel est de **−1,49** sur l'échelle GDELT (qui va de −100 à +100). Décembre est le mois le plus négatif (−2,65), octobre est le moins négatif de l'année (−0,03). À noter : le score Goldstein — qui mesure le caractère stabilisateur ou déstabilisateur des types d'événements sur une échelle de −10 à +10 — affiche une médiane positive (+1,9). Les deux indicateurs mesurent des choses différentes : le Goldstein reflète la nature des événements (coopération ou conflit), l'AvgTone reflète le registre linguistique des articles.

### 2. La couverture est concentrée au sud, mais le nord pèse plus lourd qu'il n'y paraît

**94,9 % des événements** tombent en zone « sud » — dont 91 % correspondent à une localisation générique pays « Bénin » sans ville précise. Seuls 8,8 % des événements sont localisés à la ville. Le centre représente 1,1 % des événements et est la seule zone à ton positif (+0,24). Le **nord ne représente que 4,0 % du volume**, mais affiche un **ton près de 3 fois plus négatif que le sud** (−4,10 contre −1,41). Un test de Mann-Whitney confirme que la différence est statistiquement significative (p < 0,001, effet r = 0,36 — effet modéré). La causalité sur l'image nationale n'est pas établie — c'est une asymétrie observée, pas une relation prouvée.

### 3. Le ton négatif traverse tous les types d'événements

La coopération (verbale + matérielle) représente **73,8 %** des événements, contre **26,2 % de conflits**. Contrairement à l'intuition, la coopération verbale (63,7 % du volume) affiche elle-même un ton moyen négatif (−0,35). La contribution au ton négatif global est répartie : coopération verbale 45,6 %, conflits matériels 29,0 %, conflits verbaux 16,1 %, coopération matérielle 9,3 %. Les conflits matériels restent les plus sévères (−5,34), mais le ton négatif pénètre tous les types d'événements — porté notamment par la forte présence des médias nigérians à couverture politique intense.

### 4. Trois moments-clés ont structuré l'année

L'analyse des anomalies (Z-score, MAD, fenêtre glissante) a fait ressortir **trois pics** :
- **10 janvier** — pic isolé à très forte tonalité négative (176 événements, 1 124 mentions, ton −4,01)
- **17 avril** — seul pic *positif* de l'année (218 événements, 1 315 mentions, ton +2,14)
- **7-12 décembre** — séquence de 6 jours, **2 645 événements**, ton moyen −2,77

Décembre concentre à lui seul **17,7 % du volume annuel**.

### 5. Le Nigeria est au centre de la couverture du Bénin

L'analyse des acteurs montre que **2 198 événements ont le Nigeria comme acteur principal** (Actor1CountryCode = NGA), soit **6,6 fois plus que la France** (335 événements). Par ailleurs, **22,3 % des articles** proviennent de sources à domaine `.ng` (médias nigérians), contre 0,6 % pour les sources béninoises (`.bj`). **L'image internationale du Bénin se construit d'abord à l'échelle ouest-africaine**, principalement à travers les médias nigérians, pas à travers la presse occidentale.

---

## Le modèle de classification

Nous avons entraîné un **Random Forest** pour prédire si un événement médiatique sur le Bénin sera couvert positivement ou négativement. Évaluation sur split stratifié (20 % test, `random_state=42`) :

| Métrique | Valeur |
|----------|--------|
| Baseline DummyClassifier (classe majoritaire) | 62,7 % |
| **Random Forest (`class_weight=balanced`)** | **70 %** |
| Gain sur baseline | +7 pp |
| Validation croisée (5 folds stratifiés) | 69,5 % ± 0,1 % |
| F1 Négatif | 0,74 |
| F1 Positif | 0,64 |

Les trois variables les plus influentes :

| Rang | Variable | Importance | Lecture |
|------|----------|-----------:|---------|
| 1 | **mois** | 0,34 | saisonnalité 2025 — décembre très négatif |
| 2 | **GoldsteinScale** | 0,25 | nature géopolitique de l'événement |
| 3 | **EventRootCode** | 0,13 | type d'événement (CAMEO) |

**La temporalité et le type d'événement pèsent plus que la géographie.** Le « quand » et le « quoi » comptent davantage que le « où ». Le gain de 7 pp sur la baseline est réel mais modeste : le modèle capture des tendances structurelles de 2025, pas un prédicteur causal généralisable.

---

## Cas d'usage

La méthodologie et le dashboard peuvent intéresser des équipes chargées du suivi de l'image internationale d'un pays (communication institutionnelle, diplomatie), des journalistes qui travaillent sur la couverture médiatique de l'Afrique de l'Ouest, ou des chercheurs qui souhaitent croiser des données GDELT avec d'autres sources. Le pipeline est réutilisable sur tout autre pays en changeant le filtre `ActionGeo_CountryCode`.

---

## Comment on a travaillé

| Données | Méthodes | Outils |
|---|---|---|
| 23 859 événements GDELT (2025) | Analyse exploratoire | Python · Pandas |
| 351 jours couverts sur 365 | Détection d'anomalies (Z-score, MAD) | Plotly · Streamlit |
| 108 points géolocalisés (8,8 % précis) | Random Forest (100 arbres) | Scikit-learn |
| Sources internationales | Importance des variables | BigQuery · GDELT |

---

## Limites assumées

**Sur les données.** GDELT mesure la couverture médiatique internationale, pas les événements sur le terrain. Un pays peut avoir une activité réelle sans couverture médiatique, et inversement. Les résultats décrivent comment le Bénin est *perçu* dans la presse, pas ce qui s'y passe.

**Sur la géographie.** La segmentation nord / centre / sud repose sur une correspondance textuelle entre `ActionGeo_FullName` et des listes de communes. 91,2 % des événements ont une localisation générique pays (ADM1Code = BN) et tombent en zone « sud » par défaut — ils ne sont pas spécifiquement localisés à Cotonou ou Porto-Novo. Les analyses géographiques fiables portent sur les 2 101 événements précisément localisés. Le nord représente 947 événements sur 23 859 — les chiffres régionaux sont robustes statistiquement (Mann-Whitney p < 0,001) mais restent à interpréter avec prudence.

**Sur les acteurs.** Actor1CountryCode est manquant pour 48,8 % des événements (11 633 lignes). Les analyses sur les pays acteurs portent sur 51,2 % du dataset — la domination nigériane est réelle mais les ratios exacts sont à interpréter en tenant compte de cette limite.

**Sur le modèle ML.** Le Random Forest a été entraîné sur les données 2025 uniquement. La performance de 70 % (7 pp au-dessus de la baseline de 62,7 %) n'est pas garantie sur 2026 — en particulier si la distribution mensuelle change. Sans pic de décembre comparable, l'accuracy se rapprocherait des 64 % (test sans `mois`).

**Sur la détection de pics.** Les anomalies sont détectées au moment où elles surviennent. Les signaux précurseurs n'ont pas été implémentés. Les événements réels associés aux pics (10 janvier, 17 avril, séquence décembre) n'ont pas été identifiés formellement depuis les données GDELT.

**Sur H1.** L'hypothèse initiale ("image plus négative depuis mi-2025") n'est pas testable avec une seule année de données. Ce qui est démontré : le ton est négatif sur les 12 mois de 2025. Une dégradation tendancielle nécessiterait des données 2023-2024 pour comparaison.

---

**Dépôt complet** : github.com/CarineEpitech/Hackathon_Isheero_Team04
