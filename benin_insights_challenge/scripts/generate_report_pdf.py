"""
Génération du rapport final BéninScope / TERROIR en PDF.
Utilise reportlab (déjà installé dans l'environnement).

Usage :
    python scripts/generate_report_pdf.py
Sortie :
    docs/rapport_final_beninscope.pdf
"""

from pathlib import Path
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)

# ── Chemins ────────────────────────────────────────────────────────────────────
ROOT    = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs"
OUT_DIR.mkdir(exist_ok=True)
OUT     = OUT_DIR / "rapport_final_beninscope.pdf"

TODAY   = date.today().strftime("%d %B %Y").replace(
    "January","janvier").replace("February","février").replace(
    "March","mars").replace("April","avril").replace(
    "May","mai").replace("June","juin").replace(
    "July","juillet").replace("August","août").replace(
    "September","septembre").replace("October","octobre").replace(
    "November","novembre").replace("December","décembre")

# ── Palette couleurs ───────────────────────────────────────────────────────────
C_NAVY   = colors.HexColor("#0d2137")
C_BLUE   = colors.HexColor("#1a6fa8")
C_TEAL   = colors.HexColor("#1abc9c")
C_ORANGE = colors.HexColor("#e67e22")
C_RED    = colors.HexColor("#c0392b")
C_LGRAY  = colors.HexColor("#f4f6f8")
C_GRAY   = colors.HexColor("#7f8c8d")
C_BLACK  = colors.HexColor("#1a1a2e")

# ── Styles ─────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=base[parent], **kw)
    return s

S = {
    "cover_title": style("cover_title",
        fontSize=28, textColor=C_NAVY, leading=34,
        alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=8),
    "cover_sub":   style("cover_sub",
        fontSize=14, textColor=C_BLUE, leading=18,
        alignment=TA_CENTER, fontName="Helvetica", spaceAfter=4),
    "cover_meta":  style("cover_meta",
        fontSize=10, textColor=C_GRAY, leading=14,
        alignment=TA_CENTER, fontName="Helvetica"),
    "h1": style("h1",
        fontSize=16, textColor=C_NAVY, leading=20, fontName="Helvetica-Bold",
        spaceBefore=18, spaceAfter=6),
    "h2": style("h2",
        fontSize=13, textColor=C_BLUE, leading=17, fontName="Helvetica-Bold",
        spaceBefore=12, spaceAfter=4),
    "h3": style("h3",
        fontSize=11, textColor=C_NAVY, leading=15, fontName="Helvetica-BoldOblique",
        spaceBefore=8, spaceAfter=3),
    "body": style("body",
        fontSize=10, textColor=C_BLACK, leading=15,
        alignment=TA_JUSTIFY, fontName="Helvetica", spaceAfter=6),
    "bullet": style("bullet",
        fontSize=10, textColor=C_BLACK, leading=14, fontName="Helvetica",
        leftIndent=16, spaceAfter=3),
    "code": style("code",
        fontSize=9, textColor=C_NAVY, leading=13, fontName="Courier",
        backColor=C_LGRAY, leftIndent=12, rightIndent=12,
        spaceBefore=4, spaceAfter=4),
    "caption": style("caption",
        fontSize=8, textColor=C_GRAY, leading=11, fontName="Helvetica-Oblique",
        alignment=TA_CENTER, spaceBefore=2, spaceAfter=8),
    "highlight": style("highlight",
        fontSize=10, textColor=C_NAVY, leading=14, fontName="Helvetica-Bold",
        backColor=colors.HexColor("#eaf4fb"), leftIndent=10, rightIndent=10,
        spaceBefore=6, spaceAfter=6),
    # Style dédié aux en-têtes de tableaux : texte blanc sur fond navy
    "th": style("th",
        fontSize=9, textColor=colors.white, leading=13,
        fontName="Helvetica-Bold"),
    # Style cellules de tableau corps : texte noir lisible
    "td": style("td",
        fontSize=9, textColor=C_BLACK, leading=13,
        fontName="Helvetica"),
    # Style 1ère colonne kv_table
    "td_key": style("td_key",
        fontSize=9, textColor=C_NAVY, leading=13,
        fontName="Helvetica-Bold"),
    # Lien dans le sommaire
    "toc_link": style("toc_link",
        fontSize=10, textColor=C_BLACK, leading=16,
        fontName="Helvetica"),
}


