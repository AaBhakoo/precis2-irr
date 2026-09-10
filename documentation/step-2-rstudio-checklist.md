# Step 2 RStudio execution checklist

1. Open `precis2-irr.Rproj` in RStudio.
2. Confirm that LaTeX is available. If necessary, install TinyTeX once with
   `tinytex::install_tinytex()`.
3. Install any packages named by an error from `source("run-analysis.R")`.
4. Run `source("run-analysis.R")` from the Console.
5. Confirm that the script completes without an error.
6. Inspect `outputs/reports/precis2-irr-analysis.pdf`.
7. Confirm that these files were created in `outputs/results/`:
   - `global-crude-agreement.csv`
   - `domain-crude-agreement.csv`
   - `krippendorff-alpha.csv`
   - `reviewer-deviation-from-consensus.csv`
8. Confirm the global crude-agreement rows report 115/237, 165/237, 110/211,
   and 152/237 for Total, Range, Censored, and Buckets, respectively.
9. Send the PDF and `outputs/results/krippendorff-alpha.csv` for co-author review
   before making the repository public.
