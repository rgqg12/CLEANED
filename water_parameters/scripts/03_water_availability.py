"""Monthly freshwater availability per admin-1 unit (Damerau 2024, Sections 5.2.2 and 8.3.2).

Source : WaterGAP 2.2e, ISIMIP3a, gswp3-w5e5, obsclim, histsoc, default, 0.5 deg, monthly 1901-2019
         (Mueller Schmied et al. 2023): qs = surface runoff, qr = groundwater recharge (kg m-2 s-1).
Method : 30-year monthly means 1990-2019; kg m-2 s-1 x seconds per month = mm per month;
         TotWatAvail = qs + qr; 1 mm = 10 m3/ha.
         Environmental flow requirement (EFR) per cell and month by the Variable Monthly Flow method
         (Pastor et al. 2014), as used by Rosa et al. (2018): EFR = 60% of flow in low-flow months
         (mean monthly flow <= 40% of mean annual flow), 30% in high-flow months (> 80%), 45% otherwise.
         SustWatAvail = TotWatAvail x (1 - EFR)  (Rosa et al. 2018: environmental flows are subtracted).
         RenWatAvail_Damerau keeps the Damerau (2024) formula for comparison; it reduces to
         0.45 x TotWatAvail, i.e. the average EFR share, not the available share.
Zonal  : area-weighted mean per admin-1 unit (exact coverage fractions).
Output : tables/water_availability_admin1_monthly.csv (m3/ha per month) and annual totals.
"""
import numpy as np
import xarray as xr
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from exactextract import exact_extract
from common import RAW, TABLES, ADMIN1, MONTH_DAYS

RENEWABLE_FACTOR = 0.25 * 0.30 + 0.50 * 0.45 + 0.25 * 0.60   # = 0.45, as written in Damerau (2024)

clim = {}
for v in ("qs", "qr"):
    d = xr.open_dataset(RAW / "wg" / f"{v}.nc", decode_times=False)[v]
    sel = d.isel(time=slice((1990 - 1901) * 12, (2019 - 1901 + 1) * 12))     # Jan 1990 - Dec 2019
    mm = sel.values.reshape(30, 12, *sel.shape[1:]) * (np.array(MONTH_DAYS) * 86400.0)[None, :, None, None]
    clim[v] = np.nanmean(mm, axis=0)                                       # (12, lat, lon) mm/month
    lat, lon = d.lat.values, d.lon.values

tot = clim["qs"] + clim["qr"]
maf = np.nanmean(tot, axis=0, keepdims=True)                       # mean monthly flow over the year
efr = np.where(tot <= 0.4 * maf, 0.60, np.where(tot > 0.8 * maf, 0.30, 0.45))
sust = tot * (1.0 - efr)
prof = dict(driver="GTiff", height=len(lat), width=len(lon), count=36, dtype="float64", crs="EPSG:4326",
            transform=from_origin(lon.min() - 0.25, lat.max() + 0.25, 0.5, 0.5), nodata=np.nan)
tmp = RAW / "wg_derived.tif"
with rasterio.open(tmp, "w", **prof) as dst:
    for m in range(12):
        dst.write(tot[m] * 10.0, m + 1)                 # m3/ha
        dst.write(clim["qr"][m] * 10.0, m + 13)
        dst.write(sust[m] * 10.0, m + 25)

adm = gpd.read_file(ADMIN1)
res = exact_extract(str(tmp), adm, "mean", include_cols=["GID_1"], output="pandas")
res["fill_method"] = "zonal_mean"
# Small islands and coastal units without a 0.5-degree land cell: use the mean of the cells within
# a 0.5-degree, then 1-degree, buffer (flagged in fill_method).
for buf in (0.5, 1.0):
    miss = res.band_1_mean.isna()
    if not miss.any():
        break
    sub = adm[miss.values].copy()
    sub["geometry"] = sub.geometry.buffer(buf)
    alt = exact_extract(str(tmp), sub, "mean", include_cols=["GID_1"], output="pandas").set_index("GID_1")
    idx = res.index[miss]
    for c in [c for c in res.columns if c.startswith("band_")]:
        res.loc[idx, c] = res.loc[idx, "GID_1"].map(alt[c]).values
    res.loc[idx[res.loc[idx, "band_1_mean"].notna()], "fill_method"] = f"buffer_{buf}deg"
res.loc[res.band_1_mean.isna(), "fill_method"] = "no_data"
rows = []
for m in range(12):
    t = res[f"band_{m + 1}_mean"]
    rows.append(res[["GID_1", "fill_method"]].assign(month=m + 1,
                                      TotWatAvail_m3_ha=t,
                                      GWrecharge_m3_ha=res[f"band_{m + 13}_mean"],
                                      SustWatAvail_m3_ha=res[f"band_{m + 25}_mean"],
                                      RenWatAvail_Damerau_m3_ha=t * RENEWABLE_FACTOR))
import pandas as pd
out = pd.concat(rows).sort_values(["GID_1", "month"])
out.to_csv(TABLES / "water_availability_admin1_monthly.csv", index=False, float_format="%.1f")
ann = out.groupby("GID_1")[["TotWatAvail_m3_ha", "GWrecharge_m3_ha", "SustWatAvail_m3_ha", "RenWatAvail_Damerau_m3_ha"]].sum(min_count=1).reset_index()
ann.to_csv(TABLES / "water_availability_admin1_annual.csv", index=False, float_format="%.0f")
print(ann.describe().round(0)); print("missing:", ann.TotWatAvail_m3_ha.isna().sum())
