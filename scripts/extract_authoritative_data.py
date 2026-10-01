#!/usr/bin/env python3
"""Construct and validate the finalized PRECIS-2 IRR datasets.

Purpose
-------
This script extracts the authoritative 2-by-237 reviewer-rating tables and
consensus scores from the archived re-analysis workbook. It converts them into
tidy CSV datasets, applies independently verified corrections, and generates
preflight results used to validate the primary R analysis.

The archived workbook is read without modification. Corrections are applied
only to derived files, preserving the original source for audit purposes.

Run from the repository root with:

    python scripts/extract_authoritative_data.py

Primary outputs
---------------
data/derived/
    independent_ratings_tidy.csv
    consensus_ratings_tidy.csv
    precis2_irr_final.csv
    exclusions.csv
    verified_corrections.csv

outputs/preflight/
    global_results_preflight.csv
    domain_results_preflight.csv
    reviewer_deviation_preflight.csv

The script stops if the workbook structure, rating codes, observation order,
prespecified exclusions, or independently verified results differ from their
expected values.
"""

# Package Imports
from __future__ import annotations
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from openpyxl import load_workbook

# Resolve all input and output paths relative to the repository root
# SOURCE is an archived workbook that is NOT modified by this script
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "archive" / "PRECIS-2 Re-Analysis - Spreadsheet (1).xlsx"
REFERENCE_KEY = ROOT / "data" / "included_trials.csv"
DATA_DIR = ROOT / "data" / "derived"
OUTPUT_DIR = ROOT / "outputs" / "preflight"

# final trial order used in the authoritative rating tables
TRIALS = [
    "Barcelo (2010)", "Brown (1999)", "Campbell (2001)",
    "Clay-Williams (2013)", "Fransen (2013)", "Frengley (2011)",
    "Fritz (2017)", "Fukui (2019)", "Helitzer (2011)",
    "Koerner (2014)", "Languerrand (2020)", "Nielsen (2007)",
    "Pasay (2019)", "Pieper (2016)", "Riley (2011)", "Robling (2012)",
    "Romjin (2019)", "Sagahutu (2020)", "Sorensen (2015)",
    "Strasser (2008)", "Strauven (2019)", "Thompson (2000A)",
    "Thompson (2000B)", "Zattoni (2017)",
]

# final set of ten trial design domains for the Modified PRECIS-2 framework
DOMAINS = {
    1: "Eligibility",
    2: "Recruitment",
    3: "Setting",
    4: "Organization",
    5: "Flexibility in Delivery",
    6: "Flexibility in Adherence",
    7: "Follow-up",
    8: "Primary Outcome",
    9: "Primary Analysis",
    10: "Comparator",
}

# Pre-specified exclusions: Thompson (2000B) Domains 7-9
# Individual-level measurements without a defensible prioritization or weighing
EXCLUSIONS = {("Thompson (2000B)", 7), ("Thompson (2000B)", 8), ("Thompson (2000B)", 9)}

# Corrections independently verified by Aarian Bhakoo on 2026-09-10 against original scoring records
# These are applied only to derived data; the archived workbook remains intact
VERIFIED_CORRECTIONS = {
    ("Sagahutu (2020)", 4): (5, 2),
    ("Strasser (2008)", 4): (4, 5),
    ("Thompson (2000A)", 4): (4, 3),
}

# Map every trial-domain combination to an observation ID
def observation_map():
    rows = []
    position = 0
    '''The 2x237 tables are domain-major: all trials for Domain 1, followed by
    all trials for Domain 2, and so forth.'''
    for domain_number, domain_name in DOMAINS.items():
        for trial_order, trial in enumerate(TRIALS, start=1):
            included = (trial, domain_number) not in EXCLUSIONS
            if included:
                position += 1
            rows.append({
                "trial_order": trial_order,
                "trial": trial,
                "domain_number": domain_number,
                "domain": domain_name,
                "included": included,
                "observation_id": position if included else None,
                "exclusion_reason": "Multiple individual-level measurements with no defensible prioritization or weighting" if not included else "",
            })
    # (24 trials x 10 domains) - 3 exclusions = 237 observations       
    assert position == 237
    return rows

