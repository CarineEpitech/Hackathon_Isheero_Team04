-- Requête d'extraction GDELT — Bénin Insights Challenge
-- Source : BigQuery public dataset gdelt-bq.gdeltv2.events
-- Filtre : événements géolocalisés au Bénin (code FIPS BN), année 2025
-- Résultat : environ 23 859 lignes · 351 jours couverts sur 365
--
-- Prérequis : compte Google Cloud avec accès BigQuery
-- Exécution : Google Cloud Console > BigQuery > Éditeur de requête
-- ou via la bibliothèque google-cloud-bigquery en Python
--
-- Fichier de sortie attendu : data/raw/benin_raw.csv

SELECT
    GLOBALEVENTID,
    SQLDATE,
    MONTHYEAR,
    YEAR,
    FractionDate,
    IsRootEvent,
    ActionGeo_CountryCode,
    ActionGeo_FullName,
    ActionGeo_ADM1Code,
    ActionGeo_Lat,
    ActionGeo_Long,
    Actor1Geo_CountryCode,
    Actor2Geo_CountryCode,
    Actor1CountryCode,
    Actor2CountryCode,
    Actor1Name,
    Actor2Name,
    Actor1Type1Code,
    Actor2Type1Code,
    Actor1KnownGroupCode,
    Actor2KnownGroupCode,
    EventRootCode,
    EventBaseCode,
    EventCode,
    QuadClass,
    GoldsteinScale,
    NumMentions,
    NumSources,
    NumArticles,
    AvgTone,
    SOURCEURL
FROM
    `gdelt-bq.gdeltv2.events`
WHERE
    ActionGeo_CountryCode = 'BN'AND YEAR = 2025
ORDER BY
    SQLDATE ASC;

-- Pour exporter en CSV depuis BigQuery :
-- Résultats > Enregistrer les résultats > CSV (local) ou GCS
-- Renommer le fichier téléchargé en benin_raw.csv
-- Le placer dans data/raw/benin_raw.csv avant de lancer Pipeline.py
