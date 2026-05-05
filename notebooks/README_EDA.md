# README — Notebook 02 : Analyse Exploratoire des Données

**Hackathon iSHEERO × DataCamp 2026 — Bénin Insights Challenge**

Ce document accompagne le notebook `02_eda_exploration.ipynb`. Il explique le pourquoi des choix méthodologiques, les dépendances, la procédure de reproduction et les liens avec le reste du livrable.

---

## **1. Objectif du notebook**

Produire une analyse exploratoire complète des données médiatiques GDELT concernant le Bénin sur la période **janvier → décembre 2025**, en couvrant les 5 questions analytiques définies par l'équipe en kickoff.

Le notebook est **descriptif** — pas prédictif. La modélisation prédictive (clustering, détection de ruptures, classification de sentiment) est confiée au ML Engineer dans `04_modele_ml_final.ipynb`. L'interprétation finale et la formulation des 5 insights actionnables relèvent du Data Scientist (`docs/insights_final.md`).

---

## **2. Données en entrée**

| Fichier | Localisation | Producteur | Description |
|---------|--------------|------------|-------------|
| `benin_clean.csv` | `data/processed/` | Data Engineer | Export GDELT v2.0 nettoyé et enrichi, filtré sur le Bénin (`ActionGeo_CountryCode = 'BC'`, année 2025) |

**Volumétrie :** 10 722 événements, 41 colonnes, 12,9 Mo en mémoire.

**Origine de l'enrichissement.** Les colonnes dérivées (`mois`, `trimestre`, `mois_annee`, `jour_semaine`, `ton_categorie`, `goldstein_categorie`, `quadclass_label`, `zone_benin`, `source_domaine`) sont produites dans le notebook `01_pipeline_nettoyage.ipynb`. Ce notebook EDA les utilise telles quelles pour éviter la duplication et préserver une source de vérité unique.

**Fichier brut (`benin_raw.csv`)** non utilisé ici. Il sert uniquement de référence en cas de besoin de retour aux données originales.

---

## **3. Architecture du notebook**

| Section | Objet | Question analytique |
|---------|-------|---------------------|
| 1 | Préparation environnement | — |
| 2 | Chargement | — |
| 3 | Dictionnaire des variables | — |
| 4 | Qualité des données (cohérence, NaN, doublons, aberrations) | — |
| 5 | Volumétrie temporelle (Viz 1) | Q5 |
| 6 | Tonalité médiatique (Viz 2) | Q1 |
| 7 | Sources médiatiques (Viz 3) | Q1 |
| 8 | Narratifs et QuadClass | Q2 |
| 9 | Géographie des événements (Viz 4) | Q3 |
| 10 | Score de Goldstein (Viz 5) | Q1, Q5 |
| 11 | Détection des pics et événements marquants | Q4, Q5 |
| 12 | Synthèse provisoire des 5 questions | Q1 à Q5 |

Les **5 visualisations obligatoires** définies par la roadmap Data Analyst sont signalées explicitement (Viz 1 à Viz 5).

---

## **4. Choix techniques principaux**

### **4.1. Stack de visualisation : Matplotlib + Seaborn**

Choix retenu pour la cohérence et la portabilité (export propre en PNG/PDF, pas de dépendance navigateur, taille de fichier maîtrisée). Plotly est réservé au dashboard Streamlit interactif (`app/streamlit_app.py`), qui est un livrable distinct.

### **4.2. Gestion des valeurs manquantes**

Conservées telles quelles. Chaque analyse impactée travaille sur le sous-ensemble disponible et le mentionne explicitement. L'imputation aurait masqué une réalité structurelle du dataset (la majorité des événements n'ont effectivement pas d'acteur 2 ou de type identifié).

### **4.3. Granularité temporelle**

- **Mensuelle** pour les vues globales (sections 5, 6, 8) — lisibilité maximale sur 12 points.
- **Quotidienne** pour la détection de pics (section 11) — sensibilité requise pour identifier les anomalies.
- **Lissage moyenne mobile 7 j et 30 j** pour le score de Goldstein (section 10) — équilibre entre sensibilité aux variations courtes et lecture macro.

### **4.4. Détection d'anomalies**

