"""Main-product metabolizable energy (ME, ruminants, MJ/kg DM) for ME-based crop/residue allocation
(methodology Section 5, Eqs. 7-8).

Source : Feedipedia (INRAE, CIRAD, AFZ, FAO; https://www.feedipedia.org), "ME ruminants" row of the
         nutritive-value tables, average and spread as published. One datasheet table is chosen per
         main product (as harvested, dry-matter basis); the choice is recorded in feedipedia_table.
Scope  : field crops in the i-CLEANED parameter databases that produce a main product plus a residue.
         Single-output forages (grasses, forage legumes, fodder trees) need no main-product ME: AF = 1.
Inputs : RAW/feedipedia/<node>.html (downloaded datasheets)
Outputs: tables/main_product_me.csv          (one row per main product, with i-CLEANED crop names)
         tables/feedipedia_me_all_tables.csv (every parsed table, for traceability)
"""
import glob
import os
import pandas as pd
from common import RAW, TABLES
from feedipedia_parse import parse

FP = RAW / "feedipedia"
rows = []
for f in glob.glob(str(FP / "*.html")):
    node = os.path.basename(f)[:-5]
    if node.isdigit():
        rows += parse(f, node)
allt = pd.DataFrame(rows)
allt["url"] = "https://www.feedipedia.org/node/" + allt.node
allt.to_csv(TABLES / "feedipedia_me_all_tables.csv", index=False)

# main product: (node, table title(s) averaged, i-CLEANED crop names, status, note)
D, P = "Feedipedia", "Feedipedia (proxy)"
SPEC = [
    ("Maize grain", "556", ["Maize grain, Subsaharan and East Africa"], ["Maize", "Zea mays", "Zea mays IP", "Fodder maize", "Maize-silage", "Zea mays-forage", "Zea mays-silage"], D,
     "regional tables range 13.5-13.7 MJ/kg DM"),
    ("Sorghum grain", "224", ["Sorghum grain (all types)"], ["Sorghum", "Sorghum bicolor-grain", "Sorghum bicolor (forage/silage)", "Sorghum bicolor-forage/silage"], D, ""),
    ("Pearl millet grain", "724", ["Pearl millet, grain"], [], D, "for pearl millet crops"),
    ("Finger millet grain", "721", ["Finger millet (Eleusine coracana), grain"], ["Eleusine coracana"], D, ""),
    ("Wheat grain", "223", ["Wheat grain"], ["Wheat", "Triticum", "Triticum IP", "Triticum OF"], D, ""),
    ("Barley grain", "227", ["Barley grain"], ["Barley", "Hordeum vulgare", "Hordeum vulgare-grain IP", "Hordeum vulgare-grain OFC", "Hordeum vulgare (forage)", "Hordeum vulgare-forage"], D, ""),
    ("Oat grain", "231", ["Oats from regular genotypes (see naked and dehulled oats below)"], ["Oats", "Avena sativa"], D, "regular (hulled) genotypes"),
    ("Paddy rice", "226", ["Rough rice, paddy rice"], ["Rice", "Oryza sativa"], D, "harvested as paddy; brown rice 13.3"),
    ("Buckwheat grain", "25140", ["Buckwheat (Fagopyrum esculentum) grain"], ["Fagopyrum esculentum"], D, ""),
    ("Common bean seeds", "266", ["Common bean seeds"], ["Beans", "Phaseolus vulgaris"], D, ""),
    ("Cowpea seeds", "232", ["Cowpea seeds"], ["Cowpea", "Vigna unguiculata", "Vigna mungo"], D, "Vigna mungo uses cowpea as proxy"),
    ("Faba bean seeds", "4926", ["Faba bean (Vicia faba), all cultivars"], ["Vicia faba-grain", "faba bean (vicia faba)"], D, ""),
    ("Lentil seeds", "284", ["Lentil seeds"], ["Lens culinaris", "Lentils (Lens esculenta)"], D, ""),
    ("Chickpea seeds", "319", ["Chickpea seeds, desi type", "Chickpea seeds, kabuli type"], ["Cicer arietinum"], D, "mean of desi and kabuli"),
    ("Pigeon pea seeds", "329", ["Pigeon pea (Cajanus cajan), seeds"], [], D, "for pigeon pea crops"),
    ("Lablab seeds", "297", ["Lablab (Lablab purpureus), seeds"], [], D, "only when lablab is grown for grain; forage lablab has AF = 1"),
    ("Groundnut pods (in shell)", "55", ["Peanuts, with shells"], ["Groundnut"], D, "as harvested; kernels without shells 23.0"),
    ("Soybean seeds", "42", ["Include raw and processed whole soybeans"], ["Glycine max IP"], D, "whole soybeans"),
    ("Cotton seeds (seed cotton)", "742", ["Cotton seeds, whole"], ["Cotton"], D, "ME of lint is not meaningful; whole seed used for the seed-cotton output"),
    ("Rapeseeds", "15617", ["Rapeseeds, low erucic, low glucosinolates"], ["Colza"], D, ""),
    ("Sunflower seeds", "40", ["Sunflower seeds"], [], D, "for sunflower crops"),
    ("Cassava roots", "527", ["Cassava tubers, fresh"], ["Cassava ", "cassava"], D, "dehydrated tubers 12.2"),
    ("Sweet potato tubers", "745", ["Sweet potato tubers, fresh"], ["Sweet potato"], D, ""),
    ("Taro corms", "537", ["Taro (Colocasia esculenta), tuber, dried"], ["Taro", "Cocoyam"], P, "cocoyam (Xanthosoma) uses taro as proxy"),
    ("Enset corm", "21251", ["Enset (Ensete ventricosum) corms, fresh"], ["Enset", "Kocho"], D, ""),
    ("Banana fruits", "683", ["Banana fruits, mature, fresh"], ["Banana", "Musa spp."], D, ""),
    ("Sugarcane stalks", "14462", ["Sugarcane stalks, fresh"], ["Sugarcane"], D, ""),
    ("Sugar beet roots", "535", ["Beet root, sugar type, fresh"], ["Beta vulgaris"], P, "fodder beet uses sugar beet as proxy"),
    ("Carrot roots", "539", ["Carrot roots, fresh"], ["Feed carrot"], D, ""),
    ("Tomato fruits", "7791", ["Tomato fruits, fresh"], ["Tomato"], "missing", "Feedipedia gives no ME for tomato fruits; expert value needed"),
    ("Sesame seeds", "26", ["Sesame seeds, whole"], [], "missing", "Feedipedia gives no ME for whole sesame seeds"),
]

out = []
for prod, node, titles, names, status, note in SPEC:
    sub = allt[(allt.node == node) & allt.table.isin(titles)]
    assert len(sub) == len(titles), f"table not found for {prod}: {titles}"
    r = {"main_product": prod, "icleaned_crop_names": "; ".join(names),
         "me_MJ_kgDM": round(sub.me_avg.mean(), 2) if sub.me_avg.notna().any() else None,
         "me_sd": sub.me_sd.iloc[0] if len(titles) == 1 else None,
         "dm_pct_as_fed": round(sub.dm_pct.mean(), 1),
         "status": status if sub.me_avg.notna().any() else "missing",
         "feedipedia_table": " + ".join(titles), "url": sub.url.iloc[0], "note": note}
    out.append(r)
out = pd.DataFrame(out)
out.to_csv(TABLES / "main_product_me.csv", index=False)
print(out[["main_product", "me_MJ_kgDM", "status"]].to_string())
