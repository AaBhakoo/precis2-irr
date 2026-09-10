# Step 2 change crosswalk

This document records every category of change between the archived,
statistician-reviewed `IRR Analysis.Rmd` and the reproducible analysis report
`analysis/precis2-irr-analysis.Rmd`.

## Preservation rule

The statistical implementation of Krippendorff's alpha is preserved from the
reviewed script. In particular, the following components are unchanged:

- `make_disagreement_function()`;
- the Total, Range, Censored, and Bucketed disagreement functions;
- the transformations used to create the four alpha datasets;
- `validate_alpha_data()`;
- `calculate_alpha()`, including analytical confidence intervals and disabled
  parallel processing;
- all four calls to `calculate_alpha()`; and
- extraction and display of alpha estimates and 95% confidence intervals.

The archived script remains untouched in `archive/IRR Analysis.Rmd`.

## Changes surrounding the approved core

| Area | Change | Statistical effect |
|---|---|---|
| Output format | PDF is the sole declared output format and sections are numbered. | None. |
| File paths | Removed the machine-specific `setwd()` call. A base-R check locates files relative to the repository root. | None. |
| Input format | The finalized tidy ratings and consensus tables replace manually prepared wide CSV inputs. The same two matrix orientations expected by the approved code are reconstructed. | None intended; assertions verify dimensions, codes, and ordering. |
| Input validation | Added checks for required columns, 237 unique observations, 24 trials, ten domains, trial/domain alignment, and the three Thompson (2000B) exclusions. | None; analysis stops when the specification is violated. |
| Censoring validation | Added a check that 26 observations contain code 6 or 7, leaving 211 eligible observations. | None; confirms the finalized sample. |
| Crude agreement | Retained the reviewed definitions and added regression checks for the accepted numerators and denominators. | None; unexpected results stop the report. |
| Domain analysis | Added crude agreement by domain under all four definitions and checked it against the independently generated preflight table. | New prespecified secondary output. |
| Consensus analysis | Added mean signed and absolute deviation from consensus after excluding codes 6 and 7. | New prespecified secondary output retained from the developmental script. |
| Machine-readable results | Added CSV export of global crude agreement, domain crude agreement, alpha, and reviewer-deviation tables. | None. |
| Reproducibility record | Added `sessionInfo()` and a one-command rendering script. | None. |

## Verification status

Static verification has confirmed balanced R Markdown fences and textual
preservation of the approved alpha-analysis section. Independent preflight
calculations match the accepted crude-agreement and reviewer-deviation results.

An R runtime is not installed in the current workspace. The final execution
test, package-level alpha calculation, and PDF rendering must therefore be run
in an R-enabled environment before Step 2 is considered fully verified.
