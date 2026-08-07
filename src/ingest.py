"""
NHS England A&E data ingest.

Loads monthly A&E Attendances & Emergency Admissions CSVs (downloaded from
england.nhs.uk/statistics) into SQLite, standardising column names across
publication-format changes, applying organisation merger mapping, and logging
every load so revisions replace rather than duplicate.

Usage:
    python src/ingest.py --source data/raw/
"""

import argparse
import glob
import logging
import os
import re
import sqlite3

import pandas as pd

from org_mapping import resolve_org, standardise_provider_name

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "nhs_ed.db")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ingest")

SCHEMA = """
CREATE TABLE IF NOT EXISTS ae_monthly (
    period TEXT NOT NULL,                 -- YYYY-MM
    ods_code TEXT NOT NULL,
    provider_name TEXT,
    is_merged_series INTEGER NOT NULL,
    type1_attendances INTEGER,
    type2_attendances INTEGER,
    type3_attendances INTEGER,
    total_attendances INTEGER,
    type1_within_4h INTEGER,
    total_within_4h INTEGER,
    emergency_admissions INTEGER,
    waits_over_12h INTEGER,               -- see docs/metric_definitions.md:
    twelve_hour_basis TEXT,               -- 'from_dta' or 'from_arrival'
    source_file TEXT NOT NULL,
    PRIMARY KEY (period, ods_code)
);

CREATE TABLE IF NOT EXISTS load_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT NOT NULL,
    period TEXT,
    rows_loaded INTEGER,
    replaced_existing INTEGER
);
"""

# Column name variants seen across NHS England publication formats.
# Extend this map as you encounter files; unknown columns are reported, not dropped.
COLUMN_ALIASES = {
    "org code": "ods_code",
    "organisation code": "ods_code",
    "code": "ods_code",
    "org name": "provider_name",
    "organisation name": "provider_name",
    "name": "provider_name",
    "a&e attendances type 1": "type1_attendances",
    "type 1 departments - major a&e": "type1_attendances",
    "a&e attendances type 2": "type2_attendances",
    "a&e attendances other a&e department": "type3_attendances",
    "total attendances": "total_attendances",
    "attendances over 4hrs type 1": "_t1_over4h",   # converted to within-4h below
    "total emergency admissions": "emergency_admissions",
    "emergency admissions via a&e - type 1": "emergency_admissions",
    "patients who have waited 12+ hrs from dta to admission": "waits_over_12h",
}


def normalise_columns(df: pd.DataFrame):
    df.columns = [re.sub(r"\s+", " ", c).strip().lower() for c in df.columns]
    unknown = [c for c in df.columns if c not in COLUMN_ALIASES and c not in
               ("period", "parent org")]
    if unknown:
        log.warning("Unmapped columns (kept but unused): %s", unknown)
    return df.rename(columns=COLUMN_ALIASES)


def infer_period_from_filename(path: str):
    """NHS files typically embed Month-Year in the filename."""
    m = re.search(r"(January|February|March|April|May|June|July|August|"
                  r"September|October|November|December)[-_ ]?(\d{4})", path, re.I)
    if not m:
        return None
    month = pd.to_datetime(m.group(1), format="%B").month
    return f"{m.group(2)}-{month:02d}"


def load_file(conn: sqlite3.Connection, path: str) -> None:
    period = infer_period_from_filename(path)
    if period is None:
        log.error("Cannot infer period from filename, skipping: %s", path)
        return

    df = pd.read_csv(path, skip_blank_lines=True)
    df = normalise_columns(df)

    if "ods_code" not in df.columns:
        log.error("No organisation code column found, skipping: %s", path)
        return

    # Revisions: delete any existing rows for this period before loading,
    # so re-downloaded revised files replace rather than mix vintages.
    existing = conn.execute(
        "SELECT COUNT(*) FROM ae_monthly WHERE period = ?", (period,)
    ).fetchone()[0]
    conn.execute("DELETE FROM ae_monthly WHERE period = ?", (period,))

    rows = 0
    for _, r in df.iterrows():
        code = str(r.get("ods_code", "")).strip()
        if not code or code.lower() in ("total", "england"):
            continue  # exclude national summary rows from provider table
        resolved, merged = resolve_org(code, f"{period}-01")
        t1_att = pd.to_numeric(r.get("type1_attendances"), errors="coerce")
        t1_over = pd.to_numeric(r.get("_t1_over4h"), errors="coerce")
        t1_within = (t1_att - t1_over) if pd.notna(t1_att) and pd.notna(t1_over) else None
        conn.execute(
            "INSERT INTO ae_monthly (period, ods_code, provider_name, is_merged_series, "
            "type1_attendances, type2_attendances, type3_attendances, total_attendances, "
            "type1_within_4h, total_within_4h, emergency_admissions, waits_over_12h, "
            "twelve_hour_basis, source_file) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(period, ods_code) DO UPDATE SET "
            "type1_attendances = type1_attendances + excluded.type1_attendances",
            (
                period, resolved,
                standardise_provider_name(r.get("provider_name")),
                int(merged),
                None if pd.isna(t1_att) else int(t1_att),
                _num(r, "type2_attendances"), _num(r, "type3_attendances"),
                _num(r, "total_attendances"),
                None if t1_within is None or pd.isna(t1_within) else int(t1_within),
                _num(r, "total_within_4h"),
                _num(r, "emergency_admissions"),
                _num(r, "waits_over_12h"),
                "from_dta",  # set per-file: see docs/metric_definitions.md
                os.path.basename(path),
            ),
        )
        rows += 1

    conn.execute(
        "INSERT INTO load_log (source_file, period, rows_loaded, replaced_existing) "
        "VALUES (?, ?, ?, ?)",
        (os.path.basename(path), period, rows, int(existing > 0)),
    )
    conn.commit()
    log.info("Loaded %s: %d provider rows for %s%s", os.path.basename(path),
             rows, period, " (replaced revision)" if existing else "")


def _num(row, col):
    v = pd.to_numeric(row.get(col), errors="coerce")
    return None if pd.isna(v) else int(v)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="data/raw/", help="folder of NHS CSVs")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    files = sorted(glob.glob(os.path.join(args.source, "*.csv")))
    if not files:
        log.error("No CSV files found in %s — download monthly A&E files from "
                  "england.nhs.uk/statistics first.", args.source)
        return
    for path in files:
        load_file(conn, path)


if __name__ == "__main__":
    main()
