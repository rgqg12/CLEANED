# i-CLEANED hosted water parameters

These are the parameter tables i-CLEANED hosts so users don't have to enter them. They feed the green and blue water methodology ("Green water footprint in i-CLEANED, revised methodology", Sections 3 to 10). Every table can be rebuilt from public sources with the scripts in `scripts/`.

**Spatial unit:** GADM 4.1 level-1 regions (`GID_1`) in 166 countries of the Global South: 2,620 regions in total.

**Global South definition:** all countries and territories in the UN M49 sub-regions of Africa, Latin America and the Caribbean, Asia and Oceania, except Australia, New Zealand, Japan, the Republic of Korea, Israel, Cyprus, Singapore, Taiwan, Hong Kong and Macao. See `tables/global_south_countries.csv`; it is an assumption and can be edited. Twelve small territories have no GADM level-1 units: ABW, BVT, CUW, FLK, IOT, KIR, MAF, MDV, NIU, PCN, SGS and SXM.

## Tables

| File | Contents | Unit | Used in (methodology) | Source | Status |
|---|---|---|---|---|---|
| `admin1_regions.csv` | Region list: country, name, type, area | km² | Region dropdown | GADM 4.1 | Done |
| `climate_admin1_monthly.csv` | Monthly normals per region: P, Peff (USDA-SCS), ET0 (FAO-56 Penman-Monteith), Tmean, Tmax | mm/month, °C | Eqs. 2–4, 14; drinking water Tier 2 | WorldClim 2.1, 10′, 1970–2000 (Fick & Hijmans 2017); ET0 computed from it with FAO-56 Eq. 6 | Done; 4 tiny islands use the country mean (`fill_method`) |
| `water_availability_admin1_monthly.csv`, `..._annual.csv` | Total water availability (surface runoff + groundwater recharge), groundwater recharge, and renewable availability as in Damerau (2024) | m³/ha | Eq. 18 (RWD) | WaterGAP 2.2e, ISIMIP3a, gswp3-w5e5 obsclim histsoc, 1990–2019 means (Müller Schmied et al. 2023) | Done; 45 small coastal or island regions filled from neighbouring cells and 15 remote islands from the country mean (`fill_method`) |
| `water_stress_admin1_annual.csv`, `..._monthly.csv` | Baseline water stress score (0–5) and category, area shares per category, share classed "arid and low water use" | – | Section 10.6 | WRI Aqueduct 4.0 baseline (Kuzma et al. 2023), HydroBASINS level 6, area-weighted | Done; 171 regions use the nearest basin (`fill_method`) |
| `fao56_table11_stage_lengths.csv` | Growth-stage lengths by crop and region | days | Eq. 1 | FAO-56 Table 11 (Allen et al. 1998), parsed from the FAO online edition | Done; rows where the stages don't add up to the stated total are flagged |
| `fao56_table12_kc.csv` | Single crop coefficients (Kc ini/mid/end), including grazing pasture | – | Eq. 1 | FAO-56 Table 12 | Done |
| `livestock_water_source_table.csv` | Drinking and service water by animal, age group and system | L/head/day | Eqs. 16–17 | Chapagain & Hoekstra (2003), Tables 3.8–3.9, as used by Mekonnen & Hoekstra (2010) | Done |
| `livestock_water_icleaned.csv` | The same values mapped to the 22 i-CLEANED livestock types (grazing, mixed, industrial), plus feed mixing water | L/head/day | Eqs. 16–17 | as above | Done; mappings marked "assumed" need expert review |
| `irrigation_efficiency.csv` | Field application efficiency (surface 60%, sprinkler 75%, drip 90%) and conveyance efficiency | % | Eq. 15 | Brouwer et al. (1989), FAO Training Manual 4, Annex 1, Tables 7–8 | Done |
| `crop_water_use_admin1.csv` | Crop water use for 43 crops × 2,620 regions: rainfed and irrigated totals; green rainfed, green irrigated and blue irrigated; national capillary-rise share | mm/season | Eqs. 5, 13 (Tier 1) | Mialyk et al. (2024), dataset 2.9 (CC BY 4.0). Green/blue split per Mekonnen & Hoekstra (2011): blue = irrigated − rainfed | Done; regions without the crop take the country or sub-region mean (`source_level`) |
| `icleaned_crop_mapping.csv` | All 131 crop and feed names in the i-CLEANED databases → Mialyk crop (direct or proxy) and FAO-56 Table 12 entry with Kc values | – | Tier 1 / Tier 2 choice | This work, following Mialyk et al. (2024, Table S1) and Damerau (2024, Table 1) | Done; 59 crops with Tier 1, 72 forages/pastures/trees on Tier 2; 19 fodder trees and shrubs, plus cactus, need expert Kc |
| `main_product_me.csv` | ME (ruminants, MJ/kg DM) of the main product of 31 residue-bearing crops, with the exact Feedipedia table, DM, SD and the i-CLEANED crop names it serves; `feedipedia_me_all_tables.csv` keeps every parsed table | MJ/kg DM | Eqs. 7–8 (ME-based residue allocation) | Feedipedia datasheets (INRAE, CIRAD, AFZ, FAO) | Done; 27 direct, 2 proxy (taro → cocoyam, sugar beet → fodder beet), 2 with no published ME (tomato fruits, whole sesame seeds) |

### Parameters that still need team or expert input (no public dataset)

