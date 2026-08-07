-- ===========================================================================
-- NHS Emergency Care Pressure Analysis
-- Design principles:
--   * Type 1 (major ED) performance is the headline; all-types shown only
--     for reconciliation (see docs/metric_definitions.md — Simpson's paradox)
--   * Pressure (demand) separated from performance (four-hour delivery)
--   * Persistence flag: below peer median in >= 10 of trailing 12 months
--   * Merged-series organisations flagged so persistence can be run
--     with/without merger effects
-- ===========================================================================

WITH monthly AS (
    SELECT
        period,
        ods_code,
        provider_name,
        is_merged_series,
        type1_attendances,
        total_attendances,
        emergency_admissions,
        -- Type 1 four-hour performance: the honest metric
        CASE WHEN type1_attendances > 0
             THEN type1_within_4h * 1.0 / type1_attendances
        END AS t1_four_hour_perf,
        -- All-types headline: reconciliation only
        CASE WHEN total_attendances > 0
             THEN total_within_4h * 1.0 / total_attendances
        END AS headline_perf,
        CASE WHEN total_attendances > 0
             THEN emergency_admissions * 1.0 / total_attendances
        END AS admission_rate
    FROM ae_monthly
),

-- ---------------------------------------------------------------------------
-- Rolling context per organisation
-- ---------------------------------------------------------------------------
with_rolling AS (
    SELECT
        *,
        AVG(t1_four_hour_perf) OVER w3  AS t1_perf_3m_avg,
        AVG(t1_four_hour_perf) OVER w12 AS t1_perf_12m_avg,
        AVG(type1_attendances) OVER w12 AS t1_attend_12m_avg,
        -- year-on-year change
        t1_four_hour_perf
          - LAG(t1_four_hour_perf, 12) OVER (
                PARTITION BY ods_code ORDER BY period
            ) AS t1_perf_yoy_change,
        type1_attendances * 1.0
          / NULLIF(LAG(type1_attendances, 12) OVER (
                PARTITION BY ods_code ORDER BY period
            ), 0) - 1 AS t1_attend_yoy_growth
    FROM monthly
    WINDOW
        w3  AS (PARTITION BY ods_code ORDER BY period
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
        w12 AS (PARTITION BY ods_code ORDER BY period
                ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
),

-- ---------------------------------------------------------------------------
-- Peer comparison: each org against the median of similarly-sized orgs
-- (demand-adjusted comparison — organisations are compared within volume
--  tercile, not against the whole country)
-- ---------------------------------------------------------------------------
sized AS (
    SELECT
        *,
        NTILE(3) OVER (PARTITION BY period ORDER BY t1_attend_12m_avg)
            AS volume_tercile
    FROM with_rolling
    WHERE type1_attendances IS NOT NULL
),

peer_benchmarked AS (
    SELECT
        s.*,
        -- SQLite lacks MEDIAN(); use the tercile mean as the peer benchmark
        -- and note the substitution in docs/metric_definitions.md.
        AVG(t1_four_hour_perf) OVER (PARTITION BY period, volume_tercile)
            AS peer_benchmark,
        CASE WHEN t1_four_hour_perf <
                  AVG(t1_four_hour_perf) OVER (PARTITION BY period, volume_tercile)
             THEN 1 ELSE 0
        END AS below_peer
    FROM sized s
)

-- ---------------------------------------------------------------------------
-- Final output: performance, pressure, and persistence flag
-- ---------------------------------------------------------------------------
SELECT
    period,
    ods_code,
    provider_name,
    is_merged_series,
    type1_attendances,
    ROUND(t1_four_hour_perf, 4)   AS t1_four_hour_perf,
    ROUND(headline_perf, 4)       AS headline_perf_reconciliation,
    ROUND(headline_perf - t1_four_hour_perf, 4)
                                  AS headline_flattery_gap,
    ROUND(admission_rate, 4)      AS admission_rate,
    ROUND(t1_perf_3m_avg, 4)      AS t1_perf_3m_avg,
    ROUND(t1_perf_yoy_change, 4)  AS t1_perf_yoy_change,
    ROUND(t1_attend_yoy_growth, 4) AS t1_attend_yoy_growth,
    ROUND(peer_benchmark, 4)      AS peer_benchmark,
    ROUND(t1_four_hour_perf - peer_benchmark, 4) AS gap_to_peers,
    -- persistence: below peers in >= 10 of the trailing 12 months
    SUM(below_peer) OVER (
        PARTITION BY ods_code ORDER BY period
        ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
    ) AS months_below_peers_of_12,
    CASE WHEN SUM(below_peer) OVER (
             PARTITION BY ods_code ORDER BY period
             ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
         ) >= 10
         THEN 1 ELSE 0
    END AS persistent_pressure_flag
FROM peer_benchmarked
ORDER BY ods_code, period;


-- ===========================================================================
-- Supporting queries (dashboard pages)
-- ===========================================================================

-- Winter pressure: Dec-Feb vs rest of year, Type 1 only
-- SELECT
--     ods_code, provider_name,
--     CASE WHEN CAST(SUBSTR(period, 6, 2) AS INTEGER) IN (12, 1, 2)
--          THEN 'Winter' ELSE 'Rest of year' END AS season,
--     ROUND(AVG(CASE WHEN type1_attendances > 0
--               THEN type1_within_4h * 1.0 / type1_attendances END), 4)
--         AS avg_t1_perf,
--     ROUND(AVG(type1_attendances), 0) AS avg_t1_attendances
-- FROM ae_monthly
-- GROUP BY ods_code, provider_name, season;

-- Data quality page: completeness by organisation
-- SELECT
--     ods_code, provider_name,
--     COUNT(*)                                    AS periods_reported,
--     SUM(CASE WHEN type1_attendances IS NULL THEN 1 ELSE 0 END)
--                                                 AS periods_missing_type1,
--     SUM(is_merged_series)                       AS merged_series_rows,
--     MIN(period)                                 AS first_period,
--     MAX(period)                                 AS last_period
-- FROM ae_monthly
-- GROUP BY ods_code, provider_name
-- ORDER BY periods_missing_type1 DESC;

-- Load log: revisions applied
-- SELECT * FROM load_log ORDER BY loaded_at DESC;
