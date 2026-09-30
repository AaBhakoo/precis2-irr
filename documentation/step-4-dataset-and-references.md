# Step 4: final dataset and trial reference key

## Public analysis dataset

`data/derived/precis2_irr_final.csv` is the canonical public dataset. Each row
is one included trial-domain observation and contains the two independent
ratings plus the aligned consensus rating. The file is domain-major and has
237 rows, with observation identifiers 1 through 237.

The public dataset intentionally excludes supporting quotations, reviewer
justifications, risk-of-bias work, and other fields from the original
extraction workbook. Those materials are not required to reproduce the IRR
analysis and will remain private.

## Trial reference key

`data/included_trials.csv` maps the 24 short trial labels used in the dataset
to report citations and DOIs. Ten citations were verified against the 2013
Cochrane review and/or Crossref. Five additional reports were matched using
author, year, title, and trial details but should be checked by a co-author who
has the source collection. Nine reports still require a full citation from the
source collection. These statuses are explicit in the file so no provisional
record can be mistaken for a verified citation.

## Automated validation

Running `python scripts/extract_authoritative_data.py` checks that:

- the final dataset contains 237 unique trial-domain observations;
- observation identifiers are exactly 1 through 237;
- all three score fields contain only codes 1 through 7;
- the three accepted correction pairs are applied;
- the 24-row reference key matches the dataset's trial order; and
- the previously verified crude-agreement and mean-deviation targets remain
  unchanged.

The original workbook remains untouched and is excluded from Git history.
