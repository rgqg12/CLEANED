# Green water footprint in i-CLEANED — proposed methodology (green water first, blue water extension)

Oct 8, 2026 · @Ricardo GQ

This document specifies how i-CLEANED will calculate the water footprint of a livestock enterprise. It replaces the water module described in the v1.1 proposal. Following the iCLEANED Workshop 2026, green water is calculated first; blue water is specified as a second phase (Section 9), and grey water is left for later.

The calculation runs in eight steps (Section 2). Each step is written so that it can be reproduced by hand: what goes in, the equation, what every term means and where its value comes from, the rules for special cases, and a worked example. Section 13 lists what changes relative to the current i-CLEANED calculation, why, and what extra data each change needs.

Conventions used throughout: all water volumes are in m³; 1 mm of water over 1 ha equals 10 m³; dry matter is abbreviated DM; one year is the accounting period.

## 1. Purpose, scope and system boundary

**Purpose.** The method will quantify the rainwater (green water) and, in phase 2, the surface and groundwater (blue water) consumed to produce what a herd eats and drinks in one year, and attribute that water to the herd's products. The result is a water use inventory in the sense of ISO 14046 (ISO 2014). It is not a water scarcity impact score; local context is reported beside it (Section 10).

**System boundary.** Cradle to farm gate, one production year, herd in steady state (its size and structure do not change over the year).

| Included | Excluded (and stated in every result) |
| --- | --- |
| Green water evapotranspired by every feed grown on the farm or on land the herd uses: cropland, cultivated forage, on-farm pasture, communal grazing | Grey water (pollution) |
| Green water of purchased feed, where data for the region where it was grown exist (Section 6.3) | Water embodied in fertilizer, fuel, electricity and machinery |
| Phase 2: blue water for feed irrigation, animal drinking and service (cleaning, cooling) | Evapotranspiration in fallow periods, outside the crop's growing season |
|  | Stages after the farm gate (processing, transport, retail) |
|  | Purchased feed for which no data exist (its share of intake is reported) |

**Spatial unit.** One farm or enterprise, located in one first-level administrative region (GADM 4.1 admin-1, for example a province or state). The region selects the climate, crop water use and water availability data that i-CLEANED will provide. The user can replace them with site data.

**Products and reference units.** The water footprint will be expressed per unit of each product:

| Product | Reference unit | Definition |
| --- | --- | --- |
| Milk | 1 kg fat- and protein-corrected milk (FPCM) | Milk standardized to 4.0% fat and 3.3% true protein (IDF 2022), Eq. 22 |
| Meat | 1 kg live weight output | Live weight of animals sold or slaughtered plus net herd growth over the year |
| Wool | 1 kg greasy wool | Wool as shorn |
| Edible protein | 1 kg protein in milk and meat | Used for comparison across products |
| Draught power | – | Receives its share of water (Section 8) but no per-unit figure is reported |

**Two allocation steps.** A field of maize produces grain and stover; a herd produces milk, meat and sometimes wool or draught power. Water must therefore be divided twice, and each division is made exactly once:

1. **Allocation 1, inside the crop:** between the main product (e.g. grain) and the crop residue (e.g. stover) harvested from the same field (Section 7).
2. **Allocation 2, inside the herd:** among the herd's products (Section 8).

Grazed pasture produces a single output, so Allocation 1 does not apply to it; how much of the pasture the animals actually eat is handled by a utilization fraction instead (Section 6.2).

## 2. Overview: the eight calculation steps

The calculation will always run in this order. Each step uses only the results of the steps before it.

1. **Inputs (Section 4).** Read the farm, feed basket and herd data the user enters, and look up the region's climate and other parameters i-CLEANED provides.
2. **Green water per hectare (Section 5).** For every crop, forage and pasture in the feed basket, compute the green water evapotranspired per hectare in one year (GWU, m³/ha).
3. **From hectares to the feed eaten (Section 6).** Convert water per hectare into water per tonne of each feed, and multiply by the tonnes the herd eats (G\_i, m³).
4. **Allocation 1 (Section 7).** Where a crop gives both a main product and a residue, give each its share of the field's water, by metabolizable energy (ME). This share enters Step 3.
5. **Herd total and Allocation 2 (Section 8).** Add up the water of all feeds (G\_herd) and divide it among milk, meat, wool and draught in proportion to the feed energy each function requires. Divide each share by the product quantity to get m³ per kg.
6. **Blue water, phase 2 (Section 9).** Add irrigation water of feed crops (with the same allocation factors), drinking water and service water.
7. **Local context (Section 10).** Report the regional water stress class and the herd's blue water as a share of the water that can be used sustainably in the region.
8. **Reporting (Section 11).** Report the indicators with the metadata needed to interpret them, data-quality flags and the sensitivity analysis (Section 12).

Green and blue water follow the same path through Steps 3 to 5 but are never added together.

## 3. Notation and units

Indices: *c* = crop or forage; *i* = feed item in the basket; *m* = calendar month (1–12); *t* = day of the growing season; *k* = livestock class (e.g. lactating cows); *j* = herd product (milk, meat, wool, draught).

| Symbol | Meaning | Unit | Where the value comes from |
| --- | --- | --- | --- |
| ET0,m | Reference evapotranspiration in month m | mm/month | Provided per region (Annex A); site data may replace it |
| P\_m | Precipitation in month m | mm/month | Provided per region; site data may replace it |
| Peff,m | Effective precipitation in month m | mm/month | Calculated, Eq. 4 |
| N\_m | Number of days in month m | days | Calendar (February = 28) |
| Kc,ini, Kc,mid, Kc,end | Crop coefficients for the initial, mid-season and end of the season | – | Crop table (FAO-56 Table 12) |
| L\_ini, L\_dev, L\_mid, L\_late | Length of the four growth stages | days | FAO-56 Table 11, or default fractions (Section 5.3) |
| GP | Length of the growing season | days | User, or FAO-56 Table 11, or default |
| ETc,m | Crop evapotranspiration in month m | mm/month | Eq. 3 |
| ETg,m | Green evapotranspiration in month m | mm/month | Eq. 5 |
| GWU\_c | Green water use of crop c per hectare per year | m³/ha | Eq. 1 or Eq. 6 |
| Y\_M, Y\_R | Dry-matter yield of the main product and of the residue | t DM/ha | User (existing input) or crop table |
| r\_M, r\_R | Fraction of the main product and of the residue harvested | 0–1 | User (existing input) |
| u | Utilization: fraction of pasture biomass the animals eat | 0–1 | Default by grazing type (Section 6.2) or user |
| ME\_M, ME\_R | Metabolizable energy of the main product and of the residue | MJ/kg DM | Feed table; hosted table for main products (Annex A) |
| AF\_c,R, AF\_c,M | Allocation factor of the crop's water to its residue, to its main product | 0–1 | Eqs. 13–14 |
| O\_i | Harvested or eaten output of the product feed i is made of | t DM/ha | Eq. 9 |
| DM\_i | Dry matter of feed i eaten by the herd in one year | t DM/yr | Feed basket × herd intake (existing) |
| G\_i | Green water charged to feed i | m³/yr | Eq. 10 |
| G\_herd | Green water of the whole herd | m³/yr | Eq. 20 |
| E\_j | Annual feed energy required for product j | MJ/yr | Eqs. 16–18 |
| AF\_j | Share of the herd's water allocated to product j | 0–1 | Eq. 19 |
| Q\_j | Annual quantity of product j | kg/yr | Section 8.4 |
| WF\_j | Water footprint of product j | m³/kg | Eq. 21 |

Unit rule: a depth of water in mm becomes a volume per hectare by multiplying by 10 (1 mm × 10,000 m² = 10 m³).

## 4. Step 1 – Inputs: what the user enters and what i-CLEANED will provide

The user will enter two new items; all other data are either already entered in i-CLEANED today or will be provided by i-CLEANED. Every value i-CLEANED provides can be overwritten by the user, and the result records which values were overwritten.

### 4.1 Data the user enters

