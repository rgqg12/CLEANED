"""Merge GADM 4.1 level-1 boundaries for the Global South country list into one GeoPackage.

Inputs : RAW/global_south_countries.csv, RAW/gadm/<ISO3>.json.zip (GADM 4.1, level 1)
Outputs: RAW/admin1_global_south.gpkg, tables/admin1_regions.csv
"""
import pandas as pd
import geopandas as gpd
from common import RAW, TABLES, ADMIN1

countries = pd.read_csv(RAW / "global_south_countries.csv")
frames = []
for iso in countries.ISO3:
    f = RAW / "gadm" / f"{iso}.json.zip"
    if not f.exists():
        continue
    g = gpd.read_file(f"zip://{f}")[["GID_1", "GID_0", "COUNTRY", "NAME_1", "ENGTYPE_1", "geometry"]]
    frames.append(g)

adm = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")
adm = adm.merge(countries.rename(columns={"ISO3": "GID_0", "UNregion": "un_subregion"})[["GID_0", "un_subregion"]], on="GID_0")
adm["area_km2"] = adm.to_crs("+proj=cea").area / 1e6
adm.to_file(ADMIN1, driver="GPKG")

TABLES.mkdir(parents=True, exist_ok=True)
adm.drop(columns="geometry").sort_values("GID_1").to_csv(TABLES / "admin1_regions.csv", index=False, float_format="%.1f")
print(len(adm), "admin-1 units in", adm.GID_0.nunique(), "countries")
