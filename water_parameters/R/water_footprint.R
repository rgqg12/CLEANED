# Green and blue water footprint for i-CLEANED -- reference implementation of the revised methodology
# ("Green water footprint in i-CLEANED -- revised methodology", Sections 3-10 and Annex A).
#
# Designed to slot in after cleaned::land_requirement() and cleaned::energy_requirement(); it replaces
# cleaned::water_requirement(). Hosted parameters are read from water_parameters/tables.
#
# Main entry point: water_footprint(para, land_required, energy_required, gid1, tables_dir, ...)

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
})

MONTH_DAYS <- c(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

# ---- hosted tables -----------------------------------------------------------------------------
wf_load_tables <- function(tables_dir) {
  rd <- function(f) utils::read.csv(file.path(tables_dir, f), stringsAsFactors = FALSE, check.names = FALSE)
  list(
    climate      = rd("climate_admin1_monthly.csv"),
    cwu          = rd("crop_water_use_admin1.csv"),
    crop_map     = rd("icleaned_crop_mapping.csv"),
    main_me      = rd("main_product_me.csv"),
    livestock    = rd("livestock_water_icleaned.csv"),
    availability = rd("water_availability_admin1_annual.csv"),
    stress       = rd("water_stress_admin1_annual.csv")
  )
}

# ---- Section 3: climate and crop water balance --------------------------------------------------
# USDA-SCS effective rainfall, monthly mm (Eq. 3; Smith 1992)
wf_peff <- function(p) ifelse(p <= 250, p * (125 - 0.2 * p) / 125, 125 + 0.1 * p)

# FAO-56 piecewise-linear Kc curve, one value per day of the growing period (Eq. 1)
wf_kc_daily <- function(kc_ini, kc_mid, kc_end, L) {
  L <- round(L)
  c(rep(kc_ini, L[1]),
    kc_ini + (seq_len(L[2]) / L[2]) * (kc_mid - kc_ini),
    rep(kc_mid, L[3]),
    kc_mid + (seq_len(L[4]) / L[4]) * (kc_end - kc_mid))
}

# first month of the rainy season: P >= 0.5 ET0 after a month with P < 0.5 ET0
wf_onset_month <- function(clim) {
  wet <- clim$P_mm >= 0.5 * clim$ET0_mm
  prev <- c(wet[12], wet[1:11])
  m <- which(wet & !prev)
  if (length(m)) m[1] else which.max(clim$P_mm)
}

# Monthly balance for an annual crop (Eqs. 2, 4, 14): returns ETc, ETg, ETb per month (mm)
wf_balance_annual <- function(kc_ini, kc_mid, kc_end, gp_days, start_month, clim,
                              stage_frac = c(0.15, 0.30, 0.35, 0.20)) {
  kc <- wf_kc_daily(kc_ini, kc_mid, kc_end, gp_days * stage_frac)
  et0_day <- clim$ET0_mm / MONTH_DAYS
  day_month <- rep(rep(1:12, MONTH_DAYS), 2)                   # two calendar years to allow wrap-around
  start_day <- sum(MONTH_DAYS[seq_len(start_month - 1)]) + 1
  months <- day_month[start_day:(start_day + length(kc) - 1)]
  etc <- tapply(kc * et0_day[months], factor(months, levels = 1:12), sum, default = 0)
  g <- tapply(rep(1, length(kc)), factor(months, levels = 1:12), sum, default = 0) / MONTH_DAYS
  peff <- wf_peff(clim$P_mm) * pmin(g, 1)
  data.frame(month = 1:12, ETc = as.numeric(etc), Peff = as.numeric(peff),
             ETg = pmin(as.numeric(etc), as.numeric(peff)),
             ETb = pmax(0, as.numeric(etc) - as.numeric(peff)))
}

# Perennial forage / pasture: active (Kc_mid) where P >= 0.5 ET0, otherwise Kc_ini (dry-season cover)
wf_balance_perennial <- function(kc_ini, kc_mid, clim) {
  kc <- ifelse(clim$P_mm >= 0.5 * clim$ET0_mm, kc_mid, kc_ini)
  etc <- kc * clim$ET0_mm
  peff <- wf_peff(clim$P_mm)
  data.frame(month = 1:12, ETc = etc, Peff = peff, ETg = pmin(etc, peff), ETb = pmax(0, etc - peff))
}

# ---- Section 5: allocation 1 (main crop vs residue, ME basis) -----------------------------------
wf_af_residue <- function(M, R, me_M, me_R) {
  if (R <= 0) return(0)
  R * me_R / (M * me_M + R * me_R)                                # Eqs. 7-8
}

# ---- Section 6: allocation 2 (herd co-products, feed-energy requirement) ------------------------
wf_herd_allocation <- function(er) {
  # er: cleaned::energy_requirement()$annual_results; daily MJ per head
  e <- function(col) sum(365 * er$herd_composition * er[[col]], na.rm = TRUE)
  E <- c(milk = e("er_lactation"), meat = e("er_growth") + e("er_pregnancy"),
         wool = e("er_wool"), draught = e("er_work"))
  tot <- sum(E)
  data.frame(coproduct = names(E), productive_energy_MJ = as.numeric(E),
             AF = if (tot > 0) as.numeric(E) / tot else NA_real_)       # Eq. 11
}

# Growth energy for classes whose adult_weight is missing (IPCC 2019 Eq. 10.6 needs mature weight):
# use the heaviest adult_weight recorded for the same species in the study, and flag it.
wf_fix_growth_energy <- function(er) {
  flags <- character()
  cattle <- grepl("^(Cattle|Buffalo)", er$livestock_category_name)
  mw <- suppressWarnings(max(er$adult_weight[cattle & er$adult_weight > 0], na.rm = TRUE))
  bad <- cattle & er$annual_growth > 0 & er$er_growth == 0 & (is.na(er$adult_weight) | er$adult_weight <= 0)
  if (any(bad) && is.finite(mw)) {
    c_factor <- ifelse(grepl("Adult male", er$livestock_category_name), 1.2,
                       ifelse(grepl("Cows", er$livestock_category_name), 0.8, 1.0))
    er$er_growth[bad] <- 22.02 * ((er$body_weight[bad] / (c_factor[bad] * mw))^0.75) *
      ((er$annual_growth[bad] / 365)^1.097)
    flags <- paste0("growth energy recomputed with adult weight ", mw, " kg for: ",
                    paste(er$livestock_category_name[bad], collapse = ", "))
  }
  list(er = er, flags = flags)
}

# ---- main ---------------------------------------------------------------------------------------
water_footprint <- function(para, land_required, energy_required, gid1, tables_dir,
                            irrigated = character(),          # feed_item_name of irrigated items
                            irrigation_applied_mm = list(),   # optional: named by feed item, mm per season
                            application_efficiency = 0.60,    # surface irrigation default (Eq. 15)
                            production_system = "mixed",      # drinking/service water column
                            annual_gp_days = 120,             # Tier 2 default growing period
                            main_yield_defaults = NULL) {     # data.frame(crop_name, dry_yield) from lkp_crops
  tb <- wf_load_tables(tables_dir)
  flags <- character()
  clim <- tb$climate[tb$climate$GID_1 == gid1, ][order(tb$climate$month[tb$climate$GID_1 == gid1]), ]
  stopifnot(nrow(clim) == 12)
  onset <- wf_onset_month(clim)

  # annual intake (t DM) per feed item, and item parameters
  lr <- land_required$land_requirements_all
  intake <- lr %>% group_by(feed) %>% summarise(dm_t = sum(feed_item_dm, na.rm = TRUE) / 1000, .groups = "drop")
  fi <- para$feed_items
  items <- intake %>% left_join(fi, by = c("feed" = "feed_item_name"))
  items$crop_name <- trimws(items$crop_name)

  rows <- list()
  for (i in seq_len(nrow(items))) {
    it <- items[i, ]
    num <- function(x) suppressWarnings(as.numeric(x))
    map <- tb$crop_map[trimws(tb$crop_map$icleaned_crop_name) == it$crop_name, ]
    r <- list(feed = it$feed, crop_name = it$crop_name, dm_t = it$dm_t, tier = NA, irrigated = it$feed %in% irrigated,
              GWU_m3_ha = NA, BWU_m3_ha = 0, AF = 1, output_t_ha = NA, note = "")
    if (it$crop_name == "Purchased" || (num(it$dry_yield) == 0 && num(it$residue_dry_yield) == 0)) {
      r$tier <- "excluded"; r$note <- "purchased feed without supplier data: declared exclusion (Section 4.2)"
      rows[[i]] <- r; next
    }
    # --- water use per hectare (Section 3 / 10.2)
    mialyk <- if (nrow(map)) map$mialyk_crop[1] else NA
    is_residue <- identical(it$source_type, "Residue")
    if (!is.na(mialyk) && mialyk != "") {
      cw <- tb$cwu[tb$cwu$GID_1 == gid1 & tb$cwu$crop == mialyk, ]
      r$tier <- paste0("Tier 1 (Mialyk: ", mialyk, ", ", cw$source_level, ")")
      if (r$irrigated) { r$GWU_m3_ha <- 10 * cw$green_irrigated_mm; r$BWU_m3_ha <- 10 * cw$blue_irrigated_mm }
      else r$GWU_m3_ha <- 10 * cw$green_rainfed_mm
    } else {
      kc <- c(num(it$kc_initial), num(it$kc_midseason), num(it$kc_late))
      fao <- if (nrow(map)) map$fao56_entry[1] else ""
      perennial <- grepl("Pasture|Bermuda|Rye Grass|Sudan Grass|Alfalfa|Clover", fao)
      bal <- if (perennial) wf_balance_perennial(kc[1], kc[2], clim) else
        wf_balance_annual(kc[1], kc[2], kc[3], annual_gp_days, onset, clim)
      r$tier <- paste0("Tier 2 (FAO-56, ", if (perennial) "perennial" else paste0("annual, ", annual_gp_days, " d from month ", onset), ")")
      r$GWU_m3_ha <- 10 * sum(bal$ETg)
      if (r$irrigated) {
        bwu <- 10 * sum(bal$ETb)
        app <- irrigation_applied_mm[[it$feed]]
        if (!is.null(app)) bwu <- min(bwu, 10 * application_efficiency * app)          # Eq. 15
        r$BWU_m3_ha <- bwu
      }
    }
    # --- output per hectare and allocation 1 (Sections 4-5)
    Y_M <- num(it$dry_yield); Y_R <- num(it$residue_dry_yield)
    r_M <- num(it$main_product_removal); r_R <- num(it$residue_removal)
    if (is_residue) {
      if ((is.na(Y_M) || Y_M == 0) && !is.null(main_yield_defaults)) {
        d <- main_yield_defaults$dry_yield[trimws(main_yield_defaults$crop_name) == it$crop_name]
        if (length(d)) { Y_M <- d[1]; flags <- c(flags, paste0(it$feed, ": main-product yield missing, database default ", Y_M, " t DM/ha used")) }
      }
      if (is.na(r_M) || r_M == 0) { r_M <- 1; flags <- c(flags, paste0(it$feed, ": main_product_removal is 0, set to 1 (grain harvested)")) }
      me_row <- tb$main_me[grepl(paste0("(^|; )", it$crop_name, "($|;)"), tb$main_me$icleaned_crop_names, fixed = FALSE), ]
      me_M <- if (nrow(me_row)) me_row$me_MJ_kgDM[1] else NA
      if (is.na(me_M) || is.na(Y_M) || Y_M == 0) {
        r$AF <- 1; r$note <- "AF_R = 1: main-product yield or ME missing (flagged)"
        flags <- c(flags, paste0(it$feed, ": residue allocation not possible, AF_R = 1"))
      } else {
        r$AF <- wf_af_residue(Y_M * r_M, Y_R * r_R, me_M, num(it$me_content))
        r$note <- sprintf("ME allocation: M=%.2f R=%.2f t DM/ha, ME_M=%.1f ME_R=%.1f", Y_M * r_M, Y_R * r_R, me_M, num(it$me_content))
      }
      r$output_t_ha <- Y_R * r_R
    } else {
      r$output_t_ha <- Y_M * r_M                                   # forage / pasture: u = removal (Section 4.1)
      if (grepl("pasture", it$feed, ignore.case = TRUE)) r$note <- sprintf("utilization u = %.2f", r_M)
    }
    rows[[i]] <- r
  }
  feeds <- bind_rows(lapply(rows, as.data.frame))
  feeds <- feeds %>% mutate(
    green_m3 = ifelse(tier == "excluded", 0, dm_t * GWU_m3_ha * AF / output_t_ha),       # Eq. 6
    blue_irrigation_m3 = ifelse(tier == "excluded", 0, dm_t * BWU_m3_ha * AF / output_t_ha),
    area_ha = ifelse(tier == "excluded", 0, dm_t / output_t_ha))

  # --- herd (Sections 6, 10.3-10.5)
  fix <- wf_fix_growth_energy(energy_required$annual_results)
  flags <- c(flags, fix$flags)
  er <- fix$er
  alloc <- wf_herd_allocation(er)
  lv <- para$livestock
  lw <- tb$livestock
  col_d <- paste0("drink_", production_system, "_L_d"); col_s <- paste0("service_", production_system, "_L_d")
  lvw <- lv %>% left_join(lw[, c("livetype_desc", col_d, col_s)], by = "livetype_desc")
  drink_m3 <- sum(365 * lvw$herd_composition * lvw[[col_d]], na.rm = TRUE) / 1000          # Eq. 16
  service_m3 <- sum(365 * lvw$herd_composition * lvw[[col_s]], na.rm = TRUE) / 1000

  G <- sum(feeds$green_m3)
  B <- sum(feeds$blue_irrigation_m3) + drink_m3 + service_m3                                  # Eq. 17
  milk_kg <- sum(lv$herd_composition * lv$annual_milk)
  fpcm_kg <- sum(lv$herd_composition * lv$annual_milk *
                   (0.1226 * lv$fat_milkcontent + 0.0776 * lv$protein_milkcontent + 0.2534))  # IDF 2022
  lw_kg <- sum(lv$herd_composition * lv$annual_growth)
  wool_kg <- sum(lv$herd_composition * lv$annual_wool)
  protein_kg <- sum(lv$herd_composition * (lv$annual_milk * lv$protein_milkcontent / 100 +
                                             lv$annual_growth * lv$carcass_fraction * lv$protein_meatcontent / 100))
  af <- setNames(alloc$AF, alloc$coproduct)
  per_unit <- function(water, af_j, q) if (q > 0) water * af_j / q else NA_real_
  indicators <- data.frame(
    indicator = c("green_water_total_m3", "blue_water_total_m3", "blue_feed_irrigation_m3", "blue_drinking_m3",
                  "blue_service_m3", "feed_area_ha", "green_m3_per_ha",
                  "green_m3_per_kg_FPCM", "green_m3_per_kg_LW", "green_m3_per_kg_wool", "green_m3_per_kg_protein",
                  "blue_m3_per_kg_FPCM", "blue_m3_per_kg_LW",
                  "FPCM_kg", "LW_output_kg", "share_DMI_excluded"),
    value = c(G, B, sum(feeds$blue_irrigation_m3), drink_m3, service_m3, sum(feeds$area_ha), G / sum(feeds$area_ha),
              per_unit(G, af["milk"], fpcm_kg), per_unit(G, af["meat"], lw_kg), per_unit(G, af["wool"], wool_kg),
              per_unit(G, af["milk"] + af["meat"], protein_kg),
              per_unit(B, af["milk"], fpcm_kg), per_unit(B, af["meat"], lw_kg),
              fpcm_kg, lw_kg, sum(feeds$dm_t[feeds$tier == "excluded"]) / sum(feeds$dm_t)))

  # --- local context (Section 10.6)
  av <- tb$availability[tb$availability$GID_1 == gid1, ]
  st <- tb$stress[tb$stress$GID_1 == gid1, ]
  context <- data.frame(GID_1 = gid1, sust_water_avail_m3_ha = av$SustWatAvail_m3_ha,
                        RWD = (B / sum(feeds$area_ha)) / av$SustWatAvail_m3_ha,              # Eq. 18
                        aqueduct_category = st$bws_category, onset_month = onset)
  if (sum(feeds$dm_t[feeds$tier == "excluded"]) > 0)
    flags <- c(flags, "purchased feed excluded from the boundary (share_DMI_excluded)")
  list(feeds = feeds, herd_allocation = alloc, indicators = indicators, context = context, flags = flags)
}
