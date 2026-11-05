"""11_draft2.py: turn the author's Draft 1 into Draft 2 with tracked changes.

Plain-language note: this opens your own Word manuscript and adds the
figures, tables, appendix, missing in-text citations, the Methods section,
and the number updates from your arsenic decision. Every change is a Word
tracked change by "Claude", so you can accept or reject each one. Your
original wording is otherwise untouched.

Input : <unpacked Draft 1 dir>  (after merge_runs.py)
Output: the same dir, edited in place; zip it to .docx afterwards.
"""
import copy
import datetime
import json
import shutil
import sys
from pathlib import Path

from lxml import etree
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
UN = Path(sys.argv[1])
S = json.loads((ROOT / "paper/stats.json").read_text())
T = json.loads((ROOT / "paper/pub/pub_tables.json").read_text())
A = json.loads((ROOT / "AUTHORS.json").read_text())["authors"][0]
PUB = ROOT / "paper/pub"

WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{%s}" % WNS
RNS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
AUTHOR, DATE = "Claude", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_id = [9000]


def nid():
    _id[0] += 1
    return str(_id[0])


def el(tag, attrs=None, children=()):
    e = etree.Element(W + tag)
    for k, v in (attrs or {}).items():
        e.set(W + k, str(v))
    for c in children:
        e.append(c)
    return e


def rpr(bold=False, italic=False, sz=22, sup=False):
    r = el("rPr", children=[el("rFonts", {"ascii": "Arial", "hAnsi": "Arial", "cs": "Arial"})])
    if bold:
        r.append(el("b")), r.append(el("bCs"))
    if italic:
        r.append(el("i")), r.append(el("iCs"))
    r.append(el("sz", {"val": sz})), r.append(el("szCs", {"val": sz}))
    if sup:
        r.append(el("vertAlign", {"val": "superscript"}))
    return r


def run(text, deleted=False, **fmt):
    r = el("r", children=[rpr(**fmt)])
    t = el("delText" if deleted else "t")
    t.text = text
    t.set(XML_SPACE, "preserve")
    r.append(t)
    return r


def ins(*runs):
    return el("ins", {"id": nid(), "author": AUTHOR, "date": DATE}, runs)


def dele(*runs):
    return el("del", {"id": nid(), "author": AUTHOR, "date": DATE}, runs)


def segs(spec, sz=22):
    """spec: str or list of (text, fmt dict) pieces; '**x**' style not used."""
    if isinstance(spec, str):
        spec = [(spec, {})]
    return [run(t, sz=f.get("sz", sz), bold=f.get("b", False), italic=f.get("i", False)) for t, f in spec]


def para(spec, align=None, sz=22, keep_next=False, space_after=None, bold=False):
    """A new paragraph, entirely a tracked insertion."""
    if isinstance(spec, str):
        spec = [(spec, {"b": bold})]
    ppr = el("pPr")
    if keep_next:
        ppr.append(el("keepNext"))
    sp = {"line": 240, "lineRule": "auto"}
    if space_after is not None:
        sp["after"] = space_after
    ppr.append(el("spacing", sp))
    if align:
        ppr.append(el("jc", {"val": align}))
    mark = rpr(sz=sz)
    mark.insert(0, el("ins", {"id": nid(), "author": AUTHOR, "date": DATE}))
    ppr.append(mark)
    return el("p", children=[ppr, ins(*segs(spec, sz))])


# ---------------------------------------------------------------- package parts
doc_path = UN / "word/document.xml"
tree = etree.parse(str(doc_path))
body = tree.getroot().find(W + "body")
P = list(body)  # original paragraphs by index (from Draft 1)
# normalize: drop render-cache page breaks; one content child per run, so text edits never lose siblings
for lr in list(body.iter(W + "lastRenderedPageBreak")):
    lr.getparent().remove(lr)
for r in list(body.iter(W + "r")):
    kids = [k for k in r if k.tag != W + "rPr"]
    if len(kids) > 1:
        base = r.find(W + "rPr")
        parent, pos = r.getparent(), r.getparent().index(r)
        parent.remove(r)
        for k2, kid in enumerate(kids):
            nr = etree.Element(W + "r")
            if base is not None:
                nr.append(copy.deepcopy(base))
            nr.append(kid)
            parent.insert(pos + k2, nr)