| Input | Status | Required? | Used in |
| --- | --- | --- | --- |
| Feed basket: feed items and their shares of the diet | Existing | Yes | Step 3 |
| Herd: number of animals per class, live weight, adult weight, weight gain, milk yield and composition, wool, work hours | Existing | Yes | Steps 3, 5 |
| Crop yields (main product and residue), fractions harvested, DM and ME content of feeds | Existing | Yes | Steps 3, 4 |
| **Region** (admin-1, chosen from a list) | **New** | Yes | Steps 2, 7 |
| **Irrigated yes/no for each crop** | **New** | Phase 2 only | Step 6 |
| Planting month and season length of each crop | Existing field, not used today | Optional | Step 2, Tier 2 |
| Grazing type of each pasture (communal rangeland, managed pasture, cut-and-carry) | New | Optional (default: from feed type) | Step 3 |
| Production system of each livestock class (grazing, mixed, industrial) | New | Phase 2, optional (default: mixed) | Step 6 |
| Site climate, measured evapotranspiration, local ME analyses, irrigation volume and method, farm-gate prices | New | Optional overrides | Steps 2–6, 12 |

### 4.2 Data i-CLEANED will provide

For every admin-1 region of the Global South (2,620 regions in 166 countries), i-CLEANED will provide the parameters below. Annex A gives sources, coverage and gaps.

- Monthly climate normals: precipitation, effective precipitation, reference evapotranspiration (FAO-56 Penman-Monteith) and temperature.
- Green and blue crop water use per hectare for 43 crops, rainfed and irrigated (Mialyk et al. 2024), and the link from every i-CLEANED crop to that dataset and to FAO-56.
- FAO-56 growth-stage lengths and crop coefficients.
- ME of the main products of crops that also supply residues (Feedipedia).
- Drinking and service water per livestock class and production system; irrigation efficiencies.
- Water availability (runoff plus groundwater recharge, and the share left after environmental flows) and the Aqueduct water stress class.

### 4.3 Checks before the calculation starts

The calculation will stop and ask the user for a value, instead of silently using zero, when:

- a crop residue is in the basket but the main-product yield of that crop is 0 or empty (a default from the crop table will be offered and flagged);
- an animal class with weight gain has an adult weight of 0 or empty (the heaviest adult weight of the same species in the herd will be offered and flagged);
- a feed has DM yield 0, unless it is a purchased feed (Section 6.3).

## 5. Step 2 – Green water use per hectare

For every crop, forage and pasture in the feed basket, i-CLEANED will compute GWU\_c: the rainwater evapotranspired by one hectare of that crop over its growing season in one year, in m³/ha. Green water is the part of crop evapotranspiration that rainfall can supply. It is therefore capped by rainfall, which is what distinguishes it from the crop's total water requirement (Hoekstra et al. 2011).

### 5.1 Choosing the data tier

Each crop will be computed with one of three tiers, chosen in this order:

1. **Tier 3, measured:** if the user enters measured evapotranspiration or a field water balance for the crop, that value is used.
2. **Tier 2, local FAO-56 water balance (Section 5.3):** if the user enters a planting month for the crop, or if the crop has no Tier 1 data. Forages, pastures and fodder trees (72 of the 131 crops in i-CLEANED) always use Tier 2.
3. **Tier 1, gridded data (Section 5.2):** in all other cases. This covers the 59 food and feed crops linked to the Mialyk et al. (2024) dataset, whether grown on the farm or purchased.

The tier is recorded for every feed and shown in the results. Tier 2 is the only tier that responds to a change of planting date, season length or climate, so scenario analyses on those variables must use it.

### 5.2 Tier 1: gridded crop water use

Mialyk et al. (2024) simulated the green and blue water use of 175 crops worldwide for 1990–2019 with a global crop model at 5 arc-minute resolution. i-CLEANED will provide their 2010–2019 averages for 43 crops, aggregated to each admin-1 region:

```latex
GWU_c = 10 \times CWU^{g}_{c,r}\qquad [\mathrm{m^3\,ha^{-1}\,yr^{-1}}]\qquad\text{(Eq. 1)}
```

where CWU^g\_c,r is the green crop water use of crop c in region r, in mm per season, taken from the rainfed column for rainfed crops and from the irrigated column for irrigated crops. If the crop is not grown in the region, the national mean is used, then the mean of the UN sub-region; both cases are flagged. Nineteen i-CLEANED crops have no exact match in the dataset and use the closest crop (e.g. oats use barley, cowpea uses beans, taro uses yams); these are flagged "proxy".

### 5.3 Tier 2: local FAO-56 monthly water balance

Tier 2 follows the single crop coefficient method of FAO-56 (Allen et al. 1998), computed day by day and summed by calendar month. It needs the crop's coefficients, its calendar and the monthly climate of the region.

**(a) Crop calendar.** The season starts on day 1 of the planting month *s* and lasts GP days.

- Planting month: the user's value. If none is entered, the **rainfall onset month**: the first month in which P\_m ≥ 0.5 ET0,m and the month before has P < 0.5 ET0. This is the FAO criterion for the start of the growing period. If every month is wet, or every month is dry, the month with the highest rainfall is used.
- Season length GP: the user's value; otherwise the median total length in FAO-56 Table 11 for that crop; otherwise 120 days.
- Both defaults are flagged. A season may run into the next calendar year; it is wrapped round to January.

**(b) Growth stages.** Stage lengths L\_ini, L\_dev, L\_mid and L\_late come from FAO-56 Table 11 for the crop. If they are not available, GP is split 15% / 30% / 35% / 20%, rounded to whole days (flagged).

**(c) Crop coefficient for each day.** The crop coefficient rises from Kc,ini to Kc,mid during development and falls to Kc,end during the late stage. For day *t* of the season (t = 1 … GP):

```latex
K_c(t)=\begin{cases}K_{c,ini} & t\le L_{ini}\\ K_{c,ini}+\dfrac{t-L_{ini}}{L_{dev}}\,(K_{c,mid}-K_{c,ini}) & L_{ini}<t\le L_{ini}+L_{dev}\\ K_{c,mid} & L_{ini}+L_{dev}<t\le L_{ini}+L_{dev}+L_{mid}\\ K_{c,mid}+\dfrac{t-(L_{ini}+L_{dev}+L_{mid})}{L_{late}}\,(K_{c,end}-K_{c,mid}) & t>L_{ini}+L_{dev}+L_{mid}\end{cases}\qquad\text{(Eq. 2)}
```

**(d) Monthly crop evapotranspiration.** Daily reference evapotranspiration is the monthly value divided by the days in the month. Crop evapotranspiration in month m adds up the daily values for the days of the season that fall in that month:

```latex
ET_{c,m}=\frac{ET_{0,m}}{N_m}\sum_{t\,\in\,m}K_c(t)\qquad[\mathrm{mm}]\qquad\text{(Eq. 3)}
```

Months outside the season have ETc,m = 0.

**(e) Effective precipitation.** Not all rainfall is available to the crop: part runs off or drains below the roots. Effective precipitation follows the USDA Soil Conservation Service method used in FAO CROPWAT (Smith 1992), applied to monthly totals in mm:

```latex
P_{eff,m}=\begin{cases}P_m\,\dfrac{125-0.2\,P_m}{125} & P_m\le 250\\[4pt] 125+0.1\,P_m & P_m>250\end{cases}\qquad\text{(Eq. 4)}
```

The regional values provided by i-CLEANED are computed grid cell by grid cell and then averaged, because Eq. 4 is not linear.

**(f) Green evapotranspiration.** In each month, the crop can use only the effective rain that falls while it is in the field. g\_m is the fraction of month m inside the season (days of the season in month m divided by N\_m):

```latex
ET_{g,m}=\min\left(ET_{c,m},\; g_m\,P_{eff,m}\right)\qquad[\mathrm{mm}]\qquad\text{(Eq. 5)}
```

If rain is short, the difference ETc,m − ETg,m is either supplied by irrigation (blue water, Section 9) or, on a rainfed field, not met. Rain beyond the crop's need is not counted.

**(g) Green water use per hectare.** Sum over the months and convert mm to m³/ha:

```latex
GWU_c=10\sum_{m=1}^{12}ET_{g,m}\qquad[\mathrm{m^3\,ha^{-1}\,yr^{-1}}]\qquad\text{(Eq. 6)}
```

**Annual simplification (only when monthly climate is not available).** If the user replaces the regional climate with annual site totals, the season-average coefficient is the stage-weighted mean of Eq. 2:

```latex
\bar K_c=\frac{K_{c,ini}L_{ini}+\tfrac{1}{2}(K_{c,ini}+K_{c,mid})L_{dev}+K_{c,mid}L_{mid}+\tfrac{1}{2}(K_{c,mid}+K_{c,end})L_{late}}{GP}\qquad\text{(Eq. 7)}
```

