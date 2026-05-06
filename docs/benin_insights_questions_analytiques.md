# Questions Analytiques Documentées — Bénin Insights Challenge

## Hackathon iSHEERO × DataCamp 2026 · Phase 1 · 27 avril → 5 mai 2026

**Source de données principale :** GDELT Project (Global Database of Events, Language and Tone)  
**Périmètre géographique :** Bénin (`ActionGeo_CountryCode = 'BN'`)  
**Période d'analyse :** 2025

---

## Introduction

Le présent document formalise les **5 questions analytiques prioritaires** retenues par l'équipe pour le Bénin Insights Challenge. Ces questions guident l'ensemble du pipeline analytique — de l'extraction GDELT à la construction du dashboard Streamlit, en passant par les modèles ML et les insights finaux présentés au jury.

Chaque question est documentée selon une structure commune : **formulation**, **justification stratégique**, **indicateurs GDELT mobilisables**, **méthodes d'analyse associées**, et **visualisations cibles**.

---

## Question 1 — Évolution et biais de l'image médiatique internationale du Bénin

### Formulation

> Comment l'image médiatique du Bénin a-t-elle évolué au cours des 12 derniers mois, et varie-t-elle selon les espaces médiatiques (Afrique, Occident, francophone, anglophone) ?

### Justification stratégique

Cette question fusionne deux axes analytiques complémentaires : l'**évolution temporelle** de la couverture et les **biais structurels** selon les zones géographiques et linguistiques. Elle constitue le socle interprétatif de toutes les autres questions : comprendre *comment* le Bénin est perçu, et *par qui*, conditionne la lecture de tous les narratifs et signaux faibles identifiés.

### Indicateurs GDELT mobilisables

|Indicateur GDELT|Rôle analytique|
|-|-|
|`AvgTone`|Tonalité moyenne par article (positif/négatif) — proxy de l'image|
|`Actor1CountryCode` / `Actor2CountryCode`|Identification de l'origine géographique de la couverture|
|`SOURCEURL`|Extraction du domaine source → pays et langue de l'éditeur|
|`MonthYear`|Agrégation temporelle mensuelle pour l'analyse de tendances|
|`NumMentions`|Volume de couverture par période et par espace médiatique|
|`GoldsteinScale`|Score de stabilité de l'événement couvert (−10 à +10)|

### Méthodes d'analyse

* **Analyse de tendance temporelle** : évolution mensuelle de `AvgTone` moyen pour le Bénin
* **Segmentation géographique** : regroupement des sources par continent et famille linguistique (francophone / anglophone / autre) via le domaine de la `SOURCEURL`
* **Test de différence** : comparaison statistique des moyennes de `AvgTone` entre zones (test t ou ANOVA)
* **Heatmap temporelle** : matrice Mois × Espace médiatique colorée par tonalité moyenne

### Visualisations cibles

* Courbe d'évolution temporelle de `AvgTone` (multi-série : Afrique / Occident / francophone / anglophone)
* Carte choroplèthe : intensité et tonalité de la couverture par pays source
* Boîte à moustaches (boxplot) par espace médiatique pour comparer la dispersion du ton

---

## Question 2 — Narratifs dominants et leur évolution

### Formulation

> Quels narratifs dominent actuellement la couverture médiatique du Bénin, et comment évoluent-ils ?

### Justification stratégique

Identifier les narratifs récurrents permet de dépasser la simple mesure quantitative (volume, ton) pour atteindre le **sens qualitatif** de la couverture. Cette question informe directement le travail du Data Scientist (formulation des 5 insights) et du Data Analyst (choix des visualisations thématiques du dashboard).

### Indicateurs GDELT mobilisables

|Indicateur GDELT|Rôle analytique|
|-|-|
|`EventCode` / `EventRootCode`|Code CAMEO de l'événement — taxonomie de 300+ types d'événements|
|`QuadClass`|Catégorie d'action : Verbal Coop / Material Coop / Verbal Conflict / Material Conflict|
|`AvgTone`|Tonalité associée à chaque type narratif|
|`GoldsteinScale`|Impact perçu de l'événement sur la stabilité|
|`MonthYear`|Dimension temporelle pour tracker l'évolution des narratifs|
|`Actor1Type1Code`|Type d'acteur impliqué (gouvernement, ONG, entreprise, etc.)|

### Méthodes d'analyse

