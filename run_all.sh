#!/usr/bin/env bash
# Rebuild everything from scratch. About 2 minutes after the ~300 MB download.
set -euo pipefail
cd "$(dirname "$0")"
python3 code/01_fetch.py
python3 code/02_link.py
python3 code/03_values.py
python3 code/04_scores.py
python3 code/05_qa.py > /dev/null
python3 code/06_figures.py "$@"
python3 code/07_atlas.py "$@"
python3 code/10_pub_figures.py > /dev/null  # manuscript figures; the manuscript text itself is in paper/final/
python3 code/09_verify_extract.py > /dev/null
echo "Done. Headline numbers:"
python3 -c "import json;s=json.load(open('paper/stats.json'));print('features',s['nmwi_unique_ftr_id'],'| within 2 km',s['features_tier12_any'],'| dual sites',s['site_dual'],'| validation',s['validation_pct'],'%')"
