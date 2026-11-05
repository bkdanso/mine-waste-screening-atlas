# Codebook

*Plain-language note: this lists every column in the output tables, what it means, and how it was calculated. Open it when you need to explain a number.*

## `nmwi_screening_features.csv` (one row per mine waste feature)

| Column | Meaning | Source or calculation |
|---|---|---|
| Ftr_ID, Site_ID | NMWI feature and site identifiers | NMWI v2.0 |
| Site_Name, Ftr_Name, Ftr_Type, Mine_Name, Mine_Dist, State, County, Latitude, Longitude, Commodity, Reclaimed, Superfund, Land_Mng | Descriptive fields copied unchanged | NMWI v2.0 Waste_Points |
| Area_SqKm | Feature area, square kilometers | NMWI v2.0 Waste_Polygons |
| Dep_Type_1 | Primary deposit type | NMWI v2.0 Waste_Geology |
| best_tier | 1 if scored from samples inside or within 1 km of the polygon edge; 2 if only 1 to 2 km samples exist | computed |
| n_samples | Distinct samples used for scoring (those in best_tier) | computed |
| n_tier1, n_within_2km | Distinct samples within 1 km and within 2 km | computed |
| n_on_waste | Samples used whose source is recorded as mine dump, tailings, waste, slag, or mill | from `sample_source` / `specific_name` |
| nearest_m | Distance in meters from the nearest used sample to the polygon (0 = inside) | EPSG:5070 (Alaska EPSG:3338) |
| CMI | Critical Mineral Index: sum of the 5 largest values of max(0, log10 EF) over critical elements, each capped at 3. Range 0 to 15. | see `feature_element_long.csv` |
| CMI_nonhazard | Same, excluding the 13 elements also on the hazard list | sensitivity |
| CMI_rank | Rank by CMI, 1 = highest | |
| n_crit_measured | Critical elements with at least one value and a background | |
| n_crit_EF5 | Critical elements with valid EF of at least 5 | |
| top_critical | Up to 5 critical elements with EF of at least 5, as "element EFx" | |
| HHI | Heavy-metal Hazard Index: sum of hazard ratios (HQ) over 18 metals with a detected median | |
| log10_HHI | log10 of HHI | |
| HHI_rank | Rank by HHI, 1 = highest | |
| n_haz_measured | Hazard metals with at least one value | |
| n_exceed, n_exceed_noAs | Metals with HQ of at least 1; same excluding arsenic | |
| HEF | Sum of 5 largest log10 EFs over hazard metals (enrichment view of hazard) | |
| top_hazard | Up to 5 metals with HQ of at least 1, as "element HQx" | |
| As_median_ppm, Pb_median_ppm | Feature median arsenic and lead, mg/kg (nondetects at half limit) | |
| screening_score | Mean of CMI percentile and HHI percentile (0 to 100) | |
| screening_rank | Rank by screening_score, 1 = highest | |
| priority | Dual: CMI and HHI both in top third of scored features. Resource: CMI only. Hazard: HHI only. Lower: neither. Unsampled: no sample within 2 km. | cutoffs in `qa_report.txt` |
| confidence | A: best_tier 1, at least 5 tier 1 samples, at least 1 on-waste. B: best_tier 1, at least 3 tier 1 samples. C: otherwise. U: unsampled. | |

## `feature_element_long.csv` (one row per feature and element)

| Column | Meaning |
|---|---|
| n | Samples with a value for this element |
| median_ppm, max_ppm | Median and maximum across samples, mg/kg |
| nd_frac | Share of those values that are nondetects |
| n_on_waste | On-waste samples among them |
| background_ppm | Background used (see `background_values_used.csv`) |
| EF, EF_max | median / background; max / background. EF blank when the median is a nondetect (nd_frac of 0.5 or more) |
| log_EF_pos | max(0, log10 EF) capped at 3; 0 when EF is blank |
| ef_valid | True when nd_frac is below 0.5 |
| is_critical, is_hazard | On the 2025 critical list; on the 18-metal hazard list |
| RSL_mgkg | EPA residential soil screening level used |
| HQ, HQ_max | median / RSL; max / RSL. HQ blank when the median is a nondetect |

## Value rules

- **Best value.** For each sample and element, the determination with the best `bestvalue_rank` (Granitto and others, 2019): total methods ("A") before partial ("P"), then lowest number.
- **Units.** ppm as is; pct times 10,000; ppb divided by 1,000. Oxide-basis values were already converted to elements by USGS.
- **Nondetects** (negative `qualified_value`, qualifiers `<`, `N`, `L`): absolute value divided by 2, flagged.
- **Greater-than values** (`>`, `G`, stored with trailing 1s, for example 20.11111): trailing 1s removed and the value used as a lower bound.
- **Excluded samples:** primary class "mineral" or "geologic material" (separates, not bulk), and any sample described as a concentrate or panned.

## Background

Median of soil samples from the USGS "Geochemical Landscapes" survey (Smith and others, 2013) in the same database, for elements with at least 100 samples and under 50% nondetects. Otherwise upper continental crust (Rudnick and Gao, 2014). Tellurium uses the soil median even though most soil values are nondetects; that background is an upper bound, so tellurium enrichment is understated. Rhodium has no background and is not scored. Full list: `data/processed/background_values_used.csv`.

## Hazard metals and screening levels

`data/reference/hazard_metals_rsl.csv`. Each value is checked by `04_scores.py` against the EPA workbook itself. Arsenic uses the cancer-based level (0.68 mg/kg) by default; the noncancer level (35 mg/kg) is the alternative tested in the QA report.