* **Fréquence des codes CAMEO** : top 10 des `EventRootCode` les plus fréquents sur la période
* **Analyse de clustering** (ML Engineer) : regroupement des événements par profil CAMEO + `QuadClass` pour identifier des familles narratives latentes
* **Analyse de sentiment** : corrélation entre type de narratif (`EventRootCode`) et tonalité (`AvgTone`)
* **Évolution temporelle** : courbes de fréquence mensuelle par famille narrative

### Visualisations cibles

* Treemap ou bar chart des top codes CAMEO par volume de mentions
* Diagramme de flux (Sankey) : narratifs → tonalité → espace médiatique
* Graphique linéaire multi-séries : évolution mensuelle des 3–5 narratifs dominants

---

## Question 3 — Influence des événements sécuritaires du nord sur l'image globale

### Formulation

> Les événements sécuritaires dans le nord du Bénin influencent-ils l'image globale du pays dans les médias ?

### Justification stratégique

Le nord du Bénin est confronté depuis 2021 à des incursions jihadistes en provenance du Burkina Faso et du Niger. Cette question teste l'hypothèse que la **couverture sécuritaire localisée** contamine l'image globale du pays — un mécanisme dit de "halo négatif". Elle est directement actionnelle pour les décideurs (communication institutionnelle, diplomatie) et très valorisée par les jurys de type policy/data.

### Indicateurs GDELT mobilisables

|Indicateur GDELT|Rôle analytique|
|-|-|
|`ActionGeo_ADM1Code`|Code de la région administrative → filtrer le nord (Alibori, Atacora)|
|`ActionGeo_Lat` / `ActionGeo_Long`|Géolocalisation précise des événements|
|`EventCode`|Codes CAMEO liés à la violence : 18x (Assault), 19x (Fight), 20x (Use unconventional mass violence)|
|`GoldsteinScale`|Mesure de l'impact déstabilisateur de l'événement|
|`AvgTone`|Tonalité de la couverture associée à ces événements|
|`NumMentions`|Volume de couverture internationale générée par ces événements|

### Méthodes d'analyse

* **Filtre géographique** : isolation des événements dans les départements du nord (`ActionGeo_ADM1Code` correspondant à Alibori / Atacora / Borgou)
* **Analyse de corrélation temporelle** : corrélation (Pearson ou Spearman) entre pic d'événements sécuritaires au nord et variation de `AvgTone` national
* **Test de causalité de Granger** (si données suffisantes) : les événements sécuritaires précèdent-ils statistiquement la dégradation de l'image ?
* **Comparaison régionale** : `AvgTone` nord vs reste du pays

### Visualisations cibles

* Carte de densité des événements sécuritaires au nord + overlay de la tonalité nationale par période
* Graphique de corrélation : axe X = nombre d'incidents sécuritaires au nord, axe Y = `AvgTone` moyen national
* Timeline double : incidents sécuritaires (barres) + tonalité globale (ligne) superposés

---

## Question 4 — Détection de signaux faibles et pics médiatiques précurseurs

### Formulation

> Peut-on détecter des signaux faibles ou des pics médiatiques annonçant l'émergence d'un événement critique ?

### Justification stratégique

Cette question introduit une **dimension prédictive et d'alerte précoce** qui distingue une analyse descriptive standard d'un véritable système d'intelligence médiatique. Elle est la plus technique et la plus valorisante pour le jury, car elle mobilise des méthodes ML avancées (détection d'anomalies, séries temporelles) et répond à un besoin réel des décideurs publics et des acteurs de la sécurité.

### Indicateurs GDELT mobilisables

|Indicateur GDELT|Rôle analytique|
|-|-|
|`NumMentions`|Volume brut — un pic anormal est un signal potentiel|
|`NumArticles`|Nombre d'articles distincts — indicateur de diversification de la couverture|
|`AvgTone`|Variation brutale de tonalité = signal de rupture narrative|
|`GoldsteinScale`|Chute rapide du score de stabilité = signal précurseur d'instabilité|
|`EventCode`|Apparition soudaine de codes inhabituels (violence, crise)|
|`MonthYear` / `SQLDATE`|Granularité temporelle fine pour la détection d'anomalies|

### Méthodes d'analyse

* **Détection d'anomalies statistiques** : méthode Z-score ou IQR sur les séries `NumMentions` et `AvgTone` pour identifier les dates atypiques
* **Modèle de détection de ruptures** : algorithme PELT (Pruned Exact Linear Time) ou BOCPD (Bayesian Online Change Point Detection) sur la série temporelle
* **Clustering temporel** (ML Engineer) : identifier les fenêtres temporelles où plusieurs signaux convergent simultanément
* **Analyse des précurseurs** : pour chaque pic avéré, regarder rétrospectivement les 2–4 semaines précédentes pour identifier des patterns annonciateurs

