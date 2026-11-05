"""12_final_prep.py: read the author's final manuscript and prepare it for re-styling.

Plain-language note: this reads your final Word file, keeps every sentence as
you wrote it, and only changes (1) author-year citations to numbered [n]
citations in order of first use, (2) "Figure n" to "Fig. n", and (3) heading
capitalization, to match the requested journal style. Output: paper/final/styled_spec.json
"""
import json
import re
import sys
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
UN = Path(sys.argv[1])  # unzipped author final docx
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
body = etree.parse(str(UN / "word/document.xml")).getroot().find(W + "body")
rels = {r.get("Id"): r.get("Target") for r in etree.parse(str(UN / "word/_rels/document.xml.rels")).getroot()}

# ---- citations, numbered by first appearance in the text (verified order)
CITE = [  # (pattern, replacement); longest first
    (r" ?\(Kursunoglu, 2025; Piatak et al\., 2025\)", " [2, 3]"),
    (r" ?\(Singh et al\., 2025; Kursunoglu, 2025\)", " [2, 5]"),
    (r" ?\(Lottermoser, 2010\)", " [1]"),
    (r" ?\(Piatak et al\., 2025\)", " [3]"),
    (r" ?\(U\.S\. Geological Survey, 2026\)", " [4]"),
    (r"Granitto et al\., \(2026\)|Granitto et al\. \(2026\)", "Granitto et al. [6]"),
    (r" ?\(Granitto et al\., 2019\)", " [7]"),
    (r" ?\(Smith et al\., 2013\)", " [8]"),
    (r"Rudnick and Gao \(2014\)", "Rudnick and Gao [9]"),
    (r" ?\(Rudnick and Gao, 2014\)", " [9]"),
    (r" ?\(U\.S\. Department of the Interior, 2025\)", " [10]"),
    # fixes a misplaced "; Appendix Table A2" that Claude's Draft 2 edit put outside the parenthesis
    (r"summary table; U\.S\. Environmental Protection Agency, 2024\); Appendix Table A2\.", "summary table; Appendix Table A2) [11]."),
    (r"; U\.S\. Environmental Protection Agency, 2024\)", ") [11]"),
]
TABLE_REF = {"U.S. Geological Survey (2026)": "[4]", "Granitto et al. (2026)": "[6]", "Granitto et al. (2019)": "[7]",
             "Smith et al. (2013)": "[8]", "Rudnick and Gao (2014)": "[9]", "U.S. EPA (2024)": "[11]",
             "U.S. Department of the Interior (2025)": "[10]"}
REFS = [
    "Bernd G. Lottermoser. Mine Wastes: Characterization, Treatment and Environmental Impacts. Springer, Berlin, 3rd edition, 2010. doi:10.1007/978-3-642-12419-8.",
    "Sait Kursunoglu. A review on the recovery of critical metals from mine and mineral processing tailings: Recent advances. J. Sustain. Metall., 11(3):2023–2050, 2025. doi:10.1007/s40831-025-01126-y.",
    "Nadine M. Piatak, Sarah Jane White, Sarah M. Hayes, and Robert R. Seal II. Critical minerals in mine waste. U.S. Geological Survey Fact Sheet 2025–3026, 2025. doi:10.3133/fs20253026.",
    "U.S. Geological Survey. National Mine Waste Inventory (ver. 2.0, October 2026). U.S. Geological Survey data release, 2026. doi:10.5066/P148EEUA.",
    "Sukhpreet Singh, Pankaj Maurya, Amit Karmakar, Prakash Kumar Maurya, Nidhi Pandey, Sandeep Kumar, and Tanish Gupta. Mining tailings as a frontier for sustainable nanomaterials: advancing circular economy and environmental innovation. Environ. Geochem. Health, 47(7):265, 2025. doi:10.1007/s10653-025-02566-x.",
    "Matthew Granitto, Margaret A. Goldman, Keith A. Labay, Carma A. San Juan, Jaime S. Azain, and Toni R. Rozinek. Geochemical data for rock, sediment, soil, and mineral samples, United States and territories, 1962 to 2023. U.S. Geological Survey data release, 2026. doi:10.5066/P1FXE9GK.",
    "Matthew Granitto, Bronwen Wang, Nora B. Shew, Susan M. Karl, Keith A. Labay, Melanie B. Werdon, Susan S. Seitz, and John E. Hoppe. Alaska Geochemical Database Version 3.0 (AGDB3) including “best value” data compilations for rock, sediment, soil, mineral, and concentrate sample media. U.S. Geological Survey Data Series 1117, 2019. doi:10.3133/ds1117.",
    "David B. Smith, William F. Cannon, Laurel G. Woodruff, Federico Solano, James E. Kilburn, and David L. Fey. Geochemical and mineralogical data for soils of the conterminous United States. U.S. Geological Survey Data Series 801, 2013. doi:10.3133/ds801.",
    "Roberta L. Rudnick and Shan Gao. Composition of the continental crust. In Heinrich D. Holland and Karl K. Turekian, editors, Treatise on Geochemistry, volume 4, pages 1–51. Elsevier, Oxford, 2nd edition, 2014. doi:10.1016/B978-0-08-095975-7.00301-6.",
    "U.S. Department of the Interior. Final 2025 List of Critical Minerals. Federal Register, FR Doc. 2025-19813, November 7, 2025.",
    "U.S. Environmental Protection Agency. Regional Screening Levels (RSLs) for chemical contaminants at Superfund sites, November 2024 tables, 2024. https://www.epa.gov/risk/regional-screening-levels-rsls-generic-tables.",
]
FIG = [(r"\bFigures? (\d)", r"Fig. \1")]
done_cites = []


