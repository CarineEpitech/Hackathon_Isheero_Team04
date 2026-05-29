# Préparation jury — BeninScope / TERROIR

Document de préparation pour le jury final. Questions classées par thème, avec réponse courte (à dire à l'oral) et réponse détaillée (si la question est poussée).

---

## UTILITÉ DU PRODUIT

---

**Question : Quel est le vrai problème que vous résolvez ?**

Réponse courte : Au Bénin, les acteurs de terrain — ONG, mairies, préfectures — n'ont pas d'outil pour suivre en continu les signaux d'instabilité. Ils apprennent souvent les situations trop tard. On essaie de réduire ce délai.

Réponse détaillée : Les informations existent — dans la presse internationale, dans les rapports terrain, dans les données statistiques. Le problème, c'est qu'elles sont dispersées et que les acteurs locaux n'ont ni le temps ni les outils pour les agréger. TERROIR fait cette agrégation automatiquement et donne une lecture rapide par département, toutes les 15 minutes.

---

**Question : Qui utiliserait concrètement votre application ?**

Réponse courte : En priorité, les ONG et les organisations humanitaires qui opèrent sur le terrain au Bénin. Ensuite, les préfectures et les mairies qui veulent objectiver leurs décisions. Et les journalistes qui couvrent la région.

Réponse détaillée : Ce sont des utilisateurs qui ont besoin d'une vue d'ensemble rapide, pas d'une analyse approfondie. Une ONG qui planifie une mission dans l'Atacora a besoin de savoir si la zone est calme ou tendue cette semaine — pas d'un rapport de 40 pages. TERROIR répond à ce besoin en 30 secondes.

---

**Question : Pourquoi une ONG n'utiliserait pas simplement les médias classiques ?**

Réponse courte : Parce que les médias classiques ne couvrent pas le Bénin de façon systématique, et qu'aucun journaliste ne fait une veille département par département toutes les 15 minutes.

Réponse détaillée : Les médias publient quand l'événement est déjà visible. TERROIR capte les signaux faibles avant qu'ils deviennent des crises — c'est l'intérêt d'une veille automatisée sur un flux de données structuré comme GDELT. Un analyste humain ne peut pas surveiller 18 départements en continu.

---

**Question : Qui paierait pour ça ?**

Réponse courte : Les organisations humanitaires internationales ont des budgets dédiés aux outils de sécurité et de veille terrain. C'est ce marché qu'on vise.

Réponse détaillée : OCHA, MSF, la Croix-Rouge, les agences de l'ONU ont des équipes sécurité qui paient aujourd'hui des services comme ACLED ou Crisis24. TERROIR se positionne sur le même besoin, avec un focus Afrique de l'Ouest et une granularité départementale. Sur un plan commercial, un abonnement annuel type SaaS est la piste la plus réaliste.

---

**Question : Qu'est-ce que votre outil permet de faire que personne ne peut faire aujourd'hui ?**

Réponse courte : Avoir une vue actualisée toutes les 15 minutes, par département béninois, avec un score de tension calculé automatiquement — ça n'existe pas ailleurs, à cette granularité, sur le Bénin.

Réponse détaillée : ACLED, par exemple, est très bien pour l'analyse rétrospective mais publie avec un délai de plusieurs jours. Global Incident Map est trop généraliste. Ce qu'on offre, c'est une combinaison : données quasi temps réel + scoring territorial + signalements citoyens, sur un pays précis.

---

**Question : Quelle action concrète déclenche votre application ?**

Réponse courte : Une alerte "Précaution" sur un département peut pousser une ONG à contacter son équipe locale avant d'envoyer une mission. Une alerte "Alerte" peut déclencher un report de déplacement.

Réponse détaillée : L'application ne prend pas de décision — elle aide à en prendre une plus rapidement. Elle réduit le temps entre "quelque chose se passe" et "quelqu'un compétent en est informé". La décision reste humaine, ce qui est normal pour ce type de sujet.

---

**Question : Pourquoi ce n'est pas juste un dashboard de plus ?**

Réponse courte : Parce qu'il est alimenté en continu, qu'il intègre les signalements citoyens, et qu'il produit un score composite par département — pas juste un graphique.

Réponse détaillée : La majorité des dashboards montrent ce qui s'est passé. Celui-ci montre ce qui se passe maintenant, et calcule si c'est inhabituel par rapport au contexte habituel de la zone. Le scoring territorial est la différence entre une visualisation et un outil d'aide à la décision.

---

## GDELT

---

**Question : Pourquoi GDELT ? C'est fiable ?**

Réponse courte : GDELT couvre 65 langues, 250 pays, et analyse plus de 300 000 articles par jour. Aucune autre source publique n'a cette couverture à cette fréquence.

Réponse détaillée : GDELT n'est pas parfait — il peut mal géocoder des événements, surestimer certains acteurs, et dépend de la couverture médiatique internationale. Mais c'est la meilleure source publique disponible pour ce type d'analyse en temps réel. On le complète avec les signalements terrain précisément parce qu'on sait que GDELT a des angles morts.

---

**Question : GDELT mesure la couverture médiatique, pas ce qui se passe vraiment. C'est un problème non ?**

Réponse courte : Oui, et on le dit clairement. GDELT mesure ce que la presse internationale rapporte, pas la réalité terrain. C'est une limite que l'application affiche explicitement.

Réponse détaillée : C'est une distinction importante qu'on a intégrée dans l'interface : quand un événement a peu de couverture, ça peut signifier que c'est calme, ou que personne n'en parle. C'est pourquoi les signalements citoyens existent — pour capter ce que GDELT ne voit pas. Les deux sources combinées donnent une image plus complète.

---

**Question : Que se passe-t-il si GDELT ne publie rien sur le Bénin pendant plusieurs heures ?**

Réponse courte : L'application continue de fonctionner avec les données déjà collectées. Elle indique le nombre d'événements du dernier cycle et l'heure de la dernière mise à jour.

Réponse détaillée : L'interface distingue clairement "base live" (total accumulé) et "dernier cycle" (ce que le dernier fichier 15 minutes contenait). Si un cycle est vide, ça s'affiche. Le scoring STT ne dépend pas d'un seul cycle — il porte sur une fenêtre de 14 jours, donc un cycle vide ne fausse pas le score.

---

**Question : Comment vous gérez les erreurs de téléchargement GDELT ?**

Réponse courte : Le poller note l'erreur et réessaie au cycle suivant. Les données existantes ne sont pas effacées.

Réponse détaillée : Le poller tourne en arrière-plan toutes les 15 minutes. En cas d'échec réseau, il conserve les données du cycle précédent et relance automatiquement. L'interface affiche le statut du poller — l'utilisateur voit si quelque chose ne va pas.

---

**Question : Pourquoi 22 % des sources sont nigérianes ? C'est un biais non ?**

Réponse courte : Oui, c'est un biais réel. Les médias nigérians couvrent beaucoup le Bénin voisin, et certains de leurs articles concernent en réalité Bénin City au Nigeria, pas le Bénin. On a mis un bouton pour filtrer ces sources.

Réponse détaillée : C'est ce qu'on appelle l'Indicateur de Dépendance Nigériane (IDN). Avec le bouton "Inclure / Exclure Nigéria", l'utilisateur peut voir la carte avec ou sans ces sources. Ça permet de mesurer l'impact du biais et de prendre une décision informée. C'est une transparence que peu d'outils similaires offrent.

---

**Question : Pourquoi ne pas utiliser une autre source que GDELT ?**

Réponse courte : Parce que GDELT est la seule source publique, gratuite, en temps quasi réel, avec une couverture mondiale. Les alternatives (ACLED, Crisis24) sont payantes ou n'ont pas la même fréquence.

Réponse détaillée : On a évalué ACLED — c'est excellent mais publié avec un délai de plusieurs jours et avec un accès commercial. Pour un projet académique et un prototype, GDELT est le bon choix. En version production, on pourrait croiser GDELT avec ACLED pour la validation rétrospective.

---

## GÉOLOCALISATION

---

**Question : 94,8 % de vos données sont au centroïde pays. C'est presque inutile non ?**

Réponse courte : Ce n'est pas inutile — ça indique qu'un événement s'est passé au Bénin, à une date donnée, avec un certain ton. La précision géographique manque, mais l'information reste exploitable pour le scoring temporel.

Réponse détaillée : Le STT se calcule sur la fréquence et le ton des événements par département. Pour les événements sans coordonnée précise, on utilise le département mentionné dans le texte GDELT (ADM1Code). Ce n'est pas parfait, mais ça permet quand même de produire un score par département. Les 5,2 % avec une localisation précise sont ceux qui s'affichent sur la carte avec le plus de valeur.

---

**Question : Comment vous savez qu'un point sur la carte est au bon endroit ?**

Réponse courte : On affiche le niveau de précision directement dans le popup de chaque point — "position exacte", "département estimé", ou "pays approximatif". L'utilisateur voit immédiatement la fiabilité de la localisation.

Réponse détaillée : GDELT fournit une source de géolocalisation pour chaque événement. On l'a conservée et affichée dans l'interface. C'est plus honnête que de masquer l'incertitude. Un point affiché "pays approximatif" dit clairement qu'on sait que ça s'est passé au Bénin, mais pas où exactement.

---

**Question : Bénin City au Nigeria peut apparaître dans vos données ?**

Réponse courte : C'était le cas au début. On a mis en place un filtre géographique par bounding box — les coordonnées hors du territoire béninois sont écartées.

Réponse détaillée : Le filtre combine deux critères : le code pays GDELT (BN) et la bounding box géographique du Bénin (5,5°–13°N, 0,5°–4°E). Ça élimine les événements mal géocodés qui se retrouvaient à Bénin City, Lagos ou Abuja. C'est un problème réel qu'on a résolu en cours de projet.

---

**Question : Est-ce que vos erreurs de géolocalisation peuvent déclencher de fausses alertes ?**

Réponse courte : Théoriquement oui. Un événement mal localisé peut fausser le score d'un département. En pratique, le score porte sur une fenêtre de 14 jours — un point aberrant seul ne suffit pas à déclencher une alerte.

Réponse détaillée : Le scoring STT est conçu pour être robuste aux événements isolés. Il faut une accumulation d'événements négatifs sur 14 jours pour passer en "Précaution" ou "Alerte". Un seul article mal géocodé ne change pas le score de manière significative. C'est une des raisons pour lesquelles on a choisi une fenêtre glissante plutôt qu'une analyse événement par événement.

---

## SIGNALEMENTS CITOYENS

---

**Question : Comment évitez-vous les faux signalements ?**

Réponse courte : Les signalements sont affichés mais marqués "en attente de validation". Ils ne déclenchent pas d'alerte automatique. La validation est manuelle.

Réponse détaillée : En prototype, le mécanisme de modération est humain — quelqu'un valide ou rejette les signalements. En version production, on peut ajouter une vérification par téléphone ou par réseau d'acteurs de confiance (ONG partenaires, agents communautaires). Le modèle de signalement anonyme est volontairement limité pour réduire les abus.

---

**Question : Pourquoi quelqu'un prendrait le temps de signaler un événement ?**

Réponse courte : Parce que certaines personnes veulent que ce qu'elles voient soit visible et pris en compte. Les ONG, les agents communautaires, les journalistes locaux ont intérêt à alimenter ce type d'outil.

Réponse détaillée : Dans un scénario de déploiement réel, l'application serait intégrée dans le workflow d'acteurs existants — pas proposée au grand public au sens large. Un réseau de correspondants locaux (agents ONG, chefs de village, agents de santé) peut constituer une source de signalements fiables. C'est un modèle qui existe déjà avec des outils comme Ushahidi en Afrique de l'Est.

---

**Question : Risques de désinformation via les signalements ?**

Réponse courte : C'est un risque réel. C'est pour ça que les signalements non validés sont visibles mais clairement différenciés, et qu'ils ne pèsent pas dans le scoring STT.

Réponse détaillée : Le design est volontairement conservateur sur ce point. Un signalement non validé ne modifie pas le score territorial — il est juste visible sur la carte avec un marqueur "en attente". Ça donne de la visibilité sans créer de faux positifs automatiques. En version production, un workflow de validation par des opérateurs de confiance serait nécessaire.

---

**Question : Vous stockez les données des personnes qui signalent ?**

Réponse courte : Non. Le formulaire accepte un pseudo optionnel, mais le contact n'est jamais stocké. On conserve uniquement le type d'événement, la description, la localisation et l'heure.

Réponse détaillée : C'est une décision délibérée, aussi bien pour la protection des signalants que pour la conformité RGPD. Dans un contexte de tension territoriale, anonymiser les sources n'est pas une option — c'est une nécessité. Les données de contact sont acceptées dans le formulaire pour rassurer l'utilisateur, mais elles sont explicitement jetées côté serveur.

---

## TECHNIQUE

---

**Question : Pourquoi FastAPI et pas Flask ou Django ?**

Réponse courte : FastAPI est plus rapide à développer pour une API REST, il génère automatiquement la documentation, et il gère bien les opérations asynchrones nécessaires pour le poller GDELT.

Réponse détaillée : Flask aurait fonctionné, mais FastAPI donne la validation automatique des paramètres via Pydantic, la doc Swagger sans travail supplémentaire, et de bonnes performances pour les endpoints qui tournent souvent. Django était surdimensionné pour ce projet — on n'a pas besoin d'un ORM ni d'un système d'administration.

---

**Question : Pourquoi pas React pour le frontend ?**

Réponse courte : On a fait le choix de ne pas avoir de step de build. L'interface est servie directement par FastAPI, sans Node.js, sans npm, sans webpack. C'est un choix de simplicité pour un prototype.

Réponse détaillée : Vue 3, Bootstrap et Leaflet sont chargés depuis un CDN. Ça veut dire zéro dépendance frontend à installer, un déploiement qui ne nécessite pas de build, et un fichier HTML lisible directement. Pour un hackathon, c'est une décision rationnelle. En version production, migrer vers une SPA React ou Next.js serait envisageable.

---

**Question : Pourquoi pas de base de données ?**

Réponse courte : On utilise des fichiers parquet, ce qui est suffisant pour ce volume de données et ce cas d'usage. Une base de données aurait ajouté de la complexité sans apport réel à ce stade.

Réponse détaillée : 31 500 événements dans un parquet, ça se charge en moins d'une seconde. PostgreSQL aurait demandé de configurer un serveur, une connexion, des migrations — pour aucun gain de performance visible à ce stade. Pour les signalements, on utilise un CSV simple. En production, avec plusieurs milliers de signalements et plusieurs utilisateurs simultanés, une base de données deviendrait nécessaire.

---

**Question : Pourquoi pas WebSocket pour le temps réel ?**

Réponse courte : Le polling côté client toutes les quelques minutes est suffisant pour notre fréquence de données — GDELT publie toutes les 15 minutes. Un WebSocket serait de la sur-ingénierie.

Réponse détaillée : L'interface actualise la carte toutes les 5 minutes. Puisque GDELT publie au mieux toutes les 15 minutes, une connexion WebSocket permanente ne changerait rien à la fraîcheur des données. Le polling HTTP simple est plus facile à déployer, plus facile à déboguer, et suffit largement.

---

**Question : Pourquoi pas de modèle de machine learning pour le scoring ?**

Réponse courte : Parce qu'on n'a pas de données labellisées sur ce qu'est une "véritable crise" au Bénin département par département. Un z-score sur une fenêtre glissante est plus interprétable et plus honnête.

Réponse détaillée : Un modèle supervisé aurait besoin de milliers d'exemples de "crises confirmées" par département — des données qu'on n'a pas. Le STT est une approche statistique simple : si les 14 derniers jours sont significativement plus agités que la baseline des 90 jours précédents, c'est un signal. C'est transparent, explicable, et ça ne prétend pas plus que ce qu'on peut démontrer.

---

**Question : Votre système peut-il tenir avec beaucoup d'utilisateurs simultanés ?**

Réponse courte : Dans l'état actuel, non — c'est un prototype. Un déploiement sérieux nécessiterait de revoir l'architecture, notamment mettre en cache les réponses API.

Réponse détaillée : FastAPI est performant mais on recharge le parquet à chaque requête, ce qui n'est pas optimal sous charge. En production, on mettrait les données en cache en mémoire (ou dans Redis), on séparerait le poller GDELT du serveur web, et on passerait à une vraie base de données pour les signalements. L'architecture actuelle est conçue pour démontrer le concept, pas pour supporter des milliers d'utilisateurs.

---

**Question : Railway peut mettre l'application en veille. Comment vous gérez ça ?**

Réponse courte : C'est une limite du plan gratuit. En production, on passerait sur un plan payant ou une instance dédiée pour garantir la disponibilité continue.

Réponse détaillée : Pour la démo, on s'assure que l'application est active avant la présentation. Le poller GDELT repart automatiquement au redémarrage du container. La seule perte est le cache des derniers cycles — qui se reconstitue en moins d'une heure.

---

## LIMITES

---

**Question : Quelle est votre plus grande faiblesse ?**

Réponse courte : La géolocalisation. 94,8 % de nos événements sont au centroïde pays. La carte est utile, mais les points sont souvent imprécis.

Réponse détaillée : C'est une limite de GDELT elle-même, pas de notre traitement. Les articles de presse internationale ne précisent pas toujours une ville ou une zone — ils mentionnent "Bénin" et GDELT place le point au centre du pays. On l'affiche clairement dans l'interface, mais ça reste une vraie limite pour l'analyse géographique fine.

---

**Question : Est-ce que votre STT est validé ? Vous avez des preuves qu'il fonctionne ?**

Réponse courte : Pas encore de validation formelle. C'est un prototype — le score est cohérent avec les données, mais on n'a pas pu le tester sur des crises réelles passées de façon systématique.

Réponse détaillée : On a vérifié que les scores montent sur des périodes connues d'instabilité dans les données historiques 2025. Mais une validation rigoureuse — comparer les alertes TERROIR avec des événements confirmés sur le terrain — nécessiterait un travail de plusieurs mois avec des partenaires terrain. C'est explicitement dans les perspectives.

---

**Question : Qu'est-ce qui ne marche pas encore ?**

Réponse courte : Les alertes automatiques par e-mail ou SMS sont dans les perspectives mais pas implémentées. Les signalements ne sont pas encore connectés au scoring STT.

Réponse détaillée : Les trois choses les plus importantes à faire pour aller en production : une base de données persistante pour les signalements, un système d'alertes push, et un processus de validation des signalements avec des partenaires locaux. Le reste du produit est fonctionnel.

---

**Question : Vous dépendez entièrement de GDELT. Si GDELT s'arrête, vous n'avez plus rien ?**

Réponse courte : On aurait toujours les données historiques, mais plus de mise à jour en temps réel — oui.

Réponse détaillée : C'est un risque réel pour n'importe quel outil qui repose sur une source externe. En production, on mitiger ce risque en ayant plusieurs sources (ACLED, NewsAPI, signalements terrain) et en stockant localement toutes les données traitées. GDELT a une disponibilité très élevée depuis 10 ans, mais la dépendance est réelle.

---

**Question : Votre modèle STT est-il adapté au contexte béninois ?**

Réponse courte : Il est calibré sur les données GDELT du Bénin depuis janvier 2025. Ce n'est pas un modèle générique copié-collé — il utilise la baseline réelle du pays.

Réponse détaillée : Les pondérations du STT (0,40 / 0,35 / 0,15 / 0,10) sont issues de la littérature sur les indicateurs de conflit, adaptées au contexte GDELT. La baseline de 90 jours est calculée sur les données réelles du Bénin. Ce n'est pas parfait, mais c'est ancré dans les données locales, pas dans un modèle universel.

---

## BUSINESS

---

**Question : Quel est votre modèle économique ?**

Réponse courte : Abonnement SaaS pour les organisations humanitaires et les institutions publiques. C'est le modèle des outils de veille sécuritaire existants.

Réponse détaillée : Le marché des outils de sécurité terrain pour les ONG et les agences humanitaires existe et est actif. Des entreprises comme Crisis24, Dataminr ou Control Risks facturent des dizaines de milliers d'euros par an à leurs clients institutionnels. On se positionne sur un segment plus accessible — Afrique de l'Ouest, granularité locale, prix adapté aux organisations de taille moyenne.

---

**Question : Qui financerait le développement ?**

Réponse courte : Les sources naturelles sont les bailleurs humanitaires (USAID, AFD, UE) qui financent les outils d'information pour les acteurs terrain, et des accélérateurs tech focalisés Afrique.

Réponse détaillée : Il existe des programmes de financement spécifiques pour les outils tech au service de la sécurité humanitaire — Digital Impact Alliance, Humanitarian Innovation Fund, DIAL. En parallèle, des contrats pilotes avec des ONG locales permettraient de valider le produit et de générer un premier revenu.

---

**Question : Comment vous allez scaler à d'autres pays ?**

Réponse courte : GDELT couvre 250 pays. Techniquement, il suffit de changer le filtre géographique. Le vrai travail est d'adapter le scoring et de nouer des partenariats locaux.

Réponse détaillée : L'architecture est conçue pour un pays mais pas verrouillée dessus. Étendre à d'autres pays d'Afrique de l'Ouest (Togo, Burkina Faso, Niger) serait une évolution naturelle — même zone géopolitique, même structure de risques, communauté d'ONG partiellement commune. La partie technique est simple ; la partie connaissance terrain est ce qui prend du temps.

---

**Question : Votre MVP est déployé. C'est votre seul argument ?**

Réponse courte : Non. On a un dataset de 31 500 événements, un scoring par département, une carte live, un système de signalement fonctionnel, et une démo accessible en ligne. C'est plus qu'un prototype papier.

Réponse détaillée : La démo est utilisable maintenant, pas dans 6 mois. C'est une différence importante avec beaucoup de projets présentés en hackathon. Ce qui manque pour aller en production, c'est une base de données, un système d'alertes, et un premier partenaire terrain pour valider le scoring — pas une réécriture from scratch.

---

## ÉTHIQUE

---

**Question : Votre application ne risque-t-elle pas de paniquer les populations ?**

Réponse courte : L'application est destinée à des professionnels — ONG, institutions — pas au grand public. Elle n'est pas conçue pour diffuser des alertes en masse.

Réponse détaillée : L'accès est ouvert dans cette version prototype, mais le déploiement réel supposerait un contrôle d'accès pour les organisations partenaires. Les scores et alertes s'adressent à des acteurs qui ont la capacité d'interpréter et de vérifier — pas à des citoyens qui pourraient réagir à une alerte sans contexte.

---

**Question : Vous faites de la surveillance territoriale. Ce n'est pas problématique ?**

Réponse courte : On surveille des flux d'information publics, pas des personnes. GDELT agrège des articles de presse accessibles à tous. On ne traque pas des individus.

Réponse détaillée : La distinction est importante. TERROIR est un outil de veille médiatique et de signalement volontaire — tout ce qu'on agrège est soit public (GDELT) soit soumis volontairement (signalements). On ne collecte aucune donnée personnelle sans consentement, on ne localise pas des individus, et on ne construit pas de profils. C'est une surveillance du territoire, pas des personnes.

---

**Question : Les faux positifs peuvent avoir des conséquences graves. Comment vous vous en protégez ?**

Réponse courte : Le score STT a trois niveaux, pas deux. "Précaution" ne signifie pas "danger immédiat" — c'est un signal qui recommande de vérifier, pas d'agir immédiatement.

Réponse détaillée : Le design des niveaux d'alerte est volontairement conservateur. Il faut une accumulation significative sur 14 jours pour passer en "Alerte". Un seul article négatif ne change pas le score. De plus, l'application n'envoie aucune notification automatique dans cette version — c'est un tableau de bord consultatif, pas un système d'alerte automatisé.

---

**Question : Qui est responsable si une décision basée sur votre outil cause un préjudice ?**

Réponse courte : La décision reste toujours humaine. TERROIR est un outil d'aide à la décision, pas un système de décision automatique. La responsabilité reste avec l'opérateur qui utilise l'information.

Réponse détaillée : C'est une question importante pour n'importe quel outil d'aide à la décision dans des contextes sensibles. Dans les conditions d'utilisation, on préciserait clairement que les scores et alertes sont indicatifs, basés sur des données médiatiques, et ne remplacent pas une évaluation terrain. C'est le même cadre que pour ACLED ou n'importe quelle source d'information sur les conflits.

---

**Question : Les données que vous utilisez sont-elles conformes au RGPD ?**

Réponse courte : Oui. GDELT est une base de données publique. Les signalements citoyens ne stockent aucune donnée personnelle identifiable.

Réponse détaillée : GDELT agrège des articles de presse publics — aucune donnée personnelle. Pour les signalements, on n'enregistre pas de contact, on n'enregistre pas d'adresse IP, et le pseudo est optionnel. Les seules données stockées sont : type d'événement, description, coordonnées géographiques, horodatage. C'est conforme aux obligations RGPD de minimisation des données.

---

## QUESTIONS PIÈGES

---

**Question : C'est quoi la différence avec un Google News filtré sur "Bénin" ?**

Réponse courte : Google News montre les articles. TERROIR les géolocalise, les score, les agrège par département, et produit un indicateur de tension — pas juste une liste de titres.

Réponse détaillée : Google News n'a pas de scoring territorial. Il ne dit pas "l'Atacora est plus tendue cette semaine que d'habitude". Il ne combine pas plusieurs sources pour produire un score composite. Et il ne permet pas de soumettre des signalements terrain. Ce sont deux outils différents qui répondent à des besoins différents.

---

**Question : Vous avez travaillé combien de temps sur ce projet ?**

Réponse courte : C'est un hackathon — quelques semaines de travail intensif. On ne prétend pas avoir un produit fini, on présente un prototype fonctionnel et une vision claire de ce qu'il faudrait pour aller plus loin.

Réponse détaillée : En hackathon, l'objectif est de prouver qu'une idée est réalisable et qu'une équipe peut l'exécuter. On a un backend fonctionnel, un frontend utilisable, des données réelles, et un déploiement en ligne. Ce qui manque, c'est le temps — pas la faisabilité technique.

---

**Question : Pourquoi vous et pas une équipe locale béninoise ?**

Réponse courte : C'est une bonne question. Un déploiement réel nécessiterait absolument des partenaires locaux — pour la connaissance terrain, pour les signalements, pour la validation du scoring.

Réponse détaillée : On est une équipe qui a construit un outil. On ne prétend pas remplacer des acteurs locaux — on construit quelque chose qui peut les aider. En pratique, un produit comme TERROIR ne peut fonctionner qu'avec une collaboration étroite avec des organisations béninoises. C'est une limite de tout projet tech "depuis l'extérieur", et on en est conscients.

---

**Question : Votre score STT peut-il être manipulé ? Quelqu'un pourrait publier de faux articles pour déclencher une alerte ?**

Réponse courte : Théoriquement oui, mais il faudrait un volume d'articles suffisant pour modifier la fenêtre de 14 jours de façon significative — ce qui est peu probable à l'échelle d'un département.

Réponse détaillée : GDELT agrège des milliers de sources. Pour manipuler le score d'un département, il faudrait que de nombreux médias publient des articles négatifs sur la même zone sur plusieurs jours. C'est difficile à orchestrer. Le risque est plus celui d'une surreprésentation d'une source influente (comme les médias nigérians) — ce qu'on a précisément traité avec le filtre IDN.

---

**Question : TERROIR. Pourquoi ce nom ?**

Réponse courte : TERROIR fait référence au territoire — à la surveillance du terrain. C'est aussi un mot qui ancre le projet dans une réalité locale, pas dans un concept tech abstrait.

Réponse détaillée : L'idée était de choisir un nom qui évoque le sol, la géographie, le local — à l'opposé des noms génériques de dashboards. TERROIR dit immédiatement que le produit s'intéresse à des zones précises, pas à des données agrégées mondiales.

---

*Hackathon iSHEERO × DataCamp 2026 — BeninScope*
