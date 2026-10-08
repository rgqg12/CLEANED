# Study_1 test: current code vs revised methodology

Study_1 is the i-CLEANED example farm "Rungwe" (Southern Highland Tanzania Dairy database), mapped to GADM region Mbeya, `TZA.13_1`. The herd is 1 improved cow (2,135 kg milk/yr) and 2 improved steers/heifers (125 kg gain each). They eat commercial concentrate, natural pasture, Napier grass, lablab forage and groundnut residue.

Reproduce with `Rscript water_parameters/R/example_study1.R` (see the header of that file). Unit tests: `Rscript -e 'testthat::test_file("water_parameters/R/tests/test_water_footprint.R")'` (16 checks pass).

## Headline indicators

| Indicator | `cleaned::water_requirement()` today | Revised methodology |
|---|---|---|
| Total water | 733 labelled "m³" (really mm × ha; 7,326 m³ if converted) | Green 3,092 m³; blue 57 m³ (drinking 46, service 10, irrigation 0) |
| Water per kg milk | 0.32 (all water charged to milk; FAO/GLEAM FPCM; unit error) | 0.82 m³ green per kg FPCM (IDF 2022 FPCM; milk share 0.60) |
| Water per kg meat | 5.98 (all water charged to meat, per kg carcass) | 4.92 m³ green per kg live weight (meat share 0.40) |
| Feed area | – | 0.71 ha; 4,384 m³/ha green |
| Local context | – | Aqueduct: Low–Medium stress; blue use is 4.1% of sustainable availability (1,945 m³/ha/yr) |

## Per feed item

| Feed | Tier | Intake (t DM) | Green water (m³/ha) | Allocation factor | Output (t DM/ha) | Green water charged (m³) |
|---|---|---|---|---|---|---|
| Concentrate (commercial) | excluded (purchased, no supplier data) | 0.68 | – | – | – | 0 (9.7% of intake declared excluded) |
| Groundnut residue | Tier 1, Mialyk groundnuts, Mbeya | 0.28 | 5,834 | 0.60 (ME: pods 0.56 t × 18.2 MJ vs residue 1.86 t × 8.4 MJ) | 1.86 | 536 |
| Lablab forage | Tier 2, annual, 110 days (FAO-56 Table 11, green gram/cowpea) from December onset | 3.01 | 3,225 | 1 | 10.8 | 898 |
| Natural pasture | Tier 2, perennial (extensive grazing Kc) | 1.03 | 4,895 | 1 (u = 0.9) | 11.3 | 443 |
| Napier grass | Tier 2, perennial | 2.03 | 6,591 | 1 | 11.0 | 1,214 |

## Why the numbers change

1. **Units.** The current total is in mm × ha. ×10 gives m³.
2. **Growing period and rainfall cap.** The current code applies annual ET0 to every crop for 12 months and does not cap by rainfall. The revised method uses monthly effective rainfall, and annual lablab grows for 120 days. Green water is therefore lower than the converted 7,326 m³.
3. **Residue allocation.** The groundnut residue had 100% of its field's water, because its main yield and removal are 0 in the study data. With the database default grain yield and ME allocation it takes 60%.
4. **Co-products.** The current code charges all water to milk *and* all of it again to meat. The revised method splits it 60/40 by feed-energy requirement.
5. **Growth energy bug (new finding).** The steers' `adult_weight` is 0 in Study_1. IPCC Eq. 10.6 divides by it, and `cleaned::energy_requirement()` silently turns the resulting Inf into 0. With zero growth energy, meat would get no water and feed requirements are understated. The reference implementation recomputes it with the cows' 600 kg and flags it. The fix belongs in `energy_requirement.R` and the input validation.

## Flags raised for Study_1

- Groundnut residue: main-product yield missing, database default 0.56 t DM/ha used.
- Groundnut residue: `main_product_removal` = 0, set to 1 (grain harvested).
- Growth energy recomputed with adult weight 600 kg for "Cattle - Steers/heifers (improved)".
- Purchased concentrate excluded from the boundary (9.7% of dry-matter intake).

## Assumptions used in this test (defaults, not Study_1 data)

- Region Mbeya (Rungwe district). All feed rainfed (no irrigation flag in the study). Production system "mixed" for drinking and service water.
- Lablab treated as an annual forage (FAO-56 proxy: green gram and cowpeas), 110 days from the rainfall onset month (median FAO-56 Table 11 length). Pasture and Napier treated as perennials, at Kc_mid in wet months and Kc_ini in dry months.
- Utilization of natural pasture taken from the study's `main_product_removal` (0.9). The proposed default for communal grazing (0.35) would raise pasture green water per kg about 2.6 times.
