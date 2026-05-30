"""
Peuple incidents.db avec des signalements réalistes pour la démo.
Distribution : ~65% nord (Alibori, Atacora, Borgou, Donga), ~35% sud.
4 types max : Conflit armé, Agression, Enlèvement, Tension.
Usage : python scripts/populate_demo_incidents.py
"""
import sqlite3
import random
from pathlib import Path
from datetime import datetime, timezone, timedelta

random.seed(42)

DB = Path(__file__).resolve().parents[1] / "backend" / "data" / "incidents.db"

WAT = timezone(timedelta(hours=1))

TYPES = ["Conflit armé", "Agression", "Enlèvement", "Tension"]

# ── Zones géographiques ────────────────────────────────────────────────────────
ZONES = [
    # (departement, adm1_code, lat_min, lat_max, lon_min, lon_max, weight)
    # NORD — poids forts
    ("Alibori",    "BN01", 10.8, 11.8, 2.6, 3.5,  18),
    ("Atacora",    "BN02",  9.9, 11.2, 1.1, 1.9,  16),
    ("Borgou",     "BN04",  9.2, 10.5, 2.4, 3.2,  14),
    ("Donga",      "BN03",  9.4,  9.9, 1.6, 2.1,  10),
    # SUD / CENTRE — poids faibles
    ("Collines",   "BN05",  7.9,  8.8, 2.0, 2.6,   8),
    ("Zou",        "BN10",  7.1,  7.9, 2.1, 2.6,   6),
    ("Atlantique", "BN06",  6.3,  6.8, 2.0, 2.5,   5),
    ("Mono",       "BN12",  6.4,  7.0, 1.3, 1.8,   4),
    ("Ouémé",      "BN08",  6.4,  7.1, 2.4, 2.9,   3),
]

# ── Descriptions réalistes par type et zone ───────────────────────────────────
DESCRIPTIONS = {
    "Conflit armé": [
        "Échange de tirs signalé entre éléments armés non identifiés et forces de sécurité sur l'axe Malanville–Kandi. Population du quartier évacuée vers l'école primaire.",
        "Attaque à main armée contre un convoi de commerçants sur la route nationale. Deux blessés légers transportés au centre de santé de Banikoara.",
        "Groupe armé aperçu en bordure de forêt classée au nord de Tanguiéta. Présence signalée par un berger revenant du pâturage matinal.",
        "Incident armé près du poste de contrôle douanier de Porga. Les forces de l'ordre ont sécurisé le périmètre. Circulation suspendue deux heures.",
        "Affrontement entre groupes rivaux sur fond de litige foncier au nord de Sinendé. Quatre personnes ont fui vers le village voisin de Bembèrèkè.",
        "Coups de feu entendus dans la nuit du côté du parc du W. Des patrouilles de sécurité ont été déployées à l'aube sans contact confirmé.",
    ],
    "Agression": [
        "Vol à main armée sur le marché hebdomadaire de Gogounou. Trois commerçantes dépouillées de leurs recettes. Signalement fait à la gendarmerie locale.",
        "Agression nocturne sur un agent de santé rentrant de garde au centre de santé de Kandi. Téléphone et moto dérobés. Pas de blessure grave.",
        "Attaque de moto-taxi sur l'axe Natitingou–Djougou en fin d'après-midi. Le conducteur a été roué de coups et laissé sur le bas-côté.",
        "Commerçant dépouillé de sa marchandise à la sortie du marché de Parakou-nord. Les auteurs ont pris la fuite en direction de la forêt.",
        "Agression à la machette lors d'un différend lié à un élevage dans le village de Gando-Koalou. Un blessé hospitalisé au CHD de Natitingou.",
        "Plusieurs femmes revenues du champ rapportent avoir été intimidées par des individus armés de bâtons sur la piste de Pehunco.",
    ],
    "Enlèvement": [
        "Disparition de deux éleveurs peuls dans la zone de pâturage entre Karimama et Malanville. Leurs familles sont sans nouvelles depuis 36 heures.",
        "Un enseignant du collège de Kérou aurait été retenu contre sa volonté par des inconnus selon un proche. La gendarmerie de Kérou a ouvert une enquête.",
        "Trois jeunes hommes portés disparus depuis leur départ pour couper du bois en périphérie de la forêt de Sota. Recherches en cours.",
        "Commerçant de Ségbana non rentré après son dernier trajet entre Ségbana et Malanville. Sa famille a alerté les autorités locales le soir même.",
        "Un adolescent aurait été emmené de force depuis un champ de coton à la périphérie de Bembèrèkè selon le témoignage d'un voisin.",
    ],
    "Tension": [
        "Tensions entre agriculteurs sédentaires et éleveurs transhumants au niveau des plaines de Kalalé. Médiateurs communautaires dépêchés sur place.",
        "Situation tendue au marché de Natitingou suite à un différend sur les prix du sorgho. Les chefs de quartier ont demandé le calme.",
        "Blocage de la route entre Cobly et Tanguiéta par des jeunes protestant contre le manque d'eau potable dans leurs villages. Circulation perturbée deux heures.",
        "Rumeurs de présence de groupes suspects dans la zone frontalière avec le Burkina Faso à hauteur de Tanguiéta. Vérification en cours par les autorités.",
        "Altercation entre deux communautés à propos d'un point d'eau au nord de Péhunco. La tension est retombée après l'intervention du chef de village.",
        "Inquiétude des habitants du quartier Zongo à Parakou après des mouvements suspects observés deux nuits de suite près du marché de gros.",
        "Conflit entre propriétaires terriens et migrants agricoles dans la commune de Sinendé. Le sous-préfet a convoqué les parties pour une médiation.",
        "Fermeture préventive du marché frontalier de Malanville suite à des informations sur des individus armés venus du Niger selon les autorités locales.",
    ],
}

