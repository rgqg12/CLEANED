"""FAO-56 Table 11 (growth-stage lengths) and Table 12 (single crop coefficients), parsed from the
FAO online edition of Allen et al. (1998), Chapter 6 (https://www.fao.org/4/X0490E/x0490e0b.htm).

Cleaning: footnote markers that the HTML appends to names (e.g. "Crucifers1") and to two-decimal
Kc values (e.g. "1.052" = 1.05 with footnote 2) are removed; ranges such as "0.85-1.05" and
alternatives such as "50/30" are kept as text, with numeric midpoints added.
Output : tables/fao56_table11_stage_lengths.csv, tables/fao56_table12_kc.csv
"""
import io
import re
import pandas as pd
from common import RAW, TABLES

html = open(RAW / "fao56" / "x0490e0b.htm", encoding="latin-1").read()
# footnote markers are <SUP> tags inside table cells; drop them (units such as m s<SUP>-1</SUP> are not in these tables)
html = re.sub(r"<sup>\s*\d+\s*</sup>", "", html, flags=re.I)
tabs = pd.read_html(io.StringIO(html))


def clean_name(s):
    return re.sub(r"(?<=[A-Za-z\)])\d+$", "", str(s)).strip() if pd.notna(s) else s


def clean_kc(s):
    if pd.isna(s):
        return s
    s = str(s).strip()
    return re.sub(r"^(\d\.\d\d)\d$", r"\1", s)        # 1.052 -> 1.05 (footnote digit)


def midpoint(s):
    if pd.isna(s):
        return None
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", str(s))]
    return sum(nums) / len(nums) if nums else None


# ---- Table 11: stage lengths -------------------------------------------------------------------
t11 = tabs[0].iloc[1:].copy()
t11.columns = ["crop", "_dup", "L_ini", "L_dev", "L_mid", "L_late", "L_total", "plant_date", "region"]
t11 = t11.drop(columns="_dup")
is_group = t11.crop.eq(t11.L_ini)
t11["group"] = t11.crop.where(is_group).ffill()
t11 = t11[~is_group]
t11["crop"] = t11.crop.map(clean_name)
for c in ["L_ini", "L_dev", "L_mid", "L_late", "L_total"]:
    t11[f"{c}_days"] = t11[c].map(midpoint)
# Some footnote digits are not in <SUP> tags (e.g. "103" = 10 + footnote 3). Where dropping the last
# digit of a stage length brings the stage sum closer to the stated total, apply it and flag the row.
stages = ["L_ini_days", "L_dev_days", "L_mid_days", "L_late_days"]
t11["note"] = ""
for i, r in t11.iterrows():
    for c in stages:
        v = r[c]
        if v and v >= 100:
            trial = r[stages].copy()
            trial[c] = v // 10
            if abs(trial.sum() - r.L_total_days) < abs(r[stages].sum() - r.L_total_days):
                t11.at[i, c] = v // 10
                t11.at[i, c.replace("_days", "")] = str(int(v // 10))
                t11.at[i, "note"] = f"footnote digit removed from {c.replace('_days', '')}"
t11["stage_sum_matches_total"] = (t11[stages].sum(axis=1) - t11.L_total_days).abs() <= 10
t11["source"] = "FAO-56 Table 11 (Allen et al. 1998)"
t11[["group", "crop", "L_ini", "L_dev", "L_mid", "L_late", "L_total",
     "L_ini_days", "L_dev_days", "L_mid_days", "L_late_days", "L_total_days",
     "plant_date", "region", "stage_sum_matches_total", "note", "source"]].to_csv(TABLES / "fao56_table11_stage_lengths.csv", index=False)

# ---- Table 12: Kc ------------------------------------------------------------------------------
t12 = tabs[1].iloc[1:].copy()
t12.columns = ["crop", "subtype", "Kc_ini", "Kc_mid", "Kc_end", "max_height_m"]
is_group = t12.crop.eq(t12.subtype) & t12.crop.str.match(r"^[a-p]\. ", na=False)
t12["group"] = t12.crop.where(is_group).ffill()
grp_kc_ini = t12.Kc_ini.where(is_group).ffill()           # group-level Kc_ini applies to members
t12["crop"] = t12.crop.ffill()
t12 = t12[~is_group].copy()
t12["Kc_ini"] = t12.Kc_ini.fillna(grp_kc_ini[~is_group])
t12["subtype"] = t12.apply(lambda r: None if r.subtype == r.crop else r.subtype, axis=1)
t12 = t12[~(t12[["Kc_ini", "Kc_mid", "Kc_end"]].isna().all(axis=1))]
t12 = t12[~t12.Kc_ini.astype(str).str.match(r"^[a-p]\. ")]      # sub-group header rows
t12["crop"] = t12.crop.map(clean_name)
t12["subtype"] = t12.subtype.map(clean_name)
for c in ["Kc_ini", "Kc_mid", "Kc_end"]:
    t12[c] = t12[c].map(clean_kc)
    t12[f"{c}_value"] = t12[c].map(midpoint)
t12["source"] = "FAO-56 Table 12 (Allen et al. 1998); Kc_mid/Kc_end for sub-humid climate (RHmin 45%, u2 2 m/s)"
t12[["group", "crop", "subtype", "Kc_ini", "Kc_mid", "Kc_end", "Kc_ini_value", "Kc_mid_value",
     "Kc_end_value", "max_height_m", "source"]].to_csv(TABLES / "fao56_table12_kc.csv", index=False)
print(len(t11), "stage-length rows;", len(t12), "Kc rows")