# ── Ancres et liens internes PDF ───────────────────────────────────────────────
# Identifiants d'ancre pour chaque section principale
ANCHORS = {
    1:  "resume",
    2:  "contexte",
    3:  "architecture",
    4:  "pipeline",
    5:  "stt",
    6:  "plateforme",
    7:  "insights",
    8:  "deploiement",
    9:  "disclosure",
    10: "limitations",
    11: "equipe",
}


def anchor_para(anchor_id):
    """Paragraphe invisible portant l'ancre PDF interne."""
    return Paragraph(f'<a name="{anchor_id}"/>', ParagraphStyle(
        "anchor_hidden", fontSize=0.1, leading=0.1, spaceAfter=0, spaceBefore=0))


# ── Helpers ────────────────────────────────────────────────────────────────────

def hr(color=C_TEAL, thickness=1.5):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=6, spaceBefore=2)

def sp(h=8):
    return Spacer(1, h)

def p(text, s="body"):
    return Paragraph(text, S[s])

def h1(text, section_num=None):
    """Titre H1 avec ancre PDF si section_num fourni."""
    elems = [hr(C_TEAL, 2)]
    if section_num and section_num in ANCHORS:
        elems.append(anchor_para(ANCHORS[section_num]))
    elems.append(p(text, "h1"))
    return elems

def h2(text):
    return [p(text, "h2")]

def h3(text):
    return [p(text, "h3")]

def bullet(items, prefix="—"):
    return [p(f"{prefix}  {item}", "bullet") for item in items]


def kv_table(rows, col_widths=(5.5 * cm, 11 * cm)):
    """Tableau clé-valeur : 1ère colonne en gras navy, 2e colonne en texte normal."""
    data = [
        [Paragraph(k, S["td_key"]), Paragraph(v, S["td"])]
        for k, v in rows
    ]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_LGRAY, colors.white]),
        ("GRID",           (0, 0), (-1, -1), 0.25, C_GRAY),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
    ]))
    return t


def data_table(headers, rows, col_widths=None):
    """Tableau de données : en-tête blanche sur fond navy, corps lisible."""
    # En-têtes : style blanc dédié (S["th"]) — pas de conflit avec TableStyle TEXTCOLOR
    header_row = [Paragraph(h, S["th"]) for h in headers]
    # Corps : style td avec texte noir
    body_rows  = [[Paragraph(str(c), S["td"]) for c in row] for row in rows]
    data = [header_row] + body_rows
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        # En-tête : fond navy seulement (la couleur du texte est dans le style Paragraph)
        ("BACKGROUND",     (0, 0), (-1, 0),  C_NAVY),
        ("FONTSIZE",       (0, 0), (-1, -1), 9),
        # Corps : lignes alternées
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_LGRAY, colors.white]),
        ("GRID",           (0, 0), (-1, -1), 0.25, C_GRAY),
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
    ]))
    return t


# ── Contenu ────────────────────────────────────────────────────────────────────

