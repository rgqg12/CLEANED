"""Map every crop / feed name used in the i-CLEANED parameter databases to
(a) a Mialyk et al. (2024) crop for Tier 1 crop water use, and (b) a FAO-56 Table 12 entry for Tier 2.

Mapping principles
- Same species / FAOSTAT commodity -> direct match ("direct").
- Same crop group and similar season length -> proxy ("proxy"), following the proxy logic of
  Mialyk et al. (2024, Table S1) and Damerau (2024, Table 1).
- Forage grasses, forage legumes, pastures and fodder trees are not among the 43 public crops:
  Tier 1 is unavailable and they use Tier 2 (FAO-56 water balance), as the methodology prescribes
  for grazed and cut forage. Fodder trees/shrubs have no FAO-56 coefficient: flagged for expert input.
- Whole-plant forage of a grain crop (maize/sorghum silage or green fodder) uses that crop's CWU:
  evapotranspiration is a property of the field, not of the harvested part.
Output: tables/icleaned_crop_mapping.csv
"""
import glob
import pandas as pd
from common import RAW, TABLES

D, P, N = "direct", "proxy", "none"
GP_R = "Grazing Pasture - Rotated Grazing"
GP_E = "Grazing Pasture - Extensive Grazing"
TREE = "no FAO-56 entry (fodder tree/shrub): expert Kc needed"

