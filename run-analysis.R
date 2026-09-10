# Render the complete reproducible analysis from the repository root.

required_packages <- c(
  "dplyr",
  "tidyr",
  "purrr",
  "tibble",
  "knitr",
  "rmarkdown",
  "krippendorffsalpha"
)

missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]

if (length(missing_packages) > 0L) {
  stop(
    "Install the following packages before rendering: ",
    paste(missing_packages, collapse = ", ")
  )
}

project_root <- normalizePath(".", mustWork = TRUE)

if (!dir.exists(file.path(project_root, "analysis")) ||
    !dir.exists(file.path(project_root, "data", "derived"))) {
  stop("Run this script from the precis2-irr repository root.")
}

output_directory <- file.path(project_root, "outputs", "reports")
dir.create(output_directory, recursive = TRUE, showWarnings = FALSE)

rmarkdown::render(
  input = file.path(project_root, "analysis", "precis2-irr-analysis.Rmd"),
  output_format = "pdf_document",
  output_file = "precis2-irr-analysis.pdf",
  output_dir = output_directory,
  knit_root_dir = project_root,
  envir = new.env(parent = globalenv()),
  clean = TRUE
)
