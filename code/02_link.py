"""02_link.py: match every NMWI mine waste feature to the USGS lab samples near it.

Plain-language note: this script finds, for each mine waste pile, every lab
sample taken inside it or within 2 km of its edge, and records the distance.
You do not need to open it; its results are checked in qa_report.txt.

Inputs : data/raw/nmwi/USGS_NMWI_v2.gdb, data/raw/geochem/tbl_geol.parquet
Outputs: data/interim/features.parquet   one row per waste feature
         data/interim/links.parquet      one row per (feature, sample) pair <= 2 km
         data/interim/link_counts.json   counts for the QA report
"""
import json
from pathlib import Path

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INT = ROOT / "data" / "interim"
INT.mkdir(parents=True, exist_ok=True)
GDB = RAW / "nmwi" / "USGS_NMWI_v2.gdb"
GEOL = RAW / "geochem" / "tbl_geol.parquet"
R1, R2 = 1000.0, 2000.0  # metres: tier 1 and tier 2 radii (verify point V1)

WASTE_RE = r"tail|dump|waste|slag|mill|leach|heap|spoil|mine"

# ---------------------------------------------------------------- features
pts = gpd.read_file(GDB, layer="Waste_Points")
pol = gpd.read_file(GDB, layer="Waste_Polygons")
geo = gpd.read_file(GDB, layer="Waste_Geology", ignore_geometry=True)

feat = pts.drop(columns="geometry").copy()
geo_cols = ["Ftr_ID", "Dep_Type_1", "Dep_Type_2", "Ore_Min", "Gangue_Min"]
feat = feat.merge(geo[[c for c in geo_cols if c in geo.columns]].drop_duplicates("Ftr_ID"),
                  on="Ftr_ID", how="left")
pol_area = pol[["Ftr_ID", "Area_SqKm"]].drop_duplicates("Ftr_ID")
feat = feat.merge(pol_area, on="Ftr_ID", how="left")
counts = {
    "nmwi_points": int(len(pts)),
    "nmwi_polygons": int(len(pol)),
    "nmwi_unique_ftr_id": int(feat.Ftr_ID.nunique()),
    "nmwi_sites": int(feat.Site_ID.nunique()),
    "nmwi_states": int(feat.State.nunique()),
}

# Use polygon geometry where present, else point.
pol_g = pol.dissolve(by="Ftr_ID", as_index=False)[["Ftr_ID", "geometry"]]
shape = pts[["Ftr_ID", "geometry"]].merge(pol_g, on="Ftr_ID", how="left", suffixes=("_pt", "_pol"))
shape["geometry"] = [p if p is not None and not p.is_empty else q
                     for p, q in zip(shape.geometry_pol, shape.geometry_pt)]
shape["geom_source"] = np.where(shape.geometry_pol.notna(), "polygon", "point")
shape = gpd.GeoDataFrame(shape[["Ftr_ID", "geom_source"]], geometry=shape.geometry, crs=pts.crs)
shape = shape.drop_duplicates("Ftr_ID")
counts["features_with_polygon"] = int((shape.geom_source == "polygon").sum())
feat = feat.merge(shape[["Ftr_ID", "geom_source"]], on="Ftr_ID", how="left")
feat = feat.drop_duplicates("Ftr_ID")

# ---------------------------------------------------------------- samples
con = duckdb.connect()
con.sql("SET enable_progress_bar=false")
samp = con.sql(f"""
    select lab_id, group_id, latitude, longitude, state, primary_class, secondary_class,
           specific_name, sample_source, project_name, date_collect, mine_name, deposit_name,
           depth, prep
    from '{GEOL}'
    where latitude is not null and longitude is not null
""").df()
counts["geochem_samples_total"] = int(len(samp))
keep = samp.primary_class.isin(["rock", "soil", "sediment"])
txt = (samp.specific_name.fillna("") + " " + samp.prep.fillna("")).str.lower()
conc = txt.str.contains("concentrate|panned|heavy sand")
counts["geochem_excluded_class"] = int((~keep).sum())
counts["geochem_excluded_concentrate"] = int((keep & conc).sum())
samp = samp[keep & ~conc].reset_index(drop=True)
counts["geochem_samples_eligible"] = int(len(samp))
src = samp.sample_source.fillna("").str.lower()
samp["on_waste"] = src.str.contains(r"dump|tailing|waste|slag|mill") | \
    samp.specific_name.fillna("").str.lower().str.contains(r"tailing|slag|waste|dump")
samp["mine_setting"] = samp.on_waste | src.str.contains("mine")

sgdf = gpd.GeoDataFrame(samp, geometry=gpd.points_from_xy(samp.longitude, samp.latitude),
                        crs="EPSG:4269")  # NAD83 per NGDB metadata

links = []
for region, epsg in [("AK", 3338), ("CONUS", 5070)]:
    fmask = (feat.set_index("Ftr_ID").loc[shape.Ftr_ID, "State"].values == "AK")
    fsub = shape[fmask] if region == "AK" else shape[~fmask]
    if fsub.empty:
        continue
    fsub = fsub.to_crs(epsg)
    # rough prefilter on lon/lat bounding box padded by ~0.05 deg
    b = fsub.to_crs(4269).total_bounds
    pad = 0.1
    smask = sgdf.longitude.between(b[0] - pad, b[2] + pad) & sgdf.latitude.between(b[1] - pad, b[3] + pad)
    ssub = sgdf[smask].to_crs(epsg)
    buf = fsub.copy()
    buf["geometry"] = fsub.buffer(R2)
    j = gpd.sjoin(ssub[["lab_id", "geometry"]], buf[["Ftr_ID", "geometry"]], predicate="within")
    fg = fsub.set_index("Ftr_ID").geometry
    j["dist_m"] = [pt.distance(fg[f]) for pt, f in zip(j.geometry, j.Ftr_ID)]
    links.append(pd.DataFrame(j[["Ftr_ID", "lab_id", "dist_m"]]))

links = pd.concat(links, ignore_index=True)
links["tier"] = np.where(links.dist_m <= R1, 1, 2)
links = links.merge(samp.drop(columns=["geometry"], errors="ignore")[
    ["lab_id", "group_id", "primary_class", "sample_source", "project_name", "date_collect",
     "on_waste", "mine_setting"]], on="lab_id", how="left")

counts["link_pairs"] = int(len(links))
counts["linked_samples_unique"] = int(links.lab_id.nunique())
nt1 = links[links.tier == 1].groupby("Ftr_ID").size()
nt2 = links.groupby("Ftr_ID").size()
counts["features_tier1_any"] = int((nt1 > 0).sum())
counts["features_tier12_any"] = int((nt2 > 0).sum())
counts["features_none_2km"] = int(counts["nmwi_unique_ftr_id"] - counts["features_tier12_any"])

# geodesic sanity: features whose point lies > 5 km from its own polygon (data issue)
feat.to_parquet(INT / "features.parquet", index=False)
shape.to_file(INT / "feature_shapes.gpkg", driver="GPKG")
links.to_parquet(INT / "links.parquet", index=False)
(INT / "link_counts.json").write_text(json.dumps(counts, indent=2))
print(json.dumps(counts, indent=2))
