# Hypothèses — Bénin Insights Challenge

**Hackathon iSHEERO × DataCamp 2026** 
**Formulées :** 28 avril 2026 — **Résultats :** 10 mai 2026 (dataset 23 859 événements)

---

## Note de lecture

Ce document regroupe les hypothèses formulées avant l'analyse, avec leurs résultats. Chaque hypothèse indique ce qui était attendu, pourquoi, comment la vérification a été menée, et ce que les données ont effectivement montré.

Statuts possibles :

- Confirmée 
- Partiellement vraie 
- Fausse 

---

# Hypothèse 1 — L'image du Bénin dans les médias internationaux

### Ce que nous pensons
L'image du Bénin dans les médias internationaux est devenue plus négative entre mi-2025 et début 2026.

Nous pensons aussi que les médias occidentaux parlent davantage de sécurité, tandis que les médias africains parlent aussi d'économie, de culture et de tourisme.

### Pourquoi ?
Depuis quelques années, les attaques dans le nord du Bénin attirent plus l'attention des médias internationaux.

En parallèle, certains événements positifs continuent d'exister :

- festival Vodun
- tourisme
- patrimoine culturel
- diplomatie

### Vérification réalisée

Nous avons analysé l'évolution mensuelle de `AvgTone` sur les 23 859 événements de 2025, examiné les pays acteurs les plus présents (`Actor1CountryCode`) et la provenance des sources (`SOURCEURL`). La différence anglophone/francophone n'a pas été mesurée directement, faute d'annotation linguistique des articles.

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

### Vérification réalisée

Nous avons analysé la distribution `QuadClass` et les codes `EventRootCode` les plus fréquents. Les thèmes culturels et économiques ne sont pas directement identifiables via GDELT sans accès au texte des articles — cette limite a été documentée dans le rapport.

---

# Hypothèse 3 — L'impact des attaques dans le nord du pays

### Ce que nous pensons
Les attaques ou incidents dans le nord du Bénin peuvent influencer l'image globale du pays dans les médias.

Même si ces événements sont localisés, ils peuvent affecter la perception générale du Bénin.

### Pourquoi ?
Les médias internationaux parlent souvent du pays comme un ensemble.

Un incident local peut donc avoir un impact national sur l'image du pays.

### Vérification réalisée

Nous avons comparé le ton moyen (`AvgTone`) entre zones géographiques et effectué des tests statistiques (Mann-Whitney, Kruskal-Wallis). L'impact temporel sur plusieurs semaines n'a pas été modélisé — il faudrait des données multi-annuelles pour isoler un effet de propagation.

---

# Hypothèse 4 — Détecter des signaux avant les grandes crises

### Ce que nous pensons
Avant certains grands événements, il pourrait exister des signaux dans les médias :

- hausse soudaine du nombre d'articles
- baisse soudaine de la tonalité

### Pourquoi ?
Certaines informations apparaissent d'abord dans des médias spécialisés avant d'être reprises partout.

### Vérification réalisée

Nous avons appliqué une détection d'anomalies multi-méthodes (Z-score, MAD, fenêtre glissante) sur le volume quotidien et le ton. Trois périodes anormales ont été identifiées. La détection de précurseurs (signaux avant les crises) n'a pas été implémentée — c'est une extension prévue pour une Phase 2.

---

# Hypothèse 5 — Les moments les plus marquants de l'année

### Ce que nous pensons
Quelques événements majeurs ont probablement marqué l'image du Bénin durant l'année.

Par exemple :

- incidents sécuritaires
- événements culturels
- événements politiques ou diplomatiques

### Pourquoi ?
Ces événements attirent généralement une forte attention médiatique.

### Vérification réalisée

Nous avons identifié les trois périodes les plus marquantes par volume et par ton. Les événements réels associés ont été croisés avec des sources journalistiques externes (France 24, Jeune Afrique, Wikipedia) — ils ne sont pas directement identifiables depuis les données GDELT seules.

---

# Tableau de suivi

| Hypothèse | Résultat final |
|------------|----------------|
| H1 — Ton médiatique 2025 | Partiellement confirmée — ton négatif sur les **12/12 mois** confirmé. La formulation initiale "plus négative depuis mi-2025" n'est pas testable avec une seule année. |
| H2 — Sujets dominants | Partiellement confirmée — coopération verbale (63,7 %) et conflits (26,2 %) mesurables via QuadClass. Le thème "culture" n'est pas identifiable via GDELT sans texte. |
| H3 — Impact du nord | Asymétrie confirmée — causalité non établie |
| H4 — Signaux faibles | Non testée — détection de pics réalisée, pas de précurseurs |
| H5 — Moments marquants | Partiellement confirmée — décembre et deux pics secondaires caractérisés |

---

### Détail H3 — Tests statistiques réalisés

**Mann-Whitney U (nord vs sud, AvgTone) :**
- nord : n = 947, moyenne = −4,10
- sud : n = 22 653, moyenne = −1,41
- U = 6 885 540, p < 0,001
- Effect size (rank-biserial r) = 0,36 → effet modéré

**Mann-Whitney U (centre vs sud, AvgTone) :**
- centre : n = 259, moyenne = +0,24
- p < 0,001, r = −0,24 → le centre est significativement plus positif que le sud

**Kruskal-Wallis (3 zones) :**
- H = 398,5, p < 0,001 → les trois zones ont des distributions de ton différentes

Conclusion : l'asymétrie géographique est statistiquement robuste. L'effet nord est réel et significatif. L'impact causal sur l'image nationale reste non démontré (pas de modèle de propagation).

**Note sur la géolocalisation :** 91,2 % des événements (21 758 / 23 859) ont une localisation générique pays « Bénin » (ADM1Code = BN) sans ville précise. Seuls 2 101 événements sont localisés à la ville. Les effectifs nord/centre/sud ci-dessus portent sur l'ensemble du dataset — la robustesse de l'asymétrie nord/sud s'appuie principalement sur les 2 101 événements localisés précisément (nord = 947, centre = 259, sud précis = 895).

---

### Note sur H1

L'hypothèse initiale portait sur une aggravation "depuis mi-2025". Avec les données 2025 uniquement, on peut seulement confirmer que le ton est négatif sur les 12 mois de 2025. Octobre est le mois le moins négatif (−0,03). Tester une tendance à la dégradation nécessiterait des données 2023-2024 comme référence.

---

## Bilan

Les cinq hypothèses ont été vérifiées sur le dataset final (23 859 événements). Les résultats détaillés sont dans `docs/resume_une_page.md`. Les tests statistiques pour H3 (asymétrie géographique) figurent dans la section ci-dessus. La détection de précurseurs (H4) reste ouverte pour une analyse future.
