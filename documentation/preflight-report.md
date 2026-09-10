---
title: "PRECIS-2 IRR Preflight Audit"
author: "Prepared for Aarian Bhakoo"
date: "9 September 2026"
geometry: margin=1in
fontsize: 11pt
header-includes:
  - \usepackage{booktabs}
  - \usepackage{longtable}
---

# Purpose and status

This report records the reproducibility checks completed before reorganizing
the analysis. All five supplied source files have been copied unchanged into
the project's archive and identified by SHA-256 checksum. No supplied file has
been overwritten.

The authoritative 2x237 rating table was extracted successfully. It contains
237 paired ratings, of which 26 contain at least one special nominal category
(Missing or Not Applicable). Censoring those observations leaves 211 pairs.
The consensus table contains 237 ratings.

Code reorganization is paused because the position-to-trial/domain mapping and
one global agreement result require resolution.

# Confirmed reconciliations

The following calculations from the authoritative 2x237 table agree with the
manuscript or its reported rounding.

| Result | Reconstructed value | Manuscript value | Status |
|---|---:|---:|---|
| Total crude agreement | 115/237 = 48.52% | 48.52% | Matches |
| Censored eligible observations | 211 | 211 | Matches |
| Pairs with Missing or N/A | 26/237 = 10.97% | 26/237 = 10.97% | Matches |
| Aarian mean signed deviation | -0.028436 | -0.028 | Matches rounding |
| Merrick mean signed deviation | 0.047393 | 0.047 | Matches rounding |

The preflight script also calculates censored crude agreement as 110/211 =
52.13% and bucketed crude agreement as 152/237 = 64.14%. These values should be
reconciled against the final manuscript table when that table is restored or
located.

# Issue 1: observation ordering

The supplied explanation described the 2x237 table as trial-major: Domains 1
through 10 for Barcelo, then Domains 1 through 10 for Brown, and so forth. The
workbook values do not support that ordering.

- Trial-major comparison matches only 79 of 237 Aarian values.
- A domain-major reconstruction (all trials for Domain 1, then all trials for
  Domain 2, and so forth) matches 234 of 237 Aarian values and 233 of 237
  Merrick values.

The remaining domain-major discrepancies against `Agreement (Complete)` are:

| Observation under domain-major order | 2x237 A/M | Agreement A/M |
|---|---:|---:|
| Sagahutu (2020), Domain 4 | 2 / 5 | 5 / 2 |
| Strasser (2008), Domain 4 | 5 / 4 | 4 / 5 |
| Thompson (2000A), Domain 4 | 3 / 5 | 4 / 3 |
| Thompson (2000A), Domain 7 | 6 / 6 | 6 / 7 |

In this table, A/M means Aarian/Merrick.

The first three pairs appear consistent with reviewer values having shifted or
been copied into neighboring positions; the Thompson Domain 7 difference is a
category discrepancy. This is an observation from the workbook comparison,
not a determination of which value is correct.

Until the ordering is confirmed, the extracted files retain only observation
positions and ratings. They deliberately do not assign trial or domain labels.

# Issue 2: range crude agreement

Applying the stated range rule directly to the authoritative 2x237 table gives
164 agreements out of 237, or 69.20%. The manuscript reports 70.04%, which is
166/237.

The manual `Agreement (Range)` sheet is internally inconsistent: its displayed
domain numerators sum to 165, but its global cell reports 70.04%. Thus the
reported global percentage, the visible manual counts, and the programmatic
application of the stated rule give three different totals.

The revised R workflow should calculate range agreement directly from the
authoritative ratings after the source discrepancy is resolved. It should not
copy the workbook's global percentage.

# Computational environment

PDF compilation tools are available. R is not installed in the current
workspace, so the statistician-reviewed R implementation and its analytical
confidence intervals have not yet been executed here. Python was used only for
source reconstruction and independent descriptive checks. Krippendorff alpha
confidence intervals must be validated later in an R-enabled environment.

# Next decision required

Before code reorganization, confirm whether the 2x237 table was intended to be
domain-major despite the earlier description. If so, also confirm whether its
values should prevail over the seven discrepant cells in `Agreement
(Complete)`, consistent with the stated rule that the Krippendorff table is the
ultimate authority.

Once confirmed, the project can assign trial and domain identifiers, regenerate
all four transformations from one authoritative dataset, and implement the
clean R workflow without relying on manually transformed tables.
