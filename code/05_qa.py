"""05_qa.py: quality checks, sensitivity tests, and the stats file.

Plain-language note: this script checks the results before anyone trusts
them. It counts rows at each step, tests whether piles from (say) a lead
mine actually show lead enrichment, reruns the scores under different
choices to see whether the rankings hold up, and writes every number the
paper and atlas quote into paper/stats.json. Read data/processed/qa_report.txt.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
INT, OUT, REF = ROOT / "data/interim", ROOT / "data/processed", ROOT / "data/reference"
PAPER = ROOT / "paper"
PAPER.mkdir(exist_ok=True)

lc = json.loads((INT / "link_counts.json").read_text())
vc = json.loads((INT / "values_counts.json").read_text())
sc = json.loads((INT / "score_counts.json").read_text())
f = pd.read_csv(OUT / "nmwi_screening_features.csv")
s = pd.read_csv(OUT / "nmwi_screening_sites.csv")
long = pd.read_csv(OUT / "feature_element_long.csv")
links = pd.read_parquet(INT / "links.parquet")
haz = pd.read_csv(REF / "hazard_metals_rsl.csv")
L = []
P = lambda *a: L.append(" ".join(str(x) for x in a))  # noqa: E731
scored = f[f.confidence != "U"]

import sys
FINAL = "--final" in sys.argv
P("QA REPORT: U.S. Mine Waste Critical Mineral Screening Atlas" + ("" if FINAL else "  [DRAFT]"))
P("=" * 72)
P("\n1. ROW COUNTS")
for k in ["nmwi_points", "nmwi_polygons", "nmwi_unique_ftr_id", "nmwi_sites", "nmwi_states",
          "geochem_samples_total", "geochem_excluded_class", "geochem_excluded_concentrate",
          "geochem_samples_eligible", "link_pairs", "linked_samples_unique"]:
    P(f"  {k:32s} {lc[k]:>12,}")
for k, v in vc.items():
    P(f"  {k:32s} {v:>12,}")
P(f"  output feature rows              {len(f):>12,}  (expect {lc['nmwi_unique_ftr_id']:,})")
P(f"  output site rows                 {len(s):>12,}  (expect {lc['nmwi_sites']:,})")
assert len(f) == lc["nmwi_unique_ftr_id"] and len(s) == lc["nmwi_sites"]
assert f.Ftr_ID.is_unique

P("\n2. MATCH RATES")
n = lc["nmwi_unique_ftr_id"]
P(f"  features with >=1 sample within 1 km : {lc['features_tier1_any']:,} ({lc['features_tier1_any']/n:.1%})")
P(f"  features with >=1 sample within 2 km : {lc['features_tier12_any']:,} ({lc['features_tier12_any']/n:.1%})")
P(f"  features with no sample within 2 km  : {lc['features_none_2km']:,} ({lc['features_none_2km']/n:.1%})")
un = f[f.confidence == "U"].groupby("State").size().sort_values(ascending=False)
P("  unsampled features by state         : " + ", ".join(f"{k} {v}" for k, v in un.items()))
P(f"  confidence grades                    : {sc['confidence']}")
ow = links[links.on_waste].Ftr_ID.nunique()
P(f"  features with >=1 on-waste sample <=2 km: {ow:,}")

P("\n3. RANGE AND SANITY CHECKS")
for c in ["CMI", "CMI_nonhazard", "log10_HHI", "n_exceed", "n_samples", "nearest_m"]:
    d = scored[c]
    P(f"  {c:14s} min {d.min():9.3g}  median {d.median():9.3g}  max {d.max():9.3g}  missing {d.isna().sum()}")
assert scored.CMI.between(0, 15).all()
assert (scored.nearest_m <= 2000).all()
cap = (long.log_EF_pos >= 3).sum()
P(f"  element values hitting the 1000x enrichment cap: {cap:,} of {len(long):,}")
inv = long[long.is_critical & ~long.ef_valid]
P(f"  critical element medians set aside as nondetect: {len(inv):,} "
  f"(top: {inv.species.value_counts().head(6).to_dict()})")

P("\n4. VALIDATION: DOES THE SCORE FIND THE METAL EACH MINE PRODUCED?")
SYM = {"lead": "Pb", "zinc": "Zn", "silver": "Ag", "copper": "Cu", "molybdenum": "Mo", "antimony": "Sb",
       "tungsten": "W", "manganese": "Mn", "cadmium": "Cd", "vanadium": "V", "uranium": "U", "cobalt": "Co",
       "nickel": "Ni", "bismuth": "Bi", "tin": "Sn", "arsenic": "As", "mercury": "Hg", "beryllium": "Be",
       "lithium": "Li", "tellurium": "Te", "indium": "In", "germanium": "Ge", "gallium": "Ga"}
bg = pd.read_csv(OUT / "background_values_used.csv").set_index("species").background_ppm
ef = long.copy()
ef["EF_all"] = ef.median_ppm / ef.species.map(bg)  # includes hazard-only elements (Cd, Hg, Mo)
efd = {(a, b): v for a, b, v in zip(ef.Ftr_ID, ef.species, ef.EF_all)}
val = []
for _, r in scored.iterrows():
    com = [c.split("(")[0].strip().lower() for c in str(r.Commodity).split(";")]
    sy = sorted({SYM[c] for c in com if c in SYM})
    tested = [x for x in sy if (r.Ftr_ID, x) in efd]
    if tested:
        val.append({"Ftr_ID": r.Ftr_ID, "hit": any(efd[(r.Ftr_ID, x)] >= 5 for x in tested)})
val = pd.DataFrame(val)
hit_rate = float(val.hit.mean())
P(f"  features with a listed metal commodity measured nearby: {len(val):,}")
P(f"  ... at least one commodity metal enriched >=5x over background: {val.hit.sum():,} ({hit_rate:.1%})")
# null comparison: unsampled-distance control. Same test using samples 1-2 km away only
t2 = links[links.tier == 2]

P("\n5. SENSITIVITY TESTS")
h = long[long.is_hazard].copy()
isas = (h.species == "As") & h.HQ.notna()
h_alt = h.copy()
h_alt.loc[isas, "HQ"] = h_alt.loc[isas, "HQ_cancer_As"]  # alternative: cancer-based As (0.68 mg/kg)
hhi_alt = np.log10(h_alt.groupby("Ftr_ID").HQ.sum(min_count=1))
m = scored.set_index("Ftr_ID").join(hhi_alt.rename("hhi_alt"))
rho_as = spearmanr(m.log10_HHI, m.hhi_alt, nan_policy="omit").statistic
top_c = set(m.log10_HHI.nlargest(100).index)
top_n = set(m.hhi_alt.nlargest(100).index)
P(f"  V3 default arsenic RSL = noncancer 35 mg/kg (author decision). Alternative cancer 0.68 mg/kg: "
  f"Spearman rho of HHI = {rho_as:.3f}; top-100 overlap = {len(top_c & top_n)}")
share = lambda d: (d[d.species == "As"].set_index("Ftr_ID").HQ / d.groupby("Ftr_ID").HQ.sum()).median()  # noqa: E731
as_share, as_share_cancer = float(share(h)), float(share(h_alt))
P(f"  median share of HHI contributed by arsenic: default {as_share:.1%}; with cancer RSL {as_share_cancer:.1%}")
rho_nh = spearmanr(scored.CMI, scored.CMI_nonhazard).statistic
P(f"  CMI vs CMI without the 13 hazard-list metals: Spearman rho = {rho_nh:.3f}")
mx = long[long.is_critical & long.ef_valid].copy()
mx["lmax"] = np.clip(np.log10(mx.EF_max), 0, 3)
cmi_max = mx.groupby("Ftr_ID").lmax.apply(lambda v: np.sort(v.values)[::-1][:5].sum())
mm = scored.set_index("Ftr_ID").join(cmi_max.rename("cmi_max"))
rho_mx = spearmanr(mm.CMI, mm.cmi_max, nan_policy="omit").statistic
P(f"  V2 median vs maximum value per element: Spearman rho of CMI = {rho_mx:.3f}")
rho_ch = spearmanr(scored.CMI, scored.log10_HHI).statistic
P(f"  CMI vs HHI correlation across scored features: Spearman rho = {rho_ch:.3f}")

P("\n6. NAMED SPOT CHECKS (author verifies by hand; see docs/VERIFY_CHECKLIST.md)")
names = ["Tar Creek", "Stibnite", "Red Dog", "Bingham", "Berkley Pit"]
spots = []
for nm in names:
    r = s[s.Site_Name == nm].iloc[0]
    P(f"  {nm:12s} site {r.Site_ID} rank {int(r.site_rank)}  priority {r.priority}  conf {r.confidence}")
    P(f"      top critical: {r.top_critical}")
    P(f"      top hazard  : {r.top_hazard}")
    spots.append({"site": nm, "Site_ID": r.Site_ID, "rank": int(r.site_rank), "priority": r.priority,
                  "top_critical": r.top_critical, "top_hazard": r.top_hazard, "lead_feature": r.lead_feature})
u = f[f.confidence == "U"].sort_values("Area_SqKm", ascending=False).head(5)
P("  largest unsampled features (sampling gaps):")
for _, r in u.iterrows():
    P(f"      {r.Ftr_ID} {r.Site_Name} ({r.State}) {r.Ftr_Type}, {r.Area_SqKm:.2f} km2")

P("\n7. THRESHOLD COUNTS QUOTED IN DOCUMENTS")
P(f"  priority (features): {sc['priority']}")
P(f"  priority (sites)   : {sc['site_priority']}")
P(f"  CMI cut (top third) = {sc['cmi_cut']:.3f}; log10 HHI cut = {sc['hhi_cut_log10']:.3f}")
exc_noas = int((scored.n_exceed_noAs >= 1).sum())
P(f"  scored features with >=1 metal over its RSL (excluding As): {exc_noas:,}")
pb400 = int((scored.Pb_median_ppm >= 200).sum())
P(f"  scored features with median Pb >= 200 mg/kg (RSL): {pb400:,}")

(OUT / "qa_report.txt").write_text("\n".join(L) + "\n")
print("\n".join(L))

dual_sites = s[s.priority == "Dual"]
stats = {
    **{k: lc[k] for k in lc}, **vc,
    "features_scored": sc["features_scored"], "features_unsampled": sc["features_unsampled"],
    "pct_tier1": round(100 * lc["features_tier1_any"] / n, 1),
    "pct_tier12": round(100 * lc["features_tier12_any"] / n, 1),
    "conf_A": sc["confidence"].get("A", 0), "conf_B": sc["confidence"].get("B", 0),
    "conf_C": sc["confidence"].get("C", 0), "conf_U": sc["confidence"].get("U", 0),
    "feat_dual": sc["priority"].get("Dual", 0), "feat_resource": sc["priority"].get("Resource", 0),
    "feat_hazard": sc["priority"].get("Hazard", 0), "feat_lower": sc["priority"].get("Lower", 0),
    "sites_scored": sc["sites_scored"], "site_dual": sc["site_priority"].get("Dual", 0),
    "site_resource": sc["site_priority"].get("Resource", 0), "site_hazard": sc["site_priority"].get("Hazard", 0),
    "site_unsampled": sc["site_priority"].get("Unsampled", 0),
    "dual_site_states": int(dual_sites.State.nunique()),
    "validation_n": int(len(val)), "validation_hits": int(val.hit.sum()), "validation_pct": round(100 * hit_rate, 1),
    "rho_as": round(float(rho_as), 3), "as_share_pct": round(100 * as_share, 1), "as_share_cancer_pct": round(100 * as_share_cancer, 1),
    "as_mode": sc["as_mode"],
    "rho_nonhazard": round(float(rho_nh), 3), "rho_max": round(float(rho_mx), 3), "rho_cmi_hhi": round(float(rho_ch), 3),
    "top100_overlap_as": len(top_c & top_n),
    "cmi_cut": round(sc["cmi_cut"], 2), "hhi_cut_log10": round(sc["hhi_cut_log10"], 2),
    "crit_species_listed": sc["crit_species_listed"], "crit_species_with_background": sc["crit_species_with_background"],
    "features_exceed_noAs": exc_noas, "features_pb_over_rsl": pb400, "features_on_waste_sample": int(ow),
    "spot_checks": spots, "draft": not FINAL,
}
old = json.loads((PAPER / "stats.json").read_text()) if (PAPER / "stats.json").exists() else {}
for k in ("zenodo_doi", "release_date"):
    if k in old:
        stats[k] = old[k]
(PAPER / "stats.json").write_text(json.dumps(stats, indent=2, default=int))
