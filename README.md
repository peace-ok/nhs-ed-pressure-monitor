# NHS Emergency Department Pressure Monitor

Reproducible analysis of Type 1 emergency department performance in England, built from NHS England provider level returns.

---

> **In one paragraph.** England's Type 1 four hour performance peaked at 63.9% in March 2026 and fell in every month since, reaching 61.0% in June. That national decline of 2.9 percentage points conceals a tail: seven trusts lost more than ten points over the same window, the worst losing 16.5. It also conceals the opposite problem. Change the start month from March to January and the list of worst performing trusts almost completely changes, with only one trust appearing on both. This project shows why the choice of window, department type and denominator can determine the answer more than the underlying data does.

---

## Why this exists

The four hour standard is the most quoted measure of emergency care pressure in England, and it is almost always reported as one national percentage. A single percentage cannot distinguish a system under uniform strain from a system where most sites hold steady while a handful deteriorate sharply. Those two situations call for very different responses.

This analysis separates **pressure**, meaning what arrives at the front door, from **performance**, meaning what the organisation does with it. It treats a falling national average as a question rather than a verdict.

I have worked inside hospital data, doing clinical registry abstraction and PostgreSQL analysis at Queensland Health, and my MSc research modelled how interacting system inefficiencies amplify safety risk. This project applies that sociotechnical lens to published NHS operational data.

---

## Key findings

Data window: January to June 2026. Cohort: NHS trusts operating a Type 1 department.

### 1. Performance peaked in March and has fallen every month since

| Month | Type 1 four hour performance | Providers reporting |
|---|---|---|
| January 2026 | 57.0% | 197 |
| February 2026 | 59.1% | 197 |
| March 2026 | **63.9%** (peak) | 199 |
| April 2026 | 63.6% | 190 |
| May 2026 | 61.6% | 192 |
| June 2026 | **61.0%** | 192 |

Every month in the window sits more than thirty points below the 95% constitutional standard, and more than fourteen points below the interim 78% planning objective.

### 2. The national fall of 2.9 points conceals seven trusts that lost more than ten

Decomposing the March to June change to provider level shows the national figure is not describing a uniform decline. Restricted to trusts with more than 3,000 Type 1 attendances in both months:

| Trust | March 2026 | June 2026 | Change |
|---|---|---|---|
| Sherwood Forest Hospitals | 69.9% | 53.4% | **−16.5** |
| Milton Keynes University Hospital | 67.1% | 53.1% | **−14.1** |
| London North West University Healthcare | 66.7% | 54.9% | **−11.8** |
| The Dudley Group | 80.1% | 69.1% | **−11.0** |
| Kingston and Richmond | 56.5% | 45.8% | **−10.7** |
| Airedale | 64.9% | 54.5% | **−10.4** |
| Croydon Health Services | 71.3% | 61.2% | **−10.1** |
| Blackpool Teaching Hospitals | 64.1% | 54.3% | −9.8 |
| Royal Cornwall Hospitals | 51.1% | 41.3% | −9.8 |
| Harrogate and District | 72.5% | 62.8% | −9.6 |
| Dorset County Hospital | 61.2% | 52.1% | −9.1 |
| Epsom and St Helier | 72.0% | 63.1% | −8.9 |
| Royal Devon University Healthcare | 61.3% | 53.0% | −8.3 |
| Buckinghamshire Healthcare | 68.7% | 61.1% | −7.6 |
| North Bristol | 64.5% | 57.3% | −7.2 |
| **England** | **63.9%** | **61.0%** | **−2.9** |

Sherwood Forest's decline is approximately 5.7 times the national movement.

### 3. Changing the start month changes almost the entire answer

This is the most consequential result in the project, and it is a finding about method rather than about hospitals.

Running the identical query from January instead of March produces a near disjoint list:

