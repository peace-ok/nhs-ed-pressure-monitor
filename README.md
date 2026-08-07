# NHS Emergency Care Pressure Monitor

**Demand, four-hour performance and trust-level variation — analysed without ranking hospitals like football teams**

*Author: Peace Osemegbe Okoegwale — [LinkedIn](https://linkedin.com/in/peace-okoegwale-md-815254306)*

---

## The business question

Which NHS organisations experience persistent emergency-care pressure, and how do rising attendance volumes relate to four-hour performance and emergency admissions?

The critical framing: **a low four-hour percentage is not automatically poor performance.** It may reflect unusually high demand, admission pressure, limited bed availability, seasonal surge, case-mix complexity, downstream discharge constraints, or differences in data completeness. This analysis separates *pressure* (what arrives at the front door) from *performance* (what the organisation does with it), and treats every ranking as a starting question rather than a verdict.

This reflects my professional background: I have worked inside hospital data (clinical registry abstraction and PostgreSQL analysis at Queensland Health) and my MSc research modelled how interacting system inefficiencies amplify safety risk. This project applies that sociotechnical lens to published NHS operational data.

## Key findings

> *Updated as analysis develops. Findings below reflect the current data window.*

1. **[Finding 1 — e.g. "Type 1 (major ED) four-hour performance is N points below the all-types headline figure; trusts operating co-located UTCs show the largest gap, confirming the headline metric flatters organisational configuration rather than emergency care."]**
2. **[Finding 2 — e.g. "X trusts show persistent underperformance (below their peer median in ≥10 of 12 months) even after demand adjustment — a different list from the raw bottom-10."]**
3. **[Finding 3 — e.g. "Quarter-level bed occupancy above ~92% is associated with steeper four-hour deterioration, consistent with the flow-constraint literature (ecological association, not causal claim)."]**

## The three traps this analysis avoids

Most public re-analyses of NHS A&E data fall into at least one of these. This project handles all three explicitly:

### 1. Type 1 vs all-types performance (Simpson's paradox)
Published figures mix major emergency departments (Type 1) with specialty units and urgent treatment centres (Types 2/3), which see minor cases and meet the four-hour standard almost by default. A trust's headline number therefore depends heavily on how many walk-in services it runs — and can *improve* simply by absorbing a UTC while its actual ED deteriorates. **All performance analysis here is reported for Type 1 separately, with the all-types figure shown only for reconciliation.** See `docs/metric_definitions.md`.

### 2. Organisation codes are not stable (trust mergers)
NHS trusts merge; ODS codes change; time series silently break. A naive join shows a trust "vanishing" and a new one appearing with no history, corrupting any persistence metric. `src/org_mapping.py` maintains an explicit merger mapping for the analysis window, with a documented policy (predecessor series are combined into the successor organisation and flagged). See `docs/org_code_changes.md`.

### 3. Metric definitions changed over time
The published twelve-hour wait historically counted from *decision to admit*; NHS England later began publishing twelve-hour waits from *arrival* — far larger numbers. Mixing the two shows a fake explosion in long waits. The four-hour standard itself has moved from the historic 95% target to interim thresholds. **Every metric is analysed against the definition and standard in force at the time, documented with dates in `docs/metric_definitions.md`.**

## How it works

```
NHS England monthly A&E CSVs ──►  Python ingest & cleaning  ──►  SQLite
NHS bed availability (quarterly) ─┘        │
                                            ▼
                            SQL analysis (Type 1 focus, rolling averages,
                            demand-adjusted comparison, persistence flags)
                                            │
                                            ▼
                            Power BI / Tableau dashboard (4 pages + data quality)
```

1. **Ingest** — `src/ingest.py` loads NHS England monthly A&E Attendances & Emergency Admissions files and quarterly bed availability extracts, standardising column names across publication-format changes.
2. **Reconcile** — provider names and ODS codes are standardised; known mergers are applied from `src/org_mapping.py`; unmatched codes are surfaced, never dropped silently.
3. **Analyse** — `sql/analysis.sql` computes Type 1 four-hour performance, admission rates, month-on-month and year-on-year change, 3- and 12-month rolling averages, demand-adjusted peer comparison, and persistent-pressure flags.
4. **Present** — dashboard pages: National overview, Provider comparison, Pressure relationships, and Data quality.

## Data quality and limitations

- **Suppression and revision.** Small counts are suppressed in source files and later months are revised; the ingest keeps a load log and re-imports superseding files rather than mixing vintages.
- **Bed-data granularity.** A&E data is monthly; bed occupancy is quarterly. The linkage is therefore quarter-level and any association is **ecological — no causal claim is made or implied.**
- **Winter framing.** Seasonal analysis is framed as winter pressure (Dec–Feb vs rest of year), the operational language the system actually uses, rather than a generic seasonal decomposition.
- **What this data cannot see.** Case-mix severity, workforce gaps and social-care discharge constraints are not in these files; the persistence flags identify organisations *warranting investigation*, not organisations failing.

## Technical evidence

Python (pandas, CSV ingestion across format changes) · SQLite · SQL window functions · organisational reference-data management · metric governance across definition changes · Power BI / Tableau · analytical writing

## Repository structure

```
src/            Python ingest pipeline + organisation mapping
sql/            Analysis queries
dashboard/      Dashboard file + screenshots
docs/           Metric definitions, org code changes, methodology
data/           Source CSVs and SQLite db (gitignored; sample extract included)
```

## Running it yourself

```bash
pip install -r requirements.txt
python src/ingest.py --source data/raw/     # load downloaded NHS England CSVs
python src/build_analysis.py                # run analysis, export dashboard CSVs
```

Source data: NHS England A&E Attendances and Emergency Admissions (monthly) and Bed Availability and Occupancy (quarterly), downloaded from england.nhs.uk/statistics. Used under the Open Government Licence.

---

*This is an independent analytical project using published official statistics. It is not affiliated with or endorsed by NHS England, and identifies organisations warranting investigation — not organisations to blame.*
