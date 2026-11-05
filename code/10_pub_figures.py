"""10_pub_figures.py: publication figures and tables for the author's manuscript (Draft 2).

Plain-language note: same results as 06_figures.py, drawn for a journal page:
white background, no titles inside the figures (the captions carry them),
300 dpi, numbered in the order the manuscript cites them. Also writes the
manuscript and appendix tables as CSV in paper/pub/.
"""
import json
from pathlib import Path

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[1]
OUT, REF, PUB = ROOT / "data/processed", ROOT / "data/reference", ROOT / "paper/pub"
PUB.mkdir(parents=True, exist_ok=True)
S = json.loads((ROOT / "paper/stats.json").read_text())
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
COL = {"Dual": "#1baf7a", "Resource": "#2a78d6", "Hazard": "#eb6834", "Lower": "#b9b8b2"}
ORDER = ["Dual", "Resource", "Hazard", "Lower", "Unsampled"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300,
                     "figure.facecolor": "white", "axes.facecolor": "white"})

f = pd.read_csv(OUT / "nmwi_screening_features.csv")
site = pd.read_csv(OUT / "nmwi_screening_sites.csv")
long = pd.read_csv(OUT / "feature_element_long.csv")
s = f[f.priority != "Unsampled"]

# ---------------------------------------------------------------- Figure 1 workflow
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.set_xlim(0, 100), ax.set_ylim(0, 62), ax.axis("off")


def box(x, y, w, h, title, body, fc="#f4f3ef", ec="#9c9b95"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=ec, lw=0.8))
    ax.text(x + w / 2, y + h - 2.2, title, ha="center", va="top", fontsize=8.2, fontweight="bold", color=INK)
    ax.text(x + w / 2, y + h - 6.4, body, ha="center", va="top", fontsize=6.9, color=INK2, linespacing=1.35)


def arrow(x1, y1, x2, y2):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1))


box(1, 44, 30, 16, "Mine waste features", f"NMWI v2.0 (USGS, 2026)\n{S['nmwi_unique_ftr_id']:,} features, {S['nmwi_sites']} sites,\n{S['nmwi_states']} states (polygons)")
box(35, 44, 30, 16, "Geochemical samples", f"Granitto et al. (2026)\n{S['geochem_samples_eligible']:,} bulk rock,\nsoil, and sediment samples")
box(69, 44, 30, 16, "Benchmarks", "Soil background (Smith et al., 2013)\nCrust (Rudnick and Gao, 2014)\nEPA RSLs; 2025 critical list")
box(18, 23, 30, 16, "1. Spatial linkage", "Distance to polygon edge\nTier 1: <= 1 km; Tier 2: 1 to 2 km\nBest-value result per element")
box(52, 23, 30, 16, "2. Feature indices", "Median per element\nCMI: enrichment vs background\nHHI: ratio to EPA RSL")
box(1, 2, 30, 16, "3. Classification", "Dual / Resource / Hazard /\nLower / Unsampled\nConfidence A, B, C, U")
box(35, 2, 30, 16, "4. Checks", "Commodity validation\nSensitivity tests\n14 hand-verified spot checks")
box(69, 2, 30, 16, "5. Outputs", "Ranked feature and site tables\nInteractive atlas\nOpen data and code (Zenodo)", fc="#e6f4ee", ec="#1baf7a")
arrow(16, 44, 28, 39.5), arrow(50, 44, 36, 39.5), arrow(84, 44, 70, 39.5), arrow(48, 31, 52, 31)
arrow(60, 23, 20, 18.5), arrow(31, 10, 35, 10), arrow(65, 10, 69, 10)
fig.savefig(PUB / "Figure1_workflow.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- Figure 1 workflow, numbered citations
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.set_xlim(0, 100), ax.set_ylim(0, 62), ax.axis("off")


def box(x, y, w, h, title, body, fc="#f4f3ef", ec="#9c9b95"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=ec, lw=0.8))
    ax.text(x + w / 2, y + h - 2.2, title, ha="center", va="top", fontsize=8.2, fontweight="bold", color=INK)
    ax.text(x + w / 2, y + h - 6.4, body, ha="center", va="top", fontsize=6.9, color=INK2, linespacing=1.35)


def arrow(x1, y1, x2, y2):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1))