| Trust | January 2026 | June 2026 | Change |
|---|---|---|---|
| Dorset County Hospital | 59.9% | 52.1% | −7.8 |
| Epsom and St Helier | 69.4% | 63.1% | −6.3 |
| Sherwood Forest Hospitals | 59.5% | 53.4% | −6.2 |
| Bradford Teaching Hospitals | 77.0% | 71.7% | −5.2 |
| Alder Hey Children's | 86.3% | 82.1% | −4.2 |
| Torbay and South Devon | 52.2% | 48.4% | −3.8 |
| Royal Cornwall Hospitals | 45.1% | 41.3% | −3.8 |
| Mid Cheshire Hospitals | 49.9% | 46.2% | −3.7 |
| Salisbury | 53.9% | 50.4% | −3.5 |
| Guy's and St Thomas' | 62.7% | 59.3% | −3.4 |
| Airedale | 57.6% | 54.5% | −3.1 |
| University Hospitals of Morecambe Bay | 57.2% | 54.3% | −2.9 |

**Only Sherwood Forest Hospitals appears in the top seven of both windows.** It is the one trust where the deterioration signal survives a change of start month.

The clearest illustration is London North West University Healthcare. Measured from March it is the third worst decline in England at −11.8 points. Measured from January it is one of the strongest improvements in the country at **+12.5 points**, rising from 42.4% to 54.9%. Both numbers are correct. The trust improved sharply into March and then gave part of it back.

A March baseline systematically selects trusts that had an unusually good March. Any bottom ten built on a single pair of months is measuring regression to the mean at least as much as it is measuring deterioration.

### 4. Trust level variation dwarfs the national trend

In June 2026, Type 1 performance ranged from **35.0%** at University Hospitals Plymouth to **82.1%** at Alder Hey Children's, a spread of 47 percentage points. The lowest performing trusts in the month:

| Trust | June 2026 |
|---|---|
| University Hospitals Plymouth | 35.0% |
| Royal Cornwall Hospitals | 41.3% |
| Nottingham University Hospitals | 43.1% |
| The Shrewsbury and Telford Hospital | 43.8% |
| Kingston and Richmond | 45.8% |
| Mid Cheshire Hospitals | 46.2% |
| Hull University Teaching Hospitals | 46.9% |
| Torbay and South Devon | 48.4% |
| Chesterfield Royal Hospital | 48.4% |
| Wirral University Teaching Hospital | 48.5% |

Case mix is not constant across this range. Alder Hey is a specialist children's hospital and is not comparable to a general acute trust on this measure. Level comparison is reported here for context only. The change based analysis above is the defensible comparison, because each trust acts as its own baseline.

---

## Reconciliation

Any re-analysis of published data is only trustworthy if it reproduces the published figure before it departs from it.

| Metric | Computed here | NHS England published | Variance |
|---|---|---|---|
| Type 1 four hour performance, June 2026 | 61.0% | *pending* | |
| All types four hour performance, June 2026 | *pending* | 75.7% | |
| Total attendances, June 2026 | *pending* | *pending* | |

Reconciliation runs on every data refresh. Any variance above 0.1 percentage points is treated as a defect to be investigated, not a rounding difference to be absorbed.

---

## Data

**Source:** NHS England, Monthly A&E Attendances and Emergency Admissions, provider level returns
**URL:** https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/
**Window:** January 2026 to June 2026
**Downloaded:** *to be recorded*
**Cohort:** 190 to 199 providers per month, varying. See Data quality below.

All data used here is published, aggregated, organisation level official statistics. No patient level or identifiable data is used at any point in this pipeline, and none is required to reproduce it.

---

## Method

1. Download monthly provider level returns from NHS England.
2. Load raw files into SQLite without transformation, preserving published values as an audit baseline.
3. Apply organisation code mapping to hold trust identity stable across mergers.
4. Compute the national Type 1 series as `SUM(type1_within_4h) / SUM(type1_attendances)`, weighted by attendances rather than averaged across trusts.
5. Reconcile the computed series against published national figures.
6. Decompose to provider level using an inner join on organisation code, with an explicit minimum attendance threshold and an explicit baseline month, both stated in every output.

The raw layer is never edited. Every transformation is a separate, re-runnable step, so any number published here traces back to the file it came from.

---

## Data quality notes

