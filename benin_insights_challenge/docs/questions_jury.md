# Questions jury probables — Bénin Insights Challenge

**Hackathon iSHEERO × DataCamp 2026 · Équipe 04**

---

## Q1 — Pourquoi utiliser GDELT plutôt qu'une autre source ?

**Réponse :** GDELT est la seule base publique qui couvre l'ensemble des médias mondiaux avec des métadonnées structurées (tonalité, acteurs, géolocalisation, type d'événement). Pour analyser la couverture internationale du Bénin en 2025 sans budget de données, c'est la seule option viable à cette échelle. La contrepartie connue : GDELT mesure la couverture médiatique, pas les événements réels. Nos résultats décrivent la perception internationale du Bénin, pas ce qui s'est réellement passé sur le terrain.

---

## Q2 — Le nord du Bénin est-il vraiment perçu plus négativement ?

**Réponse :** Oui, statistiquement. Le ton moyen des événements géolocalisés au nord est −4,36, contre −1,13 au sud. Le test de Mann-Whitney confirme que cette différence est significative (U = 1 213 720, p < 0,001, r = 0,42 — effet modéré à fort). Le résultat est robuste. Ce qui n'est pas établi, c'est la causalité : on observe une asymétrie géographique, pas un impact prouvé du nord sur l'image nationale. Le nord ne représente que 409 événements sur 10 722 (3,8 %) — l'effet est réel, mais à interpréter avec prudence vu ce faible volume.

---

## Q3 — Votre modèle ML prédit-il vraiment quelque chose d'utile ?

**Réponse :** Le modèle atteint 71 % d'accuracy contre 60 % pour un DummyClassifier (classe majoritaire). Le gain réel est de +11 points de pourcentage. La validation croisée (5 folds stratifiés) confirme la stabilité : 70,8 % ± 0,9 %. Ce n'est pas un prédicteur causal — il capture des tendances structurelles de 2025, notamment la saisonnalité (décembre très négatif). Sans la variable `mois`, l'accuracy tombe à 64 %. Le modèle est honnête sur ses limites : il ne prédit pas l'avenir, il classifie les patterns de 2025.

---

## Q4 — Pourquoi la variable `mois` est-elle la plus importante ?

**Réponse :** Parce que 2025 a une saisonnalité très marquée. Décembre concentre 18,2 % du volume annuel avec un ton moyen de −2,46. Octobre est le seul mois positif (+0,23). Le modèle capture ces variations temporelles spécifiques à l'année. C'est utile pour classifier les données 2025, mais c'est aussi le principal risque de généralisation : si 2026 n'a pas de pic de décembre comparable, la performance chuterait vers les 64 % (résultat confirmé par le test sans `mois`).

---

## Q5 — Peut-on généraliser vos résultats à d'autres années ou d'autres pays ?

**Réponse :** Pour d'autres années : non directement. Le modèle est entraîné sur 2025 uniquement, et `mois` capture des anomalies propres à cette année. Un test temporel (entraînement sur jan-oct, test sur nov-déc) donne 50 % — en dessous du DummyClassifier — ce qui confirme le risque de distribution shift. Pour d'autres pays : la pipeline est réutilisable (changer `ActionGeo_CountryCode`), mais le modèle devrait être réentraîné. La méthodologie est transférable, les paramètres ne le sont pas.

---

## Q6 — La couverture nigériane biaise-t-elle votre analyse ?

**Réponse :** C'est une vraie question. 21,5 % des articles proviennent de sources `.ng` et le Nigeria est l'acteur principal dans 696 événements (5× la France). Cela signifie que notre mesure du "regard international sur le Bénin" est en réalité très largement le regard ouest-africain, et plus précisément nigérian. Nous le documentons comme un résultat (insight 5) plutôt que comme un biais à corriger, parce que c'est la réalité de la couverture médiatique mondiale sur le Bénin. Une analyse par sous-groupe (sources `.ng` vs reste) permettrait de quantifier ce biais — c'est une piste pour la Phase 2.

---

## Q7 — Pourquoi n'avez-vous pas identifié les événements réels derrière les pics ?

**Réponse :** Les trois pics (10 janvier, 17 avril, séquence 7-12 décembre) ont été détectés et caractérisés statistiquement. Identifier les événements réels associés nécessiterait de croiser avec des sources externes (presse béninoise, bases d'incidents sécuritaires, agenda diplomatique) — des sources hors GDELT. Ce travail n'est pas réalisable dans le cadre du hackathon, mais c'est une extension naturelle pour la Phase 2. GDELT contient des URL sources : une exploration manuelle des `SOURCEURL` autour de ces dates serait le point de départ.

---

## Q8 — Que feriez-vous en Phase 2 avec plus de temps ?

**Réponse :** Trois priorités :

1. **Multi-pays** — Étendre le pipeline au Niger, Burkina Faso, Togo, et Ghana pour permettre une analyse comparative en Afrique de l'Ouest.
2. **Détection de précurseurs** — Implémenter un modèle de détection d'anomalies (PELT ou IsolationForest) pour identifier les signaux avant les crises, pas seulement au moment où elles surviennent.
3. **Enrichissement narratif** — Associer des thèmes lisibles aux codes CAMEO via un LLM (ex. "EventCode 14 = Protester → Manifestation") pour rendre les résultats accessibles aux décideurs non techniques.

Ces trois axes correspondent à ce que l'analyse Phase 1 ne peut pas faire seule.

---

*Bénin Insights Challenge — Équipe 04 — 9 mai 2026*
