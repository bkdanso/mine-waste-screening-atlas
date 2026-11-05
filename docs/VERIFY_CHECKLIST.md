# Your verification checklist

**Status (2026-11-01): Parts 1 to 4 completed by the author. Decisions: V1 keep 1 km / 2 km; V2 keep median; V3 noncancer arsenic (35 mg/kg) for ranking; V4 keep top third; V5 keep small-sample scores, flagged. Part 5: README summary and final manuscript done (2026-11-01); remaining items open.**

*Plain-language version: before anything goes public under your name, you check it. Total time: about 1.5 to 2 hours, in one sitting. Tick each box and write the date. When every box is ticked, tell Claude in your own words that you have checked the package and approve publishing.*

*The publish gate (`publish_gate.py`) checks the mechanical items, like leftover DRAFT stamps and placeholders, automatically. The items below are yours.*

Files you will open (all in the project folder, which Claude will send you as a zip):

- `data/processed/nmwi_screening_features.csv`, the main table. It opens in Excel or Google Sheets.
- `verify/spotcheck_targets.csv`, the 14 checks below, with what the table says.
- `verify/spotcheck_raw.csv`, every raw lab result behind those 14 checks, pulled straight from the original USGS download.
- `data/processed/qa_report.txt`, the quality report.

## Part 1: Make sure the results can be rebuilt (15 to 30 min)

Pick one:

- [ ] **Option A, run it yourself.** In a terminal inside the project folder, paste:
  `pip install -r requirements.txt && npm install && ./run_all.sh`
  It takes about 5 minutes. The last line should read:
  `features 1498 | within 2 km 1324 | dual sites 84 | validation 79.8 %` (83 before the V3 arsenic decision)
- [ ] **Option B, ask Claude.** In a new chat with Opus 5.5 or Fable 5, upload the project zip and say: "Re-run this pipeline from scratch with run_all.sh and give me the headline numbers." They should match the line above.

Then:

- [ ] Open `data/processed/qa_report.txt`. Under "1. ROW COUNTS", the output feature rows (1,498) and site rows (343) match the expected values on the same lines.
- [ ] Pick any three numbers in the paper's abstract and find each one in `paper/stats.json`. Date: ___

## Part 2: Check the sources (15 min)

Open each link. Each page should load, be free, and show the version listed.

