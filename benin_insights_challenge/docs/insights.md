# Hypothèses provisoires — Bénin Insights Challenge

**Hackathon iSHEERO × DataCamp 2026**  
**Date :** 28 avril 2026  
**Statut :** Hypothèses à vérifier avec les données  

---

## Comment lire ce document ?

Ce document présente des **hypothèses de travail** formulées avant l’analyse complète des données.

Chaque hypothèse suit une logique simple :

- **Ce que nous pensons observer**
- **Pourquoi nous pensons cela**
- **Comment nous allons le vérifier avec les données**

Après l’analyse, chaque hypothèse sera classée comme :

- ✅ Confirmée  
- ⚠️ Partiellement vraie  
- ❌ Fausse  

---

# Hypothèse 1 — L’image du Bénin dans les médias internationaux

### Ce que nous pensons
L’image du Bénin dans les médias internationaux est devenue plus négative entre mi-2025 et début 2026.

Nous pensons aussi que les médias occidentaux parlent davantage de sécurité, tandis que les médias africains parlent aussi d’économie, de culture et de tourisme.

### Pourquoi ?
Depuis quelques années, les attaques dans le nord du Bénin attirent plus l’attention des médias internationaux.

En parallèle, certains événements positifs continuent d’exister :

- festival Vodun
- tourisme
- patrimoine culturel
- diplomatie

### Comment vérifier ?
Nous allons analyser :

- l’évolution de **AvgTone** dans le temps
- les pays ou médias qui publient les articles
- la différence entre médias anglophones et francophones

---

# Hypothèse 2 — Les sujets les plus médiatisés sur le Bénin

### Ce que nous pensons
Les sujets les plus traités dans les médias sont probablement :

1. la sécurité  
2. la coopération internationale  
3. la culture et la diplomatie

### Pourquoi ?
Les questions sécuritaires sont devenues plus visibles récemment.

Mais le Bénin reste aussi présent dans les médias grâce à :

- ses relations internationales
- ses projets de développement
- ses événements culturels

### Comment vérifier ?
Nous allons étudier :

- les codes d’événements les plus fréquents
- les thèmes les plus cités
- leur évolution dans le temps

---

# Hypothèse 3 — L’impact des attaques dans le nord du pays

### Ce que nous pensons
Les attaques ou incidents dans le nord du Bénin peuvent influencer l’image globale du pays dans les médias.

Même si ces événements sont localisés, ils peuvent affecter la perception générale du Bénin.

### Pourquoi ?
Les médias internationaux parlent souvent du pays comme un ensemble.

Un incident local peut donc avoir un impact national sur l’image du pays.

### Comment vérifier ?
Nous allons comparer :

- le nombre d’incidents dans le nord
- l’évolution de la tonalité médiatique nationale

Nous regarderons aussi si cet impact dure plusieurs jours ou semaines.

---

# Hypothèse 4 — Détecter des signaux avant les grandes crises

### Ce que nous pensons
Avant certains grands événements, il pourrait exister des signaux dans les médias :

- hausse soudaine du nombre d’articles
- baisse soudaine de la tonalité

### Pourquoi ?
Certaines informations apparaissent d’abord dans des médias spécialisés avant d’être reprises partout.

### Comment vérifier ?
Nous allons rechercher :

- les pics inhabituels d’articles
- les baisses inhabituelles de tonalité
- les dates importantes liées à ces changements

---

# Hypothèse 5 — Les moments les plus marquants de l’année

### Ce que nous pensons
Quelques événements majeurs ont probablement marqué l’image du Bénin durant l’année.

Par exemple :

- incidents sécuritaires
- événements culturels
- événements politiques ou diplomatiques

### Pourquoi ?
Ces événements attirent généralement une forte attention médiatique.

### Comment vérifier ?
Nous allons identifier :

- les périodes avec le plus d’articles
- les périodes les plus positives
- les périodes les plus négatives

Puis nous chercherons quels événements réels expliquent ces pics.

---

# Tableau de suivi

| Hypothèse | Résultat final |
|------------|----------------|
| H1 — Ton médiatique 2025 | ⚠️ Partiellement confirmée — ton négatif sur 11/12 mois confirmé. La formulation initiale "plus négative depuis mi-2025" n'est pas testable avec une seule année. |
| H2 — Sujets dominants | ⚠️ Partiellement confirmée — coopération verbale (65 %) et conflits (25,5 %) mesurables via QuadClass. Le thème "culture" n'est pas identifiable via GDELT sans texte. |
| H3 — Impact du nord | ⚠️ Asymétrie confirmée — causalité non établie |
| H4 — Signaux faibles | ⏳ Non testée — détection de pics réalisée, pas de précurseurs |
| H5 — Moments marquants | ⚠️ Partiellement confirmée — décembre et deux pics secondaires caractérisés |

---

### Détail H3 — Tests statistiques réalisés

**Mann-Whitney U (nord vs sud, AvgTone) :**
- nord : n = 409, moyenne = −4,36
- sud : n = 10 179, moyenne = −1,13
- U = 1 213 720, p < 0,001
- Effect size (rank-biserial r) = 0,42 → effet modéré à fort

**Mann-Whitney U (centre vs sud, AvgTone) :**
- centre : n = 134, moyenne = +0,85
- p < 0,001, r = −0,28 → le centre est significativement plus positif que le sud

**Kruskal-Wallis (3 zones) :**
- H = 240,1, p < 0,001 → les trois zones ont des distributions de ton différentes

Conclusion : l'asymétrie géographique est statistiquement robuste. L'effet nord est réel et significatif. L'impact causal sur l'image nationale reste non démontré (pas de modèle de propagation).

---

### Note sur H1

L'hypothèse initiale portait sur une aggravation "depuis mi-2025". Avec les données 2025 uniquement, on peut seulement confirmer que le ton est négatif sur 11 des 12 mois. Le mois d'octobre (+0,23) est le seul mois positif. Tester une tendance à la dégradation nécessiterait des données 2023-2024 comme référence.

---

## Objectif final

Notre objectif est de comprendre comment les médias internationaux parlent du Bénin :

- quels sujets dominent
- ce qui améliore l’image du pays
- ce qui la dégrade
- quels événements influencent le plus cette perception

L’objectif final est de proposer une lecture claire et utile aux décideurs.

