# PRECIS-2 inter-rater reliability

Reproducibility materials for a study evaluating agreement between two
reviewers applying PRECIS-2 to 24 randomized controlled trials. The repository
contains the finalized ratings, prespecified analysis definitions, executable
R code, machine-readable results, and a rendered report.

## Repository status

This repository is private pending co-author review. Public release and
archiving in a repository that issues a persistent identifier should occur
only after final approval.

## Study dataset

- 24 randomized controlled trials
- 10 PRECIS-2 domains, with Comparator represented as Domain 10
- 2 independent reviewers: Aarian Bhakoo and Merrick Zwarenstein
- 237 paired trial-domain ratings
- 211 observations after censoring Missing and Not Applicable ratings

Scores 1-5 form the ordinal pragmatism scale. Code 6 represents Missing and
code 7 represents Not Applicable; codes 6 and 7 are distinct nominal
categories rather than extensions of the ordinal scale.

## Analyses

Crude agreement and Krippendorff's alpha are calculated under four prespecified
definitions: Total, Range, Censored, and Bucketed. Secondary analyses report
crude agreement by domain and each reviewer's mean signed deviation from
consensus. Full definitions are provided in
`documentation/analysis-specification.md` and in the analysis report.

## Reproduce the analysis

Open `precis2-irr.Rproj` in RStudio and, from the repository root, run:

```r
source("run-analysis.R")
```

The script checks required packages, validates the canonical dataset against
accepted totals, renders the PDF report, and writes the result tables. The
software versions used for the committed report are recorded in
`outputs/results/session-info.txt`.

## Repository map

| Location | Contents |
|---|---|
| `analysis/precis2-irr-analysis.Rmd` | Complete reproducible analysis |
| `data/precis2_irr_final.csv` | Canonical ratings and consensus dataset |
| `data/included_trials.csv` | Reference list for the 24 included trial reports |
| `data/exclusions.csv` | Excluded trial-domain observations and reasons |
| `data/data_dictionary.csv` | Variable definitions and permitted values |
| `documentation/analysis-specification.md` | Prespecified analysis rules |
| `outputs/results/` | Machine-readable analysis results and session information |
| `outputs/reports/` | Rendered PDF analysis report |

## Provenance

The finalized dataset uses domain-major ordering. Thompson (2000B) Domains
7-9 are excluded. Three corrections independently verified against the
original records are incorporated in the canonical dataset: Sagahutu Domain 4
(5/2), Strasser Domain 4 (4/5), and Thompson (2000A) Domain 4 (4/3), shown as
Aarian/Merrick.

## Contact

Aarian Bhakoo, Western University.