- [ ] Mine waste inventory: https://doi.org/10.5066/P148EEUA. The title should say "ver. 2.0, October 2026". License: public domain (U.S. government work).
- [ ] Geochemical database: https://doi.org/10.5066/P1FXE9GK. The page should list "1,524,014 rock, sediment, soil, and mineral samples". License: public domain.
- [ ] EPA screening levels: https://www.epa.gov/risk/regional-screening-levels-rsls-generic-tables. Check whether a table newer than November 2024 has been posted. If one has, tell Claude so the build can be updated. Newest edition seen: ___
- [ ] Critical minerals list: https://www.federalregister.gov/documents/2025/11/07/2025-19813/final-2025-list-of-critical-minerals. Compare the 60 names with `data/reference/critical_minerals_2025.csv`.
- [ ] Crustal values: open Rudnick and Gao (2014) Table 3 (a free PDF is at https://www.geol.umd.edu/~rudnick/PDF/Rudnick_Gao_Treatise.pdf). Check 5 values in `data/reference/ucc_rudnick_gao_2014.csv`: Ge 1.4, Nd 27, Dy 3.9, Ta 0.9, Ag 53 ng/g (0.053 ppm). Claude already matched all 24 against a published digital copy of the table.
- [ ] EPA values: open the EPA Summary Table (THQ 1.0, xlsx) from the EPA page. Find "Arsenic, Inorganic" (resident soil 0.68), "Cobalt" (23), "Thallium (Soluble Salts)" (0.78), and "~Lead and Compounds" (200). They should match `data/reference/hazard_metals_rsl.csv`.

## Part 3: Check rows by hand (40 to 50 min)

For each check, open `verify/spotcheck_raw.csv` and filter the `check` column to the number. For each `lab_id`, keep the row with the best `bestvalue_rank` (A before P, then the smallest number). Negative values are nondetects: halve them and drop the minus sign. `pct` values: multiply by 10,000. Then take the median of the kept values. It should match `table_median_ppm` in `verify/spotcheck_targets.csv`.

To check that a pile is real and correctly described, open the USGS viewer at https://mrdata.usgs.gov/earthmri/minewaste/, zoom to the latitude and longitude, and click the feature.

**Known sites** (places with published reports you can compare against):

- [ ] Check 1. Tar Creek, OK (feature OK000001-003, tailings): cadmium median 6,145 mg/kg from 2 rock samples (enrichment about 30,700x). Is a sphalerite-rich sample this high plausible to you? ___
- [ ] Check 2. Tar Creek, same feature: germanium median 50.5 mg/kg (36x). This agrees with USGS Fact Sheet 2025-3026 (https://doi.org/10.3133/fs20253026), which reports germanium with zinc at Tar Creek. ___
- [ ] Check 3. Stibnite, ID (ID000071-001, Hecla Heap Leach): antimony median 1,500 mg/kg from 124 samples. Antimony was the mine's commodity. ___
- [ ] Check 4. Red Dog, AK (AK000001-006, ore stockpile): zinc median 67,600 mg/kg (6.76%) from 74 samples. Note that this feature is an ore stockpile, not tailings. ___
- [ ] Check 5. Bingham, UT (UT000002-003, Black Rock Tailings Pond): copper median 16,600 mg/kg from 10 samples. ___

**Extreme values** (the most likely places for errors):

- [ ] Check 6. Berkley Pit, MT (MT000005-005), the highest-ranked feature: tellurium median 1,197.5 mg/kg from only 2 samples. Look at both raw rows. Do you accept this, or should features with fewer than 3 samples for an element be excluded? ___
- [ ] Check 7. Same feature: arsenic median 12,900 mg/kg from 4 samples (hazard ratio about 19,000 with the cancer-based level). ___
- [ ] Check 8. HB Mine, NM (NM000009-001), the lowest hazard: lead 5 mg/kg from 1 sample. ___
- [ ] Check 9. Silver Bell, AZ (AZ000017-010), the largest enrichment of any element: bismuth median 15,001.6 mg/kg from 2 samples. One is a stream sediment at 3.21 mg/kg, and the other is a rock analyzed by an old semi-quantitative method at 30,000 mg/kg. This is the "near is not in" problem from LIMITATIONS item 1. Keep as is? ___

**Random rows** (picked by the computer, seed 42):

- [ ] Check 10. Golden Chest, ID (ID000017-001): silver median 2.5 mg/kg, 9 samples.
- [ ] Check 11. Minnesota Mine, NV (NV000009-002): copper median 500 mg/kg, 7 samples.
- [ ] Check 12. Moss, AZ (AZ000024-002): silver median 7.0 mg/kg, 11 samples.
- [ ] Check 13. Sierrita-Esperanza, AZ (AZ000005-001): rhenium median 0.1565 mg/kg, 2 samples.
- [ ] Check 14. Continental Mine, NM (NM000002-002): indium median 3.2 mg/kg, 5 samples.

## Part 4: Your decisions (15 min)

The build made these choices provisionally. Agree or change each one.

- [ ] **V1. Distance.** Samples within 1 km count first, and 1 to 2 km is the fallback. Changing to 1 km only leaves 452 features unscored instead of 174. **Recommended: keep 1 km / 2 km.** Your choice: ___
- [ ] **V2. Typical value.** The score uses each element's median across nearby samples, not its maximum. Using the maximum agrees only moderately with the median version (rank agreement 0.73) and is driven by single ore specimens. **Recommended: keep median.** Your choice: ___
- [ ] **V3. Arsenic benchmark.** EPA's cancer-based level is 0.68 mg/kg, below typical U.S. soil (5.6 mg/kg). With it, arsenic makes up a median of 84% of each pile's hazard score. The noncancer level is 35 mg/kg: then the hazard score reflects lead, cadmium, thallium, and others more evenly, and 57 of the top 100 hazard features stay in the top 100. **Recommended: switch to 35 mg/kg (noncancer) for the ranking, and keep the cancer value in the element table and the paper's sensitivity section.** Your choice: ___
- [ ] **V4. Priority cutoffs.** "Dual" means the top third on both scores, which gives 83 sites. Top quarter would give fewer sites and a sharper list. **Recommended: keep top third for v0.1.** Your choice: ___
- [ ] **V5. Small sample counts.** Some high scores rest on 1 or 2 samples (checks 6 and 9). Option A: keep them, since the confidence grade already shows this. Option B: require at least 3 samples per element for enrichment to count. **Recommended: A for v0.1, and mention it in the paper.** Your choice: ___

## Part 5: Before it goes public (20 to 30 min)

- [x] (2026-11-01, author's text in README) Rewrite the README summary paragraph (it is marked "[author to rewrite in own words before release]") and the paper abstract in your own words. Claude can do this with you line by line.
- [ ] Read the paper's Discussion. Change any sentence you could not defend to a colleague.
- [ ] Your name, ORCID (0009-0006-1201-4129), affiliation, and email are correct in `AUTHORS.json`.
- [ ] You have read `docs/LIMITATIONS.md` and agree with it.
- [ ] Claude regenerates everything with `--final`, and `publish_gate.py` passes.
- [ ] Evidence log row written on release day (`docs/evidence_log.csv`).

**When every box is ticked, reply to Claude in your own words that you have checked the package and approve publishing.**
