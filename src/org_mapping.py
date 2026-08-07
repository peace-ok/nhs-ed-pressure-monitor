"""
Organisation reference data: handling NHS trust mergers and code changes.

NHS provider organisation (ODS) codes are not stable over a multi-year window.
When trusts merge, the predecessor codes stop reporting and a successor code
begins, silently breaking any naive time series join.

Policy (documented in docs/org_code_changes.md):
    Predecessor series are combined into the successor organisation, and every
    combined row is flagged `is_merged_series = 1` so persistence metrics can
    be run with and without merger-affected organisations.

IMPORTANT — before relying on results:
    Populate MERGER_MAP for your specific analysis window by checking the ODS
    change history (odsdatasearchandexport.nhs.uk) and NHS England publication
    footnotes, then record the verification date in docs/org_code_changes.md.
    The entries below are illustrative placeholders showing the required shape
    and must be replaced with verified mappings for your window.

Format: predecessor_ods_code -> (successor_ods_code, effective_date_iso)
"""

MERGER_MAP = {
    # --- ILLUSTRATIVE PLACEHOLDERS: replace with verified mappings ---
    # "RXX": ("RYY", "2024-04-01"),   # Example Trust A absorbed into Trust B
    # "RZZ": ("RYY", "2024-04-01"),   # Example Trust C absorbed into Trust B
}


def resolve_org(ods_code: str, period_date_iso: str):
    """Map an ODS code to its analysis-time successor.

    Returns (resolved_code, is_merged_series).
    Codes with no mapping pass through unchanged. Mapping applies from the
    effective date onward is irrelevant here — the point is to unify the
    *series*, so predecessors are always folded into the successor.
    """
    if ods_code in MERGER_MAP:
        successor, _effective = MERGER_MAP[ods_code]
        return successor, True
    return ods_code, False


def standardise_provider_name(name: str) -> str:
    """Normalise cosmetic name variation so joins on name never occur anyway.

    Joins in this project are always on resolved ODS code; names are display
    only. This function just tidies whitespace and casing for presentation.
    """
    if name is None:
        return ""
    return " ".join(name.split()).title().replace("Nhs", "NHS")