# Return True only for permitted integer-equivalent rating codes 1-7
def numerical(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value in range(1, 8)

# Collapse scores 1-5 into highly explanatory, mixed, and highly pragmatic buckets
def bucket(value):
    if value in (1, 2):
        return 1
    if value == 3:
        return 2
    if value in (4, 5):
        return 3
    return value

# Evaluate crude agreement under the requested agreement definition (Total, Range, Censored, Buckets)
def agrees(a, b, definition):
    if definition == "Total":
        return a == b
    
    # One-point differences count as agreement only for ordinal scores 1-5
    if definition == "Range":
        if a in range(1, 6) and b in range(1, 6):
            return abs(a - b) <= 1
        return a == b
    
    if definition == "Censored":
        return a == b
    
    # Scores agree when both map to the same predefined category
    if definition == "Bucketed":
        return bucket(a) == bucket(b)
    raise ValueError(definition)


# Construct a disagreement function for chance-corrected agreement
# Disagreement is weighed using squared standardized distance
# This minimizes the impact of minor disagreements while maximizing large discrepancies
def distance_factory(definition):
    # Setting the permitted tolerance (ordinal step where max agreement is allowed)
    # Setting the maximum effective ordinal distance
    if definition in ("Total", "Censored"):
        tolerance, maximum = 0, 4
    elif definition == "Range":
        tolerance, maximum = 1, 3
    elif definition == "Bucketed":
        tolerance, maximum = 0, 2
    else:
        raise ValueError(definition)

    # Exact matches have zero disagreement
    def distance(a, b):
        if a == b:
            return 0.0
        # Every nonidentical comparison involving nominal categories receives max disagreement
        if a in (6, 7) or b in (6, 7):
            return 1.0
        x, y = (bucket(a), bucket(b)) if definition == "Bucketed" else (a, b)
        return (max(abs(x - y) - tolerance, 0) / maximum) ** 2
    # Apply any agreement tolerance, standardize to 0-1 scale, and square
    return distance

# Calculate an independent point estimate of Krippendorff's alpha
def krippendorff_point(rows, definition):
    # Assemble paired reviewer scores and recode according to definition
    values = [(r["observer_1"], r["observer_2"]) for r in rows]
    if definition == "Censored":
        values = [(a, b) for a, b in values if a in range(1, 6) and b in range(1, 6)]
    elif definition == "Bucketed":
        values = [(bucket(a), bucket(b)) for a, b in values]
    dist = distance_factory(definition)

    # Calculate observed disagreement across the paired ratings
    observed = sum(dist(a, b) for a, b in values) / len(values)
    # Pool ratings to calculate disagreement expected by chance
    pooled = [x for pair in values for x in pair]
    counts = Counter(pooled)
    total_pairs = len(pooled) * (len(pooled) - 1) / 2
    expected_sum = 0.0
    cats = sorted(counts)
    # Sum expected disagreement across every distinct category pair
    for i, a in enumerate(cats):
        for b in cats[i + 1:]:
            expected_sum += counts[a] * counts[b] * dist(a, b)
    expected = expected_sum / total_pairs
    # Krippendorff's alpha equals one minus observed over expected disagreement
    return 1 - observed / expected

# Write a collection of dictionaries to a UTF-8 CSV file
def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# Execute source validation, data extraction, correction, and export
def main():
    # Confirm that the archived source workbook is available
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    # Load calculated cell values without modifying the original workbook
    workbook = load_workbook(SOURCE, data_only=True, read_only=False)
    # Select the authoritative linear rating tables and wide consensus table
    ratings_sheet = workbook["Krippendorf Rater Tables"]
    consensus_sheet = workbook["Consensus_Scores"]
    consensus_wide_sheet = workbook["Consensus"]

    # Extract the 237 observation IDs, paired reviewer scores, and consensus
    # Scores from the authoritative domain-major tables
    ids = [ratings_sheet.cell(4, col).value for col in range(2, 239)]
    reviewer_1 = [ratings_sheet.cell(5, col).value for col in range(2, 239)]
    reviewer_2 = [ratings_sheet.cell(6, col).value for col in range(2, 239)]
    consensus = [consensus_sheet.cell(2, col).value for col in range(2, 239)]

    # Validate
    assert ids == list(range(1, 238)), "Authoritative table IDs are not 1 through 237"
    assert all(numerical(x) for x in reviewer_1 + reviewer_2 + consensus), "Unexpected rating code"
    assert len(reviewer_1) == len(reviewer_2) == len(consensus) == 237

    # Confirm that the included-trial reference contains all 24 trials in the correct order
    with REFERENCE_KEY.open(newline="", encoding="utf-8") as handle:
        reference_rows = list(csv.DictReader(handle))
    assert len(reference_rows) == 24, "Reference key must contain 24 trial reports"
    assert [row["trial"] for row in reference_rows] == TRIALS, "Reference key is not aligned to trial order"
    assert [int(row["trial_order"]) for row in reference_rows] == list(range(1, 25))

    # Construct the domain-major observation map and verify after three exclusions
    included_map = [row for row in observation_map() if row["included"]]
    assert len(included_map) == 237
    assert len({(row["trial"], row["domain_number"]) for row in included_map}) == 237
    assert len({row["trial"] for row in included_map}) == 24
    assert {row["domain_number"] for row in included_map} == set(range(1, 11))

    # Verify that the archived workbook still contains the original values at every correction site
    # This prevents silent modification of the source data
    expected_source_corrections = {
        ("Sagahutu (2020)", 4): (2, 5),
        ("Strasser (2008)", 4): (5, 4),
        ("Thompson (2000A)", 4): (3, 5),
    }
    source_by_key = {
        (meta["trial"], meta["domain_number"]): (int(a), int(b))
        for meta, a, b in zip(included_map, reviewer_1, reviewer_2)
    }
    # Stop if any original source value differs from its documented value
    for key, expected in expected_source_corrections.items():
        assert source_by_key[key] == expected, f"Archived source changed at {key}"
    # Thompson (2000A) Domain #7 was independently checked and requires no correction
    assert source_by_key[("Thompson (2000A)", 7)] == (5, 6)

    # Validate the workbook's censored table against the complete table
    # Table 2 must reproduce Table 1 after converting codes 6 and 7 to missing.
    censored_a = [ratings_sheet.cell(10, col).value for col in range(2, 239)]
    censored_b = [ratings_sheet.cell(11, col).value for col in range(2, 239)]
    # Convert workbook missing-value representations to Python None
    def normalize_censored(value):
        return None if value in ("NA", None) else int(value)
    # Compare every censored value with its expected transformation
    for raw, censored in zip(reviewer_1 + reviewer_2, censored_a + censored_b):
        expected = None if raw in (6, 7) else int(raw)
        assert normalize_censored(censored) == expected, "Table 2 is not the expected censored transformation"

    # Reconstruct the linear consensus sequence from the wide worksheet
    # Confirm exact alignment with the 1x237 row table
    consensus_from_wide = []
    for domain_number, column in enumerate(range(3, 13), start=1):
        for row in range(2, 26):
            # Skip three excluded observations from Thompson (2000B)
            if row == 24 and domain_number in (7, 8, 9):
                continue
            consensus_from_wide.append(consensus_wide_sheet.cell(row, column).value)
    assert consensus_from_wide == consensus, "Consensus tables are not aligned"

    # Initialize the correction log and the three derived analysis datasets
    correction_rows = []
    tidy = []
    consensus_tidy = []
    final_tidy = []

# Align source ratings and consensus scores with their trial-domain metadata,
    # then apply verified corrections to derived ratings only
    for meta, source_a, source_b, c in zip(included_map, reviewer_1, reviewer_2, consensus):
        # Use the verified pair when a correction exists
        # Otherwise preserve the source reviewer scores
        verified = VERIFIED_CORRECTIONS.get((meta["trial"], meta["domain_number"]))
        final_a, final_b = verified if verified else (int(source_a), int(source_b))
        # Record the original and corrected values in an auditable change log
        if verified:
            correction_rows.append({
                "observation_id": meta["observation_id"],
                "trial": meta["trial"],
                "domain_number": meta["domain_number"],
                "domain": meta["domain"],
                "source_observer_1": int(source_a),
                "source_observer_2": int(source_b),
                "corrected_observer_1": final_a,
                "corrected_observer_2": final_b,
                "verification_basis": "Independent verification by Aarian Bhakoo on 2026-09-10",
            })
        # Store the finalized independent reviewer ratings
        tidy.append({
            "observation_id": meta["observation_id"],
            "trial_order": meta["trial_order"],
            "trial": meta["trial"],
            "domain_number": meta["domain_number"],
            "domain": meta["domain"],
            "observer_1": final_a,
            "observer_2": final_b,
        })
        # Store the corresponding consensus rating
        consensus_tidy.append({
            "observation_id": meta["observation_id"],
            "trial": meta["trial"],
            "domain_number": meta["domain_number"],
            "domain": meta["domain"],
            "consensus": int(c),
        })
        # Combine independent and consensus scores into the canonical dataset
        final_tidy.append({
            "observation_id": meta["observation_id"],
            "trial_order": meta["trial_order"],
            "trial": meta["trial"],
            "domain_number": meta["domain_number"],
            "domain": meta["domain"],
            "aarian_score": final_a,
            "merrick_score": final_b,
            "consensus_score": int(c),
        })
    # Export the prespecified exclusions seperately from included data
    exclusions = [{k: v for k, v in row.items() if k != "included"} for row in observation_map() if not row["included"]]

    # Write the finalized derived datasets and correction records
    write_csv(DATA_DIR / "independent_ratings_tidy.csv", list(tidy[0]), tidy)
    write_csv(DATA_DIR / "consensus_ratings_tidy.csv", list(consensus_tidy[0]), consensus_tidy)
    write_csv(DATA_DIR / "precis2_irr_final.csv", list(final_tidy[0]), final_tidy)
    write_csv(DATA_DIR / "exclusions.csv", list(exclusions[0]), exclusions)
    write_csv(DATA_DIR / "verified_corrections.csv", list(correction_rows[0]), correction_rows)

    # Reproduce the four agreement definitions independently
    # Used for preflight validation of the main R analysis
    definitions = ["Total", "Range", "Censored", "Bucketed"]

    # Calculate global crude agreement and an independent Krippendorff's alpha
    # point estimate under each definition
    global_rows = []
    for definition in definitions:
        eligible = tidy if definition != "Censored" else [r for r in tidy if r["observer_1"] in range(1, 6) and r["observer_2"] in range(1, 6)]
        count = sum(agrees(r["observer_1"], r["observer_2"], definition) for r in eligible)

        # Store the agreement count, denominator, percentage, and independently calculated alpha estimate
        global_rows.append({
            "definition": definition,
            "agreements": count,
            "observations": len(eligible),
            "crude_agreement_percent": round(100 * count / len(eligible), 6),
            "independently_calculated_alpha_point_estimate": round(krippendorff_point(tidy, definition), 6),
        })
    # Write the global targets used by the R analysis regression checks
    write_csv(OUTPUT_DIR / "global_results_preflight.csv", list(global_rows[0]), global_rows)

    # Repeat the crude-agreement calculations seperately for each PRECIS-2 domain and agreement definition
    domain_rows = []
    for number, name in DOMAINS.items():
        # Select all included observations belonging to the current domain
        subset = [r for r in tidy if r["domain_number"] == number]
        # Apply pairwise censoring only under the Censored definition
        for definition in definitions:
            eligible = subset if definition != "Censored" else [r for r in subset if r["observer_1"] in range(1, 6) and r["observer_2"] in range(1, 6)]
            count = sum(agrees(r["observer_1"], r["observer_2"], definition) for r in eligible)
            domain_rows.append({
                "domain_number": number,
                "domain": name,
                "definition": definition,
                "agreements": count,
                "observations": len(eligible),
                "crude_agreement_percent": round(100 * count / len(eligible), 6),
            })
    # Write the 10 domain x 4 definition preflight table (40 rows)
    write_csv(OUTPUT_DIR / "domain_results_preflight.csv", list(domain_rows[0]), domain_rows)

    # Align the independent ratings with consensus scores using the validated observation order
    # Retain a common set of observations for which both reviewers and consensus score from 1 to 5
    joined = [{**r, "consensus": c["consensus"]} for r, c in zip(tidy, consensus_tidy)]
    msd_rows = []
    eligible = [r for r in joined if r["observer_1"] in range(1, 6) and r["observer_2"] in range(1, 6) and r["consensus"] in range(1, 6)]
    for reviewer, field in [("Aarian", "observer_1"), ("Merrick", "observer_2")]:
        deviations = [r[field] - r["consensus"] for r in eligible]
        # Calculate each reviewer's signed and absolute deviation from consensus
        # Signed deviation is defined as (reviewer score - consensus score)
        msd_rows.append({
            "reviewer": reviewer,
            "observations": len(deviations),
            "mean_signed_deviation": round(sum(deviations) / len(deviations), 6),
            "mean_absolute_deviation": round(sum(abs(x) for x in deviations) / len(deviations), 6),
        })
    # Write the reviewer-level deviation summary used by the R regression check
    write_csv(OUTPUT_DIR / "reviewer_deviation_preflight.csv", list(msd_rows[0]), msd_rows)

    special = sum(r["observer_1"] in (6, 7) or r["observer_2"] in (6, 7) for r in tidy)

    # Perform final strutural and content checks before declaring the extraction successful
    # Confirm the expected observation structure and censoring counts
    assert special == 26
    assert len([r for r in tidy if r["observer_1"] in range(1, 6) and r["observer_2"] in range(1, 6)]) == 211
    assert len(final_tidy) == 237
    assert [r["observation_id"] for r in final_tidy] == list(range(1, 238))
    assert len({(r["trial"], r["domain_number"]) for r in final_tidy}) == 237
    # Confirm that all reviewer and consensus scores use permitted codes
    assert all(r["aarian_score"] in range(1, 8) and
               r["merrick_score"] in range(1, 8) and
               r["consensus_score"] in range(1, 8)
               for r in final_tidy)

    # Regression test the global crude-agreement results against the independently verified Step 1 values
    # Stop execution if any accepted numerator or denominator has changed
    expected_crude = {
        "Total": (115, 237),
        "Range": (165, 237),
        "Censored": (110, 211),
        "Bucketed": (152, 237),
    }
    for row in global_rows:
        assert (row["agreements"], row["observations"]) == expected_crude[row["definition"]]

    # Print a concise execution summary only after every validation has passed
    print("Validated 237 paired observations, 211 censored observations, and 26 pairs containing a special nominal category.")
    print(f"Applied {len(correction_rows)} independently verified correction pairs to derived data.")
    print("Global results:")
    for row in global_rows:
        print(row)
    print("Reviewer deviation:")
    for row in msd_rows:
        print(row)

# Run the extraction workflow only when this file is executed directly
if __name__ == "__main__":
    main()
    
