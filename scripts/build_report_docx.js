#!/usr/bin/env node
/* Build the Anna University style Word report from docs/report/phase1-report.md and config.json.
   Usage: node scripts/build_report_docx.js            -> docs/report/Phase1-Report.docx
   Format rules: docs/anna-university/format-guide.md (A4, Times New Roman 13, 1.5 spacing, margins in mm). */
const fs = require("fs");
const path = require("path");
const D = require("docx");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, HeadingLevel,
  Header, PageNumber, NumberFormat, ImageRun, BorderStyle, ShadingType, TableOfContents, SimpleField, VerticalAlign,
} = D;

const ROOT = path.resolve(__dirname, "..");
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "docs/report/config.json"), "utf8"));
const SRC = fs.readFileSync(path.join(ROOT, "docs/report/phase1-report.md"), "utf8");

// ---- format constants (change here if your department differs) ----
const MM = 56.693;
const mm = (n) => Math.round(n * MM);
const FONT = "Times New Roman";
const BODY = 26; // half-points: 13 pt
const MARGIN = { top: mm(32), bottom: mm(28), left: mm(38), right: mm(22), header: mm(20), footer: mm(12) };
const PAGE = { width: 11906, height: 16838 }; // A4
const CONTENT_W = PAGE.width - MARGIN.left - MARGIN.right;
const INDENT = mm(20); // first-line and division indent: 20 mm
const FIRST_LINE_OFFSET = mm(50 - 32); // headings sit 50 mm below the top edge; top margin is 32 mm

const hasTamil = (s) => /[஀-௿]/.test(s);
const font = (s) => (hasTamil(s) ? { ascii: FONT, hAnsi: FONT, cs: "Latha" } : FONT);

function runs(text, base = {}) {
  const out = [];
  for (const part of text.split(/(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`)/)) {
    if (!part) continue;
    if (part.startsWith("**")) out.push(new TextRun({ text: part.slice(2, -2), bold: true, font: font(part), size: BODY, ...base }));
    else if (part.startsWith("`")) out.push(new TextRun({ text: part.slice(1, -1), font: "Courier New", size: BODY - 4, ...base }));
    else if (part.startsWith("*")) out.push(new TextRun({ text: part.slice(1, -1), italics: true, font: font(part), size: BODY, ...base }));
    else out.push(new TextRun({ text: part, font: font(part), size: BODY, ...base }));
  }
  return out;
}

// ---- parse markdown into H1 sections of blocks ----
function expandIncludes(md) {
  return md.replace(/^\{\{include:(.+?)\}\}$/gm, (_, p) => "```\n" + fs.readFileSync(path.join(ROOT, p), "utf8").replace(/\s+$/, "") + "\n```");
}

function parse(md) {
  const lines = expandIncludes(md).split("\n");
  const sections = [];
  let cur = null;
  let pendingCaption = null;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("# ")) {
      cur = { title: line.slice(2).trim(), blocks: [] };
      sections.push(cur);
    } else if (!cur) {
      continue;
    } else if (line.startsWith("```")) {
      const code = [];
      for (i++; i < lines.length && !lines[i].startsWith("```"); i++) code.push(lines[i]);
      cur.blocks.push({ t: "code", lines: code });
    } else if (/^Table \d+(\.\d+)?: /.test(line)) {
      pendingCaption = line.replace(": ", "  ");
    } else if (line.startsWith("|")) {
      const rows = [];
      for (; i < lines.length && lines[i].startsWith("|"); i++) {
        if (!/^\|[\s:|-]+\|?$/.test(lines[i])) rows.push(lines[i].trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
      }
      i--;
      cur.blocks.push({ t: "table", rows, caption: pendingCaption });
      pendingCaption = null;
    } else if (/^!\[(.+)\]\((.+)\)$/.test(line)) {
      const [, alt, src] = line.match(/^!\[(.+)\]\((.+)\)$/);
      cur.blocks.push({ t: "image", caption: alt.replace(": ", "  "), src });
    } else if (line.startsWith("### ")) cur.blocks.push({ t: "h3", text: line.slice(4) });
    else if (line.startsWith("## ")) cur.blocks.push({ t: "h2", text: line.slice(3) });
    else if (/^\d+\. /.test(line)) cur.blocks.push({ t: "item", text: line });
    else if (line.trim()) cur.blocks.push({ t: "p", text: line.trim() });
  }
  return sections;
}

// ---- block renderers ----
const para = (text, o = {}) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: INDENT }, spacing: { line: 360, after: 120 }, children: runs(text), ...o });

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}