| Parameter | Used in | Proposed default in the methodology |
|---|---|---|
| ME for tomato fruits and whole sesame seeds (no Feedipedia value) | Eqs. 7–8 | Expert value or local analysis |
| Pasture utilization u by grazing type | Section 4.1 | 0.35 / 0.60 / 0.85 (to be verified) |
| Production system per livestock type (grazing, mixed or industrial), to pick the drinking and service water column | Eq. 16 | mixed |

## Notes for the development team

1. **Drinking water values.** The legacy `cleaned.sqlite` table `lkp_livetype.water_requirement` gives 120–160 L/day for cows. Chapagain and Hoekstra give 40–70 L/day drinking plus 5–22 L/day service water. The legacy values are probably total water intake from an undocumented source, and that column no longer exists in the current `lkp_livetype.csv` files. Recommendation: use `livestock_water_icleaned.csv` as Tier 1 drinking water.
2. **Renewable water formula (Damerau 2024).** The formula `TotWatAvail × (0.25×0.3 + 0.5×0.45 + 0.25×0.6)` simplifies to `0.45 × TotWatAvail`. In Rosa et al. (2018) these fractions are environmental flow requirements, i.e. the share to be *reserved*, which would make sustainable availability `0.55 × TotWatAvail`. The table reproduces Damerau's formula as written; please check it against Rosa et al. (2018), Table S1.
3. **Climate normals** come from WorldClim 2.1 (1970–2000), because the TerraClimate server was not reachable from the build environment. The scripts can be pointed to TerraClimate or CHIRPS later.
4. **Mialyk data access.** The 4TU repository was under maintenance during the build (8 October 2026). Dataset 2.9 and the national table were taken from the Internet Archive copies of the 4TU files (snapshots of November 2025, identical file size). Re-run `07_crop_water_use.py` against 4TU when it is back to confirm.
5. **Green/blue split of Tier 1.** Dataset 2.9 gives total crop water use per system only. Green irrigated = min(rainfed, irrigated); blue = the difference. This is the Mekonnen & Hoekstra (2011) definition described by Damerau (2024). Rainfed "green" includes capillary rise; `cr_share_national` shows its national share, which is below 1% for most crops. An exact split needs Mialyk dataset 2.8 (13 GB, annual, by water type).
6. **Effective rainfall** is calculated per grid cell and then averaged, because the USDA-SCS formula is non-linear.

## Rebuilding

```
pip install geopandas rasterio xarray netCDF4 exactextract pyogrio country_converter pdfplumber
export ICLEANED_WATER_RAW=/path/to/raw/downloads
python scripts/01_admin1.py            # GADM 4.1 level 1 (geodata.ucdavis.edu/gadm/gadm4.1/json/)
python scripts/02_climate.py           # WorldClim 2.1 10m (geodata.ucdavis.edu/climate/worldclim/2_1/base/)
python scripts/03_water_availability.py  # WaterGAP 2.2e qs, qr (files.isimip.org, ISIMIP3a)
python scripts/04_water_stress.py      # Aqueduct 4.0 (files.wri.org/aqueduct/aqueduct-4-0-water-risk-data.zip)
python scripts/05_fao56_tables.py      # FAO-56 Chapter 6 HTML (fao.org/4/X0490E/x0490e0b.htm)
python scripts/06_livestock_water.py   # values typed from Chapagain & Hoekstra (2003)
python scripts/07_crop_water_use.py    # Mialyk et al. 2024 dataset 2.9 (data.4tu.nl, doi:10.4121/7b45bcc6-...)
python scripts/08_crop_mapping.py      # needs the i-CLEANED repo next to the raw folder (data/primary_database)
python scripts/09_fill_gaps.py         # after 02 and 03
python scripts/10_main_product_me.py   # Feedipedia datasheets saved as RAW/feedipedia/<node>.html
```

## References

- Allen RG, Pereira LS, Raes D, Smith M (1998) FAO Irrigation and Drainage Paper 56. FAO, Rome.
- Brouwer C, Prins K, Heibloem M (1989) Irrigation Water Management: Irrigation Scheduling. FAO Training Manual 4.
- Chapagain AK, Hoekstra AY (2003) Virtual water flows between nations in relation to trade in livestock and livestock products. Value of Water Research Report Series No. 13, UNESCO-IHE.
- Damerau K (2024) Adapting i-CLEANED for evaluating freshwater depletion and water quality impacts of livestock systems. Final report, Alliance of Bioversity International and CIAT.
- Fick SE, Hijmans RJ (2017) WorldClim 2: new 1-km spatial resolution climate surfaces for global land areas. International Journal of Climatology 37:4302–4315.
- GADM (2022) Database of Global Administrative Areas, version 4.1.
- Kuzma S et al. (2023) Aqueduct 4.0. Technical Note, World Resources Institute.
- Mekonnen MM, Hoekstra AY (2010) Value of Water Research Report Series No. 48, UNESCO-IHE.
- Mekonnen MM, Hoekstra AY (2011) Hydrology and Earth System Sciences 15:1577–1600.
- Mialyk O et al. (2024) Scientific Data 11:206; data: doi:10.4121/7b45bcc6-686b-404d-a910-13c87156716a.v1.
- Müller Schmied H et al. (2023) WaterGAP v2.2e. Geoscientific Model Development Discussions.
- Rosa L et al. (2018) Environmental Research Letters 13:104002.
- Smith M (1992) CROPWAT. FAO Irrigation and Drainage Paper 46.
