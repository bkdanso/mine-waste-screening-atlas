# Publish guide

*Plain-language note: this is your step-by-step guide to putting the project online after you finish the verification checklist. Do not start until every box in VERIFY_CHECKLIST.md is ticked. Total time: about 45 minutes, in one sitting.*

**What Claude can do for you and what you must do yourself**

| Step | Who | Time |
|---|---|---|
| A. GitHub repository and release | Claude, if you give it a GitHub token; otherwise you, using this guide | 10 min |
| B. Turn on the public atlas (GitHub Pages) | You (one setting) | 3 min |
| C. Zenodo DOI for the dataset | Automatic once step D2 is switched on; Claude can also do it with a Zenodo token | 5 min |
| D. EarthArXiv preprint | **You only.** Submitting is a personal declaration that the work is yours. | 20 min |
| E. Log everything | You and Claude together | 5 min |

---

## Copy-ready text

**Repository name:** `mine-waste-screening-atlas`

**Title (dataset):** U.S. Mine Waste Critical Mineral Screening Atlas

**Title (preprint):** A National Screening Framework for Critical Mineral Potential and Heavy-Metal Hazard in U.S. Mine Waste

**Author:** Bezali Kwame Danso. Independent Researcher, East Lansing, Michigan, USA. ORCID 0009-0006-1201-4129. dansobez@msu.edu

**Keywords:** mine waste; critical minerals; geochemistry; mine tailings; Earth MRI; environmental hazard; heavy metals; National Mine Waste Inventory; contamination; pollution

**Abstract:** paste the abstract from `paper/final/Danso_final_styled.pdf` (your final copy).

**Release notes (v0.1.0):**
> First public release. Screens all 1,498 features of the USGS National Mine Waste Inventory v2.0 for critical-mineral enrichment and heavy-metal hazard using USGS geochemical samples within 2 km. Includes ranked feature and site tables, per-element values, QA report, code, interactive atlas, and manuscript. Verified by the author on 2026-11-05.

---

## A. GitHub (if you are not giving Claude a token)

1. Go to https://github.com/new. Owner: **bkdanso**. Repository name: `mine-waste-screening-atlas`. Choose **Public**. Leave "Add a README" **unticked**. Click **Create repository**.
2. Unzip the project folder Claude sends you. Open a terminal in that folder and paste these lines one at a time:
   ```
   git init -b main
   git add -A
   git commit -m "v0.1.0: first public release"
   git remote add origin https://github.com/bkdanso/mine-waste-screening-atlas.git
   git push -u origin main
   ```
   The screen should end with `branch 'main' set up to track 'origin/main'`.
3. **Before step 4, do step D2 below** (switch on Zenodo), so the release gets a DOI.
4. On the repository page, click **Releases**, then **Draft a new release**. Under **Choose a tag**, type `v0.1.0` and click **Create new tag**. Title: `v0.1.0`. Paste the release notes above. Click **Publish release**.

**To let Claude do A instead:** go to https://github.com/settings/tokens?type=beta, click **Generate new token**, name it "atlas upload", set it to expire in 7 days, choose **Only select repositories** (or All, if the repository does not exist yet), and under **Repository permissions** set **Contents: Read and write** and **Administration: Read and write**. Click **Generate token**, copy it, and paste it into the chat. Claude stores it only for this session. Delete it afterward at the same page.

## B. Turn on the public atlas

1. In the repository, click **Settings**, then **Pages** (left menu).
2. Under **Build and deployment**, set Source to **Deploy from a branch**, Branch to **main**, and folder to **/docs**. Click **Save**.
3. After 1 to 2 minutes, the page shows "Your site is live at https://bkdanso.github.io/mine-waste-screening-atlas/". Open it. It should open the atlas, with no draft banner.

## C and D2. Zenodo DOI (automatic)

1. Log in at https://zenodo.org with your ORCID.
2. Click your name (top right), then **GitHub**. Click **Sync now**. Find `bkdanso/mine-waste-screening-atlas` and flip its switch **On**.
3. Publish the GitHub release (step A4). Within a few minutes, a new record appears under **Upload** on Zenodo, with a DOI starting `10.5281/zenodo.`. The title, description, keywords, and license come from the `.zenodo.json` file in the project.
4. Open the record and check that your name and ORCID are shown. Copy the DOI and send it to Claude. Claude puts it in the README, `CITATION.cff`, the atlas footer, and the manuscript, and makes a v0.1.1 release so everything carries the DOI.

## D. EarthArXiv preprint (you submit)

You do this after the Zenodo DOI exists, so the paper can cite it. Claude rebuilds the PDF with the DOI first.

1. Go to https://eartharxiv.org and log in (or click **Register**; you can link your ORCID).
2. Click **Submit** (top menu), then **Submit a preprint**. Read and accept the submission agreement.
3. **Metadata.** Paste the preprint title, the abstract, and the keywords from above. Subject: choose **Geochemistry**, and add **Environmental Sciences** if offered. License: **CC BY 4.0**.
4. **Authors.** Add yourself: Bezali Kwame Danso, dansobez@msu.edu, affiliation "Independent Researcher, East Lansing, Michigan, USA", ORCID 0009-0006-1201-4129.
5. **Files.** Upload `paper/final/Danso_mine_waste_screening_final.pdf` (your final draft; Claude re-exports it once the Zenodo DOI replaces "[Zenodo DOI pending]").
6. **Data and code links**, if asked: the Zenodo DOI and https://github.com/bkdanso/mine-waste-screening-atlas.
7. **Declarations**, if asked. Competing interests: none. AI use: paste the "Use of AI tools" paragraph from the manuscript.
8. Click **Submit**. You will get an email confirmation. Moderators usually check a submission within a few days, and then it gets its own DOI. Save the confirmation email as a PDF.

## E. Log everything (same day)

For each step above, send Claude the link or DOI and the date. Claude adds a row to `docs/evidence_log.csv` and updates the README status line. Save PDFs of the GitHub release page, the Zenodo record, and the EarthArXiv confirmation in a folder named `evidence/`. Publications that are not logged the day they happen are the ones that go missing later.

Then revoke any tokens you created: GitHub at https://github.com/settings/tokens, Zenodo at https://zenodo.org/account/settings/applications/.