M = {  # i-CLEANED name: (mialyk crop, match, FAO-56 Table 12 entry, note)
    "Aftermath": (None, N, GP_E, "regrowth after harvest"),
    "Amaranthus caudatus": ("vegetables", P, "Spinach", "leafy vegetable proxy"),
    "Amaranthus – local ": ("vegetables", P, "Spinach", "leafy vegetable proxy"),
    "Andropogon gayanus": (None, N, GP_R, "tropical forage grass"),
    "Arachis pintoi": (None, N, GP_R, "forage legume (perennial peanut)"),
    "Avena sativa": ("barley", P, "Oats", "oats not among the 43 public crops; barley as small-grain proxy"),
    "Avena sativa-forage": (None, N, "Oats", "forage oats: Tier 2"),
    "Avena sativa-fourrage": (None, N, "Oats", "forage oats: Tier 2"),
    "Axonopus scoparius": (None, N, GP_R, "tropical forage grass"),
    "Banana": ("bananas", D, "Banana - 2nd year", ""),
    "Barley": ("barley", D, "Barley", ""),
    "Bauhinia purpurea": (None, N, TREE, "fodder tree"),
    "Beans": ("beans", D, "Beans, dry and Pulses", ""),
    "Beta vulgaris": ("sugar_beet", P, "Sugar Beet", "fodder beet; sugar beet proxy"),
    "Brachiaria brizantha ": (None, N, GP_R, "tropical forage grass"),
    "Brachiaria decumbens": (None, N, GP_R, "tropical forage grass"),
    "Brachiaria decumbens (hay)": (None, N, GP_R, "tropical forage grass"),
    "Brachiaria hybrid": (None, N, GP_R, "tropical forage grass"),
    "Brassica spp": ("cabbages", P, "Cabbage", ""),
    "Cactus": (None, N, "no FAO-56 entry (CAM plant): expert Kc needed", "Opuntia; very low ET"),
    "Calliandra": (None, N, TREE, "fodder shrub"),
    "Canavalia brasiliensis": (None, N, GP_R, "forage legume"),
    "Cassava ": ("cassava", D, "Cassava - year 1", ""),
    "cassava": ("cassava", D, "Cassava - year 1", ""),
    "Cenchrus clandestinus": (None, N, GP_R, "kikuyu grass"),
    "Centrosema": (None, N, GP_R, "forage legume"),
    "Cicer arietinum": ("chick_peas", D, "Chick pea", ""),
    "Cocoyam": ("yams", P, None, "taro/cocoyam not among the 43 public crops; yams as root-crop proxy"),
    "Colza": ("rape_seed", D, "Rapeseed, Canola", ""),
    "Cotton": ("seed_cotton", D, "Cotton", ""),
    "Cowpea": ("beans", P, "Green Gram and Cowpeas", "cowpea not among the 43 public crops"),
    "Cratylia": (None, N, TREE, "fodder shrub"),
    "Cynodon nlemfuensis": (None, N, "Bermuda hay - averaged cutting effects", "star grass"),
    "Dactylis glomerata": (None, N, "Rye Grass hay - averaged cutting effects", "cool-season grass"),
    "Desmodium": (None, N, GP_R, "forage legume"),
    "Dichanthium aristatum": (None, N, GP_R, "tropical forage grass"),
    "Echinochloa polystachya": (None, N, GP_R, "wetland forage grass"),
    "Elephant grass": (None, N, "Sudan Grass hay (annual) - averaged cutting effects", "Pennisetum purpureum; cut forage"),
    "Eleusine coracana": ("millet", D, "Millet", "finger millet"),
    "Enset": ("bananas", P, "Banana - 2nd year", "Ensete ventricosum; banana proxy"),
    "Fagopyrum esculentum": ("wheat", P, "Spring Wheat", "buckwheat; small-grain proxy"),
    "Feed carrot": ("vegetables", P, "Carrots", ""),
    "Ficus semicordata": (None, N, TREE, "fodder tree"),
    "Fodder maize": ("maize", D, "Maize, Field (grain) (field corn)", "whole-plant forage: same field ET"),
    "Fustuca arundinacea": (None, N, "Rye Grass hay - averaged cutting effects", "tall fescue"),
    "Garuga pinnata": (None, N, TREE, "fodder tree"),
    "Gliricidia": (None, N, TREE, "fodder tree"),
    "Glycine max IP": ("soya_beans", D, "Soybeans", "purchased"),
    "Green leaf desmodium": (None, N, GP_R, "forage legume"),
    "Groundnut": ("groundnuts", D, "Groundnut (Peanut)", ""),
    "Guatemala": (None, N, "Sudan Grass hay (annual) - averaged cutting effects", "Tripsacum laxum; cut forage"),
    "Guazuma ulmifolia": (None, N, TREE, "fodder tree"),
    "Hedysarum coronarium": (None, N, "Clover hay, Berseem - averaged cutting effects", "sulla; forage legume"),
    "Hordeum vulgare": ("barley", D, "Barley", ""),
    "Hordeum vulgare (forage)": ("barley", D, "Barley", "whole-plant forage: same field ET"),
    "Hordeum vulgare-forage": ("barley", D, "Barley", "whole-plant forage: same field ET"),
    "Hordeum vulgare-grain IP": ("barley", D, "Barley", "purchased"),
    "Hordeum vulgare-grain OFC": ("barley", D, "Barley", "purchased"),
    "Hyparrhenia rufa": (None, N, GP_E, "natural grassland grass"),
    "Improved pasture": (None, N, GP_R, ""),
    "Ischaemum ciliare": (None, N, GP_R, "tropical forage grass"),
    "Kocho": ("bananas", P, "Banana - 2nd year", "enset product; banana proxy"),
    "Lablab": (None, N, "Green Gram and Cowpeas", "forage legume"),
    "Lens culinaris": ("chick_peas", P, "Lentil", "lentil not among the 43 public crops; pulse proxy"),
    "Lentils (Lens esculenta)": ("chick_peas", P, "Lentil", "lentil not among the 43 public crops; pulse proxy"),
    "Leucaena": (None, N, TREE, "fodder tree"),
    "Leucena leucocephala": (None, N, TREE, "fodder tree"),
    "Local mixed grasses": (None, N, GP_E, ""),
    "Lolium multiflorum": (None, N, "Rye Grass hay - averaged cutting effects", "Italian ryegrass"),
    "Maize": ("maize", D, "Maize, Field (grain) (field corn)", ""),
    "Maize-silage": ("maize", D, "Maize, Field (grain) (field corn)", "whole-plant forage: same field ET"),
    "Medicago sativa": (None, N, "Alfalfa Hay - averaged cutting effects", "alfalfa not among the 43 public crops"),
    "Melia azedarach": (None, N, TREE, "fodder tree"),
    "Moringa oleifera": (None, N, TREE, "fodder tree"),
    "Morus alba": (None, N, TREE, "mulberry"),
    "Mulberry": (None, N, TREE, "mulberry"),
    "Musa spp.": ("bananas", D, "Banana - 2nd year", ""),
    "Natural occurring pasture - Kilimanjaro region": (None, N, GP_E, ""),
    "Natural pasture": (None, N, GP_E, ""),
    "Natural pasture - Desert & Desert Steppe": (None, N, GP_E, ""),
    "Natural pasture - Forest & Forest Steppe": (None, N, GP_E, ""),
    "Natural pasture - High Mountain": (None, N, GP_E, ""),
    "Natural pasture - Mpigi, Mukono, and Masaka areas": (None, N, GP_E, ""),
    "Natural pasture - Nakasongola area": (None, N, GP_E, ""),
    "Natural pasture - Tanga region": (None, N, GP_E, ""),
    "Natural pasture hay": (None, N, GP_E, ""),
    "Oats": ("barley", P, "Oats", "oats not among the 43 public crops; barley as small-grain proxy"),
    "Olive": ("olives", D, None, "FAO-56 olive entry flagged in Table 12 parse"),
    "Oryza sativa": ("rice", D, "Rice", ""),
    "Panicum maximum": (None, N, GP_R, "tropical forage grass"),
    "Paspalum notatum": (None, N, GP_R, "tropical forage grass"),
    "Pennisetum purpureum": (None, N, "Sudan Grass hay (annual) - averaged cutting effects", "Napier grass; cut forage"),
    "Pennisetum purpureum-silage": (None, N, "Sudan Grass hay (annual) - averaged cutting effects", "Napier grass; cut forage"),
    "Phaseolus vulgaris": ("beans", D, "Beans, dry and Pulses", ""),
    "Plantago spp": (None, N, GP_R, "forage herb"),
    "Purchased": (None, N, None, "generic purchased feed: Tier 1 by ingredient or declared exclusion"),
    "Pâturage naturel": (None, N, GP_E, ""),
    "Pâturage naturel OF": (None, N, GP_E, "off-farm"),
    "Red clover": (None, N, "Clover hay, Berseem - averaged cutting effects", ""),
    "Rhodes": (None, N, "Bermuda hay - averaged cutting effects", "Chloris gayana"),
    "Rice": ("rice", D, "Rice", ""),
    "Rice (bran)": ("rice", D, "Rice", "by-product: allocate with Allocation 1"),
    "Samanea saman": (None, N, TREE, "fodder tree"),
    "Sambucus peruviana": (None, N, TREE, "fodder tree"),
    "Sesbania": (None, N, TREE, "fodder shrub"),
    "Sorghum": ("sorghum", D, "Sorghum - grain", ""),
    "Sorghum bicolor (forage/silage)": ("sorghum", D, "Sorghum - grain", "whole-plant forage: same field ET"),
    "Sorghum bicolor-forage/silage": ("sorghum", D, "Sorghum - grain", "whole-plant forage: same field ET"),
    "Sorghum bicolor-grain": ("sorghum", D, "Sorghum - grain", ""),
    "Stipa tenacissima": (None, N, GP_E, "esparto grass, rangeland"),
    "Sugarcane": ("sugar_cane", D, None, "FAO-56 sugar cane in Table 12 group k"),
    "Sweet potato": ("sweet_potatoes", D, "Sweet Potato", ""),
    "Taro": ("yams", P, None, "taro not among the 43 public crops; yams as root-crop proxy"),
    "Tithonia diversifolia": (None, N, TREE, "fodder shrub"),
    "Tomato": ("tomatoes", D, "Tomato", ""),
    "Trichantera gigantea": (None, N, TREE, "fodder tree"),
    "Trifolium alexandrinum": (None, N, "Clover hay, Berseem - averaged cutting effects", "berseem"),
    "Trifolium repens": (None, N, "Clover hay, Berseem - averaged cutting effects", "white clover"),
    "Triticum": ("wheat", D, "Spring Wheat", ""),
    "Triticum IP": ("wheat", D, "Spring Wheat", "purchased"),
    "Triticum OF": ("wheat", D, "Spring Wheat", "off-farm"),
    "Vicia faba-grain": ("beans", P, "Fababean (broad bean) - Dry/Seed", "broad bean not among the 43 public crops"),
    "Vigna mungo": ("beans", P, "Green Gram and Cowpeas", ""),
    "Vigna unguiculata": ("beans", P, "Green Gram and Cowpeas", "cowpea not among the 43 public crops"),
    "Wheat": ("wheat", D, "Spring Wheat", ""),
    "Wild desmodium": (None, N, GP_E, "forage legume, wild"),
    "Zea mays": ("maize", D, "Maize, Field (grain) (field corn)", ""),
    "Zea mays IP": ("maize", D, "Maize, Field (grain) (field corn)", "purchased"),
    "Zea mays-forage": ("maize", D, "Maize, Field (grain) (field corn)", "whole-plant forage: same field ET"),
    "Zea mays-silage": ("maize", D, "Maize, Field (grain) (field corn)", "whole-plant forage: same field ET"),
    "faba bean (vicia faba)": ("beans", P, "Fababean (broad bean) - Dry/Seed", "broad bean not among the 43 public crops"),
}