def conv(t):
    for pat, rep in CITE:
        if re.search(pat, t):
            done_cites.append(rep.strip())
        t = re.sub(pat, rep, t)
    for pat, rep in FIG:
        t = re.sub(pat, rep, t)
    return t


def runs(p):
    out = []
    for r in p.iter(W + "r"):
        blip = r.find(".//" + A + "blip")
        if blip is not None:
            out.append({"img": rels[blip.get(R + "embed")]})
        t = "".join(x.text or "" for x in r if x.tag == W + "t")
        if not t:
            continue
        rp = r.find(W + "rPr")
        on = lambda tag: rp is not None and rp.find(W + tag) is not None and rp.find(W + tag).get(W + "val") not in ("0", "false")  # noqa: E731
        out.append({"t": t, "b": on("b"), "i": on("i")})
    # merge adjacent same-format text runs
    m = []
    for x in out:
        if m and "t" in x and "t" in m[-1] and x["b"] == m[-1]["b"] and x["i"] == m[-1]["i"]:
            m[-1]["t"] += x["t"]
        else:
            m.append(dict(x))
    return m


def sentence_case_heading(t):
    t = t.strip()
    m = re.match(r"^(\d+(?:\.\d+)?)\.?\s+(.*)$", t)
    if not m:
        return None, t
    num, rest = m.groups()
    if rest.isupper():
        rest = rest.capitalize()
    else:  # Title Case -> sentence case, keeping acronyms
        words = rest.split()
        rest = " ".join([words[0]] + [w if (w.isupper() or w[:1].isdigit()) else w.lower() for w in words[1:]])
    rest = {"Mine-Waste features": "Mine-waste features", "Critical mineral index": "Critical Mineral Index",
            "Heavy-Metal hazard index": "Heavy-Metal Hazard Index"}.get(rest, rest)
    return num + ".", rest


blocks = []
for el in body:
    if el.tag == W + "tbl":
        rows = [["".join(t.text or "" for t in tc.iter(W + "t")) for tc in tr.findall(W + "tc")] for tr in el.findall(W + "tr")]
        rows = [[TABLE_REF.get(c, c) for c in row] for row in rows]
        blocks.append({"type": "table", "rows": rows})
        continue
    if el.tag != W + "p":
        continue
    rs = runs(el)
    text = "".join(r.get("t", "") for r in rs).strip()
    imgs = [r["img"] for r in rs if "img" in r]
    if imgs:
        blocks.append({"type": "image", "src": imgs[0]})
        continue
    if not text:
        continue
    lst = el.find(".//" + W + "numPr") is not None
    blocks.append({"type": "p", "runs": [dict(r, t=conv(r["t"])) for r in rs if "t" in r], "text": conv(text), "list": lst})

# classify
out, section = [], "front"
for i, b in enumerate(blocks):
    if b["type"] != "p":
        out.append(b)
        continue
    t = b["text"]
    if re.match(r"^(\d+)\.\s+[A-Z][A-Z ,\-]+$", t):           # 1. INTRODUCTION
        num, rest = sentence_case_heading(t)
        out.append({"type": "h1", "num": num, "text": rest})
        section = "body"
    elif re.match(r"^\d+\.\d+\.?\s+\S", t) and len(t) < 70 and not t.endswith("."):
        num, rest = sentence_case_heading(t)
        out.append({"type": "h2", "num": num, "text": rest})
    elif re.match(r"^(Fig\.|Table) [A0-9]+\d*\.", t) or re.match(r"^Table A\d\.", t):
        out.append({"type": "caption", "runs": b["runs"]})
    elif t in ("Data and code availability", "Use of AI Tools", "Competing interests", "ABSTRACT", "REFERENCES", "APPENDIX"):
        out.append({"type": "h0", "text": t})
        if t == "REFERENCES":
            section = "refs"
    elif section == "refs":
        continue  # replaced by the numbered list
    else:
        out.append(b)

spec = {"blocks": out, "refs": REFS}
(ROOT / "paper/final").mkdir(parents=True, exist_ok=True)
(ROOT / "paper/final/styled_spec.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False))
nums = sorted({int(x) for c in done_cites for x in re.findall(r"\d+", c)})
print("citations converted:", len(done_cites), "| reference numbers used:", nums)
assert nums == list(range(1, 12)), "every reference must be cited"
# first-appearance order check
seq = [int(x) for b in out if b["type"] in ("p",) for x in re.findall(r"\[(\d+)(?:, \d+)?\]", b["text"])]
firsts = []
for b in out:
    if b["type"] == "p":
        for grp in re.findall(r"\[([\d, ]+)\]", b["text"]):
            for x in grp.split(","):
                x = int(x)
                if x not in firsts:
                    firsts.append(x)
print("first-appearance order in body text:", firsts)
for b in out:
    if b["type"] in ("h0", "h1", "h2"):
        print(b["type"], b.get("num", ""), b["text"])
