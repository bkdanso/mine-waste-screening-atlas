"""07_atlas.py: build the public web atlas (docs/atlas/index.html) for GitHub Pages.

Plain-language note: this fills the web page template with the scored data
and copies the downloadable tables next to it. Run with --final after
verification to remove the DRAFT banner.
"""
import json
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT, ATLAS = ROOT / "data/processed", ROOT / "docs/atlas"
(ATLAS / "data").mkdir(parents=True, exist_ok=True)
FINAL = "--final" in sys.argv
stats = json.loads((ROOT / "paper/stats.json").read_text())
auth = json.loads((ROOT / "AUTHORS.json").read_text())["authors"][0]
VERSION = (ROOT / "VERSION").read_text().strip() if (ROOT / "VERSION").exists() else "0.1.0"
DOI = stats.get("zenodo_doi", "[DOI pending]")
if "zenodo_doi" in stats:
    DOI = f'<a href="https://doi.org/{DOI}">{DOI}</a>'

f = pd.read_csv(OUT / "nmwi_screening_features.csv")
cols = ["Ftr_ID", "Site_Name", "Ftr_Name", "Ftr_Type", "Mine_Name", "Mine_Dist", "State", "Latitude", "Longitude",
        "Commodity", "n_samples", "CMI", "HHI", "top_critical", "top_hazard", "priority", "confidence",
        "screening_rank"]
d = f[cols].copy()
d["Latitude"] = d.Latitude.round(5)
d["Longitude"] = d.Longitude.round(5)
d["CMI"] = d.CMI.round(2)
d["HHI"] = d.HHI.apply(lambda v: float(f"{v:.3g}") if pd.notna(v) else None)
d = d.replace({np.nan: None})
meta = {"features": stats["nmwi_unique_ftr_id"], "scored": stats["features_scored"],
        "dual_sites": stats["site_dual"], "unsampled": stats["features_unsampled"], "draft": not FINAL}

html = (ROOT / "code/atlas_template.html").read_text()
for k, v in {"__DATA__": json.dumps(d.to_dict("records"), separators=(",", ":")),
             "__META__": json.dumps(meta), "__AUTHOR__": auth["name"], "__ORCID__": auth["orcid"],
             "__GITHUB__": auth["github"], "__REPO__": "mine-waste-screening-atlas", "__VERSION__": VERSION,
             "__DATE__": pd.Timestamp.today().strftime("%Y-%m-%d"), "__DOI__": DOI}.items():
    html = html.replace(k, v)
if FINAL:
    html = re.sub(r'<div class="draft" id="draftbar">.*?</div>\n', "", html)
(ATLAS / "index.html").write_text(html)
for name in ["nmwi_screening_features.csv", "nmwi_screening_sites.csv", "feature_element_long.csv"]:
    shutil.copy(OUT / name, ATLAS / "data" / name)
print(f"atlas written: {(ATLAS / 'index.html').stat().st_size/1e3:.0f} kB, {len(d)} features")