### Visualisations cibles

* Série temporelle annotée : `NumMentions` avec marqueurs sur les anomalies détectées
* Graphique de chaleur (heatmap) : intensité des signaux par semaine et par type d'indicateur
* Dashboard interactif : slider temporel permettant de naviguer et d'inspecter les pics (Streamlit)

---

## Question 5 — Événements et périodes les plus marquants pour le Bénin

### Formulation

> Quels sont les événements ou périodes les plus marquants pour le Bénin selon les données médiatiques récentes ?

### Justification stratégique

Cette question joue un rôle de **storytelling final** : elle synthétise l'ensemble des analyses précédentes en un récit chronologique des moments-clés de la vie médiatique du Bénin sur 12 mois. Elle est indispensable pour le pitch vidéo (3 min) et le résumé d'une page, car elle offre des repères temporels concrets et facilement communicables à un jury non-technique. Elle ancre l'analyse dans des faits vérifiables et narrativement forts.

### Indicateurs GDELT mobilisables

|Indicateur GDELT|Rôle analytique|
|-|-|
|`NumMentions`|Identifier les périodes de pic de couverture absolue|
|`AvgTone`|Identifier les périodes de tonalité extrême (très positive ou très négative)|
|`GoldsteinScale`|Repérer les événements à fort impact stabilisateur ou déstabilisateur|
|`EventCode`|Caractériser la nature des événements-clés|
|`SQLDATE`|Horodatage précis pour la chronologie|
|`Actor1Name` / `Actor2Name`|Acteurs impliqués dans les moments marquants|

### Méthodes d'analyse

* **Ranking des événements** : top 10 des événements par `NumMentions` et par magnitude de `GoldsteinScale`
* **Segmentation par quintile de tonalité** : identifier les 5 meilleures et 5 pires périodes en termes d'image
* **Analyse narrative qualitative** : pour chaque pic identifié, croiser avec des connaissances de contexte (élections, incidents sécuritaires, événements culturels, décisions économiques)
* **Construction d'une timeline enrichie** : chronologie visuelle annotée des 5–10 moments-clés

### Visualisations cibles

* Timeline interactive annotée (axe temporel + bulles d'événements cliquables)
* Bar chart horizontal : top 10 événements par volume de mentions avec code couleur par `QuadClass`
* Tableau récapitulatif des 5 périodes marquantes : date, nature de l'événement, tonalité, volume, espace médiatique dominant

---

## Synthèse — Matrice de correspondance des questions

|#|Question|Type d'analyse|Rôle dans le projet|
|-|-|-|-|
|Q1|Évolution et biais de l'image|Temporelle + comparative|Cadrage général — socle interprétatif|
|Q2|Narratifs dominants|Thématique + NLP|Contenu — alimentation du dashboard|
|Q3|Impact des événements sécuritaires|Causale + géospatiale|Insight sectoriel — fort potentiel jury|
|Q4|Signaux faibles et pics précurseurs|Prédictive + anomalie|Valeur ajoutée ML — différenciation technique|
|Q5|Événements et périodes marquants|Synthétique + narrative|Storytelling final — pitch et résumé|

---

## Dépendances et calendrier

|Jour|Action clé liée à ces questions|
|-|-|
|J1|✅ Ce document — questions validées en équipe|
|J2|Data Engineer livre `benin_clean.csv` → Data Analyst commence EDA sur Q1 et Q5|
|J3|ML Engineer livre clustering → alimenter Q2 et Q4 · 5 viz EDA complètes|
|J4|Data Scientist formule les 5 insights finaux · Dashboard déployé avec Q1–Q5|
|J5|Soumission finale · Pitch vidéo basé sur Q5 (storytelling)|

---

## Sources et références

* **GDELT Project** : https://www.gdeltproject.org/
* **Documentation CAMEO** : Conflict and Mediation Event Observations Codebook — Schrodt, P.A. (2012)
* **BigQuery GDELT** : `gdelt-bq.gdeltv2.events` — filtre `ActionGeo_CountryCode = 'BN'`, `Year >= 2025`
* **Colonnes clés** : `EventCode`, `GoldsteinScale`, `AvgTone`, `NumMentions`, `NumArticles`, `Actor1CountryCode`, `ActionGeo_ADM1Code`, `SOURCEURL`, `SQLDATE`

---

