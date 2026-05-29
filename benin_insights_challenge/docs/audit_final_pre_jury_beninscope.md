# AUDIT FINAL PRÉ-JURY — BENINSCOPE / TERROIR
> Audit QA complet — perspectives : testeur senior, utilisateur final, ONG, maire, jury, investisseur  
> Produit : **TERROIR** — application web territoriale quasi temps réel  
> Temps restant estimé : < 2 heures

---

## SOMMAIRE DES RISQUES

| Criticité | Nombre | Doit être corrigé avant jury |
|---|---|---|
| Critique | 7 | Oui, absolument |
| Importante | 12 | Si temps disponible |
| Mineure | 9 | À ignorer |

---

## PARTIE 1 — AUDIT PAR ÉCRAN

---

### 1.1 CARTE LIVE

#### Ce que voit un utilisateur non averti

La carte s'ouvre sur un filtre 24h. En démo live, si le poller GDELT vient de redémarrer ou n'a pas tourné depuis 24h, **la carte sera vide**. Premier contact = blanc.

Le panneau "Statut GDELT Live" en bas s'ouvre automatiquement et noie l'écran de statistiques incompréhensibles : "Fichier traité", "Évén. mondiaux", "Base live totale", "Qualité des positions". **Un maire ou une ONG ne sait pas ce que c'est. Le jury non plus, à moins d'être data engineer.**

---

#### Problèmes identifiés — Carte Live

| # | Problème | Gravité |
|---|---|---|
| C1 | Le filtre par défaut est **24h**. En démo, il est probable que la carte soit vide ou quasi-vide (live data insuffisante). | **Critique** |
| C2 | Le footer contient **`http://localhost:8501`** en dur (lien Streamlit). En production sur Railway, ce lien est cassé pour tout le monde. En démo, le jury clique et atterrit sur une page d'erreur. | **Critique** |
| C3 | La légende dit **"Neutre GDELT"** pour la couleur bleue. "GDELT" est un terme inconnu du public et du jury. | **Importante** |
| C4 | Deux boutons de refresh côte à côte : **"Rafraîchir"** et **"Actualiser GDELT"**. La différence n'est pas claire pour un utilisateur. En démo, "Actualiser GDELT" déclenche un cycle de ~30 secondes pendant lequel l'application est bloquée. | **Importante** |
| C5 | La bande contexte explique que le badge "Nouveau" marque les événements "du dernier jour de la fenêtre affichée". En filtre 30 jours, un événement d'il y a 29 jours porte le badge "Nouveau". **C'est factuellement faux et confus.** | **Importante** |
| C6 | Le panneau "Statut GDELT Live" est **ouvert par défaut** (`collapse show`). Il expose : fichier traité (URL interne GDELT), évén. mondiaux, z-scores de qualité. Tout cela est technique et fait prototype. | **Importante** |
| C7 | La légende a 3 niveaux de rouge ("Critique", "Alerte sécurité", "Sécuritaire") mais la bande contexte n'en mentionne que 2. **Incohérence entre légende et texte.** | **Mineure** |
| C8 | Le terme "Sécuritaire" dans la légende est un adjectif. Les autres items sont des noms. Hétérogénéité de style. | **Mineure** |

---

### 1.2 TERROIR (Score STT)

#### Ce que voit un maire

Il arrive sur la page TERROIR. Il voit une bannière "Zone la plus surveillée : Alibori — Score TERROIR 0.00 — Normal". Il se demande pourquoi Alibori est "la plus surveillée" si tout est Normal. **La logique est inversée : `stt.scores[0]` est le premier département par ordre d'arrivée, pas le plus dangereux.**

Il voit des cartes avec "CAMEO : 1.23" et "Tone : -0.87". Il ne sait pas ce que ça signifie. Il voit "% sensible : 12%". Il ne sait pas "sensible à quoi".

Il lit "Mise à jour en temps réel" mais doit cliquer sur "Actualiser" pour voir quelque chose.

---

#### Problèmes identifiés — TERROIR

