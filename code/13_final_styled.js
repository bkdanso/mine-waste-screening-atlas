// 13_final_styled.js: lay out the author's final manuscript in a two-column journal style
// (modeled on Nilsson et al., Precambrian Research) with numbered references (arXiv style).
// Plain-language note: the words come unchanged from your final draft via styled_spec.json;
// this script only sets the page design. Output: paper/final/Danso_final_styled.docx
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, BorderStyle,
  AlignmentType, SectionType, Header, Footer, PageNumber, LevelFormat, TabStopType, HeightRule, ExternalHyperlink,
} = require('docx');

const ROOT = path.resolve(__dirname, '..');
const SPEC = JSON.parse(fs.readFileSync(path.join(ROOT, 'paper/final/styled_spec.json')));
const MEDIA = process.argv[2]; // unzipped author docx word/ dir
const FONT = 'Times New Roman';
const BODY = 19; // 9.5 pt
const SMALL = 15; // 7.5 pt
const TEXTW = 10080; // 7 in usable width (0.75 in margins)
const BLUE = '1F5C99';
const pngSize = (f) => { const b = fs.readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };

const r = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || BODY, bold: o.b, italics: o.i,
  superScript: o.sup, color: o.color, characterSpacing: o.cs });
const runsOf = (runs, size) => runs.map((x) => r(x.t, { b: x.b, i: x.i, size }));
const rule = (pos = 'bottom', after = 120) => new Paragraph({ spacing: { after }, border: { [pos]: { style: BorderStyle.SINGLE, size: 4, color: '000000', space: 1 } }, children: [] });

// ---------------------------------------------------------------- front matter
const B = SPEC.blocks;
const textOf = (b) => (b.runs ? b.runs.map((x) => x.t).join('') : b.text);
let i = 0;
const title = textOf(B[i++]).trim();
const author = textOf(B[i++]).trim();
const affil = textOf(B[i++]).trim();          // "Independent Researcher, ... ORCID: ..."
const corr = textOf(B[i++]).trim();           // "Corresponding author: email"
const prep = textOf(B[i++]).trim();           // preprint note
i++;                                          // ABSTRACT heading
const abstract = B[i++];
const keywords = B[i++];
const affilOnly = affil.replace(/\.?\s*ORCID:.*$/, '');
const orcid = (affil.match(/ORCID:\s*([\d-X]+)/) || [])[1];
const email = corr.replace(/^Corresponding author:\s*/, '');

