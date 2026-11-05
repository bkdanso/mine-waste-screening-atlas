"""01_fetch.py: download every public input and log where it came from.

Plain-language note: this downloads the four public sources (about 300 MB in
total, mostly the USGS lab database) into data/raw/ and writes a line per file
to data/raw/PROVENANCE.txt with its size and fingerprint (SHA-256), so anyone
can confirm they used the same files. Already-downloaded files are skipped.

How the URLs were found (2026-10-31):
  - NMWI v2.0 and the geochemical release are ScienceBase items; large files use
    the "catalog/file/get/<item>?name=<file>" route (the JS file-manager link
    does not work from scripts).
  - EPA RSL workbooks are linked from the JS-rendered page
    https://www.epa.gov/risk/regional-screening-levels-rsls-generic-tables ;
    HQ/405270 = Summary Table THQ 1.0 (xlsx), HQ/405274 = Resident Soil THQ 1.0 (xlsx).
    When EPA posts a new edition these IDs change: re-read that page.
"""
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
LOG = RAW / "PROVENANCE.txt"
SB = "https://www.sciencebase.gov/catalog/file/get/"
NMWI, GEO = "686317a5d4be025653d31f09", "63a107a0d34e0de3a1f2795f"

FILES = [
    ("nmwi/USGS_NMWI_v2.zip", f"{SB}{NMWI}?name=USGS_NMWI_v2.zip", "NMWI v2.0, doi:10.5066/P148EEUA"),
    ("nmwi/datadict.csv", f"{SB}{NMWI}?name=USGS_NMWI_v2_datadict.csv", "NMWI v2.0 data dictionary"),
    ("geochem/Geochem_DataRelease_2025_11_18.parquet.zip",
     f"{SB}{GEO}?name=Geochem_DataRelease_2025_11_18.parquet.zip", "Granitto et al. 2026, doi:10.5066/P1FXE9GK"),
    ("geochem/geochem_metadata.xml", f"{SB}{GEO}?name=geochem_metadata.xml", "Granitto et al. 2026 metadata"),
    ("epa_rsl/rsl_405270.xlsx", "https://semspub.epa.gov/src/document/HQ/405270", "EPA RSL Summary THQ=1 (Summary 1124)"),
    ("epa_rsl/rsl_405272.xlsx", "https://semspub.epa.gov/src/document/HQ/405272", "EPA RSL Summary THQ=0.1"),
    ("epa_rsl/rsl_resident_405274.xlsx", "https://semspub.epa.gov/src/document/HQ/405274", "EPA RSL Resident Soil THQ=1"),
    ("census/cb_2024_us_state_20m.zip", "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip",
     "Census state boundaries 1:20M (basemap only)"),
]

for rel, url, note in FILES:
    dest = RAW / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print("have", rel)
        continue
    print("get ", rel)
    urllib.request.urlretrieve(url, dest)
    subprocess.run([sys.executable, str(ROOT / "code/provenance.py"), str(dest), url, "--log", str(LOG),
                    "--note", note], check=True)

for z, to in [("nmwi/USGS_NMWI_v2.zip", "nmwi"), ("geochem/Geochem_DataRelease_2025_11_18.parquet.zip", "geochem"),
              ("census/cb_2024_us_state_20m.zip", "census")]:
    zipfile.ZipFile(RAW / z).extractall(RAW / to)
print("done")
