# Unit tests for water_footprint.R:  Rscript -e 'testthat::test_file("water_parameters/R/tests/test_water_footprint.R")'
library(testthat)
source(testthat::test_path("..", "water_footprint.R"))

test_that("USDA-SCS effective rainfall matches CROPWAT (Eq. 3)", {
  expect_equal(wf_peff(100), 100 * (125 - 20) / 125)          # 84 mm
  expect_equal(wf_peff(300), 125 + 30)                        # 155 mm
  expect_equal(wf_peff(0), 0)
})

test_that("Kc curve has the stage-weighted mean of Eq. 1b", {
  L <- c(30, 40, 50, 30)
  kc <- wf_kc_daily(0.3, 1.2, 0.6, L)
  expect_length(kc, sum(L))
  kbar <- (0.3 * 30 + 0.5 * (0.3 + 1.2) * 40 + 1.2 * 50 + 0.5 * (1.2 + 0.6) * 30) / sum(L)
  expect_equal(mean(kc), kbar, tolerance = 0.01)
})

test_that("green water never exceeds effective rainfall or crop ET (Eq. 4)", {
  clim <- data.frame(month = 1:12, P_mm = c(5, 5, 60, 150, 200, 120, 30, 5, 5, 5, 40, 90),
                     ET0_mm = rep(130, 12))
  b <- wf_balance_annual(0.3, 1.15, 0.5, 120, 3, clim)
  expect_true(all(b$ETg <= b$ETc + 1e-9) && all(b$ETg <= b$Peff + 1e-9))
  expect_equal(b$ETg + b$ETb, b$ETc)
  expect_equal(sum(b$ETc > 0), 4)                              # 120 days from 1 March end on 28 June
})

test_that("ME allocation reproduces the maize worked example (Section 5.4)", {
  af <- wf_af_residue(M = 1.06, R = 2.69 * 0.7, me_M = 13.5, me_R = 9.13)
  expect_equal(round(af, 2), 0.55)
  expect_equal(round(4000 * af / (2.69 * 0.7)), 1159)
  expect_equal(wf_af_residue(1, 0, 13, 9), 0)                   # unharvested residue carries nothing
})

test_that("herd allocation closes to 1 and maps energy to co-products (Eq. 11)", {
  er <- data.frame(herd_composition = c(1, 2), er_lactation = c(18, 0), er_growth = c(0, 6),
                   er_pregnancy = c(3, 0), er_wool = 0, er_work = 0)
  a <- wf_herd_allocation(er)
  expect_equal(sum(a$AF), 1)
  expect_equal(a$AF[a$coproduct == "milk"], 18 / (18 + 3 + 12))
})
