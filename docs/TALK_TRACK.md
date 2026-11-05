# Talking about the Mine Waste Screening Atlas

## 60-second version
**The problem:** The U.S. has thousands of old mine waste piles. Some may hold critical minerals the country imports, and many leak toxic metals. The USGS has now mapped 1,498 of them in 23 states, but a map does not say what is inside, and sampling every pile costs too much.
**What I built:** An open screening atlas that matches every mapped pile to six decades of public USGS lab samples nearby and ranks each pile for critical-mineral enrichment and heavy-metal hazard.
**What it shows:** 88% of piles have some public lab data within 2 km. In about 80% of testable cases the method picks up the metal the mine actually produced. 84 sites stand out on both scores. 174 piles, including some of the largest copper tailings ponds in Arizona and New Mexico, have no public data at all.
**Who can use it:** USGS and state geological surveys planning Earth MRI sampling, environmental agencies, researchers, and companies looking at reprocessing.
**Where it is:** GitHub https://github.com/bkdanso/mine-waste-screening-atlas, atlas https://bkdanso.github.io/mine-waste-screening-atlas/atlas/, dataset DOI https://doi.org/10.5281/zenodo.23986699, preprint on EarthArXiv (DOI to follow).

## Two-sentence version
I built an open, ranked atlas of U.S. mine waste sites that links the new USGS National Mine Waste Inventory to public geochemical data to show which piles may hold critical minerals, which carry the most toxic metals, and which have never been sampled. It gives the federal Earth MRI program and state surveys a transparent list of where to sample first.

## Questions you may be asked
1. **Where does the data come from?** Two free USGS datasets: the National Mine Waste Inventory (October 2026) and the national geochemical database (1.5 million samples, 1962 to 2023), plus EPA screening levels and the 2025 federal critical minerals list.
2. **What are its limits?** Most nearby samples were not taken from the waste itself, so a high score means "worth sampling", not "proven resource" or "proven hazard". It does not estimate tonnage or recoverability.
3. **Why does it matter for the United States?** Critical minerals are a national security priority, and mine waste is a domestic source that also needs cleanup. A free, reproducible ranking helps public agencies spend sampling money where it counts.
