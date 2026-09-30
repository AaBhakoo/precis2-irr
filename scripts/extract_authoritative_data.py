#!/usr/bin/env python3
"""Extract and validate the authoritative PRECIS-2 IRR analysis datasets.

This script reads the archived re-analysis workbook without modifying it. It
creates tidy independent-rating and consensus datasets, then computes the
descriptive agreement results used as preflight reconciliation targets.
"""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "archive" / "PRECIS-2 Re-Analysis - Spreadsheet (1).xlsx"
REFERENCE_KEY = ROOT / "data" / "included_trials.csv"
DATA_DIR = ROOT / "data" / "derived"
OUTPUT_DIR = ROOT / "outputs" / "preflight"

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

EXCLUSIONS = {("Thompson (2000B)", 7), ("Thompson (2000B)", 8), ("Thompson (2000B)", 9)}

# Corrections independently verified by Aarian Bhakoo on 2026-09-10.
# These are applied only to derived data; the archived workbook remains intact.
VERIFIED_CORRECTIONS = {
    ("Sagahutu (2020)", 4): (5, 2),
    ("Strasser (2008)", 4): (4, 5),
    ("Thompson (2000A)", 4): (4, 3),
}


def observation_map():
    rows = []
    position = 0
    # The 2x237 tables are domain-major: all trials for Domain 1, followed by
    # all trials for Domain 2, and so forth.
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
    assert position == 237
    return rows


