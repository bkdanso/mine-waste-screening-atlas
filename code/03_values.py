"""03_values.py: pick one trustworthy value per element for every linked sample.

Plain-language note: a single sample is often tested several times by
different lab methods. This script keeps the single best result for each
element (USGS's own "best value" ranking), converts everything to mg/kg
(parts per million), and also builds the "typical U.S. soil" background
values. You do not need to open it.

Inputs : data/raw/geochem/tbl_chem.parquet, tbl_parameter_rank.parquet,
         tbl_geol.parquet, data/interim/links.parquet
Outputs: data/interim/sample_values.parquet  (lab_id, species, ppm, censor)
         data/interim/background.csv         (species, median ppm, n)
"""
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GC = ROOT / "data" / "raw" / "geochem"
INT = ROOT / "data" / "interim"

BACKGROUND_PROJECTS = ("Geochemical Landscapes", "Geochem Landscapes")


def gt_lower_bound(v: float) -> float:
    """'>'/'G' values are stored with trailing 1s appended (e.g. 20.11111 means >20)."""
    s = repr(float(v))
    if "." in s:
        whole, frac = s.split(".")
        frac = frac.rstrip("1")
        out = float(whole + "." + frac) if frac else float(whole)
        return out if out > 0 else float(v)
    return float(v)


con = duckdb.connect()
con.sql("SET enable_progress_bar=false")
links = pd.read_parquet(INT / "links.parquet")
ids = pd.DataFrame({"lab_id": links.lab_id.unique()})
con.register("ids", ids)
bg_ids = con.sql(f"""select lab_id from '{GC/'tbl_geol.parquet'}'
                     where project_name in {BACKGROUND_PROJECTS}
                       and primary_class = 'soil'""").df()
con.register("bg_ids", bg_ids)

raw = con.sql(f"""
    with want as (select lab_id, 'link' as role from ids
                  union all select lab_id, 'bg' as role from bg_ids)
    select w.role, c.lab_id, c.species, c.units, c.parameter, c.qualified_value, c.qualifier,
           r.bestvalue_rank
    from '{GC/'tbl_chem.parquet'}' c
    join want w using (lab_id)
    left join '{GC/'tbl_parameter_rank.parquet'}' r using (parameter)
    where c.units in ('ppm','pct','ppb') and c.qualified_value is not null
""").df()

# rank: 'A' (total) before 'P' (partial); lower number better; unranked last
r = raw.bestvalue_rank.fillna("Z99")
raw["rank_key"] = r.str[0].map({"A": 0, "P": 1}).fillna(2) * 1000 + \
    pd.to_numeric(r.str[1:], errors="coerce").fillna(999)
raw = raw.sort_values(["role", "lab_id", "species", "rank_key"])
best = raw.drop_duplicates(["role", "lab_id", "species"], keep="first").copy()

v = best.qualified_value.astype(float)
q = best.qualifier.fillna("")
censor = np.where(v < 0, "nd", np.where(q.isin([">", "G"]), "gt", ""))
val = np.where(v < 0, -v / 2.0, v)  # nondetect -> half detection limit
gt = censor == "gt"
val = np.where(gt, [gt_lower_bound(x) for x in v.where(gt, 1.0)], val)
factor = best.units.map({"ppm": 1.0, "pct": 1e4, "ppb": 1e-3}).values
best["ppm"] = val * factor
best["censor"] = censor
best["is_total"] = best.bestvalue_rank.fillna("").str.startswith("A")

out = best[best.role == "link"][["lab_id", "species", "ppm", "censor", "is_total", "parameter"]]
out.to_parquet(INT / "sample_values.parquet", index=False)

bg = best[best.role == "bg"]
# background: median of detected-or-half-DL values; require >= 100 samples
bgs = bg.groupby("species").agg(bg_median_ppm=("ppm", "median"), bg_n=("ppm", "size"),
                                 bg_nd_frac=("censor", lambda s: float((s == "nd").mean()))).reset_index()
bgs.to_csv(INT / "background.csv", index=False)

stats = {"chem_rows_linked_best": int(len(out)), "linked_samples_with_chem": int(out.lab_id.nunique()),
         "background_samples": int(bg.lab_id.nunique()), "background_species": int(len(bgs))}
(INT / "values_counts.json").write_text(json.dumps(stats, indent=2))
print(json.dumps(stats, indent=2))
print(bgs.to_string())