ORIG_TEXT = ["".join(t.text or "" for t in p.iter(W + "t")) for p in P]
rels_path = UN / "word/_rels/document.xml.rels"
rels = etree.parse(str(rels_path))
ct_path = UN / "[Content_Types].xml"
ct = etree.parse(str(ct_path))
if not any(d.get("Extension") == "png" for d in ct.getroot()):
    d = etree.SubElement(ct.getroot(), "{http://schemas.openxmlformats.org/package/2006/content-types}Default")
    d.set("Extension", "png"), d.set("ContentType", "image/png")
(UN / "word/media").mkdir(exist_ok=True)
_rid = [100]


def image_par(png, width_in=6.3):
    _rid[0] += 1
    rid = f"rId{_rid[0]}"
    shutil.copy(png, UN / "word/media" / png.name)
    r = etree.SubElement(rels.getroot(), "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
    r.set("Id", rid)
    r.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    r.set("Target", f"media/{png.name}")
    w, h = Image.open(png).size
    cx = int(width_in * 914400)
    cy = int(cx * h / w)
    pid = nid()
    xml = f'''<w:r xmlns:w="{WNS}" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
 xmlns:r="{RNS}"><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>
<wp:docPr id="{pid}" name="{png.stem}" descr="{png.stem.replace('_', ' ')}"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{pid}" name="{png.name}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'''
    rr = etree.fromstring(xml)
    p = para("", align="center", keep_next=True)
    p.remove(p.find(W + "ins"))
    p.append(ins(rr))
    return p


def caption(label, text):
    return para([(label + " ", {"b": True}), (text, {})], sz=20, space_after=240)


def table(header, rows, widths, sz=16):
    tot = sum(widths)
    bd = lambda: el("tblBorders", children=[el(x, {"val": "single", "sz": 4, "space": 0, "color": "999999"})  # noqa: E731
                                            for x in ["top", "left", "bottom", "right", "insideH", "insideV"]])
    tbl = el("tbl", children=[el("tblPr", children=[el("tblW", {"w": tot, "type": "dxa"}), el("jc", {"val": "center"}), bd(),
                                                     el("tblLayout", {"type": "fixed"}),
                                                     el("tblCellMar", children=[el("left", {"w": 60, "type": "dxa"}),
                                                                                el("right", {"w": 60, "type": "dxa"})])]),
                              el("tblGrid", children=[el("gridCol", {"w": w}) for w in widths])])
    for ri, row in enumerate([header] + rows):
        trpr = el("trPr", children=[el("cantSplit"), el("ins", {"id": nid(), "author": AUTHOR, "date": DATE})])
        if ri == 0:
            trpr.insert(1, el("tblHeader"))
        tr = el("tr", children=[trpr])
        for ci, (val, w) in enumerate(zip(row, widths)):
            tcpr = el("tcPr", children=[el("tcW", {"w": w, "type": "dxa"})])
            if ri == 0:
                tcpr.append(el("shd", {"val": "clear", "color": "auto", "fill": "EDEDEA"}))
            p = para([(str(val), {"b": ri == 0})], sz=sz, space_after=0)
            tr.append(el("tc", children=[tcpr, p]))
        tbl.append(tr)
    return tbl


def remerge(p):
    rs = p.findall(W + "r")
    k = 0
    while k < len(rs) - 1:
        a, b = rs[k], rs[k + 1]
        ta, tb = a.find(W + "t"), b.find(W + "t")
        same = etree.tostring(a.find(W + "rPr") if a.find(W + "rPr") is not None else el("rPr")) == \
            etree.tostring(b.find(W + "rPr") if b.find(W + "rPr") is not None else el("rPr"))
        if ta is not None and tb is not None and len(a) == len(b) == 2 and same and a.getnext() is b:
            ta.text = (ta.text or "") + (tb.text or "")
            ta.set(XML_SPACE, "preserve")
            p.remove(b)
            rs.pop(k + 1)
        else:
            k += 1


def full_text(p):
    return "".join(t.text or "" for t in p.iter(W + "t"))


def edit(p, old, new, anchor_only=False):
    remerge(p)
    """Tracked replace of `old` with `new` inside paragraph p. Requires `old` within a single run.
    If old == '' use insert_after instead."""
    for r in p.findall(W + "r"):
        t = r.find(W + "t")
        if t is None or t.text is None or old not in t.text:
            continue
        txt = t.text
        i = txt.index(old)
        before, after = txt[:i], txt[i + len(old):]
        base = r.find(W + "rPr")
        parent, pos = r.getparent(), r.getparent().index(r)
        parent.remove(r)
        out = []

        def mk(text, deleted=False):
            nr = el("r", children=[copy.deepcopy(base)] if base is not None else [])
            tt = el("delText" if deleted else "t")
            tt.text = text
            tt.set(XML_SPACE, "preserve")
            nr.append(tt)
            return nr
        if before:
            out.append(mk(before))
        if old and not anchor_only:
            out.append(dele(mk(old, deleted=True)))
        elif old and anchor_only:
            out.append(mk(old))
        if new:
            out.append(ins(mk(new)))
        if after:
            out.append(mk(after))
        for k, o in enumerate(out):
            parent.insert(pos + k, o)
        return
    raise ValueError(f"not found in one run: {old[:60]!r} | runs: {[(x.find(W + chr(116)).text if x.find(W + chr(116)) is not None else None) for x in p.findall(W + chr(114))]}")


def insert_after(p, anchor, new):
    edit(p, anchor, new, anchor_only=True)


def add_after(ref, *elements):
    pos = body.index(ref)
    for k, e in enumerate(elements):
        body.insert(pos + 1 + k, e)
    return elements[-1]


n = lambda v: f"{v:,}"  # noqa: E731
hhi_cut = 10 ** S["hhi_cut_log10"]

# ---------------------------------------------------------------- title block (top)
first = P[0]
pos = body.index(first)
for k, e in enumerate([
    para("Screening U.S. Mine Waste for Critical Minerals and Heavy-Metal Hazard by Linking the National Mine Waste "
         "Inventory to Public Geochemical Samples", align="center", sz=28, bold=True, space_after=200),
    para(A["name"], align="center", bold=True, space_after=60),
    para(f"{A['affiliation']}. ORCID: {A['orcid']}", align="center", space_after=60),
    para(f"Corresponding author: {A['email']}", align="center", space_after=60),
    para([("Preprint. This manuscript has not been peer reviewed.", {"i": True})], align="center", space_after=300),
]):
    body.insert(pos + k, e)

# ---------------------------------------------------------------- abstract
edit(P[1], "Eighty-three sites", "Eighty-four sites")
edit(P[1], "Hundred and seventy-four features", "One hundred seventy-four features")

# ---------------------------------------------------------------- introduction citations
insert_after(P[5], "surrounding soils, watersheds, and ecosystems", " (Lottermoser, 2010)")
insert_after(P[6], "reducing environmental hazards associated with legacy mining activities", " (Kursunoglu, 2025; Piatak et al., 2025)")
edit(P[9], "Kursunoglu et al., 2025", "Kursunoglu, 2025")

# ---------------------------------------------------------------- data
edit(P[19], "Granitto et al., (2026)", "Granitto et al. (2026)")
edit(P[21], "Rudnick et al., (2003)", "Rudnick and Gao (2014)")
insert_after(P[21], "were used as reference values.", " The background value and source used for each element are listed in Appendix Table A1.")
insert_after(P[23], "U.S. Environmental Protection Agency, 2024)", "; Appendix Table A2")
insert_after(P[23], "associated with mine-waste features.", " For arsenic, the noncancer screening level (35 mg/kg) was used for ranking, and the "
             "cancer-based level (0.68 mg/kg) was evaluated as a sensitivity case (Section 4.6). The data sources, versions, and "
             "their roles in the workflow are summarized in Table 1.")
t1 = [["National Mine Waste Inventory", "v2.0, Oct 2026", f"{n(S['nmwi_unique_ftr_id'])} features, {S['nmwi_sites']} sites, {S['nmwi_states']} states", "Screening units", "U.S. Geological Survey (2026)"],
      ["USGS geochemical data, 1962 to 2023", "2026 release", f"{n(S['geochem_samples_eligible'])} eligible bulk samples", "Element concentrations", "Granitto et al. (2026)"],
      ["Best-value method ranking", "AGDB3", "Rank of each analytical method", "Selection of one value per element", "Granitto et al. (2019)"],
      ["Geochemical Landscapes soils", "Within source above", f"{n(S['background_samples'])} soil samples", "Background (primary)", "Smith et al. (2013)"],
      ["Upper continental crust", "2nd ed.", "24 element abundances", "Background where soil data are lacking", "Rudnick and Gao (2014)"],
      ["EPA Regional Screening Levels", "Nov 2024", "Resident soil, THQ = 1", "Hazard benchmarks", "U.S. EPA (2024)"],
      ["Final 2025 List of Critical Minerals", "Nov 7, 2025", "60 minerals (58 as elements)", "Critical element set", "U.S. Department of the Interior (2025)"]]
add_after(P[23], caption("Table 1.", "Data sources used in this study."),
          table(["Source", "Version", "Content used", "Role", "Reference"], t1, [2100, 1200, 2300, 1800, 1960]),
          para("", space_after=120))

# ---------------------------------------------------------------- methods (new section 3)
M = [para("3. METHODS", bold=True, keep_next=True),
     para("The screening workflow consists of four steps: spatial linkage of samples to mine-waste features, selection of "
          "analytical values, calculation of two screening indices, and classification of features and sites (Figure 1)."),
     image_par(PUB / "Figure1_workflow.png", 6.3),
     caption("Figure 1.", "Screening workflow linking National Mine Waste Inventory (NMWI) features to public geochemical samples. "
             "CMI, Critical Mineral Index; HHI, Heavy-Metal Hazard Index; RSL, EPA Regional Screening Level."),
     para("3.1 Spatial Linkage", bold=True, keep_next=True),
     para("For each NMWI feature, the distance from every eligible geochemical sample to the feature polygon was computed in an "
          "equal-area projection (EPSG:5070 for the conterminous United States and EPSG:3338 for Alaska), with a distance of zero "
          "assigned to samples inside the polygon. Samples inside or within 1 km of the polygon edge were assigned to Tier 1, and "
          "samples 1 to 2 km away to Tier 2. Each feature was scored from its Tier 1 samples when any were available and otherwise "
          "from its Tier 2 samples. Samples whose recorded source was a mine dump, tailings, slag, waste, or mill material were "
          "flagged as on-waste samples."),
     para("3.2 Selection of Analytical Values", bold=True, keep_next=True),
     para("Where a sample had several determinations of the same element, the single best-ranked value was retained, with "
          "total-digestion methods preferred over partial methods and lower rank numbers preferred within each group (Granitto et "
          "al., 2019). All results were converted to mg/kg. Nondetects were set to half the reported detection limit and flagged, "
          "and values reported above an upper limit were treated as lower bounds. For each feature and element, the median across "
          "the selected samples was used as the representative concentration."),
     para("3.3 Critical Mineral Index", bold=True, keep_next=True),
     para("For each critical element, an enrichment factor (EF) was calculated as the feature median divided by the background "
          "concentration (Section 2.3; Appendix Table A1). The Critical Mineral Index (CMI) is the sum of the five largest positive "
          "log10 EF values for a feature, with each element capped at 3 (a 1,000-fold enrichment), giving a range of 0 to 15. "
          "Limiting the sum to five elements reduces bias toward samples analyzed by multi-element methods. Elements whose feature "
          "median was itself a nondetect (50% or more nondetects) contributed no enrichment, because half a detection limit can "
          "exceed crustal abundance by orders of magnitude for elements such as tellurium, rhenium, and the platinum-group elements."),
     para("3.4 Heavy-Metal Hazard Index", bold=True, keep_next=True),
     para("For 18 metals (As, Pb, Cd, Hg, Sb, Tl, Cu, Zn, Ni, Se, Ba, Be, Co, Mn, Ag, V, Mo, and U), a hazard ratio was calculated "
          "as the feature median divided by the EPA residential soil screening level (Appendix Table A2). The Heavy-Metal Hazard "
          "Index (HHI) is the sum of these ratios; an HHI of 1 corresponds to one screening level reached. Medians that were "
          "nondetects were excluded. For arsenic, the noncancer screening level (35 mg/kg) was used because the cancer-based level "
          "(0.68 mg/kg) lies below typical U.S. soil concentrations (background median 5.6 mg/kg) and would otherwise dominate the "
          "index; the cancer-based level was evaluated as a sensitivity case (Section 4.6). Chromium was not scored because the "
          "database reports total chromium, whereas screening levels are specific to its oxidation state."),
     para("3.5 Priority Classes and Confidence Grades", bold=True, keep_next=True),
     para(f"Features in the upper third of scored features for both indices were classified as Dual priority (CMI ≥ "
          f"{S['cmi_cut']:.2f} and HHI ≥ {hhi_cut:.2f}). Features in the upper third for only one index were classified as "
          "Resource or Hazard priority, the remaining scored features as Lower priority, and features with no sample within 2 km "
          "as Unsampled. Each feature also received a confidence grade reflecting the amount and type of supporting data, and each "
          "site was assigned the class of its highest-scoring feature (Table 2)."),
     caption("Table 2.", "Index definitions, priority classes, and confidence grades."),
     table(["Term", "Definition"], [
         ["Enrichment factor (EF)", "Feature median concentration divided by background concentration"],
         ["Critical Mineral Index (CMI)", "Sum of the five largest values of max(0, log10 EF) over critical elements, each capped at 3; range 0 to 15"],
         ["Hazard ratio", "Feature median concentration divided by the EPA residential soil screening level"],
         ["Heavy-Metal Hazard Index (HHI)", "Sum of hazard ratios over 18 metals with a detected median"],
         ["Dual", f"Upper third on both indices (CMI ≥ {S['cmi_cut']:.2f}; HHI ≥ {hhi_cut:.2f})"],
         ["Resource / Hazard", "Upper third on the CMI only / on the HHI only"],
         ["Lower", "Scored, but in the upper third of neither index"],
         ["Unsampled", "No eligible sample within 2 km"],
         ["Confidence A", "At least 5 samples within 1 km, including at least one on-waste sample"],
         ["Confidence B", "At least 3 samples within 1 km"],
         ["Confidence C", "Fewer than 3 samples within 1 km, or samples 1 to 2 km away only"],
         ["Confidence U", "No sample within 2 km"]], [2800, 6560]),
     para("", space_after=120),
     para("3.6 Validation, Sensitivity, and Verification", bold=True, keep_next=True),
     para("As an internal check, features whose NMWI commodity field lists a metal were tested for five-fold or greater enrichment "
          "of that metal nearby. Sensitivity was evaluated by substituting the cancer-based arsenic screening level, by using each "
          "element's maximum rather than median concentration, and by removing from the CMI the 13 elements that appear on both the "
          "critical-mineral and hazard lists. In addition, 14 feature-element results, covering known sites, extreme values, and "
          "randomly selected features, were recomputed by hand from the raw laboratory records (Appendix Table A3). The full "
          "workflow is scripted and can be reproduced from the public sources (see Data and code availability)."),
     para("", space_after=0)]
add_after(P[24], *M)

# ---------------------------------------------------------------- results 4.1
insert_after(P[27], "1,324 (88.4%) had at least one sample within 2 km", " (Figure 2)")
insert_after(P[27], "lacked a public geochemical sample within the search distance", " (Appendix Table A4)")
add_after(P[27], image_par(PUB / "Figure2_coverage_by_state.png", 5.6),
          caption("Figure 2.", "Geochemical sample coverage of NMWI v2.0 features by state, by distance from each feature "
                  "polygon to the nearest eligible sample. Values at bar ends are the number of features per state."))

# ---------------------------------------------------------------- results 4.3
edit(P[31], "A total of 304 features representing 83 sites", f"A total of {S['feat_dual']} features representing {S['site_dual']} sites")
insert_after(P[31], "classified as Dual priority sites", " (Figure 3)")
edit(P[31], "An additional 140 features were classified as primarily Resource targets and 140 as primarily Hazard targets",
     f"An additional {S['feat_resource']} features were classified as primarily Resource targets and {S['feat_hazard']} as primarily Hazard targets")
edit(P[31], "(Spearman ρ = 0.713)", f"(Spearman ρ = {S['rho_cmi_hhi']:.3f}; Figure 4)")
add_after(P[31], image_par(PUB / "Figure3_priority_map.png", 6.3),
          caption("Figure 3.", "Screening priority class of NMWI v2.0 features. Dual, upper third on both indices; Resource or "
                  "Hazard, upper third on one index; hollow circles, no public geochemical sample within 2 km. Alaska is shown as an "
                  "inset (not to scale)."),
          image_par(PUB / "Figure4_cmi_vs_hhi.png", 5.6),
          caption("Figure 4.", f"Critical Mineral Index versus Heavy-Metal Hazard Index (log10) for {n(S['features_scored'])} "
                  f"scored features. Dashed lines mark the upper-third cutoffs (CMI = {S['cmi_cut']:.2f}; HHI = {hhi_cut:.2f}). "
                  "Selected sites are labeled."))
edit(P[32], "Among the highest-ranked sites, the Berkeley Pit (Montana) exhibits elevated enrichment in Tellurium, Copper, Tungsten, "
            "Arsenic, and Antimony, while also displaying the highest hazard scores. Other important sites include Continental Mine "
            "(Montana), Tybo (Nevada), Dragon (Utah), Burgin (Utah), Bingham Canyon (Utah), Ray (Arizona), and Stibnite (Idaho).",
     "Among the highest-ranked sites with confidence grade A or B (Table 3), Eureka Mills (Utah) ranks first, combining strong "
     "Tellurium, Lead, Silver, and Indium enrichment with one of the highest hazard indices, driven by Lead, Cadmium, and Thallium. "
     "The Berkeley Pit (Montana) shares the highest Critical Mineral Index with Continental Mine (Montana), with enrichment in "
     "Tellurium, Copper, Tungsten, Arsenic, and Antimony. The single highest hazard index belongs to a mine dump at Jack Waite "
     "(Idaho), driven by Lead. Other important sites include Butte Reduction Works (Montana), Tybo and Treasure Hill (Nevada), "
     "Red Dog (Alaska), Burgin and Bingham Canyon (Utah), and Ray (Arizona).")
add_after(P[32], caption("Table 3.", "Highest-ranked sites with confidence grade A or B. Enrichment factors (x) are feature medians "
                         "relative to background; hazard ratios (x) are feature medians relative to EPA residential soil screening "
                         "levels (arsenic, noncancer level). HHI, sum of hazard ratios; Conf., confidence grade; Rank, overall site rank among all scored sites."),
          table(["Rank", "Site", "State", "Conf.", "CMI", "HHI", "Top critical-element enrichment", "Top hazard ratios"], T["t3"],
                [520, 1500, 560, 620, 520, 620, 2620, 2400]),
          para("", space_after=120))

# ---------------------------------------------------------------- results 4.4, 4.5
insert_after(P[34], "tungsten (154), and tin (146)", " (Figure 5)")
add_after(P[34], image_par(PUB / "Figure5_critical_elements.png", 5.6),
          caption("Figure 5.", "Critical elements most often enriched five-fold or more above background in scored features "
                  "(top 20 elements)."))
insert_after(P[36], "Virginia, Kansas, Arizona, Oregon, and New York", " (Figure 2; Appendix Table A4)")
insert_after(P[36], "and iron tailings facilities in New York", " (Table 4)")
add_after(P[36], caption("Table 4.", "Largest NMWI features with no public geochemical sample within 2 km."),
          table(["Feature ID", "Site", "State", "Feature type", "Area (km²)", "Commodity"], T["t4"],
                [1350, 1500, 600, 1700, 900, 3310]),
          para("", space_after=120))

# ---------------------------------------------------------------- results 4.6
edit(P[38], "Arsenic is the dominant contributor to the HHI, accounting for a median of 84.1% of hazard scores when EPA cancer-based "
            "residential screening levels are used. Substituting the non-cancer arsenic screening level produced a Spearman rank "
            "correlation of 0.67 relative to the default hazard rankings, with 57 of the top 100 features remaining unchanged.",
     f"Arsenic dominates the HHI when the EPA cancer-based residential screening level (0.68 mg/kg) is used, accounting for a median "
     f"of {S['as_share_cancer_pct']}% of each feature's hazard index; with the noncancer level adopted here (35 mg/kg), its median "
     f"share falls to {S['as_share_pct']}%. The two arsenic benchmarks give a Spearman rank correlation of {S['rho_as']:.3f} between "
     f"hazard indices, and {S['top100_overlap_as']} of the top 100 hazard-ranked features are shared (Table 5).")
add_after(P[38], caption("Table 5.", "Sensitivity of the screening indices to methodological choices."),
          table(["Test", "Comparison", "Result", "Note"], T["t5"], [2700, 3000, 1500, 2160]),
          para("", space_after=120))

# ---------------------------------------------------------------- discussion, limitations, conclusions, AI note
insert_after(P[42], "have been reported in earlier investigations", " (Piatak et al., 2025)")
insert_after(P[47], "varying detection limits and reporting practices.",
             " Some feature scores rest on only one or two samples for a given element; these are retained but flagged by the "
             "confidence grade (Table 2).")
edit(P[52], "In total, 83 sites", f"In total, {S['site_dual']} sites")
edit(P[59], "The authors used an artificial intelligence assistant to assist with the development and analysis pipeline code.",
     "The author used an artificial intelligence assistant (Claude, Anthropic) to assist with the development of the analysis "
     "pipeline code and to draft the Methods section, figure captions, and tables, which the author reviewed and edited. The author "
     "made the analytical decisions, verified the results against the source data, and takes full responsibility for the content.")

# ---------------------------------------------------------------- references
edit(P[64], "REFERENCE ", "REFERENCES")
insert_after(P[67], ", v. 11, no. 3, p. 2023-2050.", " https://doi.org/10.1007/s40831-025-01126-y")
insert_after(P[68], " (3rd ed.): Berlin, Springer.", " https://doi.org/10.1007/978-3-642-12419-8")
edit(P[69], "Piatak, N.M., Seal, R.R., Hammarstrom, J.M., and others, 2025, ", "Piatak, N.M., White, S.J., Hayes, S.M., and Seal, R.R., II, 2025, ")
edit(P[69], "Critical minerals in mine waste and mining-impacted environments", "Critical minerals in mine waste")
edit(P[69], ". [Insert full publication details.]", ": U.S. Geological Survey Fact Sheet 2025-3026. https://doi.org/10.3133/fs20253026")
insert_after(P[70], " (2nd ed.): Oxford, Elsevier, p. 1-51.", " https://doi.org/10.1016/B978-0-08-095975-7.00301-6")
insert_after(P[71], ", v. 47, no. 7, article 265.", " https://doi.org/10.1007/s10653-025-02566-x")

# ---------------------------------------------------------------- appendix (after references)
last_ref = P[75]
app = [para("", space_after=0),
       para("APPENDIX", bold=True, keep_next=True),
       caption("Table A1.", "Critical minerals on the Final 2025 List of Critical Minerals (U.S. Department of the Interior, 2025), the "
               "element used to represent each, and the background concentration used to calculate enrichment factors. Soil, median "
               "of USGS Geochemical Landscapes soil samples (Smith et al., 2013); UCC, upper continental crust (Rudnick and Gao, "
               "2014); Soil (upper bound), median dominated by nondetects, so enrichment is conservative."),
       table(["Critical mineral", "Element", "Background (mg/kg)", "Background source"], T["a1"], [2800, 1200, 1900, 3460]),
       para("", space_after=120),
       caption("Table A2.", "Hazard metals and EPA residential soil screening levels (THQ = 1; November 2024 summary table; U.S. "
               "Environmental Protection Agency, 2024) used in the Heavy-Metal Hazard Index."),
       table(["Element", "EPA analyte", "RSL used (mg/kg)", "Basis", "Alternative"], T["a2"], [900, 3300, 1500, 1900, 1760]),
       para("", space_after=120),
       caption("Table A3.", "Hand-verified spot checks. Each feature median was recomputed from the raw laboratory records "
               "(best-ranked value per sample, nondetects at half the detection limit) and matched the published value. "
               "Checks were selected on 31 October 2026, before the arsenic benchmark was finalized; feature medians do not depend on the benchmark. Random checks were drawn with seed 42."),
       table(["Check", "Type", "Feature ID", "Site", "Element", "Samples", "Median (mg/kg)"], T["a3"],
             [700, 1900, 1500, 1800, 900, 900, 1660]),
       para("", space_after=120),
       caption("Table A4.", "Feature counts, geochemical coverage, and priority classes by state."),
       table(["State", "Features", "Sites", "Sample within 1 km", "Unsampled", "Dual", "Resource", "Hazard"], T["a4"],
             [900, 1100, 900, 1600, 1200, 1000, 1300, 1360])]
add_after(last_ref, *app)

tree.write(str(doc_path), xml_declaration=True, encoding="UTF-8", standalone=True)
rels.write(str(rels_path), xml_declaration=True, encoding="UTF-8", standalone=True)
ct.write(str(ct_path), xml_declaration=True, encoding="UTF-8", standalone=True)
print("Draft 2 edits applied")