Then ETc = K̄c × ET0,annual × GP/365 and the green ET is min(ETc, Peff,annual × GP/365). This ignores the seasonality of rainfall, overstates green water in seasonal climates and is flagged.

### 5.4 Perennial forages, pastures and fodder trees

Perennials stay in the field all year, so GP = 12 months and g\_m = 1. Their activity follows the rains. A month counts as active when P\_m ≥ 0.5 ET0,m:

```latex
K_{c,m}=\begin{cases}K_{c,mid} & P_m\ge 0.5\,ET_{0,m}\ \text{(active)}\\ K_{c,ini} & \text{otherwise (dry-season cover)}\end{cases},\qquad ET_{c,m}=K_{c,m}\,ET_{0,m}\qquad\text{(Eq. 8)}
```

ETg,m and GWU then follow Eqs. 5 and 6. Where the user knows the sward is dormant and bare in some months, Kc,m = 0 for those months. Grazed pasture uses the FAO-56 Table 12 values for extensive grazing (0.30 / 0.75 / 0.75) or rotated grazing. Fodder trees, shrubs and cactus have no FAO-56 coefficient; until the team agrees values (Section 14), the coefficients stored in the i-CLEANED crop table are used and flagged "unverified".

**Other rules.** Two or more crops grown on the same land in one year are computed as separate seasons, each charged only to its own crop. Climate inputs must be long-term monthly means (at least 10 years, preferably a 30-year normal); one year's weather makes scenarios incomparable.

### 5.5 Worked example (Tier 2)

A rainfed maize crop is planted on 1 March for 120 days (to 28 June). Kc,ini = 0.30, Kc,mid = 1.20, Kc,end = 0.35. With the default fractions, the stages last 18, 36, 42 and 24 days. February is dry, so the onset rule also gives March. Regional climate (illustrative): ET0 = 150, 135, 120 and 114 mm and P = 80, 160, 90 and 20 mm in March to June.

