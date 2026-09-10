---
title: "PRECIS-2 IRR Data Finalization Report"
subtitle: "Step 1"
author: "Prepared for Aarian Bhakoo"
date: "10 September 2026"
geometry: margin=1in
fontsize: 11pt
header-includes:
  - \usepackage{booktabs}
  - \usepackage{longtable}
---

# Outcome

The analysis dataset is finalized for code reorganization. All supplied source
files remain unchanged in the project archive. The finalized derived dataset
contains 237 paired ratings with trial and domain identifiers, three documented
corrections, and three documented exclusions. Consensus scores are aligned to
the same 237 observations.

# Authoritative sources

- Independent ratings originate from Table 1 of `Krippendorf Rater Tables`.
- The 2x237 table uses domain-major ordering.
- Consensus ratings originate from `Consensus_Scores` and match the wide
  `Consensus` sheet exactly under domain-major ordering.
- Table 2 of `Krippendorf Rater Tables` matches Table 1 after converting codes
  6 and 7 to missing values.
- Agreement sheets are supporting checks rather than final analytical sources.

# Structure and coding

The dataset covers 24 trials and ten domains. Comparator is Domain 10; Domain
11 labels in historical sheets are copying errors. Scores 1 through 5 form the
ordinal PRECIS-2 scale. Code 6 represents Missing and code 7 represents Not
Applicable. Codes 6 and 7 are separate nominal categories.

Thompson (2000B), Domains 7 through 9, are excluded because separate patient-
and staff-level individual measurements could not be defensibly prioritized or
weighted. This leaves 237 of the possible 240 trial-domain observations.

\newpage

# Verified corrections

Corrections are applied only to derived data. The archived workbook is not
changed.

| Trial and domain | Archived A/M | Final A/M |
|---|---:|---:|
| Sagahutu (2020), Domain 4 | 2 / 5 | 5 / 2 |
| Strasser (2008), Domain 4 | 5 / 4 | 4 / 5 |
| Thompson (2000A), Domain 4 | 3 / 5 | 4 / 3 |

Here, A/M means Aarian/Merrick. Thompson (2000A), Domain 7, is already 5/6 in
the archived 2x237 table and therefore requires no correction. The conflicting
6/7 appears in `Agreement (Complete)`.

# Final descriptive results

| Analysis | Agreements | Denominator | Agreement |
|---|---:|---:|---:|
| Total | 115 | 237 | 48.52% |
| Range | 165 | 237 | 69.62% |
| Censored | 110 | 211 | 52.13% |
| Bucketed | 152 | 237 | 64.14% |

Twenty-six pairs contain at least one Missing or Not Applicable rating. Their
removal leaves 211 observations for censored analyses.

For bucketed agreement, the 152 agreements comprise 6 matches in the 1-2
bucket, 7 matches at score 3, 134 matches in the 4-5 bucket, 5 Missing-Missing
matches, and no Not Applicable-Not Applicable matches.

Mean signed deviation from consensus is -0.014218 for Aarian and 0.028436 for
Merrick across the 211 observations where both independent ratings and the
consensus rating are scores 1 through 5.

# Automated validation

The extraction process now stops with an error unless all of the following are
true:

- The archived Table 1 contains observation identifiers 1 through 237.
- Exactly 24 trials, ten domains, and 237 unique included trial-domain pairs
  are reconstructed.
- All independent and consensus ratings are codes 1 through 7.
- Thompson (2000B), Domains 7 through 9, remain excluded.
- The archived values underlying each verified correction have not changed.
- Thompson (2000A), Domain 7, remains 5/6 in the authoritative table.
- The censored source table is an exact transformation of Table 1.
- The linear and wide consensus tables agree exactly.
- The censored sample contains 211 observations.
- All four accepted crude-agreement numerators and denominators are reproduced.

# Files produced

- `independent_ratings_tidy.csv`
- `consensus_ratings_tidy.csv`
- `exclusions.csv`
- `verified_corrections.csv`
- `data_dictionary.csv`
- Global and domain-level descriptive reconciliation tables
- Reviewer-deviation reconciliation table

# Remaining limitation

This stage finalizes the data and descriptive reconciliation targets. It does
not finalize Krippendorff's alpha estimates or confidence intervals. Those
must be calculated with the reorganized statistician-approved R implementation
and executed in an R-enabled environment during Step 2.