box(1, 44, 30, 16, "Mine waste features", f"NMWI v2.0 [4]\n{S['nmwi_unique_ftr_id']:,} features, {S['nmwi_sites']} sites,\n{S['nmwi_states']} states (polygons)")
box(35, 44, 30, 16, "Geochemical samples", f"Granitto et al. [6]\n{S['geochem_samples_eligible']:,} bulk rock,\nsoil, and sediment samples")
box(69, 44, 30, 16, "Benchmarks", "Soil background [8]\nUpper continental crust [9]\nEPA RSLs [11]; critical list [10]")
box(18, 23, 30, 16, "1. Spatial linkage", "Distance to polygon edge\nTier 1: <= 1 km; Tier 2: 1 to 2 km\nBest-value result per element")
box(52, 23, 30, 16, "2. Feature indices", "Median per element\nCMI: enrichment vs background\nHHI: ratio to EPA RSL")
box(1, 2, 30, 16, "3. Classification", "Dual / Resource / Hazard /\nLower / Unsampled\nConfidence A, B, C, U")
box(35, 2, 30, 16, "4. Checks", "Commodity validation\nSensitivity tests\n14 hand-verified spot checks")
box(69, 2, 30, 16, "5. Outputs", "Ranked feature and site tables\nInteractive atlas\nOpen data and code (Zenodo)", fc="#e6f4ee", ec="#1baf7a")
arrow(16, 44, 28, 39.5), arrow(50, 44, 36, 39.5), arrow(84, 44, 70, 39.5), arrow(48, 31, 52, 31)
arrow(60, 23, 20, 18.5), arrow(31, 10, 35, 10), arrow(65, 10, 69, 10)
fig.savefig(PUB / "Figure1_workflow_numbered.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- Figure 2 coverage by state
g = f.assign(cov=np.select([f.best_tier == 1, f.best_tier == 2], ["<= 1 km", "1 to 2 km"], "none within 2 km"))
ct = g.groupby(["State", "cov"]).size().unstack(fill_value=0)
for c in ["<= 1 km", "1 to 2 km", "none within 2 km"]:
    ct[c] = ct.get(c, 0)
ct = ct[["<= 1 km", "1 to 2 km", "none within 2 km"]]
ct = ct.loc[ct.sum(axis=1).sort_values().index]
fig, ax = plt.subplots(figsize=(6.6, 5.4))
left = np.zeros(len(ct))
for c, colr in zip(ct.columns, ["#256abf", "#86b6ef", "#d6d5cf"]):
    ax.barh(ct.index, ct[c], left=left, color=colr, height=0.72, label=f"Nearest sample {c}",
            edgecolor="white", linewidth=0.8)
    left += ct[c].values
for y, v in enumerate(left):
    ax.text(v + 2, y, f"{int(v)}", va="center", fontsize=7, color=INK2)
ax.set_xlabel("Number of mine waste features")
ax.grid(axis="x", color=GRID, lw=0.6), ax.set_axisbelow(True)
ax.legend(frameon=False, loc="lower right", fontsize=7.5)
fig.tight_layout()
fig.savefig(PUB / "Figure2_coverage_by_state.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 3 map
st = gpd.read_file(ROOT / "data/raw/census/cb_2024_us_state_20m.shp")
fig = plt.figure(figsize=(7.2, 4.5))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
ax2 = fig.add_axes([0.0, 0.0, 0.25, 0.27])
lower = st[~st.STUSPS.isin(["AK", "HI", "PR"])].to_crs(5070)
ak = st[st.STUSPS == "AK"].to_crs(3338)
pts = gpd.GeoDataFrame(f, geometry=gpd.points_from_xy(f.Longitude, f.Latitude), crs=4269)
for a, base, sub, crs in [(ax, lower, pts[pts.State != "AK"], 5070), (ax2, ak, pts[pts.State == "AK"], 3338)]:
    base.plot(ax=a, color="#f1f0ec", edgecolor="#bdbcb6", linewidth=0.45)
    sub = sub.to_crs(crs)
    for k in reversed(ORDER):
        d = sub[sub.priority == k]
        if k == "Unsampled":
            a.scatter(d.geometry.x, d.geometry.y, s=12, facecolor="none", edgecolor=INK2, linewidth=0.7, zorder=3)
        else:
            a.scatter(d.geometry.x, d.geometry.y, s=22 if k == "Dual" else 12, color=COL[k], edgecolor="white",
                      linewidth=0.5 if k != "Lower" else 0.3, zorder=4 if k != "Lower" else 2)
    a.set_axis_off()
ax2.text(0.02, 0.98, "Alaska", transform=ax2.transAxes, fontsize=7, color=INK2, va="top")
cnt = {"Dual": S["feat_dual"], "Resource": S["feat_resource"], "Hazard": S["feat_hazard"], "Lower": S["feat_lower"],
       "Unsampled": S["conf_U"]}
h = [plt.Line2D([], [], marker="o", ls="", markersize=6 if k != "Dual" else 7, markerfacecolor=COL.get(k, "none"),
                markeredgecolor=INK2 if k == "Unsampled" else "white", label=f"{k} ({cnt[k]})") for k in ORDER]
ax.legend(handles=h, loc="lower right", frameon=False, fontsize=7.5, title="Priority class (features)", title_fontsize=7.5)
fig.savefig(PUB / "Figure3_priority_map.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- Figure 4 scatter
fig, ax = plt.subplots(figsize=(6.4, 4.9))
for k in ["Lower", "Hazard", "Resource", "Dual"]:
    d = s[s.priority == k]
    ax.scatter(d.CMI, d.log10_HHI, s=14, color=COL[k], edgecolor="white", linewidth=0.4, label=f"{k} ({cnt[k]})", zorder=3)
ax.axvline(S["cmi_cut"], color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
ax.axhline(S["hhi_cut_log10"], color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
ax.set_xlabel("Critical Mineral Index (CMI)")
ax.set_ylabel("Heavy-Metal Hazard Index, log10(HHI)")
ax.grid(color=GRID, lw=0.6, zorder=0)
ax.legend(frameon=False, loc="lower right", fontsize=7.5)
lab = {"Eureka Mills": (-78, 2), "Berkley Pit": (-30, -28), "Tar Creek": (8, -12), "Red Dog": (10, -16),
       "Stibnite": (-50, 10), "Bingham": (8, -22), "Jack Waite": (-60, 10)}
for nm, off in lab.items():
    d = s[s.Site_Name == nm].sort_values("screening_score", ascending=False).head(1)
    if len(d):
        ax.annotate("Berkeley Pit" if nm == "Berkley Pit" else nm, (d.CMI.iloc[0], d.log10_HHI.iloc[0]), xytext=off,
                    textcoords="offset points", fontsize=7.5, color=INK,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
fig.tight_layout()
fig.savefig(PUB / "Figure4_cmi_vs_hhi.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 5 elements
c = long[long.is_critical & long.ef_valid & long.Ftr_ID.isin(s.Ftr_ID)]
cn = c[c.EF >= 5].groupby("species").Ftr_ID.nunique().sort_values(ascending=True).tail(20)
fig, ax = plt.subplots(figsize=(6.4, 4.9))
ax.barh(cn.index, cn.values, color="#2a78d6", height=0.7)
for y, v in enumerate(cn.values):
    ax.text(v + 4, y, f"{v}", va="center", fontsize=7, color=INK2)
ax.set_xlabel(f"Scored features with median enrichment factor >= 5 (n = {S['features_scored']:,})")
ax.grid(axis="x", color=GRID, lw=0.6), ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(PUB / "Figure5_critical_elements.png")
plt.close(fig)

# ---------------------------------------------------------------- tables
def num(v):
    v = float(v)
    if v >= 1000:
        return f"{v:,.1f}".rstrip("0").rstrip(".")
    if v >= 1:
        return f"{v:.4g}"
    return f"{v:.3g}"


fmt = lambda v: f"{v:,.0f}" if v >= 100 else (f"{v:.1f}" if v >= 1 else f"{v:.2g}")  # noqa: E731
top = site[site.confidence.isin(["A", "B"])].head(15)
t3 = [[int(r.site_rank), "Berkeley Pit" if r.Site_Name == "Berkley Pit" else r.Site_Name, r.State, r.confidence,
       f"{r.CMI:.1f}", fmt(10 ** r.log10_HHI), r.top_critical, r.top_hazard] for r in top.itertuples()]
gaps = f[f.confidence == "U"].sort_values("Area_SqKm", ascending=False).head(10)
t4 = [[r.Ftr_ID, r.Site_Name, r.State, r.Ftr_Type, f"{r.Area_SqKm:.2f}", str(r.Commodity)] for r in gaps.itertuples()]
t5 = [["Default (this study)", "Arsenic RSL 35 mg/kg (noncancer); median per element; all 58 critical elements", "-", "-"],
      ["Cancer-based arsenic RSL (0.68 mg/kg)", "HHI rank vs default", f"{S['rho_as']:.3f}", f"{S['top100_overlap_as']} of top 100 shared"],
      ["Arsenic share of HHI", "Median across features", f"{S['as_share_pct']}% (default)", f"{S['as_share_cancer_pct']}% (cancer RSL)"],
      ["Maximum instead of median", "CMI rank vs default", f"{S['rho_max']:.3f}", "-"],
      ["Remove 13 shared critical/hazard metals", "CMI rank vs default", f"{S['rho_nonhazard']:.3f}", "-"],
      ["CMI vs HHI", "Rank correlation across scored features", f"{S['rho_cmi_hhi']:.3f}", "-"],
      ["Hazard without arsenic", "Features with >= 1 metal median above its RSL", f"{S['features_exceed_noAs']:,}", f"{S['features_pb_over_rsl']} with Pb >= 200 mg/kg"]]
# appendix A1: critical elements and background
crit = pd.read_csv(REF / "critical_minerals_2025.csv")
bg = pd.read_csv(OUT / "background_values_used.csv").set_index("species")
src = {"USGS soil (Geochemical Landscapes) median": "Soil", "Upper continental crust (Rudnick and Gao 2014)": "UCC",
       "USGS soil median, mostly nondetect (upper bound; EF conservative)": "Soil (upper bound)"}
a1 = []
for r in crit.itertuples():
    sp = r.species if isinstance(r.species, str) else ""
    if sp and sp in bg.index:
        a1.append([r.mineral, sp, num(bg.loc[sp, "background_ppm"]), src[bg.loc[sp, "source"]]])
    else:
        a1.append([r.mineral, sp or "-", "-", "Not scored" if sp else "Not measurable as an element"])
haz = pd.read_csv(REF / "hazard_metals_rsl.csv")
a2 = []
for r in haz.itertuples():
    used = r.alt_noncancer_mgkg if r.species == "As" else r.rsl_resident_mgkg
    a2.append([r.species, r.rsl_analyte.lstrip("~"), f"{used:g}", "noncancer (child, THQ 1)" if r.species == "As" else r.basis,
               f"{r.rsl_resident_mgkg:g} (cancer, sensitivity)" if r.species == "As" else "-"])
tg = pd.read_csv(ROOT / "verify/spotcheck_targets.csv")
a3 = [[int(r.check), r.kind.replace("extreme: ", "extreme, ").replace(" (cancer As)", " (cancer-based As)"), r.Ftr_ID, "Berkeley Pit" if r.site == "Berkley Pit" else r.site, r.element,
       "-" if pd.isna(r.n_samples_with_element) else int(r.n_samples_with_element), num(r.table_median_ppm)] for r in tg.itertuples()]
st_t = f.groupby("State").agg(features=("Ftr_ID", "size"), sites=("Site_ID", "nunique"),
                              t1=("best_tier", lambda v: int((v == 1).sum())), unsampled=("confidence", lambda v: int((v == "U").sum())),
                              dual=("priority", lambda v: int((v == "Dual").sum())), res=("priority", lambda v: int((v == "Resource").sum())),
                              hz=("priority", lambda v: int((v == "Hazard").sum()))).reset_index()
a4 = [[r.State, r.features, r.sites, r.t1, r.unsampled, r.dual, r.res, r.hz] for r in st_t.itertuples()]
a4.append(["Total", int(st_t.features.sum()), int(st_t.sites.sum()), int(st_t.t1.sum()), int(st_t.unsampled.sum()),
           int(st_t.dual.sum()), int(st_t.res.sum()), int(st_t.hz.sum())])
json.dump({"t3": t3, "t4": t4, "t5": t5, "a1": a1, "a2": a2, "a3": a3, "a4": a4}, open(PUB / "pub_tables.json", "w"), indent=1, default=int)
print("pub figures and tables written; A1 rows", len(a1), "A4 total", a4[-1])
