-- Requête d'extraction GDELT — Bénin Insights Challenge
-- Période : 1er janvier 2025 → hier (CURRENT_DATE - 1)
-- Source   : BigQuery public dataset gdelt-bq.gdeltv2.events
--
-- ÉTAPES :
--   1. Aller sur https://console.cloud.google.com/bigquery
--   2. Coller cette requête dans l'éditeur
--   3. Cliquer sur "Exécuter"
--   4. Résultats > "Enregistrer les résultats" > "CSV (fichier local)"
--   5. Renommer le fichier téléchargé en  benin_2026.csv
--   6. Le placer dans  data/raw/benin_2026.csv
--   7. Lancer :  python scripts/import_2026_csv.py
--
-- Note : la première requête sur gdelt-bq est gratuite (quota 1 To/mois).
-- Cette requête consomme environ 500–800 Mo (2025 + 2026 à ce jour).
-- Les doublons avec benin_enrichi.parquet (2025) sont gérés automatiquement
-- par import_2026_csv.py (déduplication par GLOBALEVENTID).

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
    ActionGeo_CountryCode = 'BN'   -- action géographique au Bénin (FIPS), cohérent avec benin_enrichi.parquet
    AND SQLDATE >= 20250101
    AND SQLDATE < CAST(FORMAT_DATE('%Y%m%d', CURRENT_DATE()) AS INT64)

ORDER BY
    SQLDATE ASC;
