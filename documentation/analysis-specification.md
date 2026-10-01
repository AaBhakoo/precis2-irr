# Analysis specification

## Study data

- Twenty-four randomized controlled trials.
- Two independent reviewers: Observer 1 is Aarian Bhakoo and Observer 2 is
  Merrick Zwarenstein.
- Ten PRECIS-2 domains per trial, with Comparator treated as Domain 10.
- Thompson (2000B) Domains 7, 8, and 9 were excluded because separate patient-
  and staff-level individual measurements could not be defensibly prioritized
  or weighted.
- The intended final sample is 237 paired ratings.
- Ratings 1 through 5 form the ordinal pragmatism scale. Code 6 represents
  Missing and code 7 represents Not Applicable. Codes 6 and 7 are special
  nominal categories, not extensions of the ordinal scale.

## Primary analyses

Crude agreement and Krippendorff's alpha are calculated under four definitions.

1. Total: exact matches fully agree. Differences among scores 1 through 5 have
   squared, standardized ordinal disagreement. Nonidentical comparisons
   involving code 6 or 7 have maximum disagreement.
2. Range: numerical scores within one point fully agree. Larger numerical
   differences have squared, standardized ordinal disagreement after applying
   and rescaling the one-point tolerance. Codes 6 and 7 follow the Total rules.
3. Censored: observations involving code 6 or 7 for either reviewer are
   excluded. Remaining scores use the Total disagreement function.
4. Bucketed: scores are grouped as 1-2, 3, and 4-5. The numerical buckets are
   ordinal; codes 6 and 7 remain distinct nominal categories.

The implementation preserves the statistician-reviewed alpha approach and
uses analytical confidence intervals in the `krippendorffsalpha` package.

## Secondary analyses

- Crude agreement within each domain under all four definitions.
- Mean signed deviation of each reviewer from consensus. This analysis retains
  only observations where both reviewer ratings and the consensus rating are
  scores 1 through 5.

All reported analyses were prespecified.

## Data authority

- Independent ratings: Table 1 in `Krippendorf Rater Tables`.
- Censored cross-check: Table 2 in `Krippendorf Rater Tables`.
- Consensus: `Consensus_Scores`.
- Agreement sheets and green columns: supporting checks, not final authority.

The 2x237 tables are confirmed to use domain-major ordering: all included
trials for Domain 1, followed by all included trials for Domain 2, and so forth.
Three independently verified corrections are incorporated in the canonical
dataset: Sagahutu Domain 4 (5/2), Strasser Domain 4 (4/5), and Thompson
(2000A) Domain 4 (4/3), shown as Aarian/Merrick. The source workbooks are
retained privately and are not part of this reproducibility repository.
