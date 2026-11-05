# A National Screening Framework for Critical Mineral Potential and Heavy-Metal Hazard in U.S. Mine Waste: Dataset and Atlas

*Repository and atlas: U.S. Mine Waste Critical Mineral Screening Atlas (Flagship 4).*

**Status: Released v0.1.0 (2026-11-05). Verified by the author. Dataset DOI: [10.5281/zenodo.23986699](https://doi.org/10.5281/zenodo.23986699).**

## Summary

This project provides the first national-scale screening assessment of critical-mineral potential and heavy-metal hazard for mine-waste features in the United States. We linked 1,498 tailings, waste-rock piles, leach facilities, and slag deposits from the U.S. Geological Survey (USGS) National Mine Waste Inventory (Version 2.0) with more than 1.5 million publicly available USGS geochemical samples collected between 1962 and 2023. Using a reproducible geospatial workflow, we calculated a Critical Mineral Index (CMI) based on enrichment relative to U.S. background concentrations and a Heavy-Metal Hazard Index (HHI) based on EPA residential soil screening levels. The result is a free table and map showing which piles to sample first, and which piles have no data at all. And the resulting dataset ranks mine-waste features according to their potential critical-mineral enrichment and environmental concern, identifies sites showing both resource opportunity and hazard, and highlights locations with little or no nearby geochemical information.

- **Atlas (map and searchable table):** `docs/atlas/index.html`, live at https://bkdanso.github.io/mine-waste-screening-atlas/atlas/
- **Dataset DOI:** [10.5281/zenodo.23986699](https://doi.org/10.5281/zenodo.23986699)
- **Preprint:** submitted to EarthArXiv; its DOI will be added here when posted
- **New to this project?** Read [docs/START_HERE.md](docs/START_HERE.md) and [docs/GLOSSARY.md](docs/GLOSSARY.md).

## Headline results (v0.1.0; every number is in `paper/stats.json`)

| | |
|---|---|
| Mine waste features screened | 1,498 at 343 sites, 23 states |
| Features with a public sample within 1 km / 2 km | 1,046 (69.8%) / 1,324 (88.4%) |
| Features with no sample within 2 km | 174 |
| Produced-commodity check (commodity metal enriched at least 5x) | 851 of 1,066 testable features (79.8%) |
| Sites high on both critical-mineral and hazard scores ("Dual") | 84 |

## What is in this repository

| Path | What it is |
|---|---|
| `data/processed/nmwi_screening_features.csv` | **Main table.** One row per mine waste feature with scores, class, confidence. Also `.geojson`. |
| `data/processed/nmwi_screening_sites.csv` | One row per site (the highest-scoring feature represents the site). |
| `data/processed/feature_element_long.csv` | Every feature-by-element value: median, max, enrichment factor, hazard ratio. |
| `data/processed/background_values_used.csv` | The background value used for each element and its source. |
| `data/processed/qa_report.txt` | Quality checks, validation, and sensitivity tests. Read before trusting anything. |
| `data/reference/` | Critical minerals list, EPA screening levels used, crustal background values. |
| `data/raw/PROVENANCE.txt` | Every downloaded file with URL, date, size, and SHA-256 fingerprint. |
| `docs/` | Codebook, limitations, verification checklist, build spec, atlas, publishing guide. |
| `paper/final/` | The author's manuscript (`Danso_Screening_Framework_final.pdf` / `.docx`). |
| `paper/` | Figures (`pub/`, `figures/`), tables, and `stats.json` (every number the paper quotes). |
| `verify/` | Small extracts of raw lab results for hand-checking. |

## How to rebuild from scratch

Needs Python 3.11 or newer, Node.js 18 or newer, and about 1.5 GB of free disk space.

```bash
pip install -r requirements.txt
npm install
./run_all.sh
```

`run_all.sh` downloads the sources (about 300 MB), runs the numbered scripts in `code/` in order, and prints the headline numbers. They should match the table above. The released outputs were built with `./run_all.sh --final`.

## Method in brief

1. **Link.** Each feature polygon is matched to every USGS rock, soil, or sediment sample inside it or within 2 km of its edge (equal-area projection). Samples within 1 km are used when any exist; otherwise samples 1 to 2 km away are used, with lower confidence.
2. **Values.** One best value per sample and element (USGS best-value ranking), converted to mg/kg. Nondetects are set to half the detection limit and never count as enrichment or hazard.
3. **Critical Mineral Index (CMI).** For each element on the 2025 U.S. critical minerals list, enrichment = feature median / typical U.S. soil (USGS national soil survey; crustal values where soil data are missing). CMI = sum of the five largest log10 enrichments, each capped at 1000x (range 0 to 15).
4. **Heavy-metal Hazard Index (HHI).** Sum over 18 metals of feature median / EPA residential soil screening level (November 2024 table; arsenic uses the noncancer level, 35 mg/kg, per author decision V3).
5. **Classes.** Dual, Resource, Hazard (top third on both or one), Lower, Unsampled; confidence A, B, C, U.

Full definitions: [docs/CODEBOOK.md](docs/CODEBOOK.md). Limits: [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Sources (all public U.S. government data)

| Source | Version | License |
|---|---|---|
| U.S. Geological Survey, National Mine Waste Inventory, https://doi.org/10.5066/P148EEUA | v2.0, October 1, 2026 | Public domain |
| Granitto and others, Geochemical data for rock, sediment, soil, and mineral samples, United States and territories, 1962 to 2023, https://doi.org/10.5066/P1FXE9GK | 2026 release (files dated 2025-11-18) | Public domain |
| U.S. EPA Regional Screening Levels, https://www.epa.gov/risk/regional-screening-levels-rsls-generic-tables | November 2024 ("Summary 1124"), current on 2026-10-31 | Public domain |
| Final 2025 List of Critical Minerals, Federal Register, FR Doc. 2025-19813 | November 7, 2025 | Public domain |
| Rudnick and Gao (2014), upper continental crust, https://doi.org/10.1016/B978-0-08-095975-7.00301-6 | Treatise on Geochemistry, 2nd ed. | Cited values |
| U.S. Census Bureau cartographic boundaries (map background only) | 2024, 1:20M | Public domain |

## License and citation

Code: MIT ([LICENSE](LICENSE)). Data, figures, and documents: CC BY 4.0 ([LICENSE-DATA.md](LICENSE-DATA.md)). Cite using [CITATION.cff](CITATION.cff).

Maintainer: Bezali Kwame Danso, Independent Researcher, East Lansing, Michigan, USA. ORCID [0009-0006-1201-4129](https://orcid.org/0009-0006-1201-4129).

AI assistance: code, data processing, and drafting were assisted by Claude (Anthropic) under the author's direction; the author made the analytic decisions and verified the results.
