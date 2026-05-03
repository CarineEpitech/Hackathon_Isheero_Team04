# Insights v0 — Hypothèses provisoires · Bénin Insights Challenge
## Hackathon iSHEERO × DataCamp 2026 · Data Scientist

**Date :** 28 avril 2026  
**Statut :** 🟡 Hypothèses — à confirmer / infirmer avec les données DA + ML  
**Version :** v0 (provisoire J2) → sera mis à jour en v1 (J3) puis final (J4)

> **Comment lire ce document :**
> Chaque insight est une hypothèse structurée formulée *avant* d'avoir toutes les données.
> Format : *"Nous pensons que [observation probable] parce que [logique contextuelle]. À confirmer avec [indicateur GDELT]."*
> Une fois les viz DA disponibles, annoter chaque insight avec ✅ Confirmé / ⚠️ Nuancé / ❌ Infirmé.

---

## Insight 1 — Évolution & biais de l'image médiatique

**Hypothèse :**
> Nous anticipons que la tonalité médiatique globale du Bénin (`AvgTone` moyen) a subi une dégradation progressive entre mi-2025 et début 2026, tirée principalement par la couverture sécuritaire des médias occidentaux anglophones, tandis que les médias africains francophones ont maintenu une tonalité plus neutre à positive, reflétant une perception différenciée du risque pays.

**Logique contextuelle :**
Les médias occidentaux anglophones couvrent le Bénin quasi-exclusivement sous l'angle sécuritaire (extension du jihadisme sahélien), alors que les médias africains intègrent davantage les narratifs de développement économique et culturel (tourisme, Voodoo Festival, restitution des trésors royaux d'Abomey).

**À confirmer avec :**
- Évolution mensuelle de `AvgTone` segmentée par pays source (`SOURCEURL`)
- Comparaison moyenne `AvgTone` : médias francophones africains vs médias anglophones occidentaux
- Test statistique (t-test ou Mann-Whitney) sur la différence de moyennes

