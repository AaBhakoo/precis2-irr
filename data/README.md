# Analysis data

## Derived files

`precis2_irr_final.csv` is the canonical public analysis dataset. It contains
one row per included trial-domain observation and places Aarian's independent
rating, Merrick's independent rating, and the aligned consensus rating in the
same record. This is the preferred file for reproducing the IRR analyses.

`independent_ratings_tidy.csv` is the finalized independent-rating dataset. It
contains one row per included trial-domain observation and applies the three
verified corrections recorded in `verified_corrections.csv`.

`consensus_ratings_tidy.csv` contains the aligned consensus score for every
included observation.

`exclusions.csv` records Thompson (2000B), Domains 7 through 9, which were not
included because separate patient- and staff-level individual measurements
could not be defensibly prioritized or weighted.

`verified_corrections.csv` records the archived 2x237 values and the
independently verified replacements. Corrections are applied to derived data
only. Archived source files remain unchanged.

The two separate ratings files are retained as audit-friendly intermediate
outputs. They contain no information beyond the canonical combined dataset.

`included_trials.csv` is the reference key for the 24 trial labels used in the
dataset. It links each short label to its full report citation and persistent
identifier where available.

## Coding

- Scores 1 through 5 are ordinal PRECIS-2 ratings.
- Code 6 means Missing.
- Code 7 means Not Applicable.
- Codes 6 and 7 are separate nominal categories and are not positions beyond 5
  on the ordinal scale.

## Ordering

The archived 2x237 tables are domain-major: all included trials for Domain 1,
then all included trials for Domain 2, continuing through Domain 10.
Comparator is Domain 10 in the finalized data. Historical workbook labels that
call Comparator Domain 11 are copying errors.
