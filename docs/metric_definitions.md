# Metric definitions and changes

Every metric in this analysis is defined against the publication rules in
force at the time. Three definitions require explicit governance.

## 1. Type 1 vs all-types four-hour performance

Published A&E figures combine Type 1 (major, consultant-led ED), Type 2
(specialty) and Type 3 (UTC/minor injury) attendances. Type 3 units meet the
four-hour standard almost by default, so the all-types headline depends on a
trust's service configuration, not its emergency care. A trust absorbing a
UTC can improve its headline while its actual ED deteriorates (Simpson's
paradox). **Type 1 performance is the headline metric throughout; the
all-types figure appears only as `headline_perf_reconciliation` alongside the
`headline_flattery_gap` column that quantifies the difference.**

## 2. Twelve-hour waits: two incompatible definitions

- Historic published measure: 12+ hours **from decision to admit (DTA)** —
  substantially understates door-to-departure waits.
- Later measure: 12+ hours **from arrival** — far larger values.

The `twelve_hour_basis` column records which definition applies to each row.
**Series using different bases are never combined in one chart.** Set the
basis per source file during ingest and verify against each publication's
footnotes.

## 3. The four-hour standard itself moved

The historic operating standard was 95%; interim recovery thresholds have
applied in later years. "Underperformance" in this analysis is defined
**relative to peers in the same period** (volume-tercile benchmark), not
against a fixed standard, precisely so the moving target does not manufacture
trend artefacts. Where a standard line is drawn on charts, the standard in
force for that period is used and labelled.

## Benchmark note

SQLite lacks a MEDIAN() window function; the peer benchmark uses the
volume-tercile mean instead. With ~40+ organisations per tercile the
difference is minor; if migrating to PostgreSQL, replace with
PERCENTILE_CONT(0.5).

Last verified against NHS England publication guidance: [DATE — update]
