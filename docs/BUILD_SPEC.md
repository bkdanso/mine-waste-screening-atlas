# Build Spec: U.S. Mine Waste Critical Mineral Screening Atlas

*Plain-language note: this is the one-page plan the code follows. You do not need to read it closely; the plain version is in START_HERE.md. Open it only if you want the exact rules.*

```
PROJECT:   U.S. Mine Waste Critical Mineral Screening Atlas (v0.1).
           Archetypes: dataset (1) + atlas (3) + analysis paper.

QUESTION:  Which mapped U.S. mine waste features already have nearby public
           lab samples showing high critical-mineral enrichment, high
           heavy-metal hazard, or both, and which have no data at all?

SOURCES:
  1. USGS National Mine Waste Inventory v2.0 (Oct 1, 2026),
     doi:10.5066/P148EEUA. Public domain. Accessed 2026-10-31.
     Layers: Waste_Points (1,498), Waste_Polygons, Waste_Geology.
  2. Granitto and others (2026), Geochemical data for rock, sediment, soil,
     and mineral samples, United States and territories, 1962 to 2023,
     doi:10.5066/P1FXE9GK (parquet release 2025-11-18). Public domain.
     1,524,014 samples; 59.8 million determinations.
  3. Background: "Geochemical Landscapes" project samples inside source 2
     (USGS national soil survey of the conterminous U.S.; Smith and
     others, 2013, doi:10.3133/ds801). Median per element = background.
  4. EPA Regional Screening Levels, Summary Table THQ=1.0, edition
     "Summary 1124" (Nov 2024), the edition posted on EPA's generic-tables
     page on 2026-10-31. Public domain. Resident soil column.
  5. Final 2025 List of Critical Minerals, 90 FR (Nov 7, 2025),
     FR Doc. 2025-19813 (60 minerals).

UNIT:      Mine waste feature (NMWI Ftr_ID). Rolled up to site (Site_ID).

LINKAGE:   Distance from each sample to the feature polygon edge (0 if
           inside), equal-area projection (EPSG:5070; Alaska EPSG:3338);
           point location if no polygon.
           Tier 1: inside or within 1 km.  Tier 2: 1 to 2 km.
           Score uses Tier 1 samples if any exist, else Tier 2.
           Samples used: rock, soil, sediment. Mineral separates and
           heavy-mineral concentrates excluded (they overstate grade).
           One value per sample per element: USGS best-value rank
           (total "A" before partial "P", then lowest rank number).
           Nondetects set to half the detection limit and flagged.
           Units converted to mg/kg.

MEASURES:
  EF_e      Enrichment factor = feature median of element e / background
            median of e.
  CMI       Critical Mineral Index = sum of the 5 largest values of
            max(0, log10 EF_e) over critical elements, capped at 3 each
            (range 0-15). Top-5 limits bias from multi-element methods.
            (Revised 2026-10-31 from an all-element sum.)
  ND rule   An element whose feature median is a nondetect (>= 50% ND)
            contributes no enrichment and no hazard. (Added 2026-10-31
            after half-DL values for Te/PGE and old As "<200 ppm" results
            produced false signals.)
  n_crit5   Number of critical elements with EF >= 5.
  HQ_e      Hazard ratio = feature median of e / EPA resident-soil RSL.
            Metals: As, Pb, Cd, Hg, Sb, Tl, Cu, Zn, Ni, Se, Ba, Be, Co,
            Mn, Ag, V, Mo, U. (Cr excluded: lab reports total Cr, RSL is
            species-specific.)
  HHI       Heavy-metal Hazard Index = sum of HQ_e (reported as log10).
  n_exceed  Number of metals with HQ >= 1.
  HEF       Hazard enrichment = sum of max(0, log10 EF) over hazard metals.
  Priority  "Dual" = CMI and HHI both in the top third of scored features;
            "Resource", "Hazard", "Lower", or "Unsampled".
  Confidence A: >=5 Tier 1 samples incl. >=1 taken on mine waste;
            B: >=3 Tier 1 samples; C: Tier 2 only or <3 samples;
            U: no samples within 2 km.

OUTPUTS:   data/processed/nmwi_screening_features.csv (+ .geojson)
           data/processed/nmwi_screening_sites.csv
           data/processed/feature_element_long.csv (every EF and HQ)
           data/processed/qa_report.txt, paper/stats.json, figures,
           docs/atlas/index.html (GitHub Pages), paper/final/Danso_Screening_Framework_final.pdf

VENUES:    GitHub (code + atlas on Pages) -> Zenodo (dataset DOI)
           -> EarthArXiv (preprint, author submits).

VERIFY POINTS (author rules on each):
  V1 Radius tiers 1 km / 2 km.  V2 Median (not max) as the feature value.
  V3 Arsenic RSL is cancer-based (0.68 mg/kg) and below natural background
     almost everywhere; keep, or use the noncancer value (35)?
  V5 Require >= 3 samples per element for enrichment to count?
  V4 Top-third cutoffs for the Priority class.
  V5 Five named spot-check sites against published reports.

LICENSE:   Code MIT. Derived data and documents CC BY 4.0.

ASSUMPTIONS: Author confirmed defaults on 2026-10-31 (tiered radius, full
           2025 critical list, EPA + background hazard, author block,
           CC BY 4.0 + MIT). Samples are screening evidence only, not
           resource estimates; many predate the waste feature or sample
           host rock, not the pile itself.
```
