# Start Here: U.S. Mine Waste Critical Mineral Screening Atlas

*Read this first. It explains your project in plain language. Words in bold are explained in [GLOSSARY.md](GLOSSARY.md).*

## What you are building

A free, ranked list and online map of U.S. mine waste piles (tailings, waste rock, slag). It shows which ones look richest in critical minerals and which ones carry the most toxic metals, so people know where to sample first.

## Why it matters

The United States has thousands of old mine waste piles. Some still hold metals the country now needs, like cobalt, gallium, germanium, tellurium, and rare earths. Many also leak arsenic, lead, and cadmium into streams. The U.S. Geological Survey (USGS) and state surveys are mapping these piles through the Earth Mapping Resources Initiative (Earth MRI). But mapping a pile does not tell you what is in it, and sampling every pile costs too much.

This project lets an agency or a researcher see, in one table, which mapped piles already have nearby lab results showing high critical mineral values, high hazard, or both, and which piles have no data at all. Think of it like a triage list in an emergency room: it does not treat anyone, but it tells you who to look at first.

## Where the information comes from

All sources are free, public, and U.S. government works with no use restrictions.

| Source | In plain terms | What one row looks like | Link |
|---|---|---|---|
| USGS National Mine Waste Inventory, version 2.0 (October 2026) | The government's new map of mine waste piles in 23 states | One pile: its name, type (for example "Tailings - pond"), location, size, the metals the mine produced | https://doi.org/10.5066/P148EEUA |
| USGS geochemical database, 1962 to 2023 (Granitto and others, 2026) | Every lab test the USGS has run on rock, soil, and stream mud samples in the U.S. | One sample: where it was taken, what kind of material, and the measured amount of each element | https://doi.org/10.5066/P1FXE9GK |

What we found when we checked (October 31, 2026):

- The mine waste inventory has **1,498 waste features** grouped into **343 mine sites** across **23 states**.
- The geochemical database has **1,524,014 samples** and about **59.8 million lab measurements**.
- About **59%** of the waste features have at least one lab sample within 1 kilometer. About **85%** have one within 2 kilometers.
- About **62,000** of the samples were taken at mines, dumps, or tailings themselves.

## What you will have at the end

- [x] **A public project page** on GitHub with all code and data, so anyone can rerun it: https://github.com/bkdanso/mine-waste-screening-atlas
- [x] **A permanent citation number (DOI)** for the ranked dataset, from Zenodo: https://doi.org/10.5281/zenodo.23986699
- [x] **A public atlas** (an online map and searchable table) on GitHub Pages: https://bkdanso.github.io/mine-waste-screening-atlas/atlas/
- [ ] **A short screening paper** posted on EarthArXiv, with its own DOI: submitted by the author (DOI to follow)

## How it connects to your work

It uses your environmental and safety engineering training, your Environmental Monitoring and Sampling certificate, and your research on heavy metals in mining watersheds. It turns that expertise into a national tool that directly supports a federal program (Earth MRI) on critical mineral supply and mine land cleanup.

## What you need to do

| Your task | When | Time |
|---|---|---|
| Create accounts (ORCID, GitHub, Zenodo, EarthArXiv) | Now | 20 min |
| Answer five setup questions | Now | 10 min |
| Check the results using the checklist | When the draft is ready | 1 to 2 hours |
| Approve publishing | After checking | 5 min |
| Submit the paper to EarthArXiv yourself, using the guide | After publishing | 20 min |

Everything else is built for you.

## The steps ahead

1. **Data collected.** Both USGS sources downloaded and labeled with where they came from. *(Done.)*
2. **Data combined.** Each waste pile is matched to the lab samples near it.
3. **Scores built.** Each pile gets a critical mineral score, a hazard score, and a data-confidence grade.
4. **Quality checks.** We count, compare, and spot-check famous sites against published facts.
5. **Atlas and figures.** You see the first map and ranked table.
6. **Draft paper.** Every number in it comes straight from the data.
7. **Ready for your check.** You verify, then we publish.

*You are here: released v0.1.0 on 2026-11-05. Next: submit the paper to EarthArXiv.*