**The reporting cohort is not constant.** Provider counts by month are 197, 197, 199, 190, 192, 192. Nine providers present in March are absent in April. Because the national figure is a ratio of summed numerators to summed denominators, a changing cohort moves the national series independently of any change in care delivery.

This bears directly on Finding 1. The March to April step coincides with the largest single month change in cohort size in the window. Cohort composition is therefore reported alongside every national figure, and all provider level analysis uses an inner join so that only trusts present in both comparison months are included.

---

## The three traps this analysis avoids

Most public re-analyses of NHS A&E data fall into at least one of these. Each is handled explicitly here, and each is evidenced in the findings above rather than simply asserted.

### 1. Type 1 versus all types performance

Published headline figures mix major emergency departments (Type 1) with specialty units and urgent treatment centres (Types 2 and 3), which see minor cases and meet the four hour standard almost by default. A trust's headline number therefore depends heavily on how many walk in services it runs, and can improve simply by absorbing a UTC while its actual emergency department deteriorates.

All performance analysis here is reported for Type 1 separately, with the all types figure shown only for reconciliation. See `docs/metric_definitions.md`.

### 2. Organisation codes are not stable

NHS trusts merge, ODS codes change, and time series silently break. A naive join shows a trust vanishing and a new one appearing with no history, corrupting any persistence metric.

`src/org_mapping.py` maintains an explicit merger mapping for the analysis window, with a documented policy: predecessor series are combined into the successor organisation and flagged. See `docs/org_code_changes.md`.

### 3. Baseline choice and small denominators

Two related failures, both demonstrated in Finding 3.

**Baseline choice.** A bottom ten built from a single pair of months preferentially selects trusts that peaked in the baseline month. Changing the baseline from March to January replaces almost the entire list. Every ranked output in this project states its baseline month, and no trust is described as deteriorating unless the signal survives more than one window.

**Small denominators.** Low volume trusts swing further on the same number of breaches. All provider level analysis applies a minimum of 3,000 Type 1 attendances in both comparison months, and attendance volumes are reported alongside every ranked change. See `docs/ranking_caveats.md`.

---

## Limitations

- Six months is a short window. Seasonality is not separated from underlying trend, and March to June spans the transition out of winter pressure. Some of the national decline is expected seasonal behaviour.
- Between May 2019 and June 2023, fourteen trusts participated in Clinical Review of Standards field testing and did not report four hour performance. Comparisons crossing that boundary are not like for like. The current window post-dates it, but the constraint is documented for anyone extending the series backwards.
- Provider level returns are subject to resubmission. Figures are as published at the download date.
- Nothing here is a causal claim. Trust level variation is described, not explained. Establishing why a specific trust moved would require local operational data that is not in this dataset.
- Level comparisons across trusts are confounded by case mix and department configuration. Change based comparisons, where each trust is its own baseline, are the defensible ones.

---

## Roadmap

Planned extensions, not yet reflected in the findings above:

- **Persistence.** Identify trusts below their peer median in ten or more of twelve months, after demand adjustment. Finding 3 suggests this will produce a shorter and far more meaningful list than any single window ranking.
- **Co-located UTC effect.** Quantify the Type 1 versus all types gap by trust, testing whether the headline metric flatters organisational configuration rather than emergency care.
- **Bed occupancy association.** Test whether quarter level occupancy above roughly 92% is associated with steeper four hour deterioration, consistent with the flow constraint literature. Ecological association only.
- **Twelve month window.** Extend backwards to separate seasonality from trend.
- **Cohort reconciliation.** Identify the nine providers absent from the April return and quantify their effect on the national series.

---

## Repository structure

```
data/raw/          Downloaded NHS England files, unmodified
data/processed/    Cleaned outputs and derived series
src/               Pipeline, org mapping, reconciliation
docs/              Metric definitions, org code changes, ranking caveats
outputs/           Charts and exported tables
```

## Running it

```bash
pip install -r requirements.txt
python src/pipeline.py
```

Outputs `national.csv`, `declines.csv` and the reconciliation report.

---

## Licence

MIT. See `LICENSE`.

## Contact

Peace Okoegwale
phokoegwale@gmail.com