**Annotation après viz DA :**
> _(à remplir dès qu'une viz de tonalité temporelle est disponible)_
> Statut : ⬜ Non encore vérifié

---

## Insight 2 — Narratifs dominants

**Hypothèse :**
> Nous anticipons que les trois narratifs dominant la couverture médiatique du Bénin sur 12 mois sont, dans l'ordre : (1) les événements sécuritaires et militaires (codes CAMEO 18x–20x), (2) la coopération internationale et l'aide au développement (codes 03x–06x), et (3) les événements culturels et diplomatiques (codes 01x–02x). La part des narratifs sécuritaires a probablement augmenté de façon significative à partir du T3 2025.

**Logique contextuelle :**
Le Bénin bénéficiait avant 2022 d'une image quasi-exclusivement positive (stabilité démocratique, culture Voodoo, croissance économique). Depuis l'extension des attaques jihadistes vers le nord du pays, le narratif sécuritaire a progressivement phagocyté la couverture internationale, en particulier dans les médias spécialisés sécurité/Afrique.

**À confirmer avec :**
- Top 10 `EventRootCode` par fréquence sur la période
- Évolution mensuelle de la part de chaque famille narrative
- Corrélation entre `QuadClass = "Material Conflict"` et `AvgTone`

**Annotation après viz DA :**
> _(à remplir)_
> Statut : ⬜ Non encore vérifié

---

## Insight 3 — Impact des événements sécuritaires du nord

**Hypothèse :**
> Nous anticipons une corrélation négative significative (r < -0,5) entre la fréquence des événements violents géolocalisés dans les départements d'Alibori et d'Atacora (`ActionGeo_ADM1Code`) et le `AvgTone` national dans les 2 à 4 semaines suivantes — suggérant un effet de halo négatif où les incidents localisés dégradent l'image globale du pays avec un décalage temporel observable.

**Logique contextuelle :**
Le mécanisme de halo négatif est documenté dans la littérature sur la communication de crise : un événement grave localisé dans un pays contamine la perception globale du pays pendant plusieurs semaines, notamment lorsque les médias internationaux ne différencient pas les régions touchées. Le Bénin étant souvent présenté comme "frontière sud du Sahel", chaque incident au nord amplifie ce cadrage.

**À confirmer avec :**
- Corrélation Spearman entre `NumMentions` filtré `ActionGeo_ADM1Code` nord et `AvgTone` national (avec décalage temporel de 2 et 4 semaines)
- Visualisation de la timeline double : incidents nord (barres) vs AvgTone national (courbe)
- Test de causalité de Granger si volume de données suffisant (>30 points mensuels)

**Annotation après viz DA :**
> _(à remplir)_
> Statut : ⬜ Non encore vérifié

---

## Insight 4 — Signaux faibles & pics précurseurs

**Hypothèse :**
> Nous anticipons que les données GDELT permettent d'identifier au moins 3 à 5 périodes d'anomalie médiatique sur 12 mois — caractérisées par un pic simultané de `NumMentions` et une chute de `AvgTone` — précédant de 1 à 3 semaines des événements critiques documentés (attaques, décisions politiques majeures, incidents diplomatiques). Ces fenêtres précurseurs se manifesteraient d'abord dans les sources spécialisées (médias sécurité, agences de presse africaines) avant de se diffuser aux médias généralistes.

**Logique contextuelle :**
GDELT agrège en temps quasi-réel des milliers de sources, y compris des sources locales et spécialisées rarement indexées ailleurs. Les signaux faibles apparaissent d'abord dans ces sources de niche avant de s'amplifier — c'est précisément là que réside la valeur prédictive du projet.

**À confirmer avec :**
- Détection d'anomalies Z-score sur `NumMentions` (seuil > 2σ)
- Détection de ruptures PELT sur la série temporelle `AvgTone`
- Croisement des dates anormales avec des événements documentés (vérification manuelle)

**Annotation après viz DA :**
> _(à remplir — à coupler avec résultats ML J3)_
> Statut : ⬜ Non encore vérifié

---

## Insight 5 — Événements & périodes marquants

**Hypothèse :**
> Nous anticipons que les 3 périodes les plus marquantes sur 12 mois sont : (1) un pic négatif lié à une ou plusieurs attaques sécuritaires dans le nord (probablement T3 2025), (2) un pic positif lié à un événement culturel ou diplomatique majeur (restitution patrimoniale, sommet régional, ou Voodoo Festival), et (3) une période de tension électorale ou institutionnelle générant un volume médiatique élevé à tonalité mixte. Ces trois moments structurent le récit annuel du Bénin dans les médias internationaux.

**Logique contextuelle :**
L'agenda médiatique du Bénin est rythmé par quelques événements prévisibles (Voodoo Festival en janvier, calendrier électoral) et des événements imprévisibles (incidents sécuritaires, décisions judiciaires). Le croisement de la connaissance contextuelle avec les pics GDELT permet d'identifier lesquels ont réellement capté l'attention internationale.

**À confirmer avec :**
- Top 10 dates par `NumMentions` absolu
- Top 5 dates par magnitude de `GoldsteinScale` (positif et négatif)
- Vérification manuelle des `SOURCEURL` et `Actor1Name` pour chaque pic identifié

**Annotation après viz DA :**
> _(à remplir — socle du storytelling pitch J4)_
> Statut : ⬜ Non encore vérifié

---

## Grille de mise à jour — À remplir au fil des viz DA

| Insight | Hypothèse | Statut après viz | Ajustement |
|---|---|---|---|
| I1 — Image & biais | Dégradation AvgTone, clivage franco/anglo | ⬜ | |
| I2 — Narratifs | Sécurité dominant, hausse T3 2025 | ⬜ | |
| I3 — Nord sécuritaire | Corrélation négative r < -0,5, halo -2/4 sem. | ⬜ | |
| I4 — Signaux faibles | 3–5 anomalies précurseurs détectables | ⬜ | |
| I5 — Événements marquants | 3 périodes clés : sécurité / culture / politique | ⬜ | |

> **Légende :** ✅ Confirmé · ⚠️ Nuancé (hypothèse partiellement juste) · ❌ Infirmé (revoir l'insight) · ⬜ Non encore vérifié

---

*Insights v0 — Hackathon iSHEERO × DataCamp 2026 · Data Scientist · 28 avril 2026*  
*→ Prochaine version : insights_v1.md (J3) après résultats ML + EDA complète*