| # | Problème | Gravité |
|---|---|---|
| T1 | **`sttTopAlert = stt.scores[0]`** : la bannière "Zone la plus surveillée" affiche toujours le premier département du tableau, indépendamment de son niveau de dangerosité. Si le tableau est trié alphabétiquement et qu'Alibori a un score 0.00, la bannière dira "Zone la plus surveillée : Alibori — Normal". Contradiction visuelle directe. | **Critique** |
| T2 | **STT scores probablement tous à 0.00** si la fenêtre live 14j est vide. Le nouveau code `stt.py` utilise `now()` comme ref_date. Si le poller n'a pas généré de données live récentes (ou si benin_live.parquet ne contient rien de < 14j), compute_all_departments retourne des scores nuls. En démo, toutes les cartes afficheront "0.00 — Normal". | **Critique** |
| T3 | **"Mise à jour en temps réel"** dans le sous-titre TERROIR. C'est faux : la mise à jour est manuelle (bouton Actualiser). Un jury attentif notera l'incohérence. | **Importante** |
| T4 | **"adm1_code" visible** dans les petites cartes : "BN01", "BN18", "Parakou" (ville, pas département). Ces codes internes ne signifient rien pour un utilisateur et font prototype. | **Importante** |
| T5 | **"z_cameo"** et **"z_tone"** affichés dans les cartes de niveau ≥ 1. Des z-scores statistiques bruts (ex: "CAMEO : 2.14", "Tone : -1.87") sont incompréhensibles pour une ONG ou un maire. | **Importante** |
| T6 | **"% sensible"** : formulation ambiguë. Sensible à quoi ? | **Importante** |
| T7 | **"Évts 14j"** : abréviation laide et peu naturelle. | **Mineure** |
| T8 | **"STT"** n'est jamais défini dans l'UI. Les cartes montrent "1.23 STT" sans explication de l'acronyme (Score de Tension Territorial). | **Importante** |
| T9 | **"Zone prioritaire Nord"** badge : très vague. Prioritaire pour qui ? Pour quoi ? | **Mineure** |
| T10 | Le graphique STT montre des barres dont la hauteur peut être trop petite pour être lisible si tous les scores sont < 0.5. Absence de message d'état visible si tous à 0. | **Mineure** |

---

### 1.3 SIGNALER

#### Ce que voit un citoyen ordinaire

Il arrive sur "Signaler un événement territorial". Il doit saisir des coordonnées GPS en degrés décimaux (Latitude : 6.0–12.5, Longitude : 0.7–3.9). **Un citoyen béninois en situation d'urgence ne connaît pas ses coordonnées GPS.** Le bouton GPS peut fonctionner, mais nécessite d'autoriser la géolocalisation dans le navigateur.

Il voit le badge "tension_communautaire" avec underscore dans la liste des signalements récents. Il voit "pression_institutionnelle". Ces valeurs internes s'affichent brutes.

---

#### Problèmes identifiés — Signaler