# all names used in the i-CLEANED parameter databases
db = RAW.parent / "icleaned" / "data" / "primary_database"
names = sorted(set(pd.concat([pd.read_csv(f, encoding="utf-8-sig").crop_name for f in glob.glob(str(db / "*" / "lkp_crops.csv"))])))
missing = [n for n in names if n not in M]
assert not missing, f"unmapped i-CLEANED crops: {missing}"

kc = pd.read_csv(TABLES / "fao56_table12_kc.csv")
kc["entry"] = (kc.crop + " " + kc.subtype.fillna("")).str.strip()
rows = []
for n in names:
    mc, match, fao, note = M[n]
    tier1 = "available" if mc else "not available: Tier 2 (FAO-56)"
    r = {"icleaned_crop_name": n, "mialyk_crop": mc, "mialyk_match": match if mc else None,
         "tier1_status": tier1, "fao56_entry": fao, "note": note}
    k = kc[kc.entry == fao]
    if len(k):
        r.update(Kc_ini=k.Kc_ini_value.iloc[0], Kc_mid=k.Kc_mid_value.iloc[0], Kc_end=k.Kc_end_value.iloc[0])
    rows.append(r)
out = pd.DataFrame(rows)
out.to_csv(TABLES / "icleaned_crop_mapping.csv", index=False)
print(out.tier1_status.value_counts()); print(out.mialyk_match.value_counts())
print("FAO-56 entries not found:", out[out.fao56_entry.notna() & out.Kc_mid.isna()][["icleaned_crop_name", "fao56_entry"]].to_string())
