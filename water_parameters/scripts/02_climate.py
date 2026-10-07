"""Monthly climate normals per admin-1 unit: P, Peff, ET0 (FAO-56 Penman-Monteith), Tmean, Tmax.

Source : WorldClim 2.1, 10 arc-minute, 1970-2000 normals (Fick and Hijmans 2017):
         prec (mm), tmin/tmax/tavg (degC), srad (kJ m-2 day-1), wind (m s-1 at 10 m),
         vapr (kPa, actual vapour pressure), elev (m).
Method : ET0 by FAO-56 Eq. 6 with monthly data (Allen et al. 1998, Ch. 3-4): Ra from latitude and
         mid-month day of year (Eqs. 21-25), Rso (Eq. 37), Rns with albedo 0.23 (Eq. 38),
         Rnl (Eq. 39), monthly soil heat flux G = 0.07 (T[m+1] - T[m-1]) (Eq. 43),
         wind adjusted from 10 m to 2 m (Eq. 47).
         Peff by USDA-SCS per grid cell, then averaged (Smith 1992).
Zonal  : area-weighted mean per admin-1 unit with exact cell coverage fractions (exactextract).
Output : tables/climate_admin1_monthly.csv
"""
import numpy as np
import pandas as pd
import rasterio
import geopandas as gpd
from exactextract import exact_extract
from common import RAW, TABLES, ADMIN1, MONTH_DAYS, MID_MONTH_DOY, peff_usda_scs

WC = RAW / "wc"


def read(var, m=None):
    name = f"wc2.1_10m_{var}.tif" if m is None else f"wc2.1_10m_{var}_{m:02d}.tif"
    with rasterio.open(WC / name) as r:
        a = r.read(1).astype("float64")
        a[a == r.nodata] = np.nan
        return a, r.profile


elev, prof = read("elev")
h, w = elev.shape
t = prof["transform"]
lat = np.deg2rad(t.f + t.e * (np.arange(h) + 0.5))[:, None] * np.ones((1, w))

P_atm = 101.3 * ((293.0 - 0.0065 * elev) / 293.0) ** 5.26          # Eq. 7
gamma = 0.000665 * P_atm                                           # Eq. 8
sigma = 4.903e-9                                                   # MJ K-4 m-2 day-1


def e0(T):
    return 0.6108 * np.exp(17.27 * T / (T + 237.3))                # Eq. 11


tavg = [read("tavg", m)[0] for m in range(1, 13)]
layers = {}
for i, m in enumerate(range(1, 13)):
    tmin, tmax, T = read("tmin", m)[0], read("tmax", m)[0], tavg[i]
    rs = read("srad", m)[0] / 1000.0                               # MJ m-2 day-1
    u2 = read("wind", m)[0] * 4.87 / np.log(67.8 * 10 - 5.42)      # Eq. 47
    ea = read("vapr", m)[0]
    prec = read("prec", m)[0]

    J = MID_MONTH_DOY[i]
    dr = 1 + 0.033 * np.cos(2 * np.pi * J / 365)                   # Eq. 23
    dec = 0.409 * np.sin(2 * np.pi * J / 365 - 1.39)               # Eq. 24
    ws = np.arccos(np.clip(-np.tan(lat) * np.tan(dec), -1, 1))     # Eq. 25
    Ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.sin(ws))
    Rso = (0.75 + 2e-5 * elev) * Ra                                # Eq. 37
    ratio = np.clip(np.where(Rso > 0, rs / Rso, 0.5), 0.3, 1.0)
    Rns = 0.77 * rs                                                # Eq. 38
    Rnl = sigma * ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2 * (0.34 - 0.14 * np.sqrt(np.maximum(ea, 0))) * (1.35 * ratio - 0.35)
    Rn = Rns - Rnl
    G = 0.07 * (tavg[(i + 1) % 12] - tavg[i - 1])                  # Eq. 43
    es = (e0(tmax) + e0(tmin)) / 2
    delta = 4098 * e0(T) / (T + 237.3) ** 2                        # Eq. 13
    et0 = (0.408 * delta * (Rn - G) + gamma * 900 / (T + 273) * u2 * np.maximum(es - ea, 0)) / (delta + gamma * (1 + 0.34 * u2))
    et0 = np.maximum(et0, 0) * MONTH_DAYS[i]

    layers[(m, "P_mm")] = prec
    layers[(m, "Peff_mm")] = peff_usda_scs(prec)
    layers[(m, "ET0_mm")] = et0
    layers[(m, "Tmean_C")] = T
    layers[(m, "Tmax_C")] = tmax

# write a multiband in-memory raster for exactextract
keys = list(layers)
prof.update(count=len(keys), dtype="float64", nodata=np.nan)
tmp = RAW / "wc_derived.tif"
with rasterio.open(tmp, "w", **prof) as dst:
    for b, k in enumerate(keys, start=1):
        dst.write(layers[k], b)
        dst.set_band_description(b, f"{k[1]}_{k[0]:02d}")

adm = gpd.read_file(ADMIN1)
res = exact_extract(str(tmp), adm, "mean", include_cols=["GID_1"], output="pandas")
res = res.rename(columns={f"band_{b}_mean": f"{k[1]}|{k[0]}" for b, k in enumerate(keys, start=1)})
long = res.melt(id_vars="GID_1", var_name="band", value_name="value")
long[["var", "month"]] = long.band.str.split("|", expand=True)
long["month"] = long.month.astype(int)
out = long.pivot_table(index=["GID_1", "month"], columns="var", values="value").reset_index()
out = out[["GID_1", "month", "P_mm", "Peff_mm", "ET0_mm", "Tmean_C", "Tmax_C"]]
out.to_csv(TABLES / "climate_admin1_monthly.csv", index=False, float_format="%.1f")
print(out.groupby("GID_1")[["P_mm", "ET0_mm"]].sum().describe())
print("units without data:", out[out.P_mm.isna()].GID_1.nunique())
