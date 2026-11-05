"""04_scores.py: score every mine waste feature and site.

Plain-language note: for each pile this script takes the typical (median)
value of each element in nearby samples, compares it with typical U.S. soil
(enrichment) and with EPA's residential soil screening levels (hazard), and
turns those comparisons into the Critical Mineral Index, the Heavy-metal
Hazard Index, a priority class, and a confidence grade. You do not need to
open it; every rule is listed in docs/CODEBOOK.md.

Outputs: data/processed/nmwi_screening_features.csv (+ .geojson)
         data/processed/nmwi_screening_sites.csv
         data/processed/feature_element_long.csv
         data/interim/score_counts.json
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INT, REF, OUT = ROOT / "data/interim", ROOT / "data/reference", ROOT / "data/processed"
OUT.mkdir(parents=True, exist_ok=True)
EF_CAP = 3.0          # log10 cap per element (1000x)
TOP_K = 5             # CMI = sum of the 5 largest positive log10 EFs
PRIORITY_Q = 2 / 3    # top third (verify point V4)
AS_MODE = "noncancer"  # author decision V3 (2026-11-01): noncancer 35 mg/kg for ranking; cancer 0.68 kept as columns

# ---------------------------------------------------------------- references
crit = pd.read_csv(REF / "critical_minerals_2025.csv").dropna(subset=["species"])
CRIT = set(crit.species)
haz = pd.read_csv(REF / "hazard_metals_rsl.csv")

# cross-check every RSL value against the EPA workbook itself
x = pd.read_excel(ROOT / "data/raw/epa_rsl/rsl_405270.xlsx", header=None)
epa = dict(zip(x[13].astype(str).str.strip(), pd.to_numeric(x[15], errors="coerce")))
for _, r in haz.iterrows():
    assert abs(epa[r.rsl_analyte] - r.rsl_resident_mgkg) < 1e-9, (r.species, epa[r.rsl_analyte])
if AS_MODE == "noncancer":
    haz.loc[haz.species == "As", "rsl_resident_mgkg"] = haz.loc[haz.species == "As", "alt_noncancer_mgkg"]
RSL = dict(zip(haz.species, haz.rsl_resident_mgkg))
AS_CANCER = float(pd.read_csv(REF / "hazard_metals_rsl.csv").set_index("species").rsl_resident_mgkg["As"])

soil = pd.read_csv(INT / "background.csv")
ucc = pd.read_csv(REF / "ucc_rudnick_gao_2014.csv")
bg = {}
bg_src = {}
good = soil[(soil.bg_n >= 100) & (soil.bg_nd_frac <= 0.5)]
for s, v in zip(good.species, good.bg_median_ppm):
    bg[s], bg_src[s] = v, "USGS soil (Geochemical Landscapes) median"
for s, v in zip(ucc.species, ucc.ucc_ppm):
    if s not in bg:
        bg[s], bg_src[s] = v, "Upper continental crust (Rudnick and Gao 2014)"
for s, v, n in zip(soil.species, soil.bg_median_ppm, soil.bg_n):
    if s not in bg and n >= 100:  # mostly nondetect: half-DL median is an upper bound
        bg[s], bg_src[s] = v, "USGS soil median, mostly nondetect (upper bound; EF conservative)"
pd.DataFrame({"species": list(bg), "background_ppm": list(bg.values()),
              "source": [bg_src[s] for s in bg]}).sort_values("species").to_csv(
    OUT / "background_values_used.csv", index=False)

# ---------------------------------------------------------------- data
feat = pd.read_parquet(INT / "features.parquet")
links = pd.read_parquet(INT / "links.parquet")
vals = pd.read_parquet(INT / "sample_values.parquet")

# use tier 1 samples if a feature has any, else tier 2
has_t1 = links.groupby("Ftr_ID").tier.min().rename("best_tier")
links = links.merge(has_t1, on="Ftr_ID")
used = links[links.tier == links.best_tier]

lv = used[["Ftr_ID", "lab_id", "on_waste"]].merge(vals, on="lab_id")
lv = lv[lv.species.isin(CRIT | set(RSL))]
g = lv.groupby(["Ftr_ID", "species"])
long = g.agg(n=("ppm", "size"), median_ppm=("ppm", "median"), max_ppm=("ppm", "max"),
             nd_frac=("censor", lambda s: float((s == "nd").mean())),
             n_on_waste=("on_waste", "sum")).reset_index()
long["background_ppm"] = long.species.map(bg)
long["EF"] = long.median_ppm / long.background_ppm
long["EF_max"] = long.max_ppm / long.background_ppm
long["log_EF_pos"] = np.clip(np.log10(long.EF), 0, EF_CAP)
# a median that is itself a nondetect says nothing about enrichment
# (half the detection limit can sit far above crustal abundance for Te, PGEs, Re)
long["ef_valid"] = long.nd_frac < 0.5
long.loc[~long.ef_valid, "log_EF_pos"] = 0.0
long.loc[~long.ef_valid, "EF"] = np.nan
long["is_critical"] = long.species.isin(CRIT)
long["is_hazard"] = long.species.isin(set(RSL))
long["RSL_mgkg"] = long.species.map(RSL)
long["HQ"] = long.median_ppm / long.RSL_mgkg
long["HQ_max"] = long.max_ppm / long.RSL_mgkg
# a nondetect median (e.g. As "<200 ppm" by old spectrographic methods) is not a measured
# hazard; half its detection limit would masquerade as one. Leave it out of the HHI.
long.loc[~long.ef_valid, "HQ"] = np.nan
# cancer-based arsenic ratio kept alongside (sensitivity and element table)
long["HQ_cancer_As"] = np.where(long.species == "As", long.median_ppm / AS_CANCER, np.nan)
long.loc[~long.ef_valid, "HQ_cancer_As"] = np.nan
long.to_csv(OUT / "feature_element_long.csv", index=False, float_format="%.6g")


def topk_sum(s, k=TOP_K):
    return float(np.sort(s.values)[::-1][:k].sum())


def top_list(df, col, thr, k=5):
    d = df[df[col] >= thr].sort_values(col, ascending=False).head(k)
    return "; ".join(f"{s} {v:.0f}x" if v >= 10 else f"{s} {v:.1f}x" for s, v in zip(d.species, d[col]))


c = long[long.is_critical & long.background_ppm.notna()]
NONHAZ = CRIT - set(RSL)
rows = []
for fid, d in c.groupby("Ftr_ID"):
    dn = d[d.species.isin(NONHAZ)]
    rows.append({"Ftr_ID": fid, "CMI": topk_sum(d.log_EF_pos), "CMI_nonhazard": topk_sum(dn.log_EF_pos),
                 "n_crit_measured": int(len(d)), "n_crit_EF5": int((d.EF >= 5).sum()),
                 "top_critical": top_list(d, "EF", 5)})
cm = pd.DataFrame(rows)
h = long[long.is_hazard]
rows = []
for fid, d in h.groupby("Ftr_ID"):
    if d.HQ.notna().sum() == 0:
        continue
    rows.append({"Ftr_ID": fid, "HHI": float(d.HQ.sum()), "n_haz_measured": int(len(d)),
                 "n_exceed": int((d.HQ >= 1).sum()), "n_exceed_noAs": int(((d.HQ >= 1) & (d.species != "As")).sum()),
                 "HEF": topk_sum(d.log_EF_pos), "top_hazard": top_list(d, "HQ", 1),
                 "As_median_ppm": d.loc[d.species == "As", "median_ppm"].max(),
                 "Pb_median_ppm": d.loc[d.species == "Pb", "median_ppm"].max()})
hm = pd.DataFrame(rows)

ns = used.groupby("Ftr_ID").agg(n_samples=("lab_id", "nunique"), n_on_waste=("on_waste", "sum"),
                                nearest_m=("dist_m", "min"))
n1 = links[links.tier == 1].groupby("Ftr_ID").lab_id.nunique().rename("n_tier1")
n2 = links.groupby("Ftr_ID").lab_id.nunique().rename("n_within_2km")
sc = feat.merge(ns, on="Ftr_ID", how="left").merge(n1, on="Ftr_ID", how="left") \
    .merge(n2, on="Ftr_ID", how="left").merge(has_t1, on="Ftr_ID", how="left") \
    .merge(cm, on="Ftr_ID", how="left").merge(hm, on="Ftr_ID", how="left")
for col in ["n_samples", "n_on_waste", "n_tier1", "n_within_2km"]:
    sc[col] = sc[col].fillna(0).astype(int)
sc["log10_HHI"] = np.log10(sc.HHI)


def grade(r):
    if r.n_within_2km == 0 or pd.isna(r.CMI) and pd.isna(r.HHI):
        return "U"
    if r.best_tier == 1 and r.n_tier1 >= 5 and r.n_on_waste >= 1:
        return "A"
    if r.best_tier == 1 and r.n_tier1 >= 3:
        return "B"
    return "C"


sc["confidence"] = sc.apply(grade, axis=1)
scored = sc.confidence != "U"
cmi_cut = sc.loc[scored, "CMI"].quantile(PRIORITY_Q)
hhi_cut = sc.loc[scored, "log10_HHI"].quantile(PRIORITY_Q)
hiC, hiH = sc.CMI >= cmi_cut, sc.log10_HHI >= hhi_cut
sc["priority"] = np.select([~scored, hiC & hiH, hiC, hiH], ["Unsampled", "Dual", "Resource", "Hazard"], "Lower")
sc["CMI_rank"] = sc.CMI.rank(ascending=False, method="min")
sc["HHI_rank"] = sc.log10_HHI.rank(ascending=False, method="min")
sc["CMI_pct"] = sc.CMI.rank(pct=True) * 100
sc["HHI_pct"] = sc.log10_HHI.rank(pct=True) * 100
sc["screening_score"] = (sc.CMI_pct + sc.HHI_pct) / 2
sc["screening_rank"] = sc.screening_score.rank(ascending=False, method="min")

keep = ["Ftr_ID", "Site_ID", "Site_Name", "Ftr_Name", "Ftr_Type", "Mine_Name", "Mine_Dist", "State", "County",
        "Latitude", "Longitude", "Area_SqKm", "Commodity", "Dep_Type_1", "Reclaimed", "Superfund", "Land_Mng",
        "best_tier", "n_samples", "n_tier1", "n_within_2km", "n_on_waste", "nearest_m",
        "CMI", "CMI_nonhazard", "CMI_rank", "n_crit_measured", "n_crit_EF5", "top_critical",
        "HHI", "log10_HHI", "HHI_rank", "n_haz_measured", "n_exceed", "n_exceed_noAs", "HEF", "top_hazard",
        "As_median_ppm", "Pb_median_ppm", "screening_score", "screening_rank", "priority", "confidence"]
sc = sc[[k for k in keep if k in sc.columns]].sort_values(["screening_rank", "Ftr_ID"])
sc.to_csv(OUT / "nmwi_screening_features.csv", index=False, float_format="%.8g")

shapes = gpd.read_file(INT / "feature_shapes.gpkg").to_crs(4326)
pts = gpd.GeoDataFrame(sc, geometry=gpd.points_from_xy(sc.Longitude, sc.Latitude), crs=4326)
pts.to_file(OUT / "nmwi_screening_features.geojson", driver="GeoJSON")

# ---------------------------------------------------------------- site rollup
s = sc[sc.confidence != "U"]
site = sc.groupby("Site_ID").agg(Site_Name=("Site_Name", "first"), State=("State", "first"),
                                 n_features=("Ftr_ID", "size"), Area_SqKm=("Area_SqKm", "sum"),
                                 Commodity=("Commodity", "first"), Superfund=("Superfund", "max")).reset_index()
best = s.sort_values("screening_score", ascending=False).drop_duplicates("Site_ID")
site = site.merge(best[["Site_ID", "Ftr_ID", "CMI", "log10_HHI", "top_critical", "top_hazard", "priority",
                        "confidence", "screening_score"]].rename(columns={"Ftr_ID": "lead_feature"}),
                  on="Site_ID", how="left")
site["n_features_scored"] = site.Site_ID.map(s.groupby("Site_ID").size()).fillna(0).astype(int)
site["priority"] = site.priority.fillna("Unsampled")
site["confidence"] = site.confidence.fillna("U")
site = site.sort_values("screening_score", ascending=False)
site["site_rank"] = site.screening_score.rank(ascending=False, method="min")
site.to_csv(OUT / "nmwi_screening_sites.csv", index=False, float_format="%.8g")

counts = {
    "features_scored": int(scored.sum()), "features_unsampled": int((~scored).sum()),
    "confidence": sc.confidence.value_counts().to_dict(), "priority": sc.priority.value_counts().to_dict(),
    "cmi_cut": float(cmi_cut), "hhi_cut_log10": float(hhi_cut),
    "sites_total": int(len(site)), "sites_scored": int((site.confidence != "U").sum()),
    "site_priority": site.priority.value_counts().to_dict(),
    "background_sources": pd.Series(bg_src).value_counts().to_dict(),
    "crit_species_with_background": int(len(CRIT & set(bg))), "crit_species_listed": int(len(CRIT)),
    "as_mode": AS_MODE,
}
(INT / "score_counts.json").write_text(json.dumps(counts, indent=2, default=str))
print(json.dumps(counts, indent=2, default=str))
