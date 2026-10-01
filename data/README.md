# Analysis data

## Files

`precis2_irr_final.csv` is the canonical public analysis dataset. It contains
one row per included trial-domain observation and places Aarian's independent
rating, Merrick's independent rating, and the aligned consensus rating in the
same record. This is the preferred file for reproducing the IRR analyses.

`exclusions.csv` records Thompson (2000B), Domains 7 through 9, which were not
included because separate patient- and staff-level individual measurements
could not be defensibly prioritized or weighted.

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

Three independently verified corrections from the working tables are
incorporated in the canonical dataset: Sagahutu Domain 4 (5/2), Strasser
Domain 4 (4/5), and Thompson (2000A) Domain 4 (4/3), shown as Aarian/Merrick.
The original working records are retained privately and are not part of this
reproducibility repository.
