"""Fill admin-1 units that have no value in the climate and water-availability tables (small islands
without a land grid cell) with the country mean, then the UN sub-region mean; flagged in fill_method.
Run after 02_climate.py and 03_water_availability.py.
"""
import pandas as pd
from common import TABLES

reg = pd.read_csv(TABLES / "admin1_regions.csv")[["GID_1", "GID_0", "un_subregion"]]


def fill(df, keys, value_cols):
    df = reg.merge(df, on="GID_1", how="left") if "month" not in df else df.merge(reg, on="GID_1", how="left")
    if "fill_method" not in df:
        df["fill_method"] = "zonal_mean"
    for level, k in (("country_mean", "GID_0"), ("subregion_mean", "un_subregion")):
        for c in value_cols:
            m = df.groupby([k, *keys])[c].transform("mean")
            idx = df[c].isna() & m.notna()
            df.loc[idx, c] = m[idx]
            df.loc[idx, "fill_method"] = level
    return df


# climate: rebuild the full GID_1 x month grid first (units with no land cell are absent)
clim = pd.read_csv(TABLES / "climate_admin1_monthly.csv")
grid = reg[["GID_1"]].merge(pd.DataFrame({"month": range(1, 13)}), how="cross")
clim = grid.merge(clim, on=["GID_1", "month"], how="left")
clim = fill(clim, ["month"], ["P_mm", "Peff_mm", "ET0_mm", "Tmean_C", "Tmax_C"])
clim[["GID_1", "month", "P_mm", "Peff_mm", "ET0_mm", "Tmean_C", "Tmax_C", "fill_method"]] \
    .to_csv(TABLES / "climate_admin1_monthly.csv", index=False, float_format="%.1f")

wa = pd.read_csv(TABLES / "water_availability_admin1_monthly.csv")
wa.loc[wa.fill_method == "no_data", "fill_method"] = None
vals = ["TotWatAvail_m3_ha", "GWrecharge_m3_ha", "SustWatAvail_m3_ha", "RenWatAvail_Damerau_m3_ha"]
wa = fill(wa.drop(columns="fill_method").assign(fill_method=wa.fill_method.fillna("zonal_mean").where(wa.fill_method.notna() | wa.TotWatAvail_m3_ha.notna(), None)), ["month"], vals)
wa[["GID_1", "fill_method", "month", *vals]].to_csv(TABLES / "water_availability_admin1_monthly.csv", index=False, float_format="%.1f")
ann = wa.groupby("GID_1")[vals].sum(min_count=1).reset_index()
ann.to_csv(TABLES / "water_availability_admin1_annual.csv", index=False, float_format="%.0f")

print("climate missing:", clim.P_mm.isna().sum(), "| availability missing:", wa.TotWatAvail_m3_ha.isna().sum())
print(clim.drop_duplicates("GID_1").fill_method.value_counts(dropna=False))
print(wa.drop_duplicates("GID_1").fill_method.value_counts(dropna=False))
