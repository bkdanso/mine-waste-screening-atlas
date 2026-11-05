"""14_finalize.py: turn the verified draft into the v0.1.0 release, with the reserved Zenodo DOI filled in.

Plain-language note: run once, after the author approved publishing and Zenodo reserved the DOI.
It removes every DRAFT label, writes the DOI and release date into the README, citation file,
atlas, guides, and the manuscript's Data and code availability sentence, and rebuilds the
final figures, atlas, and manuscript PDF.

Usage: python3 code/14_finalize.py <zenodo_doi> <YYYY-MM-DD> <unzipped author final docx dir>
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOI, DATE, UN = sys.argv[1], sys.argv[2], sys.argv[3]
REPO = "https://github.com/bkdanso/mine-waste-screening-atlas"
PAGES = "https://bkdanso.github.io/mine-waste-screening-atlas/atlas/"
run = lambda *a: subprocess.run([*a], cwd=ROOT, check=True, capture_output=True, text=True)  # noqa: E731


def sub(path, pairs):
    p = ROOT / path
    s = p.read_text()
    for a, b in pairs:
        if a not in s:
            raise SystemExit(f"{path}: not found: {a[:70]!r}")
        s = s.replace(a, b)
    p.write_text(s)


# stats + rebuilt outputs
run(sys.executable, "code/05_qa.py", "--final")
st = json.loads((ROOT / "paper/stats.json").read_text())
st.update({"zenodo_doi": DOI, "release_date": DATE, "draft": False})
(ROOT / "paper/stats.json").write_text(json.dumps(st, indent=2))
run(sys.executable, "code/06_figures.py", "--final")
run(sys.executable, "code/07_atlas.py", "--final")
run(sys.executable, "code/09_verify_extract.py")

# documents
sub("README.md", [
    ("**Status: DRAFT v0.1.0 (2026-10-31). Not yet verified by the author. Do not cite.**",
     f"**Status: Released v0.1.0 ({DATE}). Verified by the author. Dataset DOI: [{DOI}](https://doi.org/{DOI}).**"),
    ("- **Dataset DOI:** [Zenodo DOI pending]", f"- **Dataset DOI:** [{DOI}](https://doi.org/{DOI})"),
    ("- **Preprint:** [EarthArXiv DOI pending]", "- **Preprint:** submitted to EarthArXiv; its DOI will be added here when posted"),
    ("Add `--final` only after verification to remove DRAFT stamps.", "The released outputs were built with `./run_all.sh --final`."),
    ("published at https://bkdanso.github.io/mine-waste-screening-atlas/atlas/ once released", f"live at {PAGES}"),
])
sub("CITATION.cff", [('date-released: "[YYYY-MM-DD release date]"', f'date-released: "{DATE}"'),
                     ('doi: "[10.5281/zenodo.pending]"', f'doi: "{DOI}"')])
sub("docs/START_HERE.md", [
    ("- [ ] **A public project page** on GitHub with all code and data, so anyone can rerun it: [link once live]",
     f"- [x] **A public project page** on GitHub with all code and data, so anyone can rerun it: {REPO}"),
    ("- [ ] **A permanent citation number (DOI)** for the ranked dataset, from Zenodo: [DOI once minted]",
     f"- [x] **A permanent citation number (DOI)** for the ranked dataset, from Zenodo: https://doi.org/{DOI}"),
    ("- [ ] **A public atlas** (an online map and searchable table) on GitHub Pages: [link once live]",
     f"- [x] **A public atlas** (an online map and searchable table) on GitHub Pages: {PAGES}"),
    ("- [ ] **A short screening paper** posted on EarthArXiv, with its own DOI: [DOI once posted]",
     "- [ ] **A short screening paper** posted on EarthArXiv, with its own DOI: submitted by the author (DOI to follow)"),
])
s = (ROOT / "docs/START_HERE.md").read_text()
s = re.sub(r"\*You are here:.*\*", f"*You are here: released v0.1.0 on {DATE}. Next: submit the paper to EarthArXiv.*", s)
(ROOT / "docs/START_HERE.md").write_text(s)
sub("docs/TALK_TRACK.md", [("**Where it is:** GitHub [link], dataset DOI [DOI], preprint on EarthArXiv [DOI].",
                            f"**Where it is:** GitHub {REPO}, atlas {PAGES}, dataset DOI https://doi.org/{DOI}, preprint on EarthArXiv (DOI to follow).")])
sub("docs/PUBLISH_GUIDE.md", [("Verified by the author on [date].", f"Verified by the author on {DATE}."),
                              ("It should open the atlas, with no DRAFT banner.", "It should open the atlas, with no draft banner."),
                              ("paste the final abstract from `paper/manuscript.docx` after you have rewritten it in your own words.",
                               "paste the abstract from `paper/final/Danso_final_styled.pdf` (your final copy).")])

# manuscript: only the DOI sentence changes
spec_p = ROOT / "paper/final/styled_spec.json"
spec = json.loads(spec_p.read_text())
hits = 0
for b in spec["blocks"]:
    for r in b.get("runs", []):
        if "[Zenodo DOI pending]" in r.get("t", ""):
            r["t"] = r["t"].replace("[Zenodo DOI pending]", f"https://doi.org/{DOI}")
            hits += 1
    if "text" in b and "[Zenodo DOI pending]" in b["text"]:
        b["text"] = b["text"].replace("[Zenodo DOI pending]", f"https://doi.org/{DOI}")
assert hits == 1, hits
spec_p.write_text(json.dumps(spec, indent=1, ensure_ascii=False))
run("node", "code/13_final_styled.js", f"{UN}/word")
SOFFICE = "/root/.claude/skills/synced/2f5e861b-8327-4af8-8929-c8c9efe48b5f_58f891de-9344-4fa7-818e-96d008803fb7/docx/scripts/office/soffice.py"
subprocess.run([sys.executable, SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(ROOT / "paper/final"),
                str(ROOT / "paper/final/Danso_final_styled.docx")], check=True, capture_output=True)
print("finalized with", DOI, DATE)