# ── Sources réalistes ──────────────────────────────────────────────────────────
SOURCES = ["citoyen", "citoyen", "citoyen", "ong", "journaliste"]
PSEUDOS  = [
    "Idrissou M.", "Rafiou K.", "Bérnadette A.", "Anonyme", "Salimane D.",
    "Fatou B.", "Anonyme", "Karimou H.", "Anonyme", "Mariama T.",
    "Ousmane Z.", "Anonyme", "Djibril N.", "Anonyme", "Rosine E.",
]


def rand_ts(days_ago_max=7, days_ago_min=0):
    """Timestamp UTC aléatoire dans la fenêtre [days_ago_min, days_ago_max]."""
    now = datetime.now(tz=timezone.utc)
    delta = timedelta(
        seconds=random.randint(
            int(days_ago_min * 86400),
            int(days_ago_max * 86400),
        )
    )
    return (now - delta).isoformat()


def pick_zone():
    population = [(z, z[6]) for z in ZONES]
    zones, weights = zip(*population)
    return random.choices(zones, weights=weights, k=1)[0]


def generate_incident(i):
    zone = pick_zone()
    dept, code, lat_min, lat_max, lon_min, lon_max, _ = zone

    # Nord → plus de conflits armés et enlèvements
    is_north = code in ("BN01", "BN02", "BN03", "BN04")
    if is_north:
        type_ = random.choices(
            TYPES, weights=[35, 25, 20, 20], k=1)[0]
    else:
        type_ = random.choices(
            TYPES, weights=[15, 30, 10, 45], k=1)[0]

    desc = random.choice(DESCRIPTIONS[type_])
    lat  = round(random.uniform(lat_min, lat_max), 5)
    lon  = round(random.uniform(lon_min, lon_max), 5)

    # Incidents récents non validés, plus anciens souvent validés
    days_ago = random.choices(
        [0.1, 0.5, 1, 2, 3, 5, 7],
        weights=[5, 10, 20, 20, 15, 15, 15], k=1)[0]
    ts = rand_ts(days_ago_max=days_ago, days_ago_min=0)

    # Validation : incidents > 2 jours → 70% validés, récents → 20%
    validated = 1 if (days_ago > 2 and random.random() < 0.70) or \
                     (days_ago <= 2 and random.random() < 0.20) else 0

    source = random.choice(SOURCES)
    pseudo = random.choice(PSEUDOS)

    return (ts, type_, desc, lat, lon, source, pseudo, validated, code, dept)


def main():
    # Vider les données de démo existantes (pas les vraies)
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents_citoyens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                source TEXT DEFAULT 'citoyen',
                pseudo TEXT,
                validated INTEGER DEFAULT 0,
                adm1_code TEXT,
                departement TEXT
            )""")
        conn.execute("DELETE FROM incidents_citoyens")
        conn.commit()

    incidents = [generate_incident(i) for i in range(32)]

    # Trier du plus ancien au plus récent (id cohérent)
    incidents.sort(key=lambda x: x[0])

    with sqlite3.connect(DB) as conn:
        conn.executemany("""
            INSERT INTO incidents_citoyens
              (timestamp, type, description, lat, lon, source, pseudo, validated, adm1_code, departement)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, incidents)
        conn.commit()

    # Résumé
    with sqlite3.connect(DB) as conn:
        import pandas as pd
        df = pd.read_sql("SELECT type, departement, validated FROM incidents_citoyens", conn)

    print(f"\n{len(df)} signalements inseres dans {DB}\n")
    print("Par type :")
    print(df["type"].value_counts().to_string())
    print("\nPar département :")
    print(df["departement"].value_counts().to_string())
    print(f"\nValidés : {df['validated'].sum()} / {len(df)}")

    nord = df[df["departement"].isin(["Alibori","Atacora","Borgou","Donga"])]
    print(f"Nord    : {len(nord)} ({len(nord)/len(df)*100:.0f}%)")
    print(f"Sud     : {len(df)-len(nord)} ({(len(df)-len(nord))/len(df)*100:.0f}%)")


if __name__ == "__main__":
    main()
