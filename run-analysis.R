# =====================================================================
# PRECIS-2 Inter-Rater Reliability Analysis
#
# Purpose - Render the complete reproducible analysis and save the knitted PDF report
# 
# Usage:
#   1. Open "precis2-irr.Rproj" in RStudio
#   2. Ensure the working directory is the repository root
#   3. Run: source("run-analysis.R")
#
# The script stops before rendering if required packages or directories are unavailable
# Validation checks are within the R Markdown analysis script
# stop execution if accepted results have changed
# =====================================================================


# Render the complete reproducible analysis from the repository root.
# Packages required by the analysis workflow
required_packages <- c(
  "dplyr",
  "tidyr",
  "purrr",
  "tibble",
  "knitr",
  "rmarkdown",
  "krippendorffsalpha"
)

# stop if any required packages are unavailable
missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]

if (length(missing_packages) > 0L) {
  stop(
    "Install the following packages before rendering: ",
    paste(missing_packages, collapse = ", ")
  )
}

# confirm that the script is being run from the repository root
project_root <- normalizePath(".", mustWork = TRUE)

if (!dir.exists(file.path(project_root, "analysis")) ||
    !file.exists(file.path(project_root, "data", "precis2_irr_final.csv"))) {
  stop("Run this script from the precis2-irr repository root.")
}

# create the report directory if it does not already exist
output_directory <- file.path(project_root, "outputs", "reports")
dir.create(output_directory, recursive = TRUE, showWarnings = FALSE)

# render the analysis in a clean environment rooted at the repository
rmarkdown::render(
  input = file.path(project_root, "analysis", "precis2-irr-analysis.Rmd"),
  output_format = "pdf_document",
  output_file = "precis2-irr-analysis.pdf",
  output_dir = output_directory,
  knit_root_dir = project_root,
  envir = new.env(parent = globalenv()),
  clean = TRUE
)
