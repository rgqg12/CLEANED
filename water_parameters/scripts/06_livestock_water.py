"""Drinking and service water per animal per day, and their mapping to i-CLEANED livestock types.

Source : Chapagain and Hoekstra (2003), Value of Water Research Report 13, Tables 3.8 (drinking) and
         3.9 (service), litre/animal/day, industrial and grazing systems; mixed = mean of the two
         (as in the source). These are the values used by Mekonnen and Hoekstra (2010, Appendix IV).
         Ranges (e.g. "26-70") are entered as their midpoint.
Feed mixing water: 0.5 L per kg concentrate (Chapagain and Hoekstra 2003; Mekonnen and Hoekstra 2010).
Output : tables/livestock_water_source_table.csv, tables/livestock_water_icleaned.csv
"""
import pandas as pd
from common import TABLES

# category, age group, drinking industrial, drinking grazing, service industrial, service grazing (L/head/day)
SRC = [
    ("Beef cattle", "Young calves", "5", "5", "2", "0"),
    ("Beef cattle", "Adult cows", "38", "22", "11", "5"),
    ("Dairy cattle", "Calves, 0-1 yr", "5-23", "4-18", "0", "0"),
    ("Dairy cattle", "Heifers, 1-3 yr", "26-70", "18-30", "11", "4"),
    ("Dairy cattle", "Milking cows, 3-10 yr", "70", "40", "22", "5"),
    ("Swine", "Piglet", "1.8", "1.8", "5", "0"),
    ("Swine", "Adult", "14", "8", "50", "25"),
    ("Sheep", "5 lbs lamb", "0.38", "0.30", "2", "0"),
    ("Sheep", "Adult", "7.6", "6.0", "5", "5"),
    ("Goats", "5 lbs kid", "0.38", "0.30", "0", "0"),
    ("Goats", "Adult", "3.8", "3.5", "5", "5"),
    ("Broiler chicken", "Chick", "0.02", "0.02", "0.01", "0.01"),
    ("Broiler chicken", "Adult", "0.18", "0.18", "0.09", "0.09"),
    ("Laying hens", "Chick", "0.02", "0.02", "0.01", "0.01"),
    ("Laying hens", "Laying eggs", "0.30", "0.30", "0.15", "0.15"),
    ("Horses", "Foal", "3", "3", "0", "5"),
    ("Horses", "Mature horse", "45", "45", "5", "5"),
]


def mid(s):
    a = [float(x) for x in s.split("-")]
    return sum(a) / len(a)


src = pd.DataFrame(SRC, columns=["category", "age_group", "drink_industrial_txt", "drink_grazing_txt",
                                 "service_industrial_txt", "service_grazing_txt"])
for k in ("drink", "service"):
    src[f"{k}_industrial_L_d"] = src[f"{k}_industrial_txt"].map(mid)
    src[f"{k}_grazing_L_d"] = src[f"{k}_grazing_txt"].map(mid)
    src[f"{k}_mixed_L_d"] = (src[f"{k}_industrial_L_d"] + src[f"{k}_grazing_L_d"]) / 2
src["source"] = "Chapagain and Hoekstra (2003), Tables 3.8-3.9"
src.to_csv(TABLES / "livestock_water_source_table.csv", index=False)

# i-CLEANED livestock type -> source row(s); several are assumptions and flagged as such
MAP = [
    ("Cattle - Cows (local)", [("Dairy cattle", "Milking cows, 3-10 yr")], "verified mapping"),
    ("Cattle - Cows (improved)", [("Dairy cattle", "Milking cows, 3-10 yr")], "verified mapping"),
    ("Cattle - Cows (high productive)", [("Dairy cattle", "Milking cows, 3-10 yr")], "verified mapping"),
    ("Cattle - Adult male", [("Beef cattle", "Adult cows")], "assumed: adult beef animal used for bulls/oxen"),
    ("Cattle - Steers/heifers", [("Dairy cattle", "Heifers, 1-3 yr")], "verified mapping (range midpoint)"),
    ("Cattle - Steers/heifers (improved)", [("Dairy cattle", "Heifers, 1-3 yr")], "verified mapping (range midpoint)"),
    ("Cattle - Calves", [("Dairy cattle", "Calves, 0-1 yr")], "verified mapping (range midpoint)"),
    ("Cattle - Calves (improved)", [("Dairy cattle", "Calves, 0-1 yr")], "verified mapping (range midpoint)"),
    ("Buffalo - Cows", [("Dairy cattle", "Milking cows, 3-10 yr")], "assumed: no buffalo values in source; cattle used"),
    ("Buffalo - Steers/heifers", [("Dairy cattle", "Heifers, 1-3 yr")], "assumed: no buffalo values in source; cattle used"),
    ("Buffalo - Calves", [("Dairy cattle", "Calves, 0-1 yr")], "assumed: no buffalo values in source; cattle used"),
    ("Pigs - lactating/pregnant sows", [("Swine", "Adult")], "verified mapping; lactating sows likely higher"),
    ("Pigs - dry sows/boars", [("Swine", "Adult")], "verified mapping"),
    ("Pigs - growers", [("Swine", "Piglet"), ("Swine", "Adult")], "assumed: mean of piglet and adult"),
    ("Sheep - Ewes", [("Sheep", "Adult")], "verified mapping"),
    ("Sheep - Breeding Rams", [("Sheep", "Adult")], "verified mapping"),
    ("Sheep - Fattening Rams", [("Sheep", "Adult")], "verified mapping"),
    ("Sheep - Lambs", [("Sheep", "5 lbs lamb"), ("Sheep", "Adult")], "assumed: mean of newborn lamb and adult"),
    ("Goats - Does", [("Goats", "Adult")], "verified mapping"),
    ("Goats - Breeding Bucks", [("Goats", "Adult")], "verified mapping"),
    ("Goats - Fattening Bucks", [("Goats", "Adult")], "verified mapping"),
    ("Goats - Kids", [("Goats", "5 lbs kid"), ("Goats", "Adult")], "assumed: mean of newborn kid and adult"),
]
cols = [c for c in src.columns if c.endswith("_L_d")]
rows = []
for lt, refs, note in MAP:
    sub = pd.concat([src[(src.category == c) & (src.age_group == a)] for c, a in refs])
    r = {"livetype_desc": lt, "source_rows": "; ".join(f"{c} / {a}" for c, a in refs), "mapping_status": note}
    r.update(sub[cols].mean().round(2).to_dict())
    rows.append(r)
out = pd.DataFrame(rows)
out["feed_mixing_L_per_kg_concentrate"] = 0.5
out.to_csv(TABLES / "livestock_water_icleaned.csv", index=False)
print(out[["livetype_desc", "drink_grazing_L_d", "drink_mixed_L_d", "service_mixed_L_d"]].to_string())