Méthode Z-score avec seuil |z| > 2 sur la série quotidienne des mentions cumulées. Méthode simple, robuste pour cet horizon (12 mois), explicable au jury non-technique. Les méthodes plus avancées (PELT, BOCPD) sont laissées au ML Engineer.

### **4.5. Filtrage géographique pour Q3**

La colonne enrichie `zone_benin` (nord / centre / sud) est utilisée comme proxy. Elle est dérivée de la latitude par seuils géographiques. Pour une analyse plus fine au niveau département (Alibori, Atacora, Borgou), il faudrait recourir à `ActionGeo_ADM1Code` — non fait dans cette EDA pour rester lisible, à creuser dans le dashboard.

---

## **5. Convention de documentation**

Chaque section suit une structure identique :

- **Ce qu'on veut savoir** — la question posée à la donnée.
- **Ce qu'on fait** — la manipulation et la visualisation.
- **Ce qu'on observe** — la lecture des résultats en français accessible.

Pour chaque **décision méthodologique majeure**, un encadré « Note méthodologique » donne le choix retenu et au moins un (souvent deux) choix alternatifs avec la justification du rejet. Cet encadré sert deux objectifs : transparence pour le jury et pédagogie pour le reste de l'équipe.

---

## **6. Reproductibilité**

### **6.1. Dépendances**

```
pandas >= 2.0
numpy >= 1.24
matplotlib >= 3.7
seaborn >= 0.12
```

Versions exactes figées dans `requirements.txt` à la racine du repo (livrable du Data Engineer en J4).

### **6.2. Lancement**

Depuis la racine du repo :

```bash
jupyter notebook notebooks/02_eda_exploration.ipynb
```

Le notebook charge `data/processed/benin_clean.csv` automatiquement. Un fallback est prévu si le notebook est lancé depuis son propre dossier.

### **6.3. Test from scratch**

Avant la soumission, exécuter `Kernel → Restart & Run All` pour vérifier qu'aucune cellule ne dépend d'un état précédent perdu. C'est le test de reproductibilité exigé par la roadmap.

---

## **7. Livrables associés et responsabilités**

| Livrable | Rôle responsable | Lien avec ce notebook |
|----------|------------------|------------------------|
| `01_pipeline_nettoyage.ipynb` | Data Engineer | Produit les colonnes utilisées ici |
| `03_feature_engineering.ipynb` | ML Engineer | Réutilise les variables explorées ici |
| `04_modele_ml_final.ipynb` | ML Engineer | Approfondit Q4 (anomalies, ruptures) |
| `app/streamlit_app.py` | Data Analyst | Reprend Viz 1, 3, 4 en interactif |
| `docs/insights_final.md` | Data Scientist | S'appuie sur la synthèse section 12 |
| `docs/resume_une_page_final.md` | Data Scientist + Data Analyst | Reprend les 5 observations clés |

---

## **8. Limites connues**

- **Couverture temporelle** : 16 jours sur 365 sans aucun événement enregistré (4,4 %). Pas un problème pour les analyses agrégées mensuelles, à mentionner si des analyses fines hebdomadaires sont conduites.
- **Biais de source** : la couverture est dominée par la presse nigériane (5 premiers domaines). Les conclusions sur la « tonalité médiatique » sont en réalité des conclusions sur la « tonalité médiatique vue par la presse régionale ouest-africaine », pas par les médias béninois ni par les grands médias mondiaux.
- **Géographie déséquilibrée** : 94 % des événements géolocalisés au sud. La carte (Viz 4) reflète cette réalité, qui est aussi un biais de présence médiatique (Cotonou concentre les institutions et les correspondants étrangers).
- **AvgTone vs GoldsteinScale divergents** : le ton (négatif) et le Goldstein (positif) racontent deux histoires différentes. Une lecture combinée est posée en section 10, mais la causalité reste à tester par le DS / ML.

---

## **9. Mentions**

- **Données** : GDELT Project ([gdeltproject.org](https://www.gdeltproject.org)) — licence ouverte.
- **Outils IA utilisés** : assistance IA pour la rédaction des sections explicatives et la génération du squelette du notebook. Toutes les analyses, choix méthodologiques et interprétations sont validés par l'auteur. Mention conforme aux règles du hackathon (cf. PDF officiel, page 11).
- **Auteur** : Kitra (Sylvère Bamenou), Data Analyst de l'équipe.

---

*Dernière mise à jour : mai 2026.*