def numerical(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value in range(1, 8)


def bucket(value):
    if value in (1, 2):
        return 1
    if value == 3:
        return 2
    if value in (4, 5):
        return 3
    return value


def agrees(a, b, definition):
    if definition == "Total":
        return a == b
    if definition == "Range":
        if a in range(1, 6) and b in range(1, 6):
            return abs(a - b) <= 1
        return a == b
    if definition == "Censored":
        return a == b
    if definition == "Bucketed":
        return bucket(a) == bucket(b)
    raise ValueError(definition)


def distance_factory(definition):
    if definition in ("Total", "Censored"):
        tolerance, maximum = 0, 4
    elif definition == "Range":
        tolerance, maximum = 1, 3
    elif definition == "Bucketed":
        tolerance, maximum = 0, 2
    else:
        raise ValueError(definition)

    def distance(a, b):
        if a == b:
            return 0.0
        if a in (6, 7) or b in (6, 7):
            return 1.0
        x, y = (bucket(a), bucket(b)) if definition == "Bucketed" else (a, b)
        return (max(abs(x - y) - tolerance, 0) / maximum) ** 2

    return distance


def krippendorff_point(rows, definition):
    values = [(r["observer_1"], r["observer_2"]) for r in rows]
    if definition == "Censored":
        values = [(a, b) for a, b in values if a in range(1, 6) and b in range(1, 6)]
    elif definition == "Bucketed":
        values = [(bucket(a), bucket(b)) for a, b in values]
    dist = distance_factory(definition)
    observed = sum(dist(a, b) for a, b in values) / len(values)
    pooled = [x for pair in values for x in pair]
    counts = Counter(pooled)
    total_pairs = len(pooled) * (len(pooled) - 1) / 2
    expected_sum = 0.0
    cats = sorted(counts)
    for i, a in enumerate(cats):
        for b in cats[i + 1:]:
            expected_sum += counts[a] * counts[b] * dist(a, b)
    expected = expected_sum / total_pairs
    return 1 - observed / expected


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    workbook = load_workbook(SOURCE, data_only=True, read_only=False)
    ratings_sheet = workbook["Krippendorf Rater Tables"]
    consensus_sheet = workbook["Consensus_Scores"]
    consensus_wide_sheet = workbook["Consensus"]

    ids = [ratings_sheet.cell(4, col).value for col in range(2, 239)]
    reviewer_1 = [ratings_sheet.cell(5, col).value for col in range(2, 239)]
    reviewer_2 = [ratings_sheet.cell(6, col).value for col in range(2, 239)]
    consensus = [consensus_sheet.cell(2, col).value for col in range(2, 239)]
    assert ids == list(range(1, 238)), "Authoritative table IDs are not 1 through 237"
    assert all(numerical(x) for x in reviewer_1 + reviewer_2 + consensus), "Unexpected rating code"

    assert len(reviewer_1) == len(reviewer_2) == len(consensus) == 237

    with REFERENCE_KEY.open(newline="", encoding="utf-8") as handle:
        reference_rows = list(csv.DictReader(handle))
    assert len(reference_rows) == 24, "Reference key must contain 24 trial reports"
    assert [row["trial"] for row in reference_rows] == TRIALS, "Reference key is not aligned to trial order"
    assert [int(row["trial_order"]) for row in reference_rows] == list(range(1, 25))

    included_map = [row for row in observation_map() if row["included"]]
    assert len(included_map) == 237
    assert len({(row["trial"], row["domain_number"]) for row in included_map}) == 237
    assert len({row["trial"] for row in included_map}) == 24
    assert {row["domain_number"] for row in included_map} == set(range(1, 11))

    expected_source_corrections = {
        ("Sagahutu (2020)", 4): (2, 5),
        ("Strasser (2008)", 4): (5, 4),
        ("Thompson (2000A)", 4): (3, 5),
    }
    source_by_key = {
        (meta["trial"], meta["domain_number"]): (int(a), int(b))
        for meta, a, b in zip(included_map, reviewer_1, reviewer_2)
    }
    for key, expected in expected_source_corrections.items():
        assert source_by_key[key] == expected, f"Archived source changed at {key}"
    assert source_by_key[("Thompson (2000A)", 7)] == (5, 6)

    # Table 2 must equal Table 1 after converting codes 6 and 7 to missing.
    censored_a = [ratings_sheet.cell(10, col).value for col in range(2, 239)]
    censored_b = [ratings_sheet.cell(11, col).value for col in range(2, 239)]
    def normalize_censored(value):
        return None if value in ("NA", None) else int(value)
    for raw, censored in zip(reviewer_1 + reviewer_2, censored_a + censored_b):
        expected = None if raw in (6, 7) else int(raw)
        assert normalize_censored(censored) == expected, "Table 2 is not the expected censored transformation"

    # The linear consensus row must exactly match the domain-major wide sheet.
    consensus_from_wide = []
    for domain_number, column in enumerate(range(3, 13), start=1):
        for row in range(2, 26):
            if row == 24 and domain_number in (7, 8, 9):
                continue
            consensus_from_wide.append(consensus_wide_sheet.cell(row, column).value)
    assert consensus_from_wide == consensus, "Consensus tables are not aligned"
    correction_rows = []
    tidy = []
    consensus_tidy = []
    final_tidy = []
    for meta, source_a, source_b, c in zip(included_map, reviewer_1, reviewer_2, consensus):
        verified = VERIFIED_CORRECTIONS.get((meta["trial"], meta["domain_number"]))
        final_a, final_b = verified if verified else (int(source_a), int(source_b))
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
        tidy.append({
            "observation_id": meta["observation_id"],
            "trial_order": meta["trial_order"],
            "trial": meta["trial"],
            "domain_number": meta["domain_number"],
            "domain": meta["domain"],
            "observer_1": final_a,
            "observer_2": final_b,
        })
        consensus_tidy.append({
            "observation_id": meta["observation_id"],
            "trial": meta["trial"],
            "domain_number": meta["domain_number"],
            "domain": meta["domain"],
            "consensus": int(c),
        })
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

    exclusions = [{k: v for k, v in row.items() if k != "included"} for row in observation_map() if not row["included"]]
    write_csv(DATA_DIR / "independent_ratings_tidy.csv", list(tidy[0]), tidy)
    write_csv(DATA_DIR / "consensus_ratings_tidy.csv", list(consensus_tidy[0]), consensus_tidy)
    write_csv(DATA_DIR / "precis2_irr_final.csv", list(final_tidy[0]), final_tidy)
    write_csv(DATA_DIR / "exclusions.csv", list(exclusions[0]), exclusions)
    write_csv(DATA_DIR / "verified_corrections.csv", list(correction_rows[0]), correction_rows)

    definitions = ["Total", "Range", "Censored", "Bucketed"]
    global_rows = []
    for definition in definitions:
        eligible = tidy if definition != "Censored" else [r for r in tidy if r["observer_1"] in range(1, 6) and r["observer_2"] in range(1, 6)]
        count = sum(agrees(r["observer_1"], r["observer_2"], definition) for r in eligible)
        global_rows.append({
            "definition": definition,
            "agreements": count,
            "observations": len(eligible),
            "crude_agreement_percent": round(100 * count / len(eligible), 6),
            "independently_calculated_alpha_point_estimate": round(krippendorff_point(tidy, definition), 6),
        })
    write_csv(OUTPUT_DIR / "global_results_preflight.csv", list(global_rows[0]), global_rows)

    domain_rows = []
    for number, name in DOMAINS.items():
        subset = [r for r in tidy if r["domain_number"] == number]
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
    write_csv(OUTPUT_DIR / "domain_results_preflight.csv", list(domain_rows[0]), domain_rows)

    joined = [{**r, "consensus": c["consensus"]} for r, c in zip(tidy, consensus_tidy)]
    msd_rows = []
    eligible = [r for r in joined if r["observer_1"] in range(1, 6) and r["observer_2"] in range(1, 6) and r["consensus"] in range(1, 6)]
    for reviewer, field in [("Aarian", "observer_1"), ("Merrick", "observer_2")]:
        deviations = [r[field] - r["consensus"] for r in eligible]
        msd_rows.append({
            "reviewer": reviewer,
            "observations": len(deviations),
            "mean_signed_deviation": round(sum(deviations) / len(deviations), 6),
            "mean_absolute_deviation": round(sum(abs(x) for x in deviations) / len(deviations), 6),
        })
    write_csv(OUTPUT_DIR / "reviewer_deviation_preflight.csv", list(msd_rows[0]), msd_rows)

    special = sum(r["observer_1"] in (6, 7) or r["observer_2"] in (6, 7) for r in tidy)
    assert special == 26
    assert len([r for r in tidy if r["observer_1"] in range(1, 6) and r["observer_2"] in range(1, 6)]) == 211
    assert len(final_tidy) == 237
    assert [r["observation_id"] for r in final_tidy] == list(range(1, 238))
    assert len({(r["trial"], r["domain_number"]) for r in final_tidy}) == 237
    assert all(r["aarian_score"] in range(1, 8) and
               r["merrick_score"] in range(1, 8) and
               r["consensus_score"] in range(1, 8)
               for r in final_tidy)

    expected_crude = {
        "Total": (115, 237),
        "Range": (165, 237),
        "Censored": (110, 211),
        "Bucketed": (152, 237),
    }
    for row in global_rows:
        assert (row["agreements"], row["observations"]) == expected_crude[row["definition"]]

    print("Validated 237 paired observations, 211 censored observations, and 26 pairs containing a special nominal category.")
    print(f"Applied {len(correction_rows)} independently verified correction pairs to derived data.")
    print("Global results:")
    for row in global_rows:
        print(row)
    print("Reviewer deviation:")
    for row in msd_rows:
        print(row)


if __name__ == "__main__":
    main()