const front = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 160 }, children: [r(title, { size: 32 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [r(author, { size: 22 }),
    new ExternalHyperlink({ link: `https://orcid.org/${orcid}`, children: [new ImageRun({ type: 'png',
      data: fs.readFileSync(path.join(ROOT, 'paper/pub/orcid_id.png')), transformation: { width: 10, height: 10 },
      altText: { title: 'ORCID iD', description: `ORCID iD ${orcid}`, name: 'orcid' } })] }),
    r(',a,*', { size: 22, sup: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [r('a', { size: SMALL, sup: true, i: true }), r(` ${affilOnly}`, { size: SMALL, i: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [r(prep, { size: SMALL, i: true })] }),
  rule('bottom', 60),
  new Paragraph({ spacing: { before: 60, after: 100 }, children: [r('A B S T R A C T', { size: 16, cs: 20 })] }),
  new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 100, line: 252 }, children: runsOf(abstract.runs, 17) }),
  new Paragraph({ spacing: { after: 80 }, children: runsOf(keywords.runs, 17) }),
  rule('bottom', 200),
];

// ---------------------------------------------------------------- body blocks
const sections = [];
let cur = [];
let curCols = 1;
const flush = (cols) => { if (cur.length) sections.push({ cols: curCols, children: cur }); cur = []; curCols = cols; };
const want = (cols) => { if (curCols !== cols) flush(cols); };
cur.push(...front);
want(2);

const para = (runs, o = {}) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED, indent: o.noIndent ? undefined : { firstLine: 240 },
  spacing: { after: 0, line: 245 }, children: runsOf(runs, o.size || BODY),
});
let firstAfterHeading = true;
let figW = { 'media/image1.png': 6.3, 'media/image2.png': 5.0, 'media/image3.png': 6.6, 'media/image4.png': 5.0, 'media/image5.png': 5.0 };
let pendingImage = null;
let pendingTableCaption = null;
let inAppendix = false;
let lastWasList = false;

const tableEl = (rows) => {
  const ncol = rows[0].length;
  const len = rows[0].map((_, c) => Math.max(...rows.map((row) => Math.min(String(row[c]).length, 60))) + 4);
  const tot = len.reduce((a, b) => a + b, 0);
  const widths = len.map((l) => Math.floor((TEXTW * l) / tot));
  widths[ncol - 1] += TEXTW - widths.reduce((a, b) => a + b, 0);
  const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
  const line = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
  return new Table({
    width: { size: TEXTW, type: WidthType.DXA }, columnWidths: widths,
    borders: { top: line, bottom: line, left: none, right: none, insideHorizontal: none, insideVertical: none },
    rows: rows.map((row, ri) => new TableRow({
      tableHeader: ri === 0, cantSplit: true,
      children: row.map((c, ci) => new TableCell({
        width: { size: widths[ci], type: WidthType.DXA },
        borders: { top: ri === 0 ? line : none, bottom: ri === 0 ? line : none, left: none, right: none },
        margins: { top: 30, bottom: 30, left: 60, right: 60 },
        children: [new Paragraph({ keepNext: rows.length <= 30 && ri < rows.length - 1, children: [r(String(c), { size: SMALL })] })],
      })),
    })),
  });
};

for (; i < B.length; i++) {
  const b = B[i];
  if (b.type === 'h1') {
    want(2);
    cur.push(new Paragraph({ keepNext: true, spacing: { before: 260, after: 140 }, children: [r(`${b.num} ${b.text}`, { b: true })] }));
    firstAfterHeading = true; continue;
  }
  if (b.type === 'h2') {
    want(2);
    cur.push(new Paragraph({ keepNext: true, spacing: { before: 200, after: 120 }, children: [r(`${b.num} ${b.text}`, { i: true })] }));
    firstAfterHeading = true; continue;
  }
  if (b.type === 'h0') {
    const t = b.text.trim();
    if (t === 'ABSTRACT') continue;
    if (t === 'REFERENCES') {
      want(2);
      cur.push(new Paragraph({ keepNext: true, spacing: { before: 260, after: 140 }, children: [r('References', { b: true })] }));
      SPEC.refs.forEach((ref, k) => cur.push(new Paragraph({
        alignment: AlignmentType.LEFT, spacing: { after: 40 }, indent: { left: 340, hanging: 340 },
        tabStops: [{ type: TabStopType.LEFT, position: 340 }],
        children: [r(`[${k + 1}]\t`, { size: SMALL + 1 }), r(ref, { size: SMALL + 1 })],
      })));
      continue;
    }
    if (t === 'APPENDIX') {
      flush(1); inAppendix = true;
      cur.push(new Paragraph({ pageBreakBefore: true, spacing: { after: 160 }, children: [r('Appendix A. Supplementary tables', { b: true })] }));
      continue;
    }
    want(2);
    const label = t === 'Use of AI Tools' ? 'Use of AI tools' : t;
    cur.push(new Paragraph({ keepNext: true, spacing: { before: 220, after: 100 }, children: [r(label, { b: true })] }));
    firstAfterHeading = true; continue;
  }
  if (b.type === 'image') { pendingImage = b.src; continue; }
  if (b.type === 'caption') {
    const label = b.runs[0].t.trim();
    const rest = b.runs.slice(1);
    if (pendingImage) {
      want(1);
      const f = path.join(MEDIA, pendingImage);
      const [w, h] = pngSize(f);
      const wi = (figW[pendingImage] || 6) * 72;
      const src = pendingImage === 'media/image1.png' ? path.join(ROOT, 'paper/pub/Figure1_workflow_numbered.png') : f;
      cur.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 80 },
        children: [new ImageRun({ type: 'png', data: fs.readFileSync(src), transformation: { width: wi, height: (wi * h) / w } })] }));
      cur.push(new Paragraph({ spacing: { after: 220 }, alignment: AlignmentType.JUSTIFIED,
        children: [r(`${label} `, { b: true, size: SMALL + 1 }), ...runsOf(rest, SMALL + 1)] }));
      pendingImage = null;
      want(2);
    } else {
      pendingTableCaption = { label: label.replace(/\.$/, ''), rest };
    }
    continue;
  }
  if (b.type === 'table') {
    const back = inAppendix ? 1 : 2;
    want(1);
    if (pendingTableCaption) {
      cur.push(new Paragraph({ keepNext: true, spacing: { before: 160, after: 20 }, children: [r(pendingTableCaption.label, { b: true, size: SMALL + 1 })] }));
      cur.push(new Paragraph({ keepNext: true, spacing: { after: 80 }, children: runsOf(pendingTableCaption.rest, SMALL + 1) }));
      pendingTableCaption = null;
    }
    cur.push(tableEl(b.rows));
    cur.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
    want(back);
    continue;
  }
  if (b.type === 'p') {
    if (b.list) {
      cur.push(new Paragraph({ numbering: { reference: 'q', level: 0 }, alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 40, line: 245 }, children: runsOf(b.runs, BODY) }));
      lastWasList = true; continue;
    }
    cur.push(para(b.runs, { noIndent: firstAfterHeading || lastWasList }));
    firstAfterHeading = false; lastWasList = false;
  }
}
flush(1);

const headerTxt = new Header({ children: [new Paragraph({
  tabStops: [{ type: TabStopType.RIGHT, position: TEXTW }],
  children: [r('Danso B.K.', { i: true, size: SMALL }), r('\tPreprint, 2026', { i: true, size: SMALL })] })] });
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SMALL })] })] });

// corresponding-author note at the end of the front matter (as a small line, Elsevier-style footnote text)
const corrNote = new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [r('* ', { size: SMALL }),
  r('Corresponding author. E-mail address: ', { size: SMALL }), new ExternalHyperlink({ link: `mailto:${email}`, children: [r(email, { size: SMALL, color: BLUE })] }), r('.', { size: SMALL })] });
Packer.toBuffer(new Document({
  creator: author, title,
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  numbering: { config: [{ reference: 'q', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 300, hanging: 300 } } } }] }] },
  sections: sections.map((s, k) => ({
    properties: {
      type: k === 0 ? undefined : SectionType.CONTINUOUS,
      titlePage: k === 0,
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080, header: 600, footer: 600 } },
      column: s.cols === 2 ? { count: 2, space: 400, equalWidth: true } : { count: 1 },
    },
    headers: { default: headerTxt },
    footers: { default: footer, first: footer },
    children: k === 0 ? [...s.children.slice(0, 4), corrNote, ...s.children.slice(4)] : s.children,
  })),
})).then((buf) => {
  fs.writeFileSync(path.join(ROOT, 'paper/final/Danso_final_styled.docx'), buf);
  console.log('styled manuscript written; sections:', sections.length);
});
