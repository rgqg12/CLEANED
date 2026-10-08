# Run the revised water footprint on i-CLEANED Study_1 (Rungwe, Mbeya, Tanzania) and compare with
# cleaned::water_requirement(). Needs clones of CIAT/cleaned and CIAT/icleaned:
#   CLEANED_SRC=/path/cleaned ICLEANED_SRC=/path/icleaned Rscript water_parameters/R/example_study1.R
suppressMessages({library(dplyr); library(tidyr); library(jsonlite); library(stringr); library(tibble); library(purrr)})
src <- Sys.getenv("CLEANED_SRC"); app <- Sys.getenv("ICLEANED_SRC")
here <- dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE))))
for (f in c("feed_quality", "energy_requirement", "land_requirement", "water_requirement"))
  source(file.path(src, "R", paste0(f, ".R")))
source(file.path(here, "water_footprint.R"))

para <- fromJSON(file.path(app, "data/shared_folder/study_objects/Study_1.json"), flatten = TRUE)
energy_parameters <- fromJSON(file.path(src, "inst/extdata/energy_parameters.json"), flatten = TRUE)
fq <- feed_quality(para)
er <- energy_requirement(para, fq, energy_parameters)
lr <- land_requirement(fq, er, para)
old <- water_requirement(para, lr)
lk <- read.csv(file.path(app, "data/primary_database/Southern Highland Tanzania Dairy/lkp_crops.csv"), check.names = FALSE)

new <- water_footprint(para, lr, er, gid1 = "TZA.13_1", tables_dir = file.path(here, "..", "tables"),
                       main_yield_defaults = lk[, c("crop_name", "dry_yield")])
options(width = 200)
cat("\n== cleaned::water_requirement (current) ==\n"); print(old$water_use_for_production)
cat("\n== revised methodology ==\n"); print(new$feeds); print(new$herd_allocation); print(new$indicators)
print(new$context); cat(paste("FLAG:", new$flags), sep = "\n")
