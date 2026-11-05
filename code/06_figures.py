"""06_figures.py: the paper figures (PNG) for the screening atlas.

Plain-language note: draws the national map, the two-score chart, and the
element chart. Every figure says DRAFT until you approve the results; run
with --final after verification to remove the stamp.
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[1]
OUT, FIG = ROOT / "data/processed", ROOT / "paper/figures"
FIG.mkdir(parents=True, exist_ok=True)
FINAL = "--final" in sys.argv
stats = json.loads((ROOT / "paper/stats.json").read_text())

INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
COL = {"Dual": "#1baf7a", "Resource": "#2a78d6", "Hazard": "#eb6834", "Lower": "#b9b8b2", "Unsampled": "none"}
ORDER = ["Dual", "Resource", "Hazard", "Lower", "Unsampled"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "savefig.facecolor": SURF})


def stamp(fig):
    if not FINAL:
        fig.text(0.99, 0.99, "DRAFT - not verified", ha="right", va="top", color="#e34948", fontsize=9,
                 fontweight="bold")


f = pd.read_csv(OUT / "nmwi_screening_features.csv")
st = gpd.read_file(ROOT / "data/raw/census/cb_2024_us_state_20m.shp")

# ---------------------------------------------------------------- Fig 1 map
fig = plt.figure(figsize=(9, 5.6))
ax = fig.add_axes([0.0, 0.08, 1.0, 0.84])
ax2 = fig.add_axes([0.01, 0.06, 0.24, 0.26])
lower = st[~st.STUSPS.isin(["AK", "HI", "PR"])].to_crs(5070)
ak = st[st.STUSPS == "AK"].to_crs(3338)
pts = gpd.GeoDataFrame(f, geometry=gpd.points_from_xy(f.Longitude, f.Latitude), crs=4269)
for a, base, sub, crs in [(ax, lower, pts[pts.State != "AK"], 5070), (ax2, ak, pts[pts.State == "AK"], 3338)]:
    base.plot(ax=a, color="#f1f0ec", edgecolor="#cfcec8", linewidth=0.5)
    sub = sub.to_crs(crs)
    for k in reversed(ORDER):
        d = sub[sub.priority == k]
        if k == "Unsampled":
            a.scatter(d.geometry.x, d.geometry.y, s=14, facecolor="none", edgecolor=INK2, linewidth=0.8, zorder=3)
        else:
            a.scatter(d.geometry.x, d.geometry.y, s=26 if k == "Dual" else 14, color=COL[k],
                      edgecolor=SURF, linewidth=0.6 if k != "Lower" else 0.3, zorder=4 if k != "Lower" else 2)
    a.set_axis_off()
ax2.set_title("Alaska", fontsize=8, color=INK2, loc="left")
h = [plt.Line2D([], [], marker="o", ls="", markersize=6 if k != "Dual" else 7.5,
                markerfacecolor=COL[k] if k != "Unsampled" else "none",
                markeredgecolor=INK2 if k == "Unsampled" else SURF, label=f"{k} ({stats['feat_' + k.lower()] if k != 'Unsampled' else stats['conf_U']})")
     for k in ORDER]
ax.legend(handles=h, loc="lower right", frameon=False, fontsize=8, title="Priority class (features)",
          title_fontsize=8)
fig.suptitle("Screening priority of U.S. mine waste features", x=0.02, ha="left", fontsize=12, color=INK,
             fontweight="bold")
fig.text(0.02, 0.92, f"{stats['nmwi_unique_ftr_id']:,} features in {stats['nmwi_states']} states, "
         "National Mine Waste Inventory v2.0 (Oct 2026), linked to USGS geochemical samples within 2 km",
         fontsize=8.5, color=INK2)
stamp(fig)
fig.savefig(FIG / "fig1_map.png", dpi=220)
plt.close(fig)

# ---------------------------------------------------------------- Fig 2 scatter
s = f[f.priority != "Unsampled"]
fig, ax = plt.subplots(figsize=(6.6, 5))
for k in ["Lower", "Hazard", "Resource", "Dual"]:
    d = s[s.priority == k]
    ax.scatter(d.CMI, d.log10_HHI, s=16, color=COL[k], edgecolor=SURF, linewidth=0.5, label=k, zorder=3)
ax.axvline(stats["cmi_cut"], color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
ax.axhline(stats["hhi_cut_log10"], color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
ax.set_xlabel("Critical Mineral Index (sum of 5 largest log10 enrichment factors)")
ax.set_ylabel("Heavy-metal Hazard Index, log10 (sum of EPA soil screening ratios)")
ax.grid(color=GRID, lw=0.6, zorder=0)
ax.legend(frameon=False, loc="lower right", fontsize=8)
for nm in ["Tar Creek", "Stibnite", "Red Dog", "Bingham"]:
    d = s[s.Site_Name == nm].sort_values("screening_score", ascending=False).head(1)
    if len(d):
        ax.annotate(nm, (d.CMI.iloc[0], d.log10_HHI.iloc[0]), xytext=(6, -10), textcoords="offset points",
                    fontsize=8, color=INK)
ax.set_title(f"Resource and hazard scores, {stats['features_scored']:,} scored features (Spearman "
             f"rho = {stats['rho_cmi_hhi']})", loc="left", fontsize=9.5, color=INK)
fig.tight_layout()
stamp(fig)
fig.savefig(FIG / "fig2_scores.png", dpi=220)
plt.close(fig)

# ---------------------------------------------------------------- Fig 3 elements
long = pd.read_csv(OUT / "feature_element_long.csv")
c = long[long.is_critical & long.ef_valid & long.Ftr_ID.isin(s.Ftr_ID)]
cnt = c[c.EF >= 5].groupby("species").Ftr_ID.nunique().sort_values(ascending=True).tail(20)
fig, ax = plt.subplots(figsize=(6.6, 5))
ax.barh(cnt.index, cnt.values, color="#2a78d6", height=0.7)
for y, v in enumerate(cnt.values):
    ax.text(v + 5, y, f"{v}", va="center", fontsize=7.5, color=INK2)
ax.set_xlabel("Scored features with median enrichment >= 5x background")
ax.grid(axis="x", color=GRID, lw=0.6)
ax.set_axisbelow(True)
ax.set_title("Critical elements most often enriched in mine waste neighborhoods (top 20)", loc="left",
             fontsize=9.5, color=INK)
fig.tight_layout()
stamp(fig)
fig.savefig(FIG / "fig3_elements.png", dpi=220)
plt.close(fig)
cnt.sort_values(ascending=False).to_csv(ROOT / "paper/tables/element_ef5_counts.csv")
print("figures written")

# ---------------------------------------------------------------- tables for the manuscript
site = pd.read_csv(OUT / "nmwi_screening_sites.csv")
top = site[site.confidence.isin(["A", "B"])].head(15)
tab1 = [{"rank": int(r.site_rank), "site": r.Site_Name, "state": r.State, "conf": r.confidence,
         "cmi": round(r.CMI, 1), "hhi": f"{10 ** r.log10_HHI:.3g}", "crit": r.top_critical, "haz": r.top_hazard}
        for r in top.itertuples()]
gaps = f[f.confidence == "U"].sort_values("Area_SqKm", ascending=False).head(10)
tab2 = [{"id": r.Ftr_ID, "site": r.Site_Name, "state": r.State, "type": r.Ftr_Type,
         "area": round(r.Area_SqKm, 2), "commodity": str(r.Commodity)} for r in gaps.itertuples()]
bgu = pd.read_csv(OUT / "background_values_used.csv")
(ROOT / "paper/tables/tables.json").write_text(json.dumps(
    {"top_sites_AB": tab1, "largest_unsampled": tab2,
     "elements_ef5": cnt.sort_values(ascending=False).head(10).to_dict(),
     "bg_source_counts": bgu.source.value_counts().to_dict()}, indent=2))
pd.DataFrame(tab1).to_csv(ROOT / "paper/tables/table1_top_sites.csv", index=False)
pd.DataFrame(tab2).to_csv(ROOT / "paper/tables/table2_largest_unsampled.csv", index=False)
print("tables written")