| # | Problème | Gravité |
|---|---|---|
| S1 | **Les types d'incidents s'affichent avec underscores** dans la liste "Signalements récents" : `tension_communautaire`, `pression_institutionnelle`, `deplacement`. Le badge Bootstrap affiche la valeur brute du champ `type`. Très prototype. | **Critique** |
| S2 | **Champs Latitude/Longitude** : des coordonnées GPS décimales dans un formulaire citoyen. Le workaround proposé (Google Maps > clic droit) est inaccessible pour 80% des utilisateurs cibles. | **Importante** |
| S3 | **"Position obtenue : 9.35123°N, 2.12345°E"** : affichage technique inutile. L'utilisateur a juste besoin de savoir que sa position a été prise en compte. | **Mineure** |
| S4 | **3 méthodes de localisation** juxtaposées (GPS + sélection département + saisie manuelle) : surcharge cognitive pour un citoyen. | **Importante** |
| S5 | **"Profil déclarant"** : vocabulaire administratif. Une ONG et un journaliste vont comprendre, mais pas un citoyen ordinaire. | **Mineure** |
| S6 | **"Soumettre le signalement"** : le bouton est bleu Bootstrap standard, pas visuellement prioritaire. Un bouton plus rouge/urgent correspondrait mieux au contexte (situation d'urgence). | **Mineure** |
| S7 | **"Référence #{{ report.lastId }}"** après soumission affiche un ID numérique brut (ex: #42). Peu rassurant pour un utilisateur. | **Mineure** |

---

### 1.4 ANALYSE

#### Ce que voit un jury

Il voit "Analyse 2025" dans l'onglet navbar. Il voit "Dataset GDELT Bénin, janvier–décembre 2025" en sous-titre. Il voit "Événements par jour — Bénin 2025" dans le graphique. **Or le dataset couvre maintenant janvier 2025 – avril 2026** suite à la mise à jour du pipeline ce matin. Le titre est périmé depuis quelques heures.

---

#### Problèmes identifiés — Analyse

| # | Problème | Gravité |
|---|---|---|
| A1 | **Titre "Analyse 2025"** dans la navbar, le header, le sous-titre et le graphique Plotly : tous périmés. Le dataset couvre maintenant jan 2025 – avr 2026. | **Critique** |
| A2 | **"Géolocalisés précisément"** dans le KPI : le chiffre inclut les centroïdes département (pas seulement les coordonnées exactes). Le terme "précisément" est donc trompeur. | **Importante** |
| A3 | **Aucun bouton "Actualiser"** sur la page Analyse. Inconsistance avec les autres pages. | **Mineure** |
| A4 | La liste "Départements dans le dataset" peut contenir "Parakou" (ville) à côté de noms de départements. Incohérence visible. | **Mineure** |

---

## PARTIE 2 — AUDIT LINGUISTIQUE

### Anglicismes et jargon technique à corriger

| Texte actuel | Fichier | Pourquoi c'est mauvais | Proposition |
|---|---|---|---|
| `Neutre GDELT` | `index.html` légende | "GDELT" = terme technique inconnu hors data community | `Information générale` |
| `Actualiser GDELT` | `index.html` bouton | "GDELT" dans l'UI produit = prototype | `Forcer la mise à jour` |
| `Base live totale` | `index.html` panneau GDELT | Anglicisme "live", jargon backend | `Total en surveillance` ou supprimer |
| `Fichier traité` | `index.html` | URL brute GDELT affichée (technico) | Supprimer en prod |
| `Évén. mondiaux` | `index.html` | Abréviation laide | `Événements mondiaux` |
| `Mise à jour en temps réel` | `index.html` TERROIR | Inexact (c'est manuel) | `Calcul sur demande` |
| `STT` non défini | `index.html` cartes | Acronyme sans explication | Ajouter "(Score TERROIR)" à la première occurrence |
| `z_cameo / z_tone` | `index.html` | Z-scores statistiques bruts incompréhensibles | Renommer ou masquer |
| `% sensible` | `index.html` | Ambigu | `% conflictuel` |
| `Évts 14j` | `index.html` | Abréviation | `Évén. 14j` ou `Sur 14 jours` |
| `adm1_code` (BN01, BN18…) | `index.html` | Code interne visible | Supprimer, ou remplacer par le nom |
| `tension_communautaire` | backend display | Underscore visible | `Tension communautaire` |
| `pression_institutionnelle` | backend display | Underscore + terme politique | `Pression institutionnelle` |
| `deplacement` | backend display | Valeur brute | `Déplacement` |
| `Analyse 2025` | `index.html`, navbar | Périmé | `Analyse historique` |
| `Zone la plus surveillée` | `index.html` | Trompeur si niveau Normal | `Zone avec le score le plus élevé` |
| `Profil déclarant` | `index.html` | Trop formel | `Vous signalez en tant que :` |
| `Position obtenue : X°N, Y°E` | `index.html` | Incompréhensible | `Position GPS enregistrée ✓` |
| `http://localhost:8501` | footer | Cassé en prod | Retirer ou désactiver en production |

---

## PARTIE 3 — AUDIT UX

### Problèmes UX structurels

| # | Problème | Impact | Gravité | Correction rapide |
|---|---|---|---|---|
| UX1 | **Carte vide en filtre 24h** : si le live data est insuffisant, la carte est blanche au premier chargement. | Première impression catastrophique | **Critique** | Changer le filtre par défaut à 72h ou 7 jours dans `app.js` |
| UX2 | **Panneau GDELT ouvert par défaut** : 6 cellules de stats techniques visibles immédiatement, cachent le territoire. | Surcharge visuelle immédiate | **Importante** | Supprimer `show` de `class="collapse show"` sur `#gdelt-details` |
| UX3 | **2 boutons de refresh sans distinction claire** : "Rafraîchir" (la carte) vs "Actualiser GDELT" (cycle complet 30s). | Confusion utilisateur | **Importante** | Fusionner en 1 bouton ou ajouter un tooltip explicite |
| UX4 | **Bannière TERROIR "Zone la plus surveillée"** affiche toujours quelque chose, même si tout est Normal. | Contradiction logique visible | **Critique** | Conditionner la bannière à `sttTopAlert.level >= 1` |
| UX5 | **3 méthodes de localisation** dans le formulaire : GPS + département + coordonnées manuelles. | Surcharge cognitive | **Importante** | Masquer lat/lon si GPS ou département sélectionné |
| UX6 | **types underscorés dans les badges** de la liste signalements récents. | Impression prototype immédiate | **Critique** | Formatter les types avec `.replace(/_/g, " ")` dans le template |
| UX7 | **"Analyse 2025" périmé** dans navbar + titre + graphique. | Incohérence chronologique visible au jury | **Critique** | Renommer en "Analyse historique" |
| UX8 | **z_cameo / z_tone** visibles dans cartes TERROIR. | Incompréhensible, fait prototype | **Importante** | Supprimer les lignes z_cameo/z_tone de l'affichage |
| UX9 | **adm1_code (BN01, BN18)** visible dans grille TERROIR. | Technique, interne | **Importante** | Supprimer `<small class="text-muted">{{ dept.adm1_code }}</small>` |
| UX10 | **Lien localhost:8501 dans le footer**. | Lien cassé en production | **Critique** | Supprimer le lien Streamlit ou pointer vers Railway URL si disponible |

---

## PARTIE 4 — AUDIT JURY

### Les 10 choses qui donnent une impression professionnelle

1. Design épuré, palette cohérente (vert forêt, blanc, rouge/orange pour alertes) — identité visuelle sérieuse.
2. Légende bien positionnée, lisible, ancrée à gauche de la carte avec les 7 niveaux.
3. Popups Leaflet riches : badge de précision des coordonnées (`Position exacte du lieu` vs `Département estimé` vs `Pays approximatif`) — transparence méthodologique rare.
4. Playbook opérationnel par niveau (Normal/Précaution/Alerte) avec actions concrètes — exactement ce que veut une ONG.
5. Explication du score avec seuils explicites (< 2.0 / 2.0–3.0 / > 3.0) — pédagogique.
6. Animation "LIVE" pulsante dans la navbar — signal visuel de modernité.
7. Gestion des erreurs (overlay erreur carte, messages d'erreur API, spinner de chargement) — pas un écran blanc.
8. Note de confidentialité des données de signalement — essentiel pour un contexte sécuritaire.
9. Zones prioritaires Nord (Alibori, Atacora, Borgou, Donga) explicitement identifiées — contexte géopolitique ancré.
10. Barre de statut en bas de carte avec compteurs live (N événements GDELT, N sécuritaires, N signalements) — transparence des données.

### Les 10 choses qui donnent encore une impression de prototype

1. **`http://localhost:8501`** dans le footer — lien cassé visible en production.
2. **"tension_communautaire"** avec underscore dans la liste signalements récents — valeur backend exposée brute.
3. **"Analyse 2025"** comme titre de l'onglet — périmé le jour de la démo.
4. **"Zone la plus surveillée : Alibori — Normal"** — contradictoire si pas d'alerte.
5. **z_cameo / z_tone** dans les cartes TERROIR — z-scores statistiques bruts visibles.
6. **BN01, BN18 (Parakou)** dans la grille TERROIR — codes internes et incohérence de données.
7. **Panneau GDELT technique** ouvert par défaut (URL de fichier, compteurs bruts).
8. **"GDELT" dans l'UI** — terme inconnu du grand public, omniprésent dans les boutons et panneaux.
9. **Champs Latitude/Longitude dans le formulaire citoyen** — irréaliste pour le public cible.
10. **STT = 0.00 pour tous les départements** si le live data est insuffisant — l'outil semble non fonctionnel.

---

## PARTIE 5 — AUDIT DÉMO

### Risques qui peuvent casser une démonstration live

| Risque | Probabilité | Impact | Solution immédiate |
|---|---|---|---|
| **Carte vide en filtre 24h** — live data insuffisant après redéploiement | **Haute** | Catastrophique | Changer le filtre par défaut à 72h dans `app.js` ligne `mapHours: ref(24)` → `ref(72)` |
| **STT scores tous à 0.00** — fenêtre 14j vide | **Haute** | Catastrophique | Vérifier le contenu de `benin_live.parquet` ; si vide, utiliser ref_date = max(SQLDATE) comme fallback |
| **Lien Streamlit → localhost:8501** — jury clique et voit une erreur | **Certaine** | Mauvaise impression | Supprimer le lien Streamlit du footer |
| **"Actualiser GDELT"** bloque l'app 30s en démo si cliqué | **Modérée** | Désagréable | Ajouter un tooltip "Cycle complet : ~30 secondes" |
| **underscores dans les badges** si un signalement de démo est créé | **Haute si demo signalement** | Impression prototype | Corriger le template avec `.replace(/_/g, " ")` |
| **"Analyse 2025" périmé** — jury lit le titre | **Certaine** | Note jury | Renommer en "Analyse historique" |
| **Bannière "Zone la plus surveillée : X — Normal"** — contradiction visible | **Certaine si scores normaux** | Confusion jury | Conditionner à `level >= 1` |
| **API /stt lente** — 29k événements × 12 départements | **Modérée** | Spinner long | Pré-charger les scores au démarrage de l'application |
| **Panneau GDELT ouvert** avec compteurs à 0 si poller pas encore tourné | **Modérée** | Impression non fonctionnel | Fermer le panneau par défaut |
| **Erreur API 500** si benin_enrichi.parquet non chargé sur Railway | **Faible si push ok** | Catastrophique | Vérifier les logs Railway avant démo |

---

## PARTIE 6 — PLAN DE CORRECTION FINAL

---

### À FAIRE ABSOLUMENT AVANT LE JURY (< 2h)

Ces 8 corrections prennent chacune 2 à 10 minutes. **Aucune ne touche la logique métier.**

#### F1 — Changer le filtre par défaut : 24h → 72h
**Fichier :** `backend/static/js/app.js`, ligne ~58  
**Avant :** `const mapHours = ref(24);`  
**Après :** `const mapHours = ref(72);`  
*Évite la carte vide en démo.*

#### F2 — Supprimer le lien localhost:8501 du footer
**Fichier :** `backend/static/index.html`, ligne ~1169–1172  
Supprimer entièrement le `<a>` vers Streamlit, ou remplacer par le texte "Streamlit (local)".  
*Évite un lien cassé visible.*

#### F3 — Conditionner la bannière "Zone la plus surveillée"
**Fichier :** `backend/static/index.html`, ligne ~428  
**Avant :** `v-if="sttTopAlert"`  
**Après :** `v-if="sttTopAlert && sttTopAlert.level >= 1"`  
*Évite la contradiction "Zone la plus surveillée — Normal".*

#### F4 — Corriger l'affichage des types d'incidents (underscores)
**Fichier :** `backend/static/index.html`, ligne ~931 (badge du type dans la liste récente)  
**Avant :** `{{ inc.type }}`  
**Après :** `{{ (inc.type || '').replace(/_/g, ' ') }}`  
*Supprime les underscores visibles.*

#### F5 — Renommer "Analyse 2025" → "Analyse historique" (4 occurrences)
**Fichiers :** `backend/static/index.html` (navbar ligne 55, titre ligne 1039, sous-titre ligne 1040, graphique ligne 1126)  
*Évite l'incohérence de date au jury.*

#### F6 — Fermer le panneau GDELT par défaut
**Fichier :** `backend/static/index.html`, ligne ~251  
**Avant :** `<div class="collapse show" id="gdelt-details">`  
**Après :** `<div class="collapse" id="gdelt-details">`  
*Réduit la surcharge technique visible.*

#### F7 — Supprimer adm1_code de la grille TERROIR
**Fichier :** `backend/static/index.html`, ligne ~543  
Supprimer `<small class="text-muted">{{ dept.adm1_code }}</small>`  
*Supprime les codes internes BN01, BN18.*

#### F8 — Supprimer z_cameo / z_tone de l'affichage
**Fichier :** `backend/static/index.html`, lignes ~569–572  
Supprimer le bloc `<div v-if="dept.level >= 1" class="stt-zscores">`.  
*Supprime les z-scores statistiques bruts incompréhensibles.*

---

### À FAIRE SI TEMPS DISPONIBLE

#### G1 — Renommer "Neutre GDELT" → "Information générale"
**Fichier :** `backend/static/index.html`, ligne ~195  
*Supprime le jargon GDELT de la légende.*

#### G2 — Renommer "Mise à jour en temps réel" → "Calcul sur demande"
**Fichier :** `backend/static/index.html`, ligne ~364  
*Évite l'inexactitude qui agace un jury attentif.*

#### G3 — Renommer "% sensible" → "% conflictuel"
**Fichier :** `backend/static/index.html`, lignes ~497 et ~564  
*Rend le terme compréhensible.*

#### G4 — Renommer "Évts 14j" → "Sur 14j"
**Fichier :** `backend/static/index.html`, plusieurs occurrences  
*Abréviation plus naturelle.*

#### G5 — Ajouter "(Score de Tension Territorial)" à la première occurrence de STT
**Fichier :** `backend/static/index.html`, section explication du score  
*Définit l'acronyme pour le jury.*

#### G6 — Vérifier que benin_live.parquet contient des données récentes
```powershell
python -c "import pandas as pd; df = pd.read_parquet('data/processed/benin_live.parquet'); print(df['SQLDATE'].max(), len(df))"
```
Si vide ou données trop anciennes : modifier `stt.py` pour avoir un fallback sur `max(SQLDATE)` quand live < 14j.

#### G7 — Définir sttTopAlert correctement par score max (pas index 0)
**Fichier :** `backend/static/js/app.js`, ligne ~227  
**Avant :** `const sttTopAlert = computed(() => stt.scores.length ? stt.scores[0] : null);`  
**Après :** `const sttTopAlert = computed(() => stt.scores.length ? [...stt.scores].sort((a, b) => b.stt - a.stt)[0] : null);`  
*Bannière montre vraiment la zone la plus risquée.*

#### G8 — Pré-charger STT au démarrage de l'app (pas seulement au clic)
**Fichier :** `backend/static/js/app.js`, section watch route  
Ajouter `loadStt()` au mount ou au premier chargement en parallèle.

#### G9 — Renommer "Profil déclarant" → "Vous signalez en tant que :"
**Fichier :** `backend/static/index.html`, ligne ~875  
*Plus naturel pour un citoyen.*

#### G10 — Remplacer "Position obtenue : X°N, Y°E" par "Position GPS enregistrée ✓"
**Fichier :** `backend/static/index.html`, ligne ~806  

---

### À IGNORER (ne vaut pas le risque de casser quelque chose)

- Refonte du formulaire de localisation (lat/lon → carte interactive) : trop complexe en 2h
- Masquage du panneau GDELT en production uniquement : nécessite logique d'env
- Traduction complète des CAMEO codes vers des labels métier : risque de régression
- Ajout d'un bouton "Actualiser" sur la page Analyse : cosmétique, pas prioritaire
- Correction de l'anomalie "Parakou" dans les départements TERROIR : touche les données
- Réécriture du playbook avec des actions plus spécifiques par département : contenu métier
- Fusion des deux boutons de refresh en un seul : risque de régression fonctionnelle

---

## ANNEXE — RÉCAPITULATIF TECHNIQUE DES CORRECTIONS F1–F8

```
F1  app.js:58       mapHours ref(24) → ref(72)
F2  index.html:1169 Supprimer lien localhost:8501
F3  index.html:428  v-if="sttTopAlert" → v-if="sttTopAlert && sttTopAlert.level >= 1"
F4  index.html:931  inc.type → (inc.type||'').replace(/_/g,' ')
F5  index.html:55,1039,1040,1126  "2025" → "historique" ou "2025–2026"
F6  index.html:251  class="collapse show" → class="collapse"
F7  index.html:543  Supprimer <small>{{ dept.adm1_code }}</small>
F8  index.html:569  Supprimer bloc .stt-zscores entier
```

**Temps estimé total F1–F8 : 25 à 40 minutes.**  
**Impact : élimination de 6 des 7 bugs critiques.**
