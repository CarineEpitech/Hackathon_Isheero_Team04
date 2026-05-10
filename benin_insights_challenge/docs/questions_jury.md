# Questions jury probables — Bénin Insights Challenge

**Hackathon iSHEERO × DataCamp 2026 · Équipe 04**
**Mis à jour : 10 mai 2026 — dataset 23 859 événements**

---

## Q1 — Pourquoi utiliser GDELT plutôt qu'une autre source ?

**Réponse :** GDELT est la seule base publique qui couvre l'ensemble des médias mondiaux avec des métadonnées structurées (tonalité, acteurs, géolocalisation, type d'événement). Pour analyser la couverture internationale du Bénin en 2025 sans budget de données, c'est la seule option viable à cette échelle. La contrepartie connue : GDELT mesure la couverture médiatique, pas les événements réels. Nos résultats décrivent la perception internationale du Bénin, pas ce qui s'est réellement passé sur le terrain.

---

## Q2 — Le nord du Bénin est-il vraiment perçu plus négativement ?

**Réponse :** Oui, statistiquement. Le ton moyen des événements géolocalisés au nord est −4,10, contre −1,41 au sud. Le test de Mann-Whitney confirme que cette différence est significative (U = 6 885 540, p < 0,001, r = 0,36 — effet modéré). Le résultat est robuste. Ce qui n'est pas établi, c'est la causalité : on observe une asymétrie géographique, pas un impact prouvé du nord sur l'image nationale. Le nord représente 947 événements sur 23 859 (4,0 %) — l'effet est réel, mais à interpréter avec prudence vu ce volume relatif. À noter : 91,2 % des événements ont une localisation générique pays, sans ville précise — les analyses géographiques fines portent sur les 8,8 % d'événements précisément localisés.

---

## Q3 — Votre modèle ML prédit-il vraiment quelque chose d'utile ?

**Réponse :** Le modèle atteint 70 % d'accuracy contre 62,7 % pour un DummyClassifier (classe majoritaire — 62,7 % des événements sont négatifs dans le nouveau dataset). Le gain réel est de +7 points de pourcentage. La validation croisée (5 folds stratifiés) confirme la stabilité : 69,5 % ± 0,1 %. Ce n'est pas un prédicteur causal — il capture des tendances structurelles de 2025, notamment la saisonnalité (décembre très négatif). Sans la variable `mois`, l'accuracy tombe à 65 %. Le modèle est honnête sur ses limites : il ne prédit pas l'avenir, il classifie les patterns de 2025.

---

## Q4 — Pourquoi la variable `mois` est-elle la plus importante ?

**Réponse :** Parce que 2025 a une saisonnalité très marquée. Décembre concentre 17,7 % du volume annuel avec un ton moyen de −2,65. Octobre est le mois le moins négatif (−0,03). Le modèle capture ces variations temporelles spécifiques à l'année. C'est utile pour classifier les données 2025, mais c'est aussi le principal risque de généralisation : si 2026 n'a pas de pic de décembre comparable, la performance chuterait vers les 65 % (résultat confirmé par le test sans `mois`).

---

## Q5 — Peut-on généraliser vos résultats à d'autres années ou d'autres pays ?

**Réponse :** Pour d'autres années : non directement. Le modèle est entraîné sur 2025 uniquement, et `mois` capture des anomalies propres à cette année. Un test temporel (entraînement sur jan-oct, test sur nov-déc) donne 50 % — en dessous du DummyClassifier — ce qui confirme le risque de distribution shift. Pour d'autres pays : la pipeline est réutilisable (changer `ActionGeo_CountryCode`), mais le modèle devrait être réentraîné. La méthodologie est transférable, les paramètres ne le sont pas.

---

## Q6 — La couverture nigériane biaise-t-elle votre analyse ?

**Réponse :** C'est une vraie question. 22,3 % des articles proviennent de sources `.ng` et le Nigeria est l'acteur principal dans 2 198 événements (6,6 × la France). Cela signifie que notre mesure du "regard international sur le Bénin" est en réalité très largement le regard ouest-africain, et plus précisément nigérian. Nous le documentons comme un résultat (insight 5) plutôt que comme un biais à corriger, parce que c'est la réalité de la couverture médiatique mondiale sur le Bénin. Une analyse par sous-groupe (sources `.ng` vs reste) permettrait de quantifier ce biais — c'est une piste pour la Phase 2.

---

## Q7 — Pourquoi n'avez-vous pas identifié les événements réels derrière les pics ?

**Réponse :** Les trois pics (10 janvier — 176 événements, ton −4,01 ; 17 avril — 218 événements, ton +2,14 ; séquence 7-12 décembre — 2 645 événements) ont été détectés et caractérisés statistiquement. Identifier les événements réels associés nécessiterait de croiser avec des sources externes (presse béninoise, bases d'incidents sécuritaires, agenda diplomatique) — des sources hors GDELT. Ce travail n'est pas réalisable dans le cadre du hackathon, mais c'est une extension naturelle pour la Phase 2. GDELT contient des URL sources : une exploration manuelle des `SOURCEURL` autour de ces dates serait le point de départ.

---

## Q9 — Pourquoi autant d'événements dans le Sud du Bénin ?

**Réponse :** Ce n'est pas que l'activité médiatique est concentrée au sud. C'est que 91,2 % des événements ont une localisation générique : GDELT attribue au centroïde pays (coordonnées dans le sud du Bénin, code ADM1=BN) tous les articles qui mentionnent "le Bénin" sans préciser de ville. Ces 21 758 événements ne se "passent" pas au sud — ils n'ont simplement pas de localisation plus précise. On le documente explicitement dans le dashboard (avertissement visible dans la section "Géographie interne") et dans tous nos documents. Les analyses géographiques fiables portent uniquement sur les 2 101 événements précisément localisés.

---

## Q8 — Que feriez-vous en Phase 2 avec plus de temps ?

**Réponse :** Trois priorités :

1. **Multi-pays** — Étendre le pipeline au Niger, Burkina Faso, Togo, et Ghana pour permettre une analyse comparative en Afrique de l'Ouest.
2. **Détection de précurseurs** — Implémenter un modèle de détection d'anomalies (PELT ou IsolationForest) pour identifier les signaux avant les crises, pas seulement au moment où elles surviennent.
3. **Enrichissement narratif** — Associer des thèmes lisibles aux codes CAMEO via un LLM (ex. "EventCode 14 = Protester → Manifestation") pour rendre les résultats accessibles aux décideurs non techniques.

Ces trois axes correspondent à ce que l'analyse Phase 1 ne peut pas faire seule.

---

*Bénin Insights Challenge — Équipe 04 — 10 mai 2026*