def build_story():
    story = []

    # ── PAGE DE COUVERTURE ─────────────────────────────────────────────────────
    story += [
        sp(60),
        p("BENINSCOPE — TERROIR", "cover_title"),
        p("Plateforme de veille territoriale quasi temps réel pour le Bénin", "cover_sub"),
        sp(4),
        hr(C_TEAL, 2),
        sp(4),
        p("Rapport technique et analytique", "cover_meta"),
        p(f"Hackathon iSHEERO x DataCamp 2026  |  Equipe 04  |  {TODAY}", "cover_meta"),
        PageBreak(),
    ]

    # ── SOMMAIRE avec liens PDF cliquables ─────────────────────────────────────
    story += [hr(C_TEAL, 2), p("Sommaire", "h1"), sp(6)]

    toc_entries = [
        ("1.",  "Résumé exécutif",                  ANCHORS[1]),
        ("2.",  "Contexte et problématique",         ANCHORS[2]),
        ("3.",  "Architecture du système",           ANCHORS[3]),
        ("4.",  "Pipeline de données GDELT",         ANCHORS[4]),
        ("5.",  "Score de Tension Territorial (STT)",ANCHORS[5]),
        ("6.",  "Plateforme web TERROIR",            ANCHORS[6]),
        ("7.",  "Insights clés et résultats",        ANCHORS[7]),
        ("8.",  "Déploiement et infrastructure",     ANCHORS[8]),
        ("9.",  "Divulgation IA",                    ANCHORS[9]),
        ("10.", "Limitations et travaux futurs",     ANCHORS[10]),
        ("11.", "Equipe et stack technique",         ANCHORS[11]),
    ]
    for num, title, anchor in toc_entries:
        # Lien PDF interne cliquable vers l'ancre de la section
        story.append(
            Paragraph(
                f'<b>{num}</b>  <a href="#{anchor}" color="#1a6fa8">{title}</a>',
                S["toc_link"]
            )
        )
    story.append(PageBreak())

    # ── 1. RÉSUMÉ EXÉCUTIF ─────────────────────────────────────────────────────
    story += h1("1. Résumé exécutif", 1)
    story += [
        p("BéninScope — TERROIR est une plateforme de veille sécuritaire et territoriale "
          "destinée au Bénin, développée dans le cadre du Hackathon iSHEERO x DataCamp 2026. "
          "Elle répond à un besoin concret : agréger, structurer et rendre exploitables les "
          "signaux d'événements géopolitiques et sécuritaires disponibles dans les flux "
          "médiatiques internationaux, en les croisant avec des signalements citoyens géolocalisés."),
        p("La plateforme ingère en continu les données GDELT v2 (Global Database of Events, "
          "Language, and Tone), soit plus de 31 500 événements référencés sur le Bénin "
          "entre janvier 2025 et fin mai 2026. Un algorithme composite, le Score de Tension "
          "Territorial (STT), synthétise par département les dimensions de conflictualité, "
          "de tonalité médiatique, de volume et de diversité des sources, sur une fenêtre "
          "glissante de 14 jours comparée à un baseline de 90 jours."),
        p("La plateforme est accessible via une interface web interactive (carte Leaflet, "
          "clustering de marqueurs, filtres temporels) et un tableau de bord analytique "
          "Streamlit. Elle est déployée en continu sur Railway (backend FastAPI) et "
          "Streamlit Community Cloud (dashboard)."),
        sp(4),
        kv_table([
            ("Volume de données",  "31 529 événements GDELT, janvier 2025 — mai 2026"),
            ("Latence GDELT",      "15 minutes (cycle de polling automatique)"),
            ("Couverture",         "12 départements du Bénin, coordonnées enrichies par priorité"),
            ("Déploiement",        "Railway (API) + Streamlit Cloud (dashboard), GitHub CI/CD"),
            ("Signalements",       "Module citoyen géolocalisé avec validation croisée GDELT"),
        ]),
        sp(6),
    ]

    # ── 2. CONTEXTE ET PROBLÉMATIQUE ───────────────────────────────────────────
    story += h1("2. Contexte et problématique", 2)
    story += h2("2.1 Déséquilibre de la couverture médiatique")
    story += [
        p("L'analyse des données GDELT sur le Bénin révèle un déséquilibre structurel majeur : "
          "les départements du nord — Alibori, Atacora, Borgou — ne représentent que 4 % "
          "de la couverture médiatique internationale attribuée au pays. Or, le ton moyen "
          "de cette couverture nordiste est près de quatre fois plus négatif que celui du "
          "reste du territoire (−4,10 contre −1,09 en score AvgTone GDELT)."),
        p("Lorsque cette zone est couverte, c'est quasi exclusivement pour des incidents "
          "sécuritaires : vols de bétail, tensions sur les axes routiers commerciaux, "
          "conflits communautaires liés au foncier, incidents aux marchés frontaliers avec "
          "le Niger, le Burkina Faso et le Nigeria. Le gradient nord-sud est systématique "
          "et persistant sur toute la période analysée."),
    ]
    story += h2("2.2 Absence d'outil de centralisation")
    story += [
        p("Ces signaux existent dans les flux GDELT, mis à jour toutes les 15 minutes. "
          "Ils ne sont ni agrégés, ni localisés avec précision, ni mis en relation avec "
          "les remontées de terrain. Les ONG, les cellules de crise préfectorales et les "
          "journalistes d'investigation n'ont aucun outil unifié pour :"),
        *bullet([
            "visualiser la distribution géographique des événements sécuritaires en temps réel,",
            "distinguer les sources médiatiques locales des sources internationales (notamment nigérianes),",
            "comparer la tension actuelle d'un département à sa moyenne historique,",
            "croiser un événement GDELT avec un signalement citoyen de même zone.",
        ]),
        p("TERROIR répond directement à ce vide."),
    ]

    # ── 3. ARCHITECTURE ────────────────────────────────────────────────────────
    story += [PageBreak()]
    story += h1("3. Architecture du système", 3)
    story += [
        p("L'architecture de BéninScope est organisée en trois couches distinctes, "
          "communiquant par des fichiers Parquet persistants et une API REST."),
    ]
    story += h2("3.1 Vue d'ensemble")
    story += [
        data_table(
            ["Couche", "Composant", "Rôle"],
            [
                ["Données",   "GDELT v2 (masterfilelist + live poller)", "Source primaire, 15-min updates"],
                ["Données",   "benin_enrichi.parquet",                   "Historique jan 2025 — mai 2026"],
                ["Données",   "benin_live.parquet",                      "Fenêtre glissante 30 jours"],
                ["Données",   "incidents.db (SQLite)",                   "Signalements citoyens"],
                ["Backend",   "FastAPI (Python)",                        "API REST /events, /incidents, /stt"],
                ["Backend",   "gdelt_live_poller",                       "Thread daemon, cycle 15 min"],
                ["Frontend",  "Vue 3 + Leaflet + Bootstrap 5",           "Interface carte, filtres, signalement"],
                ["Dashboard", "Streamlit",                               "Analyse approfondie, STT, timeline"],
                ["Déploiement","Railway + Streamlit Cloud",              "CI/CD automatique sur push GitHub"],
            ],
            col_widths=[3.2*cm, 6.5*cm, 6.8*cm],
        ),
        sp(8),
    ]
    story += h2("3.2 Fusion des données")
    story += [
        p("La fonction load_combined_data() fusionne les deux sources Parquet "
          "(historique + live) en déduplicant sur GLOBALEVENTID. Chaque endpoint de "
          "l'API consomme cette vue unifiée, garantissant que les filtres temporels "
          "(fenêtre de 30 jours par défaut) opèrent sur l'intégralité des données "
          "disponibles, pas uniquement sur les derniers événements live."),
    ]

    # ── 4. PIPELINE GDELT ──────────────────────────────────────────────────────
    story += h1("4. Pipeline de données GDELT", 4)
    story += h2("4.1 Source de données")
    story += [
        p("GDELT v2 publie toutes les 15 minutes un fichier CSV compressé recensant "
          "l'intégralité des événements géopolitiques détectés dans la presse mondiale. "
          "Chaque ligne correspond à un événement : deux acteurs, un type d'action "
          "(code CAMEO), une localisation géographique, un score Goldstein et un "
          "score de ton médiatique (AvgTone)."),
    ]
    story += h2("4.2 Filtrage Bénin")
    story += [
        p("Le filtrage géographique s'opère en deux passes :"),
        *bullet([
            "Filtre primaire : ActionGeo_CountryCode == 'BN' (code ISO Bénin dans GDELT).",
            "Filtre secondaire (bbox) : latitude 5.5–13.0 N, longitude 0.5–4.0 E, "
              "pour éliminer les homonymies géographiques et les événements mal localisés.",
        ]),
        p("Les sources médiatiques nigérianes (domaines .ng, mots-clés 'nigeria', 'naij.com') "
          "font l'objet d'un comptage séparé (indicateur IDN%) et peuvent être exclues "
          "via un filtre dédié dans l'interface, sans affecter le calcul global."),
    ]
    story += h2("4.3 Enrichissement des coordonnées")
    story += [
        p("GDELT fournit plusieurs niveaux de géolocalisation par événement. Un système "
          "de priorité assigne la coordonnée la plus précise disponible :"),
        data_table(
            ["Priorité", "Source", "Description"],
            [
                ["1 (max)", "ActionGeo",     "Coordonnée exacte du lieu de l'action"],
                ["2",       "Actor1Geo",     "Coordonnée de l'acteur principal béninois"],
                ["3",       "Actor2Geo",     "Coordonnée de l'acteur secondaire béninois"],
                ["4",       "centroid_adm1", "Centroïde du département identifié"],
                ["5 (min)", "centroid_pays", "Centre géographique du Bénin (fallback)"],
            ],
            col_widths=[2.5*cm, 4*cm, 10*cm],
        ),
        sp(4),
        p("Les événements assignés au centroïde national (niveau 5) reçoivent un jitter "
          "gaussien (sigma = 0.06 degré) pour éviter la superposition des marqueurs "
          "sur la carte. Le clustering Leaflet.MarkerCluster agrège les points proches "
          "en bulles numérotées, avec désagrégation automatique au zoom >= 9."),
    ]
    story += h2("4.4 Historique et remplissage de gap")
    story += [
        p("Un pipeline de remplissage (scripts/fill_gap_2026.py) a téléchargé et "
          "traité 3 935 fichiers GDELT en parallèle (6 threads) pour couvrir la "
          "période avril–mai 2026. Au total, 31 529 événements couvrent la période "
          "du 1er janvier 2025 au 28 mai 2026 dans le fichier benin_enrichi.parquet."),
    ]

    # ── 5. STT ─────────────────────────────────────────────────────────────────
    story += [PageBreak()]
    story += h1("5. Score de Tension Territorial (STT)", 5)
    story += h2("5.1 Définition")
    story += [
        p("Le STT est un indice composite calculé par département sur une fenêtre "
          "glissante de 14 jours, comparée à un baseline de 90 jours. Il quantifie "
          "l'intensité relative de la tension sécuritaire et médiatique d'une zone "
          "par rapport à sa propre moyenne historique."),
    ]
    story += h2("5.2 Formule")
    story += [
        p("STT = 0,40 x z_cameo  +  0,35 x z_tone  +  0,15 x z_volume  +  0,10 x z_sources",
          "highlight"),
        data_table(
            ["Composante", "Poids", "Description"],
            [
                ["z_cameo",   "40 %", "Score CAMEO moyen normalisé (conflictualité type d'action)"],
                ["z_tone",    "35 %", "Tonalité médiatique moyenne normalisée (AvgTone inversé)"],
                ["z_volume",  "15 %", "Volume d'événements normalisé sur 14 j vs baseline 90 j"],
                ["z_sources", "10 %", "Nombre de sources distinctes normalisé"],
            ],
            col_widths=[3*cm, 2*cm, 11.5*cm],
        ),
        sp(4),
    ]
    story += h2("5.3 Niveaux d'alerte")
    story += [
        data_table(
            ["Niveau", "Seuil STT", "Signification", "Action recommandée"],
            [
                ["Normal",    "< 2,0",   "Tension dans la norme historique",
                 "Veille habituelle"],
                ["Précaution","2,0 – 3,0","Tension modérément supérieure à la moyenne",
                 "Vérification avec relais local, surveillance 24h"],
                ["Alerte",   "> 3,0",   "Tension significativement élevée",
                 "Contacter relais terrain, informer coordinateur sécurité"],
            ],
            col_widths=[2.5*cm, 2.5*cm, 5.5*cm, 6*cm],
        ),
        sp(6),
    ]
    story += h2("5.4 Validation croisée")
    story += [
        p("Les signalements citoyens non validés sont automatiquement rapprochés des "
          "événements GDELT sécuritaires récents (rayon 50 km, fenêtre 24 h). Un "
          "signalement ayant un événement GDELT correspondant est validé automatiquement "
          "par l'algorithme auto_validate_with_gdelt()."),
    ]

    # ── 6. PLATEFORME WEB ──────────────────────────────────────────────────────
    story += h1("6. Plateforme web TERROIR", 6)
    story += h2("6.1 Architecture frontend")
    story += [
        p("L'interface est une Single Page Application (SPA) construite avec Vue 3 "
          "(CDN, sans bundler), Bootstrap 5 et Leaflet.js. Elle est servie statiquement "
          "par FastAPI via StaticFiles. Quatre vues sont accessibles par routing hash :"),
        *bullet([
            "Carte live (#/live) — carte Leaflet avec événements GDELT et signalements citoyens, "
              "filtres par type, fenêtre temporelle (24h à 30j), exclusion Nigeria, clustering.",
            "Analyse TERROIR (#/terroir) — scores STT par département, graphique Plotly, "
              "fiches par département avec niveau d'alerte et phrase explicative.",
            "Statistiques (#/analysis) — timeline des événements, répartition CAMEO, "
              "indicateurs globaux sur la période.",
            "Signalement (#/report) — formulaire citoyen avec géolocalisation GPS ou "
              "sélection par département, liste des 5 signalements récents.",
        ]),
    ]
    story += h2("6.2 Temps réel et synchronisation")
    story += [
        p("Les incidents citoyens apparaissent sur la carte dans la seconde suivant "
          "la soumission (appel loadLiveMap() post-POST). Un intervalle automatique "
          "de 60 secondes synchronise les marqueurs pour tous les utilisateurs connectés "
          "simultanément. Le statut GDELT se rafraîchit toutes les 2 minutes."),
    ]
    story += h2("6.3 Localisation temporelle")
    story += [
        p("Tous les horodatages affichés utilisent le fuseau horaire du Bénin "
          "(Africa/Porto-Novo, WAT = UTC+1, sans heure d'été). Les timestamps stockés "
          "en base sont en UTC avec suffixe Z explicite pour garantir une interprétation "
          "correcte par les navigateurs de n'importe quelle région."),
    ]

    # ── 7. INSIGHTS ────────────────────────────────────────────────────────────
    story += [PageBreak()]
    story += h1("7. Insights clés et résultats", 7)
    story += [
        data_table(
            ["Insight", "Observation", "Implication"],
            [
                [
                    "Biais de couverture nord",
                    "Alibori, Atacora, Borgou : < 4 % des articles GDELT Bénin",
                    "La sous-représentation médiatique masque l'intensité réelle "
                    "des tensions — nécessite une veille active, pas passive",
                ],
                [
                    "Gradient de ton",
                    "Ton nord : −4,10 | Sud : −1,09 (ratio 3,8x)",
                    "Quand le nord est couvert, c'est quasi exclusivement "
                    "pour des incidents négatifs",
                ],
                [
                    "Contamination nigériane",
                    "15 à 20 % des événements GDELT Bénin proviennent "
                    "de médias nigérians (.ng)",
                    "Sans filtre, la veille intègre une perspective extérieure "
                    "potentiellement biaisée — filtrage activable en 1 clic",
                ],
                [
                    "Latence GDELT",
                    "Délai médian source vers GDELT : 15–60 min",
                    "Fenêtre suffisante pour une veille préventive ; "
                    "insuffisante pour une alerte push automatique (V2)",
                ],
                [
                    "Corrélation GDELT / terrain",
                    "Signalements citoyens et événements GDELT proches "
                    "convergent sur les mêmes foyers",
                    "La validation croisée automatique (50 km / 24h) réduit "
                    "la charge de modération manuelle",
                ],
            ],
            col_widths=[3.5*cm, 5.5*cm, 7.5*cm],
        ),
        sp(8),
    ]

    # ── 8. DÉPLOIEMENT ─────────────────────────────────────────────────────────
    story += h1("8. Déploiement et infrastructure", 8)
    story += [
        kv_table([
            ("Backend API",   "Railway — déploiement automatique sur push GitHub (branche main). "
                              "Serveur Uvicorn, Python 3.11."),
            ("Dashboard",     "Streamlit Community Cloud — déploiement depuis le même repo GitHub, "
                              "branche main, fichier dashboard/app.py."),
            ("CI/CD",         "Aucune pipeline custom. Le push GitHub déclenche le redéploiement "
                              "automatique sur les deux plateformes (< 3 min)."),
            ("Persistance",   "benin_enrichi.parquet versionné dans le repo (données historiques). "
                              "incidents.db versionné avec schéma vide (créé sur Railway au premier démarrage). "
                              "benin_live.parquet régénéré par le poller toutes les 15 min."),
            ("Monitoring",    "Endpoint /api/health + /api/gdelt/status exposant l'état du poller, "
                              "le nombre d'événements live et l'heure du dernier cycle (heure Bénin)."),
        ]),
        sp(6),
    ]

    # ── 9. DISCLOSURE IA ───────────────────────────────────────────────────────
    story += h1("9. Divulgation IA", 9)
    story += [
        p("Conformément au règlement du hackathon, l'équipe déclare l'usage des "
          "systèmes d'intelligence artificielle suivants :"),
        *bullet([
            "Claude Sonnet 4.6 (Anthropic) — assistant au développement logiciel : "
              "architecture du pipeline de données, conception de l'algorithme STT, debugging "
              "des pipelines Parquet/GDELT, rédaction de scripts Python, corrections des "
              "erreurs de fuseau horaire, génération du présent rapport.",
            "GDELT Project (NLP intégré) — les scores AvgTone, GoldsteinScale et les "
              "codes CAMEO présents dans les données brutes sont produits par les modèles NLP "
              "du projet GDELT, extérieurs à l'équipe. Ils sont utilisés comme features, "
              "non recalculés.",
        ]),
        p("Aucun modèle propriétaire n'a été entraîné par l'équipe. Aucune donnée "
          "personnelle n'a été transmise à un service LLM externe. Les signalements "
          "citoyens sont stockés exclusivement en base SQLite locale."),
    ]

    # ── 10. LIMITATIONS ────────────────────────────────────────────────────────
    story += [PageBreak()]
    story += h1("10. Limitations et travaux futurs", 10)
    story += h2("10.1 Limitations actuelles")
    story += [
        *bullet([
            "Précision géographique : 60 à 70 % des événements GDELT Bénin "
              "tombent au niveau centroïde département ou pays (pas de coordonnée exacte). "
              "Le jitter appliqué est une approximation visuelle, pas une localisation réelle.",
            "Couverture médiatique : GDELT indexe principalement des sources "
              "en ligne en anglais et français. Les événements couverts uniquement par "
              "des médias locaux non indexés (radio, presse imprimée) sont absents.",
            "Persistance signalements : incidents.db est stocké sur le filesystem "
              "Railway (éphémère entre redéploiements pour les signalements survenus après "
              "le dernier commit). Une base de données managée (PostgreSQL) est recommandée.",
            "STT baseline : les 90 jours de baseline intègrent des événements "
              "des deux sources (historique + live). Sur les premières semaines de vie "
              "de la plateforme, le baseline peut être insuffisant pour les petits départements.",
        ]),
    ]
    story += h2("10.2 Travaux futurs (V2)")
    story += [
        *bullet([
            "Géolocalisation par NLP sur contenu d'article : la limitation principale "
              "de GDELT est que ses coordonnées sont extraites des métadonnées de surface "
              "(titre, entités nommées), sans lecture du corps du texte. Nous prévoyons de "
              "développer un modèle NLP dédié qui analysera le contenu complet des articles "
              "sources pour extraire les lieux mentionnés (villes, marchés, axes routiers, "
              "quartiers), les désambiguïser dans le contexte béninois et produire des "
              "coordonnées de précision sous-départementale. Ce modèle enrichirait ou "
              "corrigerait les coordonnées GDELT existantes, réduisant drastiquement "
              "la part des événements actuellement assignés au centroïde pays (niveau 5).",
            "Alertes push (email / SMS) déclenchées automatiquement quand le STT "
              "d'un département franchit le seuil Alerte.",
            "Migration incidents.db vers PostgreSQL managé pour la persistance multi-déploiement.",
            "Intégration de sources locales béninoises non indexées par GDELT "
              "(Frissons d'Afrique, L'Evénement Précis, etc.).",
            "Module de cartographie des acteurs (Actor1 / Actor2) pour détecter "
              "les réseaux d'acteurs récurrents dans les zones de tension.",
        ]),
    ]

    # ── 11. EQUIPE ─────────────────────────────────────────────────────────────
    story += h1("11. Equipe et stack technique", 11)
    story += h2("11.1 Stack technique")
    story += [
        data_table(
            ["Categorie", "Technologies"],
            [
                ["Traitement de données", "Python 3.11, Pandas, PyArrow, Parquet"],
                ["API backend",           "FastAPI, Uvicorn, Pydantic"],
                ["Base de données",       "SQLite (signalements), Parquet (GDELT)"],
                ["Source de données",     "GDELT v2, BigQuery (exploration initiale)"],
                ["Frontend web",          "Vue 3 (CDN), Leaflet.js, Leaflet.MarkerCluster, Bootstrap 5, Plotly.js"],
                ["Dashboard analytique",  "Streamlit"],
                ["Déploiement",           "Railway (API), Streamlit Community Cloud (dashboard)"],
                ["CI/CD",                 "GitHub (push-to-deploy)"],
                ["IA / Assistance",       "Claude Sonnet 4.6 (Anthropic)"],
            ],
            col_widths=[5*cm, 11.5*cm],
        ),
        sp(8),
        hr(C_TEAL, 1),
        sp(4),
        p("Rapport généré automatiquement le " + TODAY + ". "
          "BéninScope — TERROIR, Hackathon iSHEERO x DataCamp 2026, Equipe 04.",
          "caption"),
    ]

    return story


# ── Génération PDF ─────────────────────────────────────────────────────────────

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(C_GRAY)
    w, h = A4
    if doc.page > 1:
        canvas.drawString(2 * cm, 1.2 * cm,
                          "BéninScope — TERROIR  |  Hackathon iSHEERO x DataCamp 2026")
        canvas.drawRightString(w - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.4 * cm,
        title="BéninScope — TERROIR : Rapport technique",
        author="Equipe 04 — Hackathon iSHEERO x DataCamp 2026",
        subject="Plateforme de veille territoriale pour le Bénin",
    )
    story = build_story()
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF genere : {OUT}")
    print(f"Taille     : {OUT.stat().st_size / 1024:.1f} Ko")


if __name__ == "__main__":
    main()
