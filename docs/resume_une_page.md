# Ce que les médias mondiaux disent du Bénin — et ce que ça change
## Résumé d'une page · v2 · Bénin Insights Challenge · Hackathon iSHEERO × DataCamp 2026

---

### Ce qu'on a fait

Nous avons analysé **10 722 documents médiatiques** publiés sur le Bénin dans les médias du monde entier sur toute l'année 2025 (349 jours couverts sur 365), grâce à GDELT — une base de données qui surveille la presse internationale en temps réel. Nous avons ensuite appliqué des algorithmes de détection d'anomalies pour identifier les moments-charnières invisibles à l'œil nu.

---

### Ce qu'on a trouvé — 5 résultats clés

**1 — L'image médiatique du Bénin est structurellement négative**

Sur l'ensemble de l'année 2025, le ton moyen des articles consacrés au Bénin reste négatif chaque mois, sans exception. Le Nigeria domine la couverture, aussi bien comme pays d'origine des acteurs couverts que comme source médiatique principale. La coopération diplomatique est le type d'événement le plus fréquent (65 % des événements), mais ce sont les événements conflictuels qui génèrent la tonalité la plus défavorable.

*Chiffre clé : ton moyen annuel = −1,22 (sur une échelle de −100 à +100) — aucun mois positif sur 12.*

---

**2 — La conflictualité représente plus d'un quart des événements couverts**

Les événements de coopération verbale dominent le volume (65,2 %), mais les conflits verbaux et matériels combinés représentent 25,5 % de la couverture. Le paradoxe central : le score de stabilité géopolitique (Goldstein) est légèrement positif (+0,56 en moyenne) alors que la tonalité médiatique est négative (−1,22) — les médias perçoivent les événements béninois plus durement que leur impact réel ne le justifierait.

*Chiffre clé : 25,5 % de la couverture = événements conflictuels (verbal + matériel).*

---

**3 — Le nord du Bénin est disproportionnellement négatif dans les médias**

Le nord (départements Alibori, Atacora, Borgou) ne représente que 4,9 % des événements géolocalisés. Pourtant, son profil médiatique est radicalement différent du reste du pays : ton moyen de −4,29 contre −1,09 pour le sud, et 22,8 % d'événements sécuritaires contre 6,7 %. L'asymétrie de caractère est réelle, même si la causalité entre incidents au nord et image globale reste à établir.

*Chiffre clé : le nord affiche un ton 3 fois plus négatif que le sud (−4,29 vs −1,09), sur 4,9 % des événements.*

---

**4 — Les pics médiatiques sont détectables et concentrés en décembre**

Notre approche multi-méthodes (Z-score, MAD, fenêtre glissante) a identifié 8 dates anormales sur l'année : 10 janvier, 17 avril, et une séquence de 6 jours consécutifs du 7 au 12 décembre 2025. Décembre représente à lui seul 18,2 % du volume annuel — soit +131 % au-dessus du volume médian mensuel. Ces pics sont détectés au moment où ils surviennent ; la détection de signaux *précurseurs* reste l'étape suivante.

*Chiffre clé : 8 dates anormales détectées — dont 6 concentrées sur une seule semaine de décembre.*

---

**5 — Décembre 2025 a dominé l'image du Bénin cette année**

Sur les 12 derniers mois, décembre concentre à lui seul 1 954 événements sur 10 722, soit 18,2 % du volume annuel total. Les deux autres moments notables sont le 10 janvier 2025 (pic isolé à ton négatif, Goldstein = −1,97) et le 17 avril 2025 (pic à ton positif, Goldstein = +0,94 — seul moment de tonalité positive parmi les anomalies). Ces trois séquences résument l'essentiel de l'agenda médiatique du Bénin en 2025.

*Chiffre clé : 3 séquences temporelles (janvier, avril, décembre) concentrent les moments les plus marquants de l'année.*

---

### Ce que ça veut dire concrètement

Pour les décideurs publics, les communicants et les investisseurs, ces résultats suggèrent trois actions prioritaires :

1. **Différencier l'image du nord et du reste du pays** dans les communications internationales, pour éviter que chaque incident localisé ne contamine la réputation globale.

2. **Investir dans une veille médiatique en temps réel** basée sur des outils comme GDELT, pour détecter les crises de réputation avant qu'elles ne s'amplifient.

3. **Capitaliser sur les événements culturels et diplomatiques** — qui génèrent une couverture positive — pour rééquilibrer le narratif international sur le Bénin.

---

### Comment on a travaillé

| Données utilisées | Méthodes appliquées | Outils |
|---|---|---|
| 10 722 événements médiatiques GDELT (2025) | Analyse de tendances temporelles | Python · Pandas |
| Sources internationales (Nigeria dominant) | Détection d'anomalies (Z-score, MAD, rolling) | Scikit-learn |
| Couverture du 1er janv. au 31 déc. 2025 | Segmentation géographique nord/centre/sud | Streamlit |
| 349 jours sur 365 couverts | Analyse des codes CAMEO (17 catégories) | GDELT BigQuery |

---

*Résumé d'une page v2 — Hackathon iSHEERO × DataCamp 2026 · 6 mai 2026*
