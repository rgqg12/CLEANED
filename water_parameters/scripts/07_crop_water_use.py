"""Tier 1 crop water use per admin-1 unit: green and blue, rainfed and irrigated, 43 crops.

Source : Mialyk et al. (2024), dataset 2.9 "Global gridded crop water use of 43 selected crops"
         (cwu_{crop}_average_2010_2019.nc; 5 arcmin; mm per growing season; layers cwu_rainfed,
         cwu_irrigated, harvested-area-weighted 2010-2019 means), doi:10.4121/7b45bcc6-686b-404d-a910-13c87156716a
         (CC BY 4.0). Retrieved from the Internet Archive copy of the 4TU file (snapshot 2025-11-07)
         while 4TU storage was under maintenance; file size identical to the 4TU listing (82.7 MB).
Split  : dataset 2.9 gives total water use per production system only. Green and blue are derived as
         in Mekonnen and Hoekstra (2011), as described by Damerau (2024, Section 3.1):
           green_rainfed  = CWU_rainfed               (includes capillary rise; see cr_share_national)
           green_irrigated = min(CWU_rainfed, CWU_irrigated)
           blue_irrigated  = CWU_irrigated - green_irrigated
         i.e. blue water is the extra evapotranspiration made possible by irrigation.
Zonal  : area-weighted mean over the grid cells where the crop is simulated (cells without the crop are
         NaN in the source); harvested-area weighting is not possible with dataset 2.9 alone.
Fallback where a region has no simulated cell for a crop: country mean, then UN sub-region mean
         (unweighted mean of admin-1 values), recorded in source_level.
Output : tables/crop_water_use_admin1.csv (mm per season)
"""
import re
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from exactextract import exact_extract
from common import RAW, TABLES, ADMIN1

MI = RAW / "mialyk"
adm = gpd.read_file(ADMIN1)
regions = pd.read_csv(TABLES / "admin1_regions.csv")[["GID_1", "GID_0", "un_subregion"]]

# national capillary-rise share, for transparency on the rainfed "green" value
nat = pd.read_csv(MI / "national_wf_2010_2019.csv", skiprows=3)
nat["cr_share_national"] = nat.wfb_cr_m3_t / nat.wf_tot_m3_t
nat["crop_key"] = nat.crop_name.str.lower()

rows = []
for f in sorted((MI / "nc").glob("cwu_*_average_2010_2019.nc")):
    crop = re.sub(r"^cwu_|_average_2010_2019\.nc$", "", f.name)
    d = xr.open_dataset(f)
    title = d.attrs.get("title", "")
    fao_code = int(re.search(r"FAO code: (\d+)", title).group(1)) if "FAO code" in title else None
    lat = d.lat.values
    res = abs(lat[1] - lat[0])
    prof = dict(driver="GTiff", height=d.sizes["lat"], width=d.sizes["lon"], count=2, dtype="float32",
                crs="EPSG:4326", transform=from_origin(-180.0, 90.0, res, res), nodata=np.nan, compress="deflate")
    tif = RAW / "mialyk_tmp.tif"
    with rasterio.open(tif, "w", **prof) as dst:
        for b, v in enumerate(["cwu_rainfed", "cwu_irrigated"], start=1):
            a = d[v].values.astype("float32")
            a[(a > 1e19) | (a < 0)] = np.nan
            if lat[0] < lat[-1]:
                a = a[::-1]
            dst.write(a, b)
    ex = exact_extract(str(tif), adm, ["mean", "count"], include_cols=["GID_1"], output="pandas")
    ex = ex.rename(columns={"band_1_mean": "cwu_rainfed_mm", "band_2_mean": "cwu_irrigated_mm",
                            "band_1_count": "cells_rainfed", "band_2_count": "cells_irrigated"})
    ex["crop"] = crop
    ex["faostat_code"] = fao_code
    rows.append(ex)
    print(crop, int(ex.cwu_rainfed_mm.notna().sum()), "regions with rainfed values")

cwu = pd.concat(rows, ignore_index=True).merge(regions, on="GID_1")
cwu["source_level"] = np.where(cwu.cwu_rainfed_mm.notna() | cwu.cwu_irrigated_mm.notna(), "admin1", None)

# fallbacks: country mean, then UN sub-region mean
for level, key in (("country_mean", "GID_0"), ("subregion_mean", "un_subregion")):
    for col in ("cwu_rainfed_mm", "cwu_irrigated_mm"):
        means = cwu.groupby(["crop", key])[col].transform("mean")
        fill = cwu[col].isna() & means.notna()
        cwu.loc[fill & cwu.source_level.isna(), "source_level"] = level
        cwu.loc[fill, f"{col}_filled_from"] = level
        cwu.loc[fill, col] = means[fill]

cwu["green_rainfed_mm"] = cwu.cwu_rainfed_mm
cwu["green_irrigated_mm"] = np.fmin(cwu.cwu_rainfed_mm, cwu.cwu_irrigated_mm)
cwu["blue_irrigated_mm"] = (cwu.cwu_irrigated_mm - cwu.green_irrigated_mm).clip(lower=0)

cwu = cwu.merge(nat[["country_iso3", "crop_code", "cr_share_national"]],
                left_on=["GID_0", "faostat_code"], right_on=["country_iso3", "crop_code"], how="left") \
         .drop(columns=["country_iso3", "crop_code"])

cols = ["GID_1", "crop", "faostat_code", "cwu_rainfed_mm", "cwu_irrigated_mm", "green_rainfed_mm",
        "green_irrigated_mm", "blue_irrigated_mm", "cr_share_national", "cells_rainfed", "cells_irrigated",
        "source_level", "cwu_rainfed_mm_filled_from", "cwu_irrigated_mm_filled_from"]
cwu = cwu[cols].sort_values(["GID_1", "crop"])
cwu.to_csv(TABLES / "crop_water_use_admin1.csv", index=False, float_format="%.1f")
print(cwu.source_level.value_counts(dropna=False))