| Month | Days in season | Mean Kc | ET0 (mm) | ETc, Eq. 3 (mm) | P (mm) | Peff, Eq. 4 (mm) | g\_m | g\_m × Peff (mm) | ETg, Eq. 5 (mm) | Not met by rain (mm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| March | 31 | 0.373 | 150 | 56.0 | 80 | 69.8 | 1.000 | 69.8 | 56.0 | 0 |
| April | 30 | 0.989 | 135 | 133.5 | 160 | 119.0 | 1.000 | 119.0 | 119.0 | 14.5 |
| May | 31 | 1.200 | 120 | 144.0 | 90 | 77.0 | 1.000 | 77.0 | 77.0 | 67.0 |
| June | 28 | 0.821 | 114 | 87.3 | 20 | 19.4 | 0.933 | 18.1 | 18.1 | 69.2 |
| **Total** | 120 |  |  | **420.8** |  |  |  |  | **270.2** | **150.7** |

GWU = 10 × 270.2 = **2,702 m³/ha** (Eq. 6). The crop's full water requirement would be 4,208 m³/ha; the 1,507 m³/ha not met by rain becomes blue water only if the crop is irrigated (Section 9). Check: the stage-weighted mean of Eq. 7 is 0.845, equal to the mean of the daily Kc values.

## 6. Step 3 – From hectares to the feed eaten

Step 2 gives water per hectare. The herd, however, eats tonnes of feed. Step 3 converts one into the other: water per hectare divided by the tonnes of that feed produced per hectare gives water per tonne of feed, which is then multiplied by the tonnes the herd eats.

### 6.1 General equation

First, the output per hectare of the product that feed *i* is made of:

| Feed type | Output O\_i (t DM/ha) | Allocation factor AF\_c,i |
| --- | --- | --- |
| Grain or other main product, residue also harvested | Y\_M × r\_M | AF\_c,M (Eq. 14) |
| Crop residue (stover, straw, haulms, vines) | Y\_R × r\_R | AF\_c,R (Eq. 13) |
| Main product, residue left in the field | Y\_M × r\_M | 1 |
| Cultivated forage cut and carried as the whole plant | Y × r | 1 |
| Grazed pasture (on-farm or communal) | Y × u | 1 |

(Eq. 9 is the output column of this table.) The green water charged to feed *i* is then:

```latex
G_i = DM_i\times\frac{GWU_c\times AF_{c,i}}{O_i}\qquad[\mathrm{m^3\,yr^{-1}}]\qquad\text{(Eq. 10)}
```

- DM\_i: tonnes of DM of feed i eaten by the herd in one year (from the feed basket and the herd's intake, as in i-CLEANED today);
- GWU\_c: green water per hectare of the crop the feed comes from (Step 2);
- AF\_c,i: the share of that crop's water allocated to this product (Step 4; 1 when the crop has a single product);
- O\_i: output of that product per hectare.

The ratio GWU\_c × AF\_c,i / O\_i is the **green water intensity** of the feed, in m³ per t DM. The land the herd needs for feed i is A\_i = DM\_i / O\_i (ha). Intercropped feeds use the same land-share correction as the i-CLEANED land requirement, so land and water stay consistent.

### 6.2 Grazed pasture: utilization

Grazing animals eat only part of the biomass a pasture grows; the rest is trampled, decays or remains as cover. The utilization fraction *u* is the share eaten. Because the whole sward evapotranspires, the water charged per tonne eaten rises as u falls: it is 1/u times the water per tonne grown.

- **Convention A (default): whole-sward attribution.** O = Y × u. All the green water of the land the herd needs is charged to the herd. This keeps water consistent with the land the herd occupies.
- **Convention B (sensitivity, for communal rangeland): eaten-only attribution.** O = Y. Only the water of the biomass eaten is charged, on the argument that uneaten vegetation would evapotranspire with or without livestock. B is reported beside A for communal rangeland.

Default utilization, pending field data (Section 14):

| Grazing type | Default u | Range for sensitivity |
| --- | --- | --- |
| Communal rangeland | 0.35 | 0.30–0.50 |
| Managed on-farm pasture | 0.60 | 0.50–0.75 |
| Cut-and-carry forage | 0.85 | 0.75–0.95 |

*Example.* A communal pasture grows Y = 5 t DM/ha with GWU = 4,000 m³/ha. Under convention A, O = 5 × 0.35 = 1.75 t DM/ha and the intensity is 4,000 / 1.75 = 2,286 m³ per t DM eaten. Under convention B it is 4,000 / 5 = 800 m³/t DM. A herd eating 10 t DM of this pasture is charged 22,857 m³ (A) or 8,000 m³ (B).

### 6.3 Purchased feed

Purchased feed did not grow under the farm's climate, so the farm's climate is never used for it.

1. **Single crop products with a known region of origin** (e.g. maize grain from another province): Tier 1 for the region of origin (Eq. 1), the crop-table yield for that crop, and the same allocation as for farm crops (Step 4).
2. **Origin unknown:** the farm's country is assumed and flagged.
3. **Compound concentrates and by-products without data:** excluded. The excluded share of the herd's dry-matter intake is reported with every result:

```latex
S_{excl}=\frac{\sum_{i\,\in\,excluded}DM_i}{\sum_i DM_i}\qquad\text{(Eq. 11)}
```

## 7. Step 4 – Allocation 1: main product and crop residue

When a crop yields both a main product (grain, pods, roots) and a residue that is fed (stover, straw, haulms), the water of the field will be split between them in proportion to the **metabolizable energy (ME)** each carries. The split is made once per crop and depends only on what the crop produces, not on which of the two products the herd happens to eat. Mass and economic allocation will be reported as sensitivity cases only.

### 7.1 Why metabolizable energy

ISO 14044 (ISO 2006, §4.3.4.2) sets the order of preference: avoid allocation; otherwise divide by a physical relationship; only then by another relationship such as economic value. Allocation cannot be avoided here, because grain and stover come from the same plants, and replacing the residue by a substitute (system expansion) needs a stable substitute that smallholder systems do not have. ME is the preferred physical basis because:

- **It reflects why the residue is valued:** in i-CLEANED the residue matters as feed energy, so each product is charged for the share of the crop's useful energy it carries.
- **It is stable:** unlike prices, ME does not change with markets, so results remain comparable between years and countries (Damerau 2024 recommends a biophysical basis; Nemecek and Thoma 2020).
- **It is consistent with Allocation 2,** which also uses feed energy (Section 8).
- **It needs no new data from the user:** ME per kg DM is already stored for every feed in i-CLEANED.

Mass allocation is not the default because it charges a bulky, low-energy residue with most of the field's water. Gross energy is not used because it is almost the same for grain and straw (about 18 MJ/kg DM), which would give nearly the mass result. Economic allocation needs farm-gate prices for residues, which are rarely available.

### 7.2 Equations

Harvested outputs per hectare:

```latex
M = Y_M\,r_M,\qquad R = Y_R\,r_R\qquad[\mathrm{t\,DM\,ha^{-1}}]\qquad\text{(Eq. 12)}
```

Allocation factors, with ME\_M and ME\_R in MJ/kg DM:

```latex
AF_{c,R}=\frac{R\,ME_R}{M\,ME_M+R\,ME_R}\qquad\text{(Eq. 13)}
```

```latex
AF_{c,M}=1-AF_{c,R}\qquad\text{(Eq. 14)}
```

Substituting into Eq. 10, the green water intensity of the residue (m³ per t DM) is:

```latex
WI_{c,R}=\frac{GWU_c\,AF_{c,R}}{R}=\frac{GWU_c\,ME_R}{M\,ME_M+R\,ME_R}\qquad\text{(Eq. 15)}
```

Sensitivity cases: mass, AF\_c,R = R / (M + R); economic, AF\_c,R = R p\_R / (M p\_M + R p\_R), with p the farm-gate price per t DM, only when the user enters prices.

### 7.3 Rules

1. **Source of ME.** The residue's ME is taken from the i-CLEANED feed table. The main product's ME is taken from the feed table when the main product is itself a listed feed; otherwise from the table of main-product ME that i-CLEANED will provide (Feedipedia values for ruminants; Annex A). Examples: maize grain 13.6, paddy rice 10.1, groundnut pods 18.2, cassava roots 12.4 MJ/kg DM. A local laboratory value always overrides a default.
2. **Main product without an ME value** (tomato fruits and whole sesame seeds at present): mass allocation is used for that crop and flagged until a value is supplied.
3. **Residue left in the field** (r\_R = 0): it is not an output and carries no water; AF\_c,M = 1.
4. **Closure.** For each crop AF\_c,M + AF\_c,R = 1 exactly. When grain and residue of the same crop are both in the basket, both refer to the same crop record so their factors are computed together and can never add up to more than 100% of the field's water.
5. **Missing main-product data.** If a residue is fed but the main-product yield or removal of that crop is 0 or empty, i-CLEANED will ask for them. If the user does not supply them, the crop-table yield and a removal of 1 are used and flagged. A residue is never given 100% of the field's water by default.
6. **Purchased residue** (e.g. bought straw): crop-table yields for the region of origin and the feed-table ME values.
7. **Same factors for blue water.** The factor belongs to the crop, so it is applied unchanged to irrigation water (Section 9).

### 7.4 Worked example

Maize with Y\_M = 1.06 and Y\_R = 2.69 t DM/ha, r\_M = 1.0 and r\_R = 0.7, so M = 1.06 and R = 1.883 t DM/ha (Eq. 12). ME from the i-CLEANED feed table: grain 13.5, stover 9.13 MJ/kg DM. GWU = 4,000 m³/ha (illustrative).

AF\_c,R = (1.883 × 9.13) / (1.06 × 13.5 + 1.883 × 9.13) = 17.19 / (14.31 + 17.19) = **0.55**, and AF\_c,M = 0.45. The stover then carries 4,000 × 0.546 / 1.883 = 1,159 m³ per t DM and the grain 4,000 × 0.454 / 1.06 = 1,714 m³ per t DM. Together, 1.883 t of stover and 1.06 t of grain carry exactly the 4,000 m³ of the hectare.

| Basis | AF\_c,R | Stover water intensity (m³/t DM) |
| --- | --- | --- |
| No allocation (all water to the residue) | 1.00 | 2,124 |
| Mass (sensitivity) | 0.64 | 1,360 |
| **ME (default)** | **0.55** | **1,159** |
| ME, low-quality stover (6.9 MJ/kg DM) | 0.48 | 1,011 |
| Economic, residue price 10% of grain (sensitivity) | 0.15 | 320 |

The basis changes the residue's water by a factor of up to four, which is why the basis and AF\_c,R will be reported with every result.

## 8. Step 5 – Herd total and Allocation 2: milk, meat, wool and draught

The green water of all feeds is added up for the herd, then divided among the herd's products in proportion to the **feed energy each product requires**. Each share is divided by the quantity of the product to give m³ per kg. The method needs no new input: i-CLEANED already computes every energy term to estimate feed requirements.

### 8.1 Why feed energy

Animals eat to meet their energy requirement, and the feed that supplies that energy is what carries the green water. Dividing water by the energy each function demands is therefore a causal, physical relationship, which ISO 14044 prefers to economic allocation. Mass does not work here, because a kilogram of milk, of live weight and of wool are not comparable. The approach is the same as the net-energy allocation of the dairy standard (IDF 2022), which replaced an earlier regression that gives negative factors for dual-purpose herds.

### 8.2 Energy required by each function

The daily net energy (NE, MJ per head per day) of each function follows IPCC (2019, Vol. 4, Ch. 10, Tier 2), the equations i-CLEANED already uses for feed requirements. For cattle and buffalo:

| Function | Equation | Terms |
| --- | --- | --- |
| Maintenance (17a) | NEm = Cf × W^0.75 | W live weight (kg); Cf by animal category (IPCC Table 10.4) |
| Activity (17b) | NEa = Ca × NEm | Ca = 0 stall-fed, 0.17 pasture, 0.36 large grazing areas |
| Growth (17c) | NEg = 22.02 × (BW / (C × MW))^0.75 × WG^1.097 | BW mean live weight, MW mature (adult) weight (kg); WG daily gain (kg/day); C = 0.8 females, 1.0 castrates, 1.2 bulls |
| Lactation (17d) | NEl = Milk × (1.47 + 0.40 × Fat) | Milk (kg/day); Fat (%) |
| Pregnancy (17e) | NEp = Cp × NEm | Cp = 0.10 for cattle, applied to the share of females pregnant |
| Work (17f) | NEwork = 0.10 × NEm × Hours | Hours of work per day |
| Wool (17g) | NEwool = EVwool × Prwool / 365 | EVwool = 24 MJ/kg; Prwool annual wool (kg) |

Sheep and goats use the IPCC equivalents (growth by Eq. 10.7 of IPCC 2019, with the species coefficients). Note that Eq. 17c divides by the mature weight MW: if MW is missing or zero the growth energy cannot be computed, so the check in Section 4.3 applies.

The annual energy of function f for the whole herd adds up all classes k, each with N\_k head:

```latex
E_f=\sum_k 365\times N_k\times NE_{k,f}\qquad[\mathrm{MJ\,yr^{-1}}]\qquad\text{(Eq. 16)}
```

### 8.3 Allocation factors and water footprint

Productive energy is assigned to products as follows; maintenance and activity are overhead and are shared in proportion to productive energy (they do not appear in the equation):

```latex
E_{milk}=E_l,\quad E_{meat}=E_g+E_p,\quad E_{wool}=E_{wool},\quad E_{draught}=E_{work}\qquad\text{(Eq. 18)}
```

```latex
AF_j=\frac{E_j}{E_{milk}+E_{meat}+E_{wool}+E_{draught}},\qquad \sum_j AF_j=1\qquad\text{(Eq. 19)}
```

```latex
G_{herd}=\sum_i G_i\qquad\text{(Eq. 20)}
```

```latex
WF_j=\frac{AF_j\times G_{herd}}{Q_j}\qquad[\mathrm{m^3\ green\ per\ kg\ of\ }j]\qquad\text{(Eq. 21)}
```

Growth of replacement animals counts towards meat: in a steady-state herd, net live-weight output equals the animals that leave the herd.

### 8.4 Product quantities Q\_j

| Product | Q\_j | How it is calculated |
| --- | --- | --- |
| Milk | kg FPCM/yr | Eq. 22 below, from milk yield, fat % and true protein % |
| Meat | kg live weight/yr | Σ\_k N\_k × annual weight gain of class k (steady state); carcass weight reported as a derived figure |
| Wool | kg greasy wool/yr | Σ\_k N\_k × annual wool of class k |
| Edible protein | kg protein/yr | Protein in milk plus protein in meat; its water is (AF\_milk + AF\_meat) × G\_herd, so wool and draught water are not charged to food |

```latex
FPCM = Milk\times(0.1226\,F + 0.0776\,P_{true} + 0.2534)\qquad\text{(Eq. 22; IDF 2022)}
```

with Milk in kg, F the fat content (%) and P\_true the true protein content (%). If only crude protein is recorded, it must be converted to true protein before use.

### 8.5 Rules

1. **Pregnancy** is charged to meat, because the foetus becomes the calf. A sensitivity case charges it to milk, since in dairy herds pregnancy is a precondition of lactation.
2. **Manure** receives no share. It is an internal flow to the farm's crops; giving it water would count that water twice.
3. **Product not produced:** if Q\_j = 0 then E\_j = 0 and AF\_j = 0, and the result says "not produced" instead of 0 or infinity.
4. **Dairy comparison:** for herds selling milk and meat, AF\_milk from Eq. 19 is reported beside the IDF (2022) net-energy value (Eq. 23, coefficients to be checked against IDF Bulletin 520 †). A difference above 0.10 is flagged for review.
5. **No double counting:** Σ\_j AF\_j × G\_herd = G\_herd. The same cubic metre is never charged to two products.

```latex
AF_{milk}^{IDF}=\frac{NE_L\,M_{milk}}{NE_L\,M_{milk}+NE_G\,M_{meat}}\qquad\text{(Eq. 23)}
```

### 8.6 Worked example

A herd of one improved cow and two growing steers (the Study\_1 farm, Section 16): E\_milk = 6,811 MJ/yr and E\_meat = 4,506 MJ/yr; no wool or draught.

- AF\_milk = 6,811 / (6,811 + 4,506) = **0.60**; AF\_meat = **0.40** (Eq. 19).
- G\_herd = 3,092 m³ (Eq. 20); FPCM = 2,280 kg/yr; live weight output = 250 kg/yr.
- WF\_milk = 0.60 × 3,092 / 2,280 = **0.82 m³/kg FPCM**; WF\_meat = 0.40 × 3,092 / 250 = **4.92 m³/kg live weight** (Eq. 21).
- Check: 0.816 × 2,280 + 4.92 × 250 = 1,861 + 1,231 = 3,092 m³, the herd total, so no water is counted twice.

## 9. Step 6 – Blue water (phase 2)

Blue water is surface or groundwater **consumed**: evaporated, built into the product or not returned to the same catchment in the same period (Hoekstra et al. 2011; ISO 2014). It is counted as consumption, not withdrawal. It has three parts, each reported separately and never added to green water: irrigation of feed crops, drinking water and service water. It needs one more user input: whether each crop is irrigated.

### 9.1 Irrigation of feed crops

**Tier 1 (default for the 59 linked crops):**

```latex
BWU_c=10\times CWU^{b,irr}_{c,r}\qquad[\mathrm{m^3\,ha^{-1}\,yr^{-1}}]\qquad\text{(Eq. 24)}
```

where CWU^b,irr is the blue water use of irrigated crop c in region r from Mialyk et al. (2024), in mm per season.

**Tier 2 (forages and any crop with a user calendar):** the part of crop evapotranspiration not met by effective rain, from the same monthly balance as green water (Section 5.3):

```latex
ET_{b,m}=\max\left(0,\;ET_{c,m}-g_m\,P_{eff,m}\right),\qquad BWU_c=10\sum_m ET_{b,m}\qquad\text{(Eq. 25)}
```

Eq. 25 assumes the crop receives all the water it needs. Smallholders often irrigate less. When the user enters the volume applied I (m³/ha/yr) and the method, the consumed volume is capped:

```latex
BWU_c=\min\left(10\sum_m ET_{b,m},\; e_a\times I\right)\qquad\text{(Eq. 26)}
```

where e\_a is the field application efficiency: surface 0.60, sprinkler 0.75, drip 0.90 (Brouwer et al. 1989, Annex 1, Table 8). In the worked example of Section 5.5, an irrigated maize crop would consume BWU = 1,507 m³/ha; if the farmer applied only 2,000 m³/ha by furrow, the cap would be 0.60 × 2,000 = 1,200 m³/ha.

Blue water per feed then follows Eq. 10 with BWU in place of GWU, using the **same** Allocation 1 and Allocation 2 factors.

Rules: rice uses its existing rice-ecosystem field (irrigated or rainfed) instead of a second question; purchased feed uses Tier 1 for the region of origin weighted by the irrigated share of that crop there; the monthly balance is required, because an annual balance hides the dry-season deficit, which is when irrigation happens.

### 9.2 Drinking water

```latex
B_{drink}=\sum_k 365\times N_k\times WR_k\,/\,1000\qquad[\mathrm{m^3\,yr^{-1}}]\qquad\text{(Eq. 27)}
```

WR\_k is drinking water per head per day (L) for class k and its production system, from Chapagain and Hoekstra (2003, Table 3.8), as used by Mekonnen and Hoekstra (2010). Examples:

| Livestock class | Grazing | Mixed (default) | Industrial |
| --- | --- | --- | --- |
| Dairy cow | 40 | 55 | 70 |
| Heifer or steer, 1–3 years | 24 | 36 | 48 |
| Calf, under 1 year | 11 | 12.5 | 14 |
| Adult sheep | 6.0 | 6.8 | 7.6 |
| Adult goat | 3.5 | 3.65 | 3.8 |
| Adult pig | 8 | 11 | 14 |

(L per head per day.) All drinking water counts as consumed, as in Mekonnen and Hoekstra (2010); water excreted is not subtracted. Feed moisture is not subtracted either, because these are free-water values. Example: 10 dairy cows in a mixed system drink 10 × 55 × 365 / 1000 = 201 m³/yr.

Optional Tier 2 for cattle: published equations predicting intake from dry-matter intake, milk yield and temperature (Meyer et al. 2004 for dairy cows; Winchester and Morris 1956 for beef cattle †), after checking them for tropical breeds.

### 9.3 Service water

```latex
B_{service}=\sum_k 365\times N_k\times SW_k\,/\,1000 \;+\; 0.5\times C_{conc}\,/\,1000\qquad\text{(Eq. 28)}
```

SW\_k is service water (cleaning, cooling) per head per day from Chapagain and Hoekstra (2003, Table 3.9), e.g. 5 L for a dairy cow in grazing systems, 13.5 L in mixed and 22 L in industrial systems. The second term is feed-mixing water, 0.5 L per kg of concentrate fed (C\_conc, kg/yr); it is about 0.03% of the total and may be omitted if declared.

### 9.4 Herd total and allocation

```latex
B_{herd}=\sum_i B_i+B_{drink}+B_{service},\qquad WF_{b,j}=\frac{AF_j\times B_{herd}}{Q_j}\qquad\text{(Eq. 29)}
```

Reported: total blue water split into irrigation, drinking and service; the monthly irrigation profile; and blue water per kg FPCM, per kg live weight and per kg wool.

**Capillary rise.** Mialyk et al. (2024) count water rising from shallow groundwater into the root zone as blue water, even in rainfed crops. Because nobody abstracts it, it will be reported as a separate line and not added to B\_herd, pending a team decision (Section 14). Rainwater harvested in ponds or pans is runoff, so it counts as blue water when used.

## 10. Step 7 – Local water availability and stress

The same volume of blue water matters more in a dry basin than in a wet one (Boulay et al. 2021). Following Damerau (2024), i-CLEANED will report two context indicators for the farm's region. They are shown beside the footprint and are not multiplied into it.

### 10.1 Water stress class (qualitative)

The baseline water stress of WRI Aqueduct 4.0 (Kuzma et al. 2023) is the ratio of water withdrawals to available renewable water in each river basin. i-CLEANED will report the area-weighted class of the basins in the farm's region:

| Class | Withdrawals as % of available water |
| --- | --- |
| Low | < 10% |
| Low–medium | 10–20% |
| Medium–high | 20–40% |
| High | 40–80% |
| Extremely high | > 80% |
| Arid and low water use | Reported as a separate share of the region, not scored |

Aqueduct gives arid, low-use basins the maximum score; they are kept as their own category so deserts are not labelled "extremely high stress". Annual and monthly classes are available.

### 10.2 Sustainable water availability (quantitative)

Total renewable water in a grid cell and month is surface runoff plus groundwater recharge, both from the WaterGAP 2.2e global hydrological model averaged over 1990–2019 (Müller Schmied et al. 2023):

```latex
TWA_m = q_{s,m}+q_{r,m}\qquad[\mathrm{mm\,month^{-1}}]\qquad\text{(Eq. 30)}
```

Part of that water must stay in rivers for ecosystems. The environmental flow requirement (EFR) follows the Variable Monthly Flow method (Pastor et al. 2014), as applied by Rosa et al. (2018). With MAF the mean of the twelve monthly values of TWA in the cell:

```latex
EFR_m=\begin{cases}0.60\,TWA_m & TWA_m\le 0.4\,MAF\ \text{(low-flow month)}\\ 0.45\,TWA_m & 0.4\,MAF<TWA_m\le 0.8\,MAF\\ 0.30\,TWA_m & TWA_m>0.8\,MAF\ \text{(high-flow month)}\end{cases}\qquad\text{(Eq. 31)}
```

```latex
SWA = 10\sum_{m=1}^{12}\left(TWA_m-EFR_m\right)\qquad[\mathrm{m^3\,ha^{-1}\,yr^{-1}}]\qquad\text{(Eq. 32)}
```

SWA is computed per grid cell and averaged over the region. Across all regions it is on average 67.5% of TWA. Damerau (2024) multiplied TWA by 0.45; that factor is the average share **reserved** for the environment, not the share available, so it is kept only as a comparison column.

The herd's use is compared with the sustainable availability of the land it occupies:

```latex
RWD=\frac{B_{herd}\,/\,\sum_i A_i}{SWA}\qquad\text{(Eq. 33)}
```

where Σ A\_i is the feed area (Section 6.1). RWD = 0.10 means the herd's blue water equals 10% of the water that can be used sustainably on its land. Damerau's ratio uses crop irrigation only; drinking and service water are added here because they draw on the same resource. No threshold is set in this version. The monthly AWARE factors (Boulay et al. 2018) can be reported as an optional third indicator for comparison with life cycle assessment studies.

*Example (Study\_1):* B\_herd = 57 m³, feed area 0.705 ha, SWA = 1,945 m³/ha/yr: RWD = (57 / 0.705) / 1,945 = 0.04; Aqueduct class low–medium.

## 11. Step 8 – Indicators and reporting rules

i-CLEANED will report the indicators below. Blue-water indicators appear in phase 2 and have the same form.

| Indicator | Unit | Definition |
| --- | --- | --- |
| Total green water of the enterprise | m³/yr | G\_herd (Eq. 20) |
| Green water per hectare of feed land | m³/ha/yr | G\_herd / Σ A\_i |
| Green water per feed item | m³/yr and % of total | G\_i (Eq. 10) |
| Green water footprint of milk | m³/kg FPCM | WF\_milk (Eq. 21) |
| Green water footprint of meat | m³/kg live weight | WF\_meat (Eq. 21) |
| Green water footprint of wool; of edible protein | m³/kg | Eq. 21; Section 8.4 |
| Green water productivity | kg FPCM/m³; kg live weight/m³ | Q\_j / (AF\_j × G\_herd), the form required by FAO (2019) |
| Share of effective rainfall used for feed | % | Σ ETg over the feed land / Σ Peff over the same land and months; never above 100% |
| Excluded share of intake | % | S\_excl (Eq. 11) |
| Water stress class; RWD | class; ratio | Section 10 (phase 2) |

**Metadata reported with every result:**

- Allocation 1: basis (ME by default), ME values and AF\_c,R for each crop.
- Allocation 2: AF\_j for every product, and the IDF comparison value for dairy herds.
- Utilization u for each pasture and the attribution convention (A or B).
- Data tier of each feed, and the share of G\_herd from each tier.
- Climate source and period; whether the annual simplification was used.
- Every default used and every value the user overwrote, with its data-quality flag (Section 12).

**Never:** add green, blue and grey water together; compare a Tier 1 result with a Tier 2 result without the tier label; report a per-product figure without its allocation factor.

## 12. Data quality, sensitivity and validation

In data-scarce systems defaults dominate the result, so every result will show how much it depends on them.

**Data-quality flag.** Every default carries one of three labels: *verified* (traced to a cited source for the region), *assumed* (expert judgement, or transferred from another region or crop) or *unverified* (origin unknown). The result reports the share of G\_herd that depends on assumed or unverified values.

**Mandatory one-at-a-time sensitivity.** Each parameter below is set to its low and high value while all others stay at default, and the change in WF\_milk and WF\_meat is reported:

| Parameter | Low | Default | High | Expected effect |
| --- | --- | --- | --- | --- |
| Pasture utilization u (communal rangeland) | 0.30 | 0.35 | 0.50 | Water per kg eaten ∝ 1/u |
| Residue ME | −20% | Feed table | +20% | Moderate (Section 7.4) |
| Feed yield Y | −30% | User value | +30% | Water per kg ∝ 1/Y |
| Growth-stage lengths | FAO-56 Table 11 | Default fractions | Mid-season ±20% | Small to moderate |
| Effective rainfall method | 80% of P | USDA-SCS (Eq. 4) | FAO dependable rain | Moderate in dry months |
| Pregnancy energy | To milk | To meat | – | Shifts AF\_milk |
| Allocation 1 basis | Economic (if prices) | ME | Mass | Large (Section 7.4) |
| Attribution convention (communal rangeland) | B | A | – | Large (factor 1/u) |

**Optional Monte Carlo.** Where ranges exist, draw at least 1,000 values from triangular distributions (low, default, high) and report the median and the 5th–95th percentile range.

**Validation before any published result.**

1. Hand-calculate one complete case and compare it with the tool's output; differences must be explained to the last cubic metre.
2. Run at least two contrasting case studies: one rainfed (Study\_1, Section 16) and one with irrigated fodder (to be chosen, Section 14).
3. Compare results with published ranges for similar systems (Mekonnen and Hoekstra 2012) and explain any deviation larger than a factor of two.

## 13. Changes from the current i-CLEANED method

The table compares the current i-CLEANED water calculation (as described in the v1.1 proposal and in Damerau 2024) with this methodology. The last column says what data each change needs: **P** = provided by i-CLEANED, **U** = entered by the user.

| Component | Current i-CLEANED | This methodology | Justification | Data needed |
| --- | --- | --- | --- | --- |
| What is reported | One "water use" figure equal to the crop water requirement; no green/blue split | Green and blue reported separately, never added (Sections 5, 9) | Only blue water is competed for; the two differ physically (Hoekstra et al. 2011; Boulay et al. 2021; Damerau 2024) | – |
| Crop coefficient | Unweighted mean of the three Kc values | Daily FAO-56 Kc curve (Eq. 2) | FAO-56 defines Kc by growth stage; the mean gives the short initial and late stages too much weight | P: stage lengths (FAO-56 Table 11) |
| Period counted | Annual ET0 for 12 months, for every crop | Growing season only, month by month (Eq. 3) | Annual crops grow 3–5 months; fallow ET is not caused by the crop | U (optional): planting month and season length; otherwise defaults |
| Green water | Crop ET not capped by rainfall, i.e. a water requirement | Green = min(crop ET, effective rain) (Eqs. 4–6) | Definition of green water in the Water Footprint Assessment Manual (Hoekstra et al. 2011) | P: monthly P, Peff, ET0 per region |
| Units | mm × ha reported as m³ | ×10 conversion (Eq. 6) | 1 mm over 1 ha = 10 m³ | – |
| Data sources | Local Kc calculation only | Three tiers: measured, local FAO-56, gridded Mialyk et al. 2024 (Section 5.1) | Gridded per-hectare values let the user's own yield enter (Damerau 2024); the iCLEANED Workshop 2026 asked for field data plus gridded defaults | P: Mialyk per region and crop link; U: region |
| Main crop vs residue | Mass share, applied twice in per-feed results; a residue with no main yield takes 100% | One ME-based split per crop, closing to 100% (Section 7) | ISO 14044 physical basis; consistent with Allocation 2; avoids double counting | P: ME of main products |
| Grazed pasture | Removal fraction 0.9 treated as utilization | Utilization u with realistic defaults and two attribution conventions (Section 6.2) | Grazing animals eat 30–50% of rangeland biomass; the result scales with 1/u | U (optional): grazing type, local u |
| Purchased feed | Farm climate applied; concentrates count as zero | Tier 1 for the region of origin, or a declared, quantified exclusion (Section 6.3) | Water belongs to where the feed grew (ISO 2014) | U (optional): region of origin |
| Milk, meat, wool | Total water divided by each product separately, so the same water is counted two or three times | Feed-energy allocation that sums to 100% (Section 8) | Causal, physical (ISO 14044); matches IDF (2022); recommended by Damerau (2024) | None (energy terms already computed) |
| Reference units | FAO/GLEAM FPCM; carcass weight | IDF 2022 FPCM; live weight output; wool (Section 8.4) | Comparability with the dairy standard | – |
| Blue water: irrigation | Not calculated, except rice | Tier 1 or monthly deficit, optional volume cap (Section 9.1) | Hoekstra et al. 2011; Damerau 2024; needed for irrigation scenarios | U: irrigated yes/no; P: efficiencies |
| Blue water: drinking | A fixed undocumented value per animal type (e.g. 140 L/day per cow), not used | Published values by class and production system (Section 9.2) | Drinking is most blue water in rainfed systems (Mekonnen and Hoekstra 2010); the old values are 2–3 times published drinking water | P: Chapagain and Hoekstra table; U (optional): system |
| Blue water: service | None | Per head per day plus feed mixing (Section 9.3) | Mekonnen and Hoekstra 2010 | P |
| Local context | None | Aqueduct stress class and RWD with environmental flows (Section 10) | A volume is not an impact without availability (Boulay et al. 2018, 2021; Damerau 2024) | P: Aqueduct, WaterGAP |
| Growth energy check | Growth energy silently set to 0 when adult weight is 0 | Input check (Section 4.3) | Without it, meat receives no water and feed requirements are understated | U: adult weight |
| Uncertainty | Not reported | Flags, mandatory sensitivity, optional Monte Carlo (Section 12) | Defaults dominate in data-scarce systems (v1.1; Damerau 2024) | – |

## 14. Decisions pending and the defaults used until then

None of these items stops the calculation: each has a default that is flagged in the results until the team decides.

| Decision | Default until decided | Why it matters |
| --- | --- | --- |
| Pasture utilization defaults | 0.35 / 0.60 / 0.85 (Section 6.2) | The most sensitive default: moving from 0.9 to 0.35 multiplies pasture water per kg by about 2.6 |
| Crop coefficients for 19 fodder trees and shrubs, and cactus | Coefficients in the i-CLEANED crop table, flagged unverified | No FAO-56 values exist; the stored values differ between databases, and the cactus value (Kc,mid 1.15) is implausible for a plant that saves water |
| ME for tomato fruits and whole sesame seeds | Mass allocation for those crops | No published value |
| Default data tier | Tier 1 for the 59 linked crops, Tier 2 for forages and pastures (Section 5.1) | Tier 1 needs no planting date; Tier 2 responds to scenarios |
| Production system of each livestock class | Mixed | Selects drinking and service water |
| Capillary rise | Reported separately, not added to blue water | Mialyk et al. (2024) count it as blue water |
| Purchased feed in phase 1 | Tier 1 where data exist, otherwise excluded (iCLEANED Workshop 2026: "on-farm only?") | Can be a large share of intake in dairy systems |
| Climate normals | WorldClim 2.1, 1970–2000 | A 1991–2020 normal (TerraClimate or CHIRPS) would match the other datasets better |
| Second validation case | Not chosen | Irrigated systems are untested |
| Livestock and crop proxies (buffalo, lambs, kids, growers; oats, lentils, cowpea, taro and others) | Current mappings, flagged assumed | Expert review needed |
| True or crude protein in the milk records | Treated as true protein | FPCM (Eq. 22) needs true protein |

## 15. Limitations

- **No soil-water carry-over.** Each month is computed on its own (Eq. 5), so rain stored at the end of the wet season and used early in the dry season is missed; green water is underestimated for deep-rooted perennials. An FAO-56 soil water balance is the upgrade path.
- **No water-stress coefficient.** Under drought, actual evapotranspiration can fall below min(ETc, Peff).
- **Fallow excluded.** FAO (2019) may require evapotranspiration between harvests to be included †. This is a declared deviation.
- **Inventory, not impact.** Whether natural vegetation would have used the same rain is addressed only through convention B; no consensus factor exists for green water scarcity (Boulay et al. 2021).
- **One climate per enterprise:** the regional mean unless site data are entered. Large or mountainous regions hide local gradients, and distant communal grazing may have a different climate.
- **Different periods:** climate normals 1970–2000, Mialyk 2010–2019 and WaterGAP 1990–2019.
- **Tier 1 green/blue split is approximate:** the public Mialyk data give total water use per system; green irrigated is taken as the smaller of rainfed and irrigated use, and blue as the difference (Mekonnen and Hoekstra 2011). Rainfed green includes capillary rise, below 1% nationally for most crops.
- **Environmental flows on local runoff:** the Variable Monthly Flow method was designed for river discharge; applying it to runoff and recharge per grid cell is an approximation.
- **Purchased compound feed** without data is outside the boundary (reported as S\_excl).
- **Limited validation so far:** one rainfed farm (Section 16).

## 16. Illustration on the Study\_1 example farm

The method was tested by hand and in a prototype on Study\_1, the i-CLEANED example farm "Rungwe" (Mbeya region, Tanzania): one improved dairy cow producing 2,135 kg milk/yr and two improved steers gaining 125 kg each, all rainfed. The feed basket is commercial concentrate, natural pasture, Napier grass, lablab forage and groundnut residue.

| Feed | Tier | Intake (t DM/yr) | GWU (m³/ha) | AF | Output (t DM/ha) | Green water (m³/yr) |
| --- | --- | --- | --- | --- | --- | --- |
| Commercial concentrate | Excluded (no data) | 0.68 | – | – | – | 0 |
| Groundnut residue | Tier 1 | 0.28 | 5,834 | 0.60 (ME) | 1.86 | 536 |
| Lablab forage | Tier 2, 110 days from December | 3.01 | 3,225 | 1 | 10.8 | 898 |
| Natural pasture | Tier 2, perennial | 1.03 | 4,895 | 1 | 11.3 | 443 |
| Napier grass | Tier 2, perennial | 2.03 | 6,591 | 1 | 11.0 | 1,214 |
| **Herd total** |  | 7.03 |  |  |  | **3,092** |

Groundnut residue AF (Eq. 13): pods 0.56 t × 18.2 MJ and haulms 1.86 t × 8.4 MJ give AF\_R = 15.6 / (10.2 + 15.6) = 0.60. Allocation 2 and the per-product results are worked in Section 8.6.

| Indicator | Current i-CLEANED | This methodology |
| --- | --- | --- |
| Total water | 733 labelled m³ (really mm × ha, about 7,300 m³) | 3,092 m³ green; 57 m³ blue (drinking 46, service 10) |
| Milk | 0.32 per kg FPCM, all water to milk | 0.82 m³ green per kg FPCM (AF 0.60) |
| Meat | 5.98 per kg carcass, all water again to meat | 4.92 m³ green per kg live weight (AF 0.40) |
| Concentrate | Silently zero | 9.7% of intake reported as excluded |
| Local context | – | Aqueduct low–medium; RWD 0.04 |

The results move in opposite directions: the unit correction multiplies the current value by 10, while the rainfall cap, the growing-season limit and the end of double counting reduce it. The test also revealed defaults that had to be applied: the groundnut main yield was missing (crop-table default 0.56 t DM/ha used), and the steers' adult weight was 0 (600 kg used, Section 4.3). Using the default utilization of 0.35 instead of the farm's 0.9 would raise pasture water about 2.6 times.

## Annex A. Parameters i-CLEANED will host

i-CLEANED will host the following tables so that users do not have to find these values. Spatial tables cover 2,620 GADM 4.1 admin-1 regions in 166 countries of the Global South (all countries of Africa, Latin America and the Caribbean, Asia and Oceania except Australia, New Zealand, Japan, the Republic of Korea, Israel, Cyprus, Singapore, Taiwan, Hong Kong and Macao). All tables have been built from public sources and can be regenerated.

| Table | Parameters | Unit | Used in | Source | Coverage and gaps |
| --- | --- | --- | --- | --- | --- |
| Regions | Region list and area | km² | Region input | GADM 4.1 | 12 small territories have no admin-1 units |
| Climate | Monthly P, Peff, ET0 (FAO-56 Penman-Monteith), mean and maximum temperature | mm/month, °C | Eqs. 3–5, 8, 25 | WorldClim 2.1, 10′, 1970–2000 (Fick and Hijmans 2017) | All regions; 4 small islands use the country mean |
| Crop water use | Green rainfed, green irrigated and blue irrigated water use; national capillary-rise share | mm/season | Eqs. 1, 24 | Mialyk et al. (2024), 2010–2019 | 43 crops; missing region–crop pairs use country or sub-region means (flagged) |
| Crop link | Each of 131 i-CLEANED crops → Mialyk crop (direct or proxy) and FAO-56 entry | – | Section 5.1 | This work, after Mialyk et al. (2024) and Damerau (2024) | 59 crops Tier 1 (40 direct, 19 proxy); 72 Tier 2 |
| Main-product ME | ME for ruminants of 31 main products, with DM and standard deviation | MJ/kg DM | Eq. 13 | Feedipedia (INRAE, CIRAD, AFZ, FAO) | 27 direct, 2 proxy; tomato fruits and whole sesame seeds missing |
| FAO-56 Table 11 | Growth-stage lengths by crop and region | days | Eq. 2 | Allen et al. (1998) | 167 rows |
| FAO-56 Table 12 | Kc ini, mid, end, including grazing pasture | – | Eqs. 2, 8 | Allen et al. (1998) | 129 rows |
| Livestock water | Drinking and service water for 22 i-CLEANED livestock classes × 3 production systems; feed-mixing water | L/head/day | Eqs. 27–28 | Chapagain and Hoekstra (2003), Tables 3.8–3.9 | Buffalo, lambs, kids and growers use assumed mappings |
| Irrigation efficiency | Field application and conveyance efficiency | % | Eq. 26 | Brouwer et al. (1989), Annex 1, Tables 7–8 | – |
| Water availability | Monthly runoff + recharge, recharge alone, sustainable availability after environmental flows; Damerau's formula for comparison | m³/ha | Eqs. 30–33 | WaterGAP 2.2e, 1990–2019 (Müller Schmied et al. 2023) | 60 small islands or coastal regions filled from neighbouring cells or the country mean |
| Water stress | Baseline stress score and class, annual and monthly; share arid and low water use | – | Section 10.1 | WRI Aqueduct 4.0 (Kuzma et al. 2023) | 171 regions use the nearest basin |

**Notes on the build.** WorldClim was used because TerraClimate could not be reached; the build can switch source. The Mialyk files were taken from Internet Archive copies of the 4TU repository while it was offline and must be re-checked against 4TU before publication. Effective rainfall was computed per grid cell before averaging, because Eq. 4 is not linear.

## References

Items marked † must have the exact clause or value checked against the original before the methodology is finalized.

- Allen RG, Pereira LS, Raes D, Smith M (1998) Crop evapotranspiration: guidelines for computing crop water requirements. FAO Irrigation and Drainage Paper 56. FAO, Rome.
- Boulay AM, Bare J, Benini L et al. (2018) The WULCA consensus characterization model for water scarcity footprints: assessing impacts of water consumption based on available water remaining (AWARE). International Journal of Life Cycle Assessment 23:368–378.
- Boulay AM, Drastig K, Amanullah et al. (2021) Building consensus on water use assessment of livestock production systems and supply chains: outcome and recommendations from the FAO LEAP Partnership. Ecological Indicators 129:107988.
- Brouwer C, Prins K, Heibloem M (1989) Irrigation water management: irrigation scheduling. Training Manual No. 4. FAO, Rome. Annex 1, Tables 7–8 (efficiencies verified).
- Chapagain AK, Hoekstra AY (2003) Virtual water flows between nations in relation to trade in livestock and livestock products. Value of Water Research Report Series No. 13. UNESCO-IHE, Delft. Tables 3.8–3.9.
- Damerau K (2024) Adapting i-CLEANED for evaluating freshwater depletion and water quality impacts of livestock systems. Final report for the Tropical Forages Program, Alliance of Bioversity International and CIAT, 27 December 2024.
- FAO (2016a) Environmental performance of animal feeds supply chains: guidelines for assessment. LEAP Partnership. FAO, Rome. † (allocation of feed co-products)
- FAO (2016b) Environmental performance of large ruminant supply chains: guidelines for assessment. LEAP Partnership. FAO, Rome.
- FAO (2019) Water use in livestock production systems and supply chains: guidelines for assessment, version 1. LEAP Partnership. FAO, Rome. † (accounting period, reporting form)
- Fick SE, Hijmans RJ (2017) WorldClim 2: new 1-km spatial resolution climate surfaces for global land areas. International Journal of Climatology 37:4302–4315.
- Feedipedia (2012–2024) Animal feed resources information system. INRAE, CIRAD, AFZ and FAO. https://www.feedipedia.org (datasheets cited by node in main\_product\_me.csv; accessed 8 October 2026).
- GADM (2022) Database of Global Administrative Areas, version 4.1. University of California, Berkeley.
- Hoekstra AY, Chapagain AK, Aldaya MM, Mekonnen MM (2011) The water footprint assessment manual: setting the global standard. Earthscan, London.
- IDF (2022) The IDF global carbon footprint standard for the dairy sector. Bulletin of the IDF 520/2022. Brussels. † (net-energy allocation coefficients, FPCM)
- IPCC (2019) 2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories, Vol. 4, Ch. 10. IPCC, Geneva.
- ISO (2006) ISO 14044:2006 Life cycle assessment: requirements and guidelines. ISO, Geneva.
- ISO (2014) ISO 14046:2014 Water footprint: principles, requirements and guidelines. ISO, Geneva.
- Kuzma S, Bierkens MFP, Lakshman S et al. (2023) Aqueduct 4.0: updated decision-relevant global water risk indicators. Technical Note. World Resources Institute, Washington, DC.
- Mekonnen MM, Hoekstra AY (2010) The green, blue and grey water footprint of farm animals and animal products. Value of Water Research Report Series No. 48. UNESCO-IHE, Delft.
- Mekonnen MM, Hoekstra AY (2011) The green, blue and grey water footprint of crops and derived crop products. Hydrology and Earth System Sciences 15:1577–1600.
- Mekonnen MM, Hoekstra AY (2012) A global assessment of the water footprint of farm animal products. Ecosystems 15:401–415.
- Meyer U, Everinghoff M, Gädeken D, Flachowsky G (2004) Investigations on the water intake of lactating dairy cows. Livestock Production Science 90:117–121. † (coefficients)
- Mialyk O, Schyns JF, Booij MJ, Su H, Hogeboom RJ, Berger M (2024) Water footprints and crop water use of 175 individual crops for 1990–2019 simulated with a global crop model. Scientific Data 11:206. Data: doi:10.4121/7b45bcc6-686b-404d-a910-13c87156716a.
- Müller Schmied H, Träutlein T, Ackermann S et al. (2023) The global water resources and use model WaterGAP v2.2e: description and evaluation of modifications and new features. Geoscientific Model Development Discussions, preprint.
- Nemecek T, Thoma G (2020) Allocation between milk and meat in dairy LCA: critical discussion of the International Dairy Federation's standard methodology. 12th International Conference on Life Cycle Assessment of Food (LCA Food 2020), Berlin (virtual).
- Nemecek T, Roesch A, Bystricky M et al. (2024) Swiss agricultural life cycle assessment: a method to assess the emissions and environmental impacts of agricultural systems and products. International Journal of Life Cycle Assessment 29:433–455.
- Pastor AV, Ludwig F, Biemans H, Hoff H, Kabat P (2014) Accounting for environmental flow requirements in global water assessments. Hydrology and Earth System Sciences 18:5041–5059.
- Rosa L, Rulli MC, Davis KF et al. (2018) Closing the yield gap while ensuring water sustainability. Environmental Research Letters 13:104002.
- Smith M (1992) CROPWAT: a computer program for irrigation planning and management. FAO Irrigation and Drainage Paper 46. FAO, Rome.
- Thoma G, Jolliet O, Wang Y (2013) A biophysical approach to allocation of life cycle environmental burdens for fluid milk supply chain analysis. International Dairy Journal 31:S41–S49.
- Winchester CF, Morris MJ (1956) Water intake rates of cattle. Journal of Animal Science 15:722–740. † (coefficients)