function renderTable(block) {
  const cols = block.rows[0].length;
  const weights = Array.from({ length: cols }, (_, c) => Math.max(8, Math.min(40, Math.max(...block.rows.map((r) => (r[c] || "").length)))));
  const total = weights.reduce((a, b) => a + b, 0);
  let widths = weights.map((w) => Math.floor((w / total) * CONTENT_W));
  widths[cols - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const rows = block.rows.map((r, ri) =>
    new TableRow({
      tableHeader: ri === 0,
      cantSplit: true,
      children: widths.map((w, c) =>
        new TableCell({
          width: { size: w, type: WidthType.DXA },
          borders,
          margins: { top: 40, bottom: 40, left: 80, right: 80 },
          shading: ri === 0 ? { type: ShadingType.CLEAR, fill: "D9D9D9", color: "auto" } : undefined,
          children: [new Paragraph({ spacing: { line: 240 }, children: runs(r[c] || "", { size: 22, bold: ri === 0 }) })],
        })
      ),
    })
  );
  const out = [];
  if (block.caption) out.push(new Paragraph({ style: "TableCaption", keepNext: true, children: [new TextRun({ text: block.caption, font: FONT, size: BODY })] }));
  out.push(new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: widths, rows }));
  out.push(new Paragraph({ spacing: { after: 160 }, children: [] }));
  return out;
}

function renderImage(block) {
  const { w, h, data } = pngSize(path.join(ROOT, block.src));
  const width = 520;
  const height = Math.round((h / w) * width);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120 }, children: [new ImageRun({ type: "png", data, transformation: { width, height }, altText: { title: block.caption, description: block.caption, name: path.basename(block.src) } })] }),
    new Paragraph({ style: "FigureCaption", children: [new TextRun({ text: block.caption, font: FONT, size: BODY })] }),
  ];
}

function renderCode(block) {
  return block.lines.map((l) =>
    new Paragraph({ spacing: { line: 240 }, shading: { type: ShadingType.CLEAR, fill: "F2F2F2", color: "auto" }, children: [new TextRun({ text: l.replace(/\t/g, "    ") || " ", font: "Courier New", size: 16 })] })
  );
}

function renderBlocks(blocks, { double = false } = {}) {
  const out = [];
  for (const b of blocks) {
    if (b.t === "p") out.push(para(b.text, double ? { spacing: { line: 480, after: 0 } } : {}));
    else if (b.t === "h2") out.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: b.text, bold: true, font: FONT, size: BODY })] }));
    else if (b.t === "h3") out.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text: b.text, bold: true, font: FONT, size: BODY })] }));
    else if (b.t === "item") out.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { left: INDENT + 360, hanging: 360 }, spacing: { line: 360, after: 60 }, children: runs(b.text) }));
    else if (b.t === "table") out.push(...renderTable(b));
    else if (b.t === "image") out.push(...renderImage(b));
    else if (b.t === "code") out.push(...renderCode(b));
  }
  return out;
}

const heading1 = (lines, { first = false } = {}) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    alignment: AlignmentType.CENTER,
    pageBreakBefore: !first,
    spacing: { before: FIRST_LINE_OFFSET, after: 360, line: 360 },
    children: lines.flatMap((t, i) => [new TextRun({ text: t, bold: true, font: FONT, size: 28, break: i ? 1 : 0 })]),
  });

