# Organisation code changes and merger policy

NHS provider (ODS) codes are not stable across a multi-year window. Trust
mergers retire predecessor codes and introduce successor codes, silently
breaking naive time-series joins: the predecessor "vanishes" and the
successor appears with no history, corrupting persistence metrics.

## Policy

Predecessor series are combined into the successor organisation via the
mapping in `src/org_mapping.py`. Every affected row is flagged
`is_merged_series = 1`, so all persistence analysis can be run both including
and excluding merger-affected organisations.

Alternative considered and rejected: truncating predecessor history. This
preserves code purity but destroys exactly the longitudinal signal the
project exists to measure.

## Maintaining the mapping

1. Identify codes that stop/start reporting mid-window (the data quality
   query in sql/analysis.sql surfaces these).
2. Verify each against the ODS change history
   (odsdatasearchandexport.nhs.uk) and publication footnotes.
3. Add verified mappings to MERGER_MAP with the effective date.
4. Record the verification date below.

Names are display-only; joins are always on resolved ODS code.

Last verified: [DATE — update when you populate the map]
