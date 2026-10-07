"""Baseline water stress per admin-1 unit, annual and monthly (Damerau 2024, Sections 5.1 and 8.3.1).

Source : WRI Aqueduct 4.0, baseline (1979-2019), HydroBASINS level 6 (Kuzma et al. 2023).
Method : intersect admin-1 units with sub-basins (equal-area projection); area-weighted mean of
         bws_score (0-5; Aqueduct scores "arid and low water use" basins as 5, kept as in source;
         "no data" basins excluded); category from the weighted score using Aqueduct's score bands;
         share of area per category reported so a mixed unit is visible.
Output : tables/water_stress_admin1_annual.csv, tables/water_stress_admin1_monthly.csv
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from common import RAW, TABLES, ADMIN1

AQ = RAW / "aq" / "Aqueduct40_waterrisk_download_Y2023M07D05"
LABELS = ["Low (<10%)", "Low - Medium (10-20%)", "Medium - High (20-40%)", "High (40-80%)", "Extremely High (>80%)"]


def cat_from_score(s):
    return pd.cut(s, [-0.001, 1, 2, 3, 4, 5.001], labels=LABELS, right=False)


basins = gpd.read_file(AQ / "GDB" / "Aq40_Y2023D07M05.gdb", layer="baseline_monthly")
monthly_cols = [f"bws_{m:02d}_score" for m in range(1, 13)]
monthly_cats = [f"bws_{m:02d}_cat" for m in range(1, 13)]
basins = basins[["pfaf_id", *monthly_cols, *monthly_cats, "geometry"]]
ann = pd.read_csv(AQ / "CVS" / "Aqueduct40_baseline_annual_y2023m07d05.csv",
                  usecols=["pfaf_id", "bws_score", "bws_cat"]).drop_duplicates("pfaf_id")
basins = basins.merge(ann, on="pfaf_id", how="left")

adm = gpd.read_file(ADMIN1)[["GID_1", "geometry"]]
ea = "+proj=cea"
inter = gpd.overlay(adm.to_crs(ea), basins.to_crs(ea), how="intersection", keep_geom_type=True)
inter["a"] = inter.area


def wmean(df, col, catcol):
    # exclude "no data" (-9999) and "arid and low water use" (-1, scored 5 by Aqueduct) basins
    d = df[(df[col] >= 0) & (df[catcol] >= 0)]
    return (d[col] * d.a).sum() / d.a.sum() if d.a.sum() > 0 else np.nan


rows = []
for gid, g in inter.groupby("GID_1"):
    tot = g.a.sum()
    r = {"GID_1": gid, "bws_score": wmean(g, "bws_score", "bws_cat"),
         "share_arid_low_use": g.loc[g.bws_cat == -1, "a"].sum() / tot,
         "share_no_data": g.loc[g.bws_cat == -9999, "a"].sum() / tot}
    for k, lab in enumerate(LABELS):
        r[f"share_cat{k}"] = g.loc[g.bws_cat == k, "a"].sum() / tot
    rows.append(r)
annual = pd.DataFrame(rows)
annual["fill_method"] = "area_weighted"

# Units with no intersecting basin or only "no data" basins (mostly small islands and coastal slivers):
# take the nearest basin with data, flagged.
valid = basins[(basins.bws_score >= 0) & (basins.bws_cat >= 0)].to_crs(ea)
has_info = annual.bws_score.notna() | (annual.share_arid_low_use > 0)   # fully arid units keep their class
missing = adm[~adm.GID_1.isin(annual.loc[has_info, "GID_1"])].to_crs(ea)
near = gpd.sjoin_nearest(missing.assign(geometry=missing.representative_point()), valid, how="left")
near = near.drop_duplicates("GID_1")
fill = pd.DataFrame({"GID_1": near.GID_1, "bws_score": near.bws_score, "fill_method": "nearest_basin"})
annual = pd.concat([annual[has_info], fill], ignore_index=True)
annual["bws_category"] = cat_from_score(annual.bws_score).astype(object)
annual.loc[annual.share_arid_low_use > 0.5, "bws_category"] = "Arid and Low Water Use"
annual.to_csv(TABLES / "water_stress_admin1_annual.csv", index=False, float_format="%.3f")

mrows = []
for gid, g in inter.groupby("GID_1"):
    for m, c in enumerate(monthly_cols, start=1):
        share_arid = g.loc[g[monthly_cats[m - 1]] == -1, "a"].sum() / g.a.sum()
        mrows.append({"GID_1": gid, "month": m, "bws_score": wmean(g, c, monthly_cats[m - 1]), "share_arid_low_use": share_arid})
inter_ids = set(annual.loc[annual.fill_method == "area_weighted", "GID_1"])
mrows = [r for r in mrows if r["GID_1"] in inter_ids]
for _, r in near.iterrows():
    for m, c in enumerate(monthly_cols, start=1):
        mrows.append({"GID_1": r.GID_1, "month": m, "bws_score": r[c] if r[monthly_cats[m - 1]] >= 0 else np.nan,
                      "share_arid_low_use": float(r[monthly_cats[m - 1]] == -1)})
monthly = pd.DataFrame(mrows)
monthly = monthly.sort_values("bws_score", na_position="first").drop_duplicates(["GID_1", "month"], keep="last")
monthly = monthly.sort_values(["GID_1", "month"])
monthly["bws_category"] = cat_from_score(monthly.bws_score).astype(object)
monthly.loc[monthly.share_arid_low_use > 0.5, "bws_category"] = "Arid and Low Water Use"
monthly.to_csv(TABLES / "water_stress_admin1_monthly.csv", index=False, float_format="%.3f")

print(annual.bws_category.value_counts(dropna=False))
print("units without basins:", len(adm) - annual.GID_1.nunique())
