# Limitations

*Plain-language note: what this project cannot tell you. Read it before you describe the results to anyone.*

1. **Near is not the same as in.** Most samples linked to a pile were not taken from the pile. Many are ore, vein rock, host rock, soil, or stream mud collected for mineral exploration. A high value near a pile can describe the ore deposit, not the waste. Only 343 of 1,498 features have a sample recorded as taken on mine waste within 2 km. The confidence grade and the `n_on_waste` column show this, but do not fix it. Example: Silver Bell (AZ000017-010) gets a bismuth enrichment of about 88,000x from the median of two samples, one of them a single rock analyzed by an old semi-quantitative method at 30,000 mg/kg.
2. **Timing.** Many samples were collected before the waste existed, before reclamation, or decades ago.
3. **Mixed lab methods.** Results span 1962 to 2023 and more than 100 methods with very different detection limits. Old spectrographic methods have high limits and coarse value steps. Nondetects never count as enrichment or hazard here, which avoids false alarms but can miss real signals.
4. **National background.** Enrichment is measured against typical U.S. soil, not local soil. Naturally mineralized districts look enriched even where nothing was mined.
5. **The score is not a resource estimate.** It ignores tonnage, mineral form, recoverability, processing cost, and price. Every critical element counts equally. The 1000x cap means the top features tie at the maximum score.
6. **The hazard score is a screen, not a risk assessment.** EPA residential soil screening levels are a common yardstick. Exceeding one means "look closer", not "unsafe". The ranking uses EPA's noncancer arsenic level (35 mg/kg). With the cancer-based level (0.68 mg/kg, below typical U.S. soil) arsenic would make up a median 84% of each feature's index; with the level used it is about 9%. Chromium is not scored because total chromium cannot be compared with species-specific levels.
7. **Features at the same site often share samples.** Neighboring features can get identical scores. Site-level results avoid double counting.
8. **Few samples.** Some high scores rest on one or two samples for an element (for example Berkeley Pit tellurium, Silver Bell bismuth). They are kept and flagged by the confidence grade (author decision V5).
9. **Coverage follows the inventory.** Only the 23 states in NMWI v2.0 are included. Features under about 2,000 square meters are not in the inventory.
10. **The commodity check is internal.** It shows the method recovers known mining signatures. It is not an independent field validation.
11. **Edition dates.** EPA's newest posted screening table (November 2024) and the 2025 critical minerals list were current on 2026-10-31. Later editions will change some results.