const plainHeading = (text) =>
  new Paragraph({ alignment: AlignmentType.CENTER, pageBreakBefore: true, spacing: { before: FIRST_LINE_OFFSET, after: 360 }, children: [new TextRun({ text, bold: true, font: FONT, size: 28 })] });

const centered = (text, size, o = {}) =>
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { line: 360, before: o.before || 0, after: o.after || 0 }, children: [new TextRun({ text, bold: o.bold !== false, italics: !!o.italics, font: FONT, size: size * 2 })] });

// ---- front matter ----
function cover() {
  return [
    centered(cfg.title, 18, { before: mm(18), after: 600 }),
    centered(cfg.report_type, 14, { after: 600 }),
    centered("Submitted by", 14, { italics: true, after: 200 }),
    centered(cfg.candidate, 16, { after: 100 }),
    centered(`(Register No. ${cfg.register_no})`, 14, { bold: false, after: 600 }),
    centered("in partial fulfillment for the award of the degree of", 14, { after: 300 }),
    centered("MASTER OF ENGINEERING IN", 16),
    centered(cfg.programme, 16, { after: 800 }),
    centered(cfg.department, 16),
    centered(cfg.college, 16),
    centered(cfg.affiliation, 12, { after: 800 }),
    centered(cfg.month_year, 14),
  ];
}

function bonafide() {
  const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const nb = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
  const half = CONTENT_W / 2;
  const sign = (lines) => new TableCell({ width: { size: half, type: WidthType.DXA }, borders: nb, children: lines.map((l, i) => new Paragraph({ spacing: { before: i === 0 ? 800 : 0 }, children: [new TextRun({ text: l, bold: i === 1, font: FONT, size: 24 })] })) });
  const kind = cfg.report_type.startsWith("PHASE I ") ? "Report" : "Thesis";
  return [
    new Paragraph({ pageBreakBefore: true, alignment: AlignmentType.CENTER, spacing: { before: FIRST_LINE_OFFSET }, children: [new TextRun({ text: cfg.college, bold: true, font: FONT, size: 36 })] }),
    centered(cfg.affiliation, 12, { bold: false, after: 360 }),
    centered("BONAFIDE CERTIFICATE", 16, { after: 360 }),
    new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: INDENT }, spacing: { line: 480 }, children: runs(`Certified that this ${kind} titled “${cfg.title}” is the bonafide work of **${cfg.candidate}** (Register No. ${cfg.register_no}) who carried out the work under my supervision. Certified further that to the best of my knowledge the work reported herein does not form part of any other thesis or dissertation on the basis of which a degree or award was conferred on an earlier occasion on this or any other candidate.`) }),
    new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [half, half], rows: [new TableRow({ children: [
      sign(["<<Signature of the HOD with date>>", cfg.hod_name, cfg.hod_designation, cfg.department_title, cfg.college_title]),
      sign(["<<Signature of the Supervisor with date>>", cfg.supervisor_name, cfg.supervisor_designation, cfg.department_title, cfg.college_title]),
    ] })] }),
  ];
}

