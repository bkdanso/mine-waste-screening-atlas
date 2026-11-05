"""09_verify_extract.py: build the small spreadsheets the author uses to check results by hand.

Plain-language note: the USGS lab database is too large to open in Excel. This
script pulls, straight from the original download, every raw lab result for the
handful of pile-and-element pairs on your checklist, so you can recompute the
median yourself and compare it with the published table.

Output: verify/spotcheck_targets.csv   one row per check: what the table says
        verify/spotcheck_raw.csv       every raw lab result behind those rows
"""
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GC, INT, OUT = ROOT / "data/raw/geochem", ROOT / "data/interim", ROOT / "data/processed"
V = ROOT / "verify"
V.mkdir(exist_ok=True)

f = pd.read_csv(OUT / "nmwi_screening_features.csv")
s = pd.read_csv(OUT / "nmwi_screening_sites.csv")
long = pd.read_csv(OUT / "feature_element_long.csv")
links = pd.read_parquet(INT / "links.parquet")

# The 14 checks the author verified by hand on 2026-11-01 (selected 2026-10-31 under the
# cancer-arsenic default: known sites, extremes, and 5 random features drawn with seed 42).
# Frozen here so the appendix reports exactly what was verified.
targets = [("known", "OK000001-003", "Cd"), ("known", "OK000001-003", "Ge"), ("known", "ID000071-001", "Sb"),
           ("known", "AK000001-006", "Zn"), ("known", "UT000002-003", "Cu"),
           ("extreme: highest CMI", "MT000005-005", "Te"), ("extreme: highest HHI (cancer As)", "MT000005-005", "As"),
           ("extreme: lowest HHI", "NM000009-001", "Pb"), ("extreme: largest EF overall", "AZ000017-010", "Bi"),
           ("random (seed 42)", "ID000017-001", "Ag"), ("random (seed 42)", "NV000009-002", "Cu"),
           ("random (seed 42)", "AZ000024-002", "Ag"), ("random (seed 42)", "AZ000005-001", "Re"),
           ("random (seed 42)", "NM000002-002", "In")]

rows, want = [], []
for i, (kind, fid, sp) in enumerate(targets, 1):
    l = long[(long.Ftr_ID == fid) & (long.species == sp)]
    fr = f[f.Ftr_ID == fid].iloc[0]
    bt = links[links.Ftr_ID == fid].tier.min()
    labs = links[(links.Ftr_ID == fid) & (links.tier == bt)].lab_id.unique()
    want += [(i, x) for x in labs]
    lr = l.iloc[0] if len(l) else None
    rows.append({"check": i, "kind": kind, "Ftr_ID": fid, "site": fr.Site_Name, "state": fr.State,
                 "element": sp, "tier_used": int(bt), "n_samples_with_element": None if lr is None else int(lr.n),
                 "table_median_ppm": None if lr is None else lr.median_ppm,
                 "background_ppm": None if lr is None else lr.background_ppm,
                 "table_EF": None if lr is None else lr.EF, "table_HQ": None if lr is None else lr.HQ,
                 "lat": fr.Latitude, "lon": fr.Longitude})
tg = pd.DataFrame(rows)
tg.to_csv(V / "spotcheck_targets.csv", index=False, float_format="%.6g")

w = pd.DataFrame(want, columns=["check", "lab_id"]).merge(tg[["check", "element"]], on="check")
con = duckdb.connect()
con.sql("SET enable_progress_bar=false")
con.register("w", w)
raw = con.sql(f"""
  select w.check, c.lab_id, c.species, c.parameter, c.units, c.qualifier, c.qualified_value,
         r.bestvalue_rank, g.primary_class, g.sample_source, g.date_collect, g.latitude, g.longitude
  from '{GC/'tbl_chem.parquet'}' c join w on c.lab_id = w.lab_id and c.species = w.element
  left join '{GC/'tbl_parameter_rank.parquet'}' r using (parameter)
  left join '{GC/'tbl_geol.parquet'}' g on g.lab_id = c.lab_id
  order by w.check, c.lab_id, r.bestvalue_rank
""").df()
raw.to_csv(V / "spotcheck_raw.csv", index=False)
print(tg[["check", "kind", "Ftr_ID", "site", "element", "n_samples_with_element", "table_median_ppm", "table_EF", "table_HQ"]].to_string())
print(len(raw), "raw rows")