function buildFront(sections) {
  const find = (t) => sections.find((s) => s.title === t);
  const out = [...cover(), ...bonafide()];
  const abs = find("ABSTRACT"), tam = find("ABSTRACT (TAMIL)"), ack = find("ACKNOWLEDGEMENT"), abbr = find("LIST OF ABBREVIATIONS");
  out.push(heading1(["ABSTRACT"]), ...renderBlocks(abs.blocks, { double: true }));
  out.push(heading1(["ABSTRACT (TAMIL)"]), ...renderBlocks(tam.blocks, { double: true }));
  out.push(plainHeading("ACKNOWLEDGEMENT"), ...ack.blocks.map((b) => para(b.text, { spacing: { line: 480, after: 0 } })));
  out.push(new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { before: 800 }, children: [new TextRun({ text: cfg.candidate, bold: true, font: FONT, size: BODY })] }));
  out.push(plainHeading("TABLE OF CONTENTS"));
  out.push(new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }));
  out.push(heading1(["LIST OF TABLES"]));
  out.push(new Paragraph({ children: [new SimpleField('TOC \\h \\z \\t "Table Caption,1"', "Right-click here and choose Update Field to build the list of tables.")] }));
  out.push(heading1(["LIST OF FIGURES"]));
  out.push(new Paragraph({ children: [new SimpleField('TOC \\h \\z \\t "Figure Caption,1"', "Right-click here and choose Update Field to build the list of figures.")] }));
  out.push(heading1(["LIST OF ABBREVIATIONS"]), ...renderBlocks(abbr.blocks));
  return out;
}

function buildMain(sections) {
  const out = [];
  let firstMain = true;
  for (const s of sections) {
    const ch = s.title.match(/^CHAPTER (\d+): (.+)$/);
    const ap = s.title.match(/^APPENDIX (\d+): (.+)$/);
    if (ch) out.push(heading1([`CHAPTER ${ch[1]}`, ch[2]], { first: false }));
    else if (ap) out.push(heading1([`APPENDIX ${ap[1]}`, ap[2]]));
    else if (s.title === "REFERENCES") {
      out.push(heading1(["REFERENCES"]));
      for (const b of s.blocks) out.push(new Paragraph({ alignment: AlignmentType.LEFT, indent: { left: 567, hanging: 567 }, spacing: { line: 240, after: 160 }, children: runs(b.text) }));
      continue;
    } else continue;
    out.push(...renderBlocks(s.blocks));
    firstMain = false;
  }
  return out;
}

// ---- document ----
const sections = parse(SRC);
const pageNum = new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 24 })] })] });
const blank = new Header({ children: [new Paragraph({ children: [] })] });
const page = (fmt) => ({ size: PAGE, margin: MARGIN, pageNumbers: { start: 1, formatType: fmt } });

const doc = new Document({
  creator: "Manikandan Sankaranarayanan",
  title: cfg.title,
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: BODY }, paragraph: { spacing: { line: 360 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 28, bold: true }, paragraph: { alignment: AlignmentType.CENTER, outlineLevel: 0, keepNext: true } },
      { id: "Heading2", name: "heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: BODY, bold: true }, paragraph: { alignment: AlignmentType.LEFT, outlineLevel: 1, keepNext: true, indent: { left: INDENT }, spacing: { before: 240, after: 120, line: 360 } } },
      { id: "Heading3", name: "heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: BODY, bold: true }, paragraph: { alignment: AlignmentType.LEFT, outlineLevel: 2, keepNext: true, indent: { left: INDENT }, spacing: { before: 200, after: 120, line: 360 } } },
      { id: "TableCaption", name: "Table Caption", basedOn: "Normal", next: "Normal", run: { font: FONT, size: BODY }, paragraph: { alignment: AlignmentType.LEFT, keepNext: true, spacing: { before: 200, after: 80, line: 240 } } },
      { id: "FigureCaption", name: "Figure Caption", basedOn: "Normal", next: "Normal", run: { font: FONT, size: BODY }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 80, after: 240, line: 240 } } },
    ],
  },
  sections: [
    { properties: { titlePage: true, page: page(NumberFormat.LOWER_ROMAN) }, headers: { default: pageNum, first: blank }, children: buildFront(sections) },
    { properties: { page: page(NumberFormat.DECIMAL) }, headers: { default: pageNum }, children: buildMain(sections) },
  ],
});

const out = path.join(ROOT, "docs/report/Phase1-Report.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(out, buf);
  console.log("wrote", path.relative(ROOT, out), `(${Math.round(buf.length / 1024)} KB)`);
});
