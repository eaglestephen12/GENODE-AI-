import copy
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_MARK
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "SIC_AI_Capstone Project_Presentation Slide Template.pptx"
OUT = ROOT / "GENEODE_SIC_Capstone_Presentation.pptx"

BLUE = RGBColor(0x19, 0x3E, 0xB0)
TINT = RGBColor(0xEE, 0xF1, 0xFB)
TINT2 = RGBColor(0xCB, 0xD4, 0xF3)
MID = RGBColor(0x7F, 0x95, 0xD9)
TXT = RGBColor(0x26, 0x26, 0x26)
GRAY = RGBColor(0x6B, 0x6B, 0x6B)
LINE = RGBColor(0xD0, 0xD5, 0xE5)
AMBER = RGBColor(0xE0, 0x8A, 0x1E)
GRAYBAR = RGBColor(0xA6, 0xA6, 0xA6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

F4 = "SamsungOne 400"
F7 = "SamsungOne 700"

prs = Presentation(SRC)
LAY_CONTENT = [l for l in prs.slide_layouts if l.name == "2_Table of Contents"][0]

# ---- footer project name in layouts ------------------------------------
for lay in prs.slide_layouts:
    for sh in lay.shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.text.strip() == "Project Name":
                        r.text = "GENEODE Bioinformatics"


# ---- helpers ------------------------------------------------------------
def _noshadow(shape):
    spPr = shape._element.spPr
    if spPr.find(qn("a:effectLst")) is None:
        eff = etree.SubElement(spPr, qn("a:effectLst"))
        # effectLst must come after ln if present; python-pptx appends at end which is valid here


def rect(slide, x, y, w, h, fill=None, line=None, rounded=False, radius=0.06, shape=None):
    st = shape or (MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE)
    s = slide.shapes.add_shape(st, Inches(x), Inches(y), Inches(w), Inches(h))
    if rounded and shape is None:
        s.adjustments[0] = radius
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(0.75)
    _noshadow(s)
    return s


def _run(p, text, size, color, bold=False, italic=False):
    r = p.add_run()
    r.text = text
    f = r.font
    f.size = Pt(size)
    f.name = F7 if bold else F4
    f.color.rgb = color
    f.italic = italic
    rPr = r._r.get_or_add_rPr()
    ea = etree.SubElement(rPr, qn("a:ea"))
    ea.set("typeface", F7 if bold else F4)
    return r


def fill_tf(tf, paras, size=13, color=TXT, align=PP_ALIGN.LEFT, after=0, bullet=False, line=None):
    """paras: list of str | list of (text, opts) runs."""
    first = True
    for para in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.space_after = Pt(after)
        if line:
            p.line_spacing = line
        runs = [(para, {})] if isinstance(para, str) else para
        for text, o in runs:
            _run(p, text, o.get("size", size), o.get("color", color), o.get("b", False), o.get("i", False))
        if bullet:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", "171450")
            pPr.set("indent", "-171450")
            bc = etree.SubElement(pPr, qn("a:buClr"))
            sc = etree.SubElement(bc, qn("a:srgbClr"))
            sc.set("val", "193EB0")
            bu = etree.SubElement(pPr, qn("a:buChar"))
            bu.set("char", "•")


def tb(slide, x, y, w, h, paras, size=13, color=TXT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
       after=0, bullet=False, line=None):
    t = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = t.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    fill_tf(tf, paras, size, color, align, after, bullet, line)
    return t


def badge(slide, x, y, d, text, fill=BLUE, color=WHITE, size=14):
    s = rect(slide, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)
    tf = s.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    fill_tf(tf, [text], size, color, PP_ALIGN.CENTER)
    for r in tf.paragraphs[0].runs:
        r.font.name = F7
    return s


def new_slide(num, sub, unit, title, notes=None):
    s = prs.slides.add_slide(LAY_CONTENT)
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx == 15:
            ph._element.getparent().remove(ph._element)
    s.placeholders[10].text_frame.text = num
    s.placeholders[11].text_frame.text = sub
    s.placeholders[12].text_frame.text = unit
    s.placeholders[13].text_frame.text = "UNIT"
    s.placeholders[13].text_frame.word_wrap = False
    s.shapes.title.text_frame.text = title
    for r in s.shapes.title.text_frame.paragraphs[0].runs:
        r.font.size = Pt(28)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def card(slide, x, y, w, h, fill=WHITE, line=LINE):
    return rect(slide, x, y, w, h, fill=fill, line=line, rounded=True, radius=0.04)


def style_chart(ch, size=12):
    ch.font.size = Pt(size)
    ch.font.name = F4
    ch.font.color.rgb = TXT
    ch.has_title = False


def bar_chart(slide, x, y, w, h, cats, vals, colors, fmt="0.00", horizontal=True, vmax=1.0, name="Value"):
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series(name, vals)
    kind = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
    gf = slide.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    style_chart(ch)
    ch.has_legend = False
    plot = ch.plots[0]
    plot.gap_width = 45
    plot.vary_by_categories = False
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = fmt
    dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(12)
    dl.font.name = F7
    va = ch.value_axis
    va.minimum_scale = 0
    va.maximum_scale = vmax
    va.has_major_gridlines = False
    va.visible = False
    ca = ch.category_axis
    ca.has_major_gridlines = False
    ca.major_tick_mark = XL_TICK_MARK.NONE
    ca.tick_labels.font.size = Pt(12)
    ca.format.line.color.rgb = LINE
    if horizontal:
        ca.reverse_order = True
    ser = plot.series[0]
    for i, c in enumerate(colors):
        pt = ser.points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = c
    return ch


def stat_row(slide, x, y, w, h, big, label, fill=TINT, bigcolor=BLUE, bigw=1.5, bigsize=28):
    rect(slide, x, y, w, h, fill=fill, rounded=True, radius=0.06)
    tb(slide, x + 0.2, y, bigw, h, [big], size=bigsize, color=bigcolor, anchor=MSO_ANCHOR.MIDDLE)
    for r in slide.shapes[-1].text_frame.paragraphs[0].runs:
        r.font.name = F7
    tb(slide, x + 0.2 + bigw + 0.1, y, w - bigw - 0.5, h, [label], size=13, anchor=MSO_ANCHOR.MIDDLE)


def cap(slide, x, y, w, text):
    tb(slide, x, y, w, 0.3, [text], size=12, color=GRAY)


L = 0.49
W = 9.85
TOP = 2.4

# ======================= slide 1: cover ====================================
s1 = prs.slides[0]
for sh in s1.shapes:
    if sh.is_placeholder and sh.placeholder_format.type is not None and sh.placeholder_format.idx == 0:
        p = sh.text_frame.paragraphs[0]
        rs = [r for r in p.runs]
        rs[0].text = "GENEODE"
        rs[1].text = "Bioinformatics"
    elif sh.is_placeholder and sh.placeholder_format.idx == 11:
        tf = sh.text_frame
        tf.text = "Stephen Mburu Mwangi"
        p2 = tf.add_paragraph()
        p2.text = "BSc Biochemistry and Molecular Biology, JKUAT"
tb(s1, 0.79, 5.15, 6.4, 0.7,
   ["An AI-powered integrated platform for in-silico molecular biology research, with its first AI module: phage host prediction."],
   size=13, color=GRAY)

# # ======================= slide 2: agenda ===================================
# agenda = [
#     ("Unit 1. Project Overview", ["1.1. The Fragmentation Problem", "1.2. The GENEODE Solution", "1.3. Competitive Landscape"]),
#     ("Unit 2. Platform Design", ["2.1. Workflow & Architecture", "2.2. Seamless Integrations", "2.3. Roadmap, Risk & Budget"]),
#     ("Unit 3. AI Phage Module", ["3.1. Problem & Data", "3.2. Honest Validation", "3.3. Confidence, Helper & Limits"]),
# ]
# s2 = prs.slides[1]
# s2.shapes[0].text_frame  # ensure exists
# groups = [sh for sh in s2.shapes if sh.shape_type == 6]
# groups.sort(key=lambda g: g.top)
# for g, (ttl, subs) in zip(groups, agenda):
#     rects = [c for c in g.shapes if c.has_text_frame and c.text_frame.text.strip()]
#     rects.sort(key=lambda c: c.top)
#     rects[0].text_frame.paragraphs[0].runs[0].text = ttl
#     for p, t in zip(rects[1].text_frame.paragraphs, subs):
#         p.runs[0].text = t
# ======================= slide 2: agenda ===================================
agenda = [
    ("Unit 1. Project Overview", ["1.1. The Fragmentation Problem", "1.2. The GENEODE Solution", "1.3. Competitive Landscape"]),
    ("Unit 2. Platform Design", ["2.1. Workflow & Architecture", "2.2. Seamless Integrations", "2.3. Roadmap, Risk & Budget"]),
    ("Unit 3. AI Phage Module", ["3.1. Problem & Data", "3.2. Honest Validation", "3.3. Confidence, Helper & Limits"]),
]
s2 = prs.slides[1]

groups = [sh for sh in s2.shapes if sh.shape_type == 6]
groups.sort(key=lambda g: g.top)

for g, (ttl, subs) in zip(groups, agenda):
    # Keep the .text.strip() filter so empty decorative shapes are ignored
    child_shapes = [c for c in g.shapes if c.has_text_frame and c.text_frame.text.strip()]
    child_shapes.sort(key=lambda c: c.top)
    
    if len(child_shapes) >= 2:
        p0 = child_shapes[0].text_frame.paragraphs[0]
        if p0.runs:
            p0.runs[0].text = ttl
        else:
            p0.text = ttl
            
        for p, t in zip(child_shapes[1].text_frame.paragraphs, subs):
            if p.runs:
                p.runs[0].text = t
            else:
                p.text = t
# ======================= UNIT 1 ============================================
# 1.1 problem
s = new_slide("1.1", "The Fragmentation Problem", "01", "Bioinformatics tools are fragmented")
tb(s, L, TOP, W, 0.6,
   ["Bioinformatics research currently relies on a highly fragmented set of databases and computational tools."],
   size=14)
items = [
    ("Scattered Resources", "Sequence repositories, structure archives and pathway databases operate independently."),
    ("Manual Stitching", "Researchers constantly transfer data between websites, converting formats by hand."),
    ("High Barrier to Entry", "Students and early-career researchers face a steep learning curve."),
    ("Lost Efficiency", "Time is spent navigating systems instead of interpreting biological data."),
]
cw, ch_ = 4.8, 1.65
for i, (h, d) in enumerate(items):
    cx = L + (i % 2) * (cw + 0.25)
    cy = 3.2 + (i // 2) * (ch_ + 0.2)
    card(s, cx, cy, cw, ch_)
    badge(s, cx + 0.25, cy + 0.3, 0.5, str(i + 1))
    tb(s, cx + 0.95, cy + 0.28, cw - 1.2, 0.3, [[(h, {"b": True, "size": 15, "color": BLUE})]])
    tb(s, cx + 0.95, cy + 0.7, cw - 1.2, 0.85, [d], size=13)

# 1.2 solution
s = new_slide("1.2", "The GENEODE Solution", "01", "GENEODE: one unified, intelligent platform")
rect(s, L, TOP, W, 1.45, fill=TINT, rounded=True, radius=0.05)
tb(s, L + 0.3, TOP + 0.18, W - 0.6, 1.2,
   [[("GENEODE Bioinformatics is an AI-assisted platform that integrates complex biological databases and tools into a single environment.", {"b": True, "size": 14, "color": BLUE})],
    "It does not replace scientific expertise. It acts as an intelligent assistant: it accepts sequence data, runs core analyses, retrieves external annotations and gives a clear, AI-generated interpretation."],
   size=13, after=6)
caps = [
    ("Core Analysis Engine", "Upload FASTA/FASTQ files for instant validation, GC content analysis, Open Reading Frame (ORF) detection and automated DNA-to-protein translation."),
    ("Deep Integration", "Seamlessly queries established global databases like NCBI (BLAST), UniProt and KEGG to pull sequence alignments and annotations automatically."),
    ("AI Interpretation Layer", "Transforms raw computational output into plain-language biological summaries, lowering the barrier for students analysing complex multi-omics data."),
]
cw = (W - 0.5) / 3
for i, (h, d) in enumerate(caps):
    cx = L + i * (cw + 0.25)
    card(s, cx, 4.1, cw, 2.65)
    badge(s, cx + 0.25, 4.32, 0.5, str(i + 1))
    tb(s, cx + 0.25, 4.98, cw - 0.5, 0.3, [[(h, {"b": True, "size": 15, "color": BLUE})]])
    tb(s, cx + 0.25, 5.4, cw - 0.5, 1.3, [d], size=13)

# 1.3 competitive landscape
s = new_slide("1.3", "Competitive Landscape", "01", "A low-barrier niche between Galaxy and Benchling")
rows = [
    ("FEATURE", "GALAXY", "BENCHLING / GENEIOUS", "GENEODE"),
    ("Primary audience", "Bioinformaticians, core labs", "Industry and funded academic", "Students, early-career"),
    ("Tool breadth", "Very large ecosystem", "Broad, commercially curated", "Targeted, phased approach"),
    ("AI interpretation", "Not a core feature", "Limited availability", "Core first-class feature"),
    ("Cost and access", "Free, self-host", "Commercial licensing", "Intended low-cost / free"),
    ("Learning curve", "Moderate to high", "Low (with paid onboarding)", "Designed to be low"),
]
colw = [2.15, 2.5, 2.7, 2.5]
gt = s.shapes.add_table(len(rows), 4, Inches(L), Inches(TOP), Inches(W), Inches(3.3))
tbl = gt.table
tblPr = tbl._tbl.tblPr
sid = tblPr.find(qn("a:tableStyleId"))
if sid is not None:
    tblPr.remove(sid)
tbl.first_row = True
tbl.horz_banding = False
for i, cwid in enumerate(colw):
    tbl.columns[i].width = Inches(cwid)


def cell_border(cell, color="D0D5E5", w=9525):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT"):
        ln = etree.SubElement(tcPr, qn(tag))
        ln.set("w", "0")
        etree.SubElement(ln, qn("a:noFill"))
    ln = etree.SubElement(tcPr, qn("a:lnB"))
    ln.set("w", str(w))
    sf = etree.SubElement(ln, qn("a:solidFill"))
    c = etree.SubElement(sf, qn("a:srgbClr"))
    c.set("val", color)


for r, row in enumerate(rows):
    tbl.rows[r].height = Inches(0.55)
    for c, val in enumerate(row):
        cell = tbl.cell(r, c)
        cell.margin_left = Inches(0.15)
        cell.margin_right = Inches(0.1)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        hdr = r == 0
        if hdr:
            color = WHITE
            bold = True
            fillc = BLUE
        elif c == 0:
            color, bold, fillc = TXT, True, WHITE
        elif c == 3:
            color, bold, fillc = BLUE, True, TINT
        else:
            color, bold, fillc = TXT, False, WHITE
        fill_tf(tf, [[(val, {"b": bold, "color": color, "size": 13 if not hdr else 12})]], size=13)
        cell.fill.solid()
        cell.fill.fore_color.rgb = fillc
        cell_border(cell)
rect(s, L, 5.95, W, 0.85, fill=TINT, rounded=True, radius=0.08)
tb(s, L + 0.25, 5.95, W - 0.5, 0.85,
   [[("Built for students and early-career researchers. ", {"b": True, "color": BLUE}),
     ("Benchling carries high licensing fees and Galaxy needs significant setup; GENEODE connects a minimal but highly accurate subset of components end-to-end.", {})]],
   size=13, anchor=MSO_ANCHOR.MIDDLE)

# ======================= UNIT 2 ============================================
# 2.1 workflow
s = new_slide("2.1", "Workflow & Architecture", "02", "System workflow: from upload to report")
steps = [
    ("Data Upload", "User uploads validated FASTA/FASTQ sequence data into the secure web interface."),
    ("Automated Analysis", "Core engine runs sequence statistics, translation, and queries NCBI/BLAST for alignment."),
    ("Context Retrieval", "Platform retrieves relevant annotations, pathways and structures from UniProt and KEGG."),
    ("AI & Reporting", "AI generates natural-language summaries, compiled into a downloadable PDF report."),
]
cw = (W - 0.6) / 4
rect(s, L + cw / 2, TOP + 0.3, W - cw, 0.03, fill=TINT2)
for i, (h, d) in enumerate(steps):
    cx = L + i * (cw + 0.2)
    badge(s, cx + cw / 2 - 0.3, TOP + 0.02, 0.6, str(i + 1), size=18)
    card(s, cx, 3.35, cw, 3.1, fill=TINT, line=None)
    tb(s, cx + 0.2, 3.6, cw - 0.4, 0.6, [[(h, {"b": True, "size": 15, "color": BLUE})]])
    tb(s, cx + 0.2, 4.3, cw - 0.4, 2.0, [d], size=13)

# 2.1 architecture
s = new_slide("2.1", "Workflow & Architecture", "02", "System architecture")
cols = [
    ("Back-End & Core Engine",
     "Built for stability and scientific accuracy, relying on proven programmatic primitives rather than reinventing algorithms.",
     [("Biopython: ", "standardised sequence parsing and BLAST wrappers."),
      ("FastAPI/Flask: ", "lightweight, high-performance API routing."),
      ("PostgreSQL: ", "relational database for secure user history and run storage.")]),
    ("Front-End & Interpretation",
     "Focused on user experience, providing clear biological context directly alongside raw statistical outputs.",
     [("LLM layer: ", "natural-language generation via API, strictly sandboxed as an explanatory add-on."),
      ("Dynamic UI: ", "clean web interface built with HTML/CSS/JS and Plotly/Matplotlib visuals."),
      ("Report generator: ", "automated PDF compilation of findings.")]),
]
cw = (W - 0.3) / 2
for i, (h, intro, its) in enumerate(cols):
    cx = L + i * (cw + 0.3)
    card(s, cx, TOP, cw, 4.35)
    tb(s, cx + 0.3, TOP + 0.25, cw - 0.6, 0.35, [[(h, {"b": True, "size": 17, "color": BLUE})]])
    tb(s, cx + 0.3, TOP + 0.75, cw - 0.6, 0.9, [intro], size=13, color=GRAY)
    paras = [[(a, {"b": True}), (b, {})] for a, b in its]
    tb(s, cx + 0.3, TOP + 1.8, cw - 0.6, 2.4, paras, size=13, after=9, bullet=True)

# 2.2 integrations
s = new_slide("2.2", "Seamless Integrations", "02", "Seamless integrations with public databases")
ints = [
    ("BLAST API", "NCBI & GenBank", "Direct sequence similarity searching via the BLAST API, establishing the foundational biological identity of uploads."),
    ("3D Models", "PDB & AlphaFold DB", "Retrieval and interactive display of existing, highly accurate 3D structural models without heavy local compute."),
    ("Pathways", "UniProt & KEGG", "Pulling deep protein annotations and metabolic pathway context to situate findings in complex biological networks."),
]
cw = (W - 0.5) / 3
for i, (tag, h, d) in enumerate(ints):
    cx = L + i * (cw + 0.25)
    card(s, cx, TOP, cw, 3.35)
    rect(s, cx + 0.2, TOP + 0.2, cw - 0.4, 0.85, fill=TINT, rounded=True, radius=0.1)
    tb(s, cx + 0.2, TOP + 0.2, cw - 0.4, 0.85, [[(tag, {"b": True, "size": 18, "color": BLUE})]],
       align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, cx + 0.25, TOP + 1.3, cw - 0.5, 0.3, [[(h, {"b": True, "size": 15})]])
    tb(s, cx + 0.25, TOP + 1.75, cw - 0.5, 1.5, [d], size=13)
rect(s, L, 6.0, W, 0.7, fill=TINT, rounded=True, radius=0.1)
tb(s, L + 0.25, 6.0, W - 0.5, 0.7,
   [[("Phase 3 stretch goals (after week 14): ", {"b": True, "color": BLUE}), ("Ensembl, Gene Ontology and cloning design.", {})]],
   size=13, anchor=MSO_ANCHOR.MIDDLE)

# 2.3 roadmap
s = new_slide("2.3", "Roadmap, Risk & Budget", "02", "14-week development roadmap")
sw = W / 14
for wk in range(1, 15):
    c = BLUE if wk <= 9 else MID
    sq = rect(s, L + (wk - 1) * sw + 0.02, TOP, sw - 0.04, 0.42, fill=c)
    tf = sq.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    fill_tf(tf, [str(wk)], 12, WHITE, PP_ALIGN.CENTER)
tb(s, L, TOP + 0.5, 6.0, 0.3, [[("Phase 1: Core MVP (weeks 1–9)", {"b": True, "color": BLUE})]], size=12)
tb(s, L + 6.0, TOP + 0.5, W - 6.0, 0.3, [[("Phase 2: Annotation (weeks 10–14)", {"b": True, "color": MID})]],
   size=12, align=PP_ALIGN.RIGHT)
road = [
    ("Weeks 1–5", BLUE, "Setup & Core Engine. ", "Database schema design, sequence upload validation (FASTA/FASTQ). Biopython for GC%, codon usage and BLAST integration."),
    ("Weeks 6–9", BLUE, "AI Layer & MVP Web UI. ", "LLM APIs for plain-language summaries. Minimal viable web interface for uploads and result viewing."),
    ("Weeks 10–13", MID, "Annotations & Reporting. ", "UniProt/KEGG lookups linked to sequence results, PDB structure display and downloadable PDF reports."),
    ("Week 14", MID, "Evaluation & Testing. ", "System testing against reference data, usability walkthroughs with student users, checking AI explanation accuracy, final documentation."),
]
ry = TOP + 0.95
for i, (wk, col, h, d) in enumerate(road):
    y = ry + i * 0.8
    chip = rect(s, L, y, 1.55, 0.72, fill=col, rounded=True, radius=0.1)
    tf = chip.text_frame
    tf.margin_left = tf.margin_right = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    fill_tf(tf, [wk], 14, WHITE, PP_ALIGN.CENTER)
    for r in tf.paragraphs[0].runs:
        r.font.name = F7
    rect(s, L + 1.7, y, W - 1.7, 0.72, fill=TINT, rounded=True, radius=0.1)
    tb(s, L + 1.9, y, W - 2.1, 0.72, [[(h, {"b": True, "color": BLUE}), (d, {})]], size=13, anchor=MSO_ANCHOR.MIDDLE)
tb(s, L, 6.52, W, 0.3, [[("Phase 3 stretch goals sit beyond the 14-week window: Ensembl, Gene Ontology, cloning design.", {"i": True})]],
   size=12, color=GRAY)

# 2.3 risk & budget
s = new_slide("2.3", "Roadmap, Risk & Budget", "02", "Risks, mitigation and a lean budget")
cw = (W - 0.5) / 3
risks = [
    ("AI Hallucinations",
     "AI-generated explanations may sound fluent but be factually incorrect, undermining scientific credibility.",
     "The AI layer is strictly an explanatory add-on and never generates the base sequence results. Outputs are spot-checked by domain experts during development to tune prompts."),
    ("API Dependency & Data",
     "External API downtime (NCBI/UniProt) or handling sensitive biological data.",
     "Graceful degradation is built in: if KEGG fails, BLAST still works. Results are cached locally. No Patient Identifying Information (PII) is collected; only raw sequence text is processed."),
]
for i, (h, r_, m_) in enumerate(risks):
    cx = L + i * (cw + 0.25)
    card(s, cx, TOP, cw, 4.3)
    tb(s, cx + 0.25, TOP + 0.25, cw - 0.5, 0.3, [[(h, {"b": True, "size": 15, "color": BLUE})]])
    tb(s, cx + 0.25, TOP + 0.75, cw - 0.5, 3.4,
       [[("Risk: ", {"b": True}), (r_, {})], [("Mitigation: ", {"b": True}), (m_, {})]], size=13, after=10)
cx = L + 2 * (cw + 0.25)
rect(s, cx, TOP, cw, 4.3, fill=BLUE, rounded=True, radius=0.04)
tb(s, cx + 0.25, TOP + 0.3, cw - 0.5, 0.95, [[("$250", {"b": True, "size": 48, "color": WHITE})]])
tb(s, cx + 0.25, TOP + 1.3, cw - 0.5, 0.3, [[("Max est. monthly cost", {"b": True, "size": 14, "color": WHITE})]])
tb(s, cx + 0.25, TOP + 1.85, cw - 0.5, 2.3,
   ["Designed for free or near-free tiers: public APIs (NCBI, UniProt, KEGG, PDB) and open-source tools (Biopython, PostgreSQL). Only variable costs: basic cloud hosting and capped AI API usage."],
   size=13, color=WHITE)

# ======================= UNIT 3 ============================================
SUB31, SUB32, SUB33 = "Problem & Data", "Honest Validation", "Confidence, Helper & Limits"

# 3.1 why
s = new_slide("3.1", SUB31, "03", "Phage therapy needs the right phage",
              notes="Keep this short. Resistance makes alternatives necessary; phages are one candidate; but a phage only works on bacteria it can infect. Many sequenced phages have no tested host, so a first guess from the genome has value. This is the first AI module of GENEODE.")
why = [
    ("Resistance is rising", "Infections that antibiotics no longer clear need new treatment options."),
    ("Phages are a candidate", "Phage therapy works only when the phage matches the bacterium it must kill."),
    ("The host is often unknown", "Many sequenced phages have no experimentally tested host, so a fast first guess from the genome helps."),
]
cw = (W - 0.5) / 3
for i, (h, d) in enumerate(why):
    cx = L + i * (cw + 0.25)
    card(s, cx, TOP, cw, 2.6)
    badge(s, cx + 0.25, TOP + 0.25, 0.5, str(i + 1))
    tb(s, cx + 0.25, TOP + 0.95, cw - 0.5, 0.3, [[(h, {"b": True, "size": 15, "color": BLUE})]])
    tb(s, cx + 0.25, TOP + 1.4, cw - 0.5, 1.2, [d], size=13)
rect(s, L, 5.3, W, 1.3, fill=BLUE, rounded=True, radius=0.08)
tb(s, L + 0.4, 5.3, W - 0.8, 1.3,
   [[("Can the genome alone suggest the host, and say how far to trust that guess?", {"b": True, "size": 20, "color": WHITE})]],
   anchor=MSO_ANCHOR.MIDDLE)

# 3.1 data / model
s = new_slide("3.1", SUB31, "03", "A small, simple model, validated honestly",
              notes="Data: 150 complete phage genomes for each of six host genera from NCBI, a random sample. Features: how often each 4-letter DNA word appears, plus GC content, since phages adapt their composition to their host. Models are deliberately simple. The effort went into validation. Be upfront that labels come from the NCBI record title, a weak label.")
stats = [("900", "complete phage genomes from NCBI (150 per genus)"), ("6", "host genera"),
         ("257", "features: 4-mer frequencies and GC content"), ("188", "homology clusters")]
cw = (W - 0.6) / 4
for i, (n, l) in enumerate(stats):
    cx = L + i * (cw + 0.2)
    rect(s, cx, TOP, cw, 1.95, fill=TINT, rounded=True, radius=0.06)
    tb(s, cx + 0.2, TOP + 0.2, cw - 0.4, 0.7, [[(n, {"b": True, "size": 36, "color": BLUE})]])
    tb(s, cx + 0.2, TOP + 1.0, cw - 0.4, 0.9, [l], size=13)
cw2 = (W - 0.3) / 2
card(s, L, 4.55, cw2, 2.15)
tb(s, L + 0.25, 4.7, cw2 - 0.5, 0.3, [[("Six host genera", {"b": True, "size": 15, "color": BLUE})]])
tb(s, L + 0.25, 5.15, cw2 - 0.5, 1.5,
   ["Escherichia, Klebsiella, Salmonella, Pseudomonas, Staphylococcus and Mycobacterium.",
    "Label = genus named in the NCBI record, a weak label."], size=13, after=8)
card(s, L + cw2 + 0.3, 4.55, cw2, 2.15)
tb(s, L + cw2 + 0.55, 4.7, cw2 - 0.5, 0.3, [[("Models and splits", {"b": True, "size": 15, "color": BLUE})]])
tb(s, L + cw2 + 0.55, 5.15, cw2 - 0.5, 1.5,
   ["Majority baseline, logistic regression and random forest.",
    "Homology clusters keep relatives from straddling train and test."], size=13, after=8)

# 3.2 leaky vs honest
s = new_slide("3.2", SUB32, "03", "A naive split inflates the score by 0.29",
              notes="This is the strongest slide. Random split: near-identical phages sit on both sides, so the model looks great (0.92). Honest split groups related genomes so whole clusters are train or test: 0.63 to 0.68. Shuffled labels land at chance, 0.17, which shows the pipeline itself does not leak. Majority baseline is near zero because it predicts one genus. Logistic regression and random forest are within fold-to-fold noise of each other.")
cap(s, L, TOP - 0.05, 6.0, "Macro-F1 across 6 host genera (chance = 0.17)")
bar_chart(s, L, TOP + 0.3, 6.0, 4.05,
          ["Majority baseline", "Shuffled labels", "Logistic regression (honest)", "Random forest (honest)", "Random forest (leaky split)"],
          [0.054, 0.164, 0.677, 0.629, 0.921],
          [GRAYBAR, GRAYBAR, BLUE, BLUE, AMBER], fmt="0.00", name="Macro-F1")
defs = [
    ("Honest split", "Related genomes are grouped, so whole clusters go to train or test, never both.", BLUE),
    ("Leaky split", "Near-identical phages land on both sides, which inflates the score.", AMBER),
    ("Shuffled labels", "Fall to chance, so the pipeline itself does not leak.", GRAYBAR),
]
for i, (h, d, col) in enumerate(defs):
    y = TOP + i * 1.5
    card(s, 6.75, y, 3.59, 1.35)
    sq = rect(s, 6.95, y + 0.2, 0.18, 0.18, fill=col)
    tb(s, 7.25, y + 0.15, 2.9, 0.3, [[(h, {"b": True, "size": 14})]])
    tb(s, 6.95, y + 0.55, 3.2, 0.8, [d], size=13)

# 3.2 threshold
s = new_slide("3.2", SUB32, "03", "Honest scores fall as phages grow distant",
              notes="We varied how strictly relatives are separated (Jaccard distance on shared 10-mers). Looser grouping 0.6: honest about 0.78. Default 0.8: about 0.63, which we fixed before seeing any results and report as the headline. Strictest 0.9: about 0.43, but only 76 clusters so folds are less stable. The leaky score never moves, about 0.9, because it separates nothing. Message: the model recognises phages like ones it has seen; distant phages need gene-level features.")
cap(s, L, TOP - 0.05, 6.0, "Macro-F1 vs grouping threshold")
cd = CategoryChartData()
cd.categories = ["0.6 (looser)", "0.8 (default)", "0.9 (stricter)"]
cd.add_series("Random forest, leaky split", [0.921, 0.921, 0.9])
cd.add_series("Random forest, honest", [0.777, 0.629, 0.428])
cd.add_series("Logistic regression, honest", [0.806, 0.677, 0.365])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(L), Inches(TOP + 0.3), Inches(6.0), Inches(3.45), cd)
ch = gf.chart
style_chart(ch)
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.BOTTOM
ch.legend.include_in_layout = False
ch.legend.font.size = Pt(12)
pl = ch.plots[0]
pl.gap_width = 60
pl.overlap = -5
pl.has_data_labels = True
pl.data_labels.number_format = "0.00"
pl.data_labels.number_format_is_linked = False
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.data_labels.font.size = Pt(11)
ch.value_axis.minimum_scale = 0
ch.value_axis.maximum_scale = 1.05
ch.value_axis.has_major_gridlines = False
ch.value_axis.visible = False
ch.category_axis.major_tick_mark = XL_TICK_MARK.NONE
ch.category_axis.tick_labels.font.size = Pt(12)
ch.category_axis.format.line.color.rgb = LINE
for ser, col in zip(pl.series, [AMBER, BLUE, MID]):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = col
sr = [("0.78", "looser grouping (0.6)"), ("0.63", "default (0.8), our headline"), ("0.43", "strictest (0.9), less stable folds")]
for i, (n, l) in enumerate(sr):
    fillc = BLUE if i == 1 else TINT
    stat_row(s, 6.75, TOP + i * 1.22, 3.59, 1.1, n, l, fill=fillc, bigcolor=WHITE if i == 1 else BLUE, bigw=1.05, bigsize=26)
    if i == 1:
        for sh in list(s.shapes)[-1:]:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    r.font.color.rgb = WHITE
rect(s, L, 6.2, W, 0.55, fill=TINT, rounded=True, radius=0.1)
tb(s, L + 0.25, 6.2, W - 0.5, 0.55,
   [[("The model recognises phages like ones it has seen. ", {"b": True, "color": BLUE}), ("Distant phages need gene-level features.", {})]],
   size=13, anchor=MSO_ANCHOR.MIDDLE)

# 3.2 per genus
s = new_slide("3.2", SUB32, "03", "Distinct hosts are easy, Enterobacteria blur",
              notes="Per-genus F1 for the random forest on the honest split. Mycobacterium has a distinctive high-GC signature; Staphylococcus phages are also compositionally distinct. Escherichia, Klebsiella and Salmonella are closely related hosts whose phages have similar composition and sometimes cross between hosts. That is a biologically sensible error pattern and it points to the next step: protein-level features such as receptor-binding proteins.")
cap(s, L, TOP - 0.05, 6.0, "F1 per host genus (random forest, honest split)")
bar_chart(s, L, TOP + 0.3, 6.0, 4.1,
          ["Mycobacterium", "Staphylococcus", "Pseudomonas", "Escherichia", "Klebsiella", "Salmonella"],
          [0.96, 0.88, 0.79, 0.49, 0.39, 0.27],
          [BLUE, BLUE, BLUE, AMBER, AMBER, AMBER], fmt="0.00", name="F1")
cards = [
    ("Distinct composition", "Mycobacterium and Staphylococcus phages carry a clear composition signature.", BLUE),
    ("Related hosts", "Escherichia, Klebsiella and Salmonella share similar phages. Protein-level features such as receptor-binding proteins are the next step.", AMBER),
]
for i, (h, d, col) in enumerate(cards):
    y = TOP + i * 2.2
    card(s, 6.75, y, 3.59, 2.05)
    rect(s, 6.95, y + 0.22, 0.18, 0.18, fill=col)
    tb(s, 7.25, y + 0.17, 2.9, 0.3, [[(h, {"b": True, "size": 14})]])
    tb(s, 6.95, y + 0.65, 3.2, 1.35, [d], size=13)

# 3.3 confidence
s = new_slide("3.3", SUB33, "03", "Higher confidence really means more reliable",
              notes="Out-of-fold predictions under the honest split, grouped by the model's top probability. Below 0.6 the model is right about a third to 40 percent of the time, so the helper says do not act. At 0.8 and above it is right 98.5 percent of the time on 259 genomes. Acting only at 0.6 and above covers about 46 percent of genomes (417 of 900) at roughly 94 percent accuracy, which is my arithmetic from the table. This is at the default grouping threshold.")
cap(s, L, TOP - 0.05, 6.0, "Share of predictions correct, by model confidence")
bar_chart(s, L, TOP + 0.3, 6.0, 4.1,
          ["0.0–0.4\n(n=184)", "0.4–0.6\n(n=299)", "0.6–0.8\n(n=158)", "0.8–1.0\n(n=259)"],
          [0.337, 0.411, 0.88, 0.985],
          [GRAYBAR, GRAYBAR, BLUE, BLUE], fmt="0.0%", horizontal=False, vmax=1.15, name="Correct")
cs = [("98.5%", "correct at confidence 0.8 or higher (259 genomes)"),
      ("88%", "correct at confidence 0.6 to 0.8 (158 genomes)"),
      ("~94%", "correct on 46% of genomes if we act only at 0.6 or higher")]
for i, (n, l) in enumerate(cs):
    stat_row(s, 6.75, TOP + i * 1.5, 3.59, 1.35, n, l, bigw=1.2, bigsize=26)

# 3.3 helper
s = new_slide("3.3", SUB33, "03", "The helper: a call, checks and next steps",
              notes="Walk through the four parts, then the T7 example. Be clear on two limits: it predicts host GENUS, not strain; and the next-step list is rule-based workflow guidance, not something the model learned. For the T7 example, be upfront that a close relative is in the training set, so this particular case is not an independent test. The tool itself says so, which is the point.")
parts = [
    ("Soft checks", "Length, GC content against the predicted host, ambiguous bases, gene density."),
    ("Host call", "Top 3 genera with a confidence backed by validation."),
    ("Novelty check", "Does the sequence have a relative in the training set, or is it far from everything?"),
    ("Next steps", "Annotation, safety screening, taxonomy, lab host-range test (rule-based guidance)."),
]
for i, (h, d) in enumerate(parts):
    y = TOP + i * 1.08
    card(s, L, y, 4.75, 0.98)
    badge(s, L + 0.2, y + 0.24, 0.5, str(i + 1))
    tb(s, L + 0.9, y + 0.12, 3.7, 0.3, [[(h, {"b": True, "size": 14, "color": BLUE})]])
    tb(s, L + 0.9, y + 0.45, 3.7, 0.5, [d], size=12)
px = L + 4.95
pw = W - 4.95
rect(s, px, TOP, pw, 4.3, fill=BLUE, rounded=True, radius=0.03)
tb(s, px + 0.3, TOP + 0.22, pw - 0.6, 0.3, [[("Example: Escherichia phage T7 (NC_001604)", {"b": True, "size": 14, "color": WHITE})]])
tb(s, px + 0.3, TOP + 0.62, pw - 0.6, 0.3, ["39,937 bp  |  GC 48.4%  |  81% gene-dense"], size=12, color=TINT2)
tb(s, px + 0.3, TOP + 1.12, pw - 0.6, 0.45, [[("Escherichia 68.8%", {"b": True, "size": 22, "color": WHITE})]])
tb(s, px + 0.3, TOP + 1.68, pw - 0.6, 0.3, ["Salmonella 14.6%  |  Klebsiella 13.6%"], size=12, color=TINT2)
tb(s, px + 0.3, TOP + 2.15, pw - 0.6, 0.55,
   ["In validation, predictions in this band (0.6 to 0.8) were correct 88% of the time."], size=12, color=WHITE)
tb(s, px + 0.3, TOP + 2.95, pw - 0.6, 1.3,
   [[("Flag: ", {"b": True, "color": WHITE}), ("top candidates are all Enterobacteria, so test before assuming the genus.", {"color": WHITE})],
    [("Flag: ", {"b": True, "color": WHITE}), ("a close relative is in the training set, so this is not an independent test.", {"color": WHITE})]],
   size=12, after=6)

# 3.3 limits & next
s = new_slide("3.3", SUB33, "03", "Honest limits, and what comes next",
              notes="Close on honesty. Limits: labels come from record titles; genus not strain; composition only; six genera and 900 genomes; no separate held-out test set or tuning yet. Roadmap: protein-level features and Evo 2 embeddings aimed at the Enterobacteria confusion; a cluster-separated held-out test set and a neural network baseline; curated host-range labels and species level; integration as a GENEODE module. Finish on the headline: 0.63 macro-F1 under honest validation, with confidence you can trust.")
lim = ["Labels come from NCBI record titles, not tested host range",
       "Predicts host genus, not strain",
       "Composition only; no gene content yet",
       "6 genera and 900 genomes",
       "No separate held-out test set or tuning yet"]
nxt = ["Protein-level features and Evo 2 embeddings",
       "Cluster-separated held-out test set and a neural network baseline",
       "Curated host-range labels, species level",
       "Ship as a GENEODE module with confidence reporting"]
cw2 = (W - 0.3) / 2
for i, (h, items_, col) in enumerate([("Limits", lim, AMBER), ("Next steps", nxt, BLUE)]):
    cx = L + i * (cw2 + 0.3)
    card(s, cx, TOP, cw2, 3.55)
    rect(s, cx + 0.3, TOP + 0.3, 0.2, 0.2, fill=col)
    tb(s, cx + 0.65, TOP + 0.22, 3.5, 0.35, [[(h, {"b": True, "size": 17, "color": BLUE})]])
    tb(s, cx + 0.3, TOP + 0.85, cw2 - 0.6, 2.6, items_, size=13, after=8, bullet=True)
rect(s, L, 6.15, W, 0.7, fill=BLUE, rounded=True, radius=0.1)
tb(s, L + 0.3, 6.15, W - 0.6, 0.7,
   [[("Headline: 0.63 macro-F1 under honest validation, with a confidence score you can trust.", {"b": True, "size": 15, "color": WHITE})]],
   anchor=MSO_ANCHOR.MIDDLE)

# ---- reorder: closing slide to end; drop template sample slide 3 ----------
sldIdLst = prs.part._element.find(qn("p:sldIdLst"))
ids = list(sldIdLst)
sample = ids[2]
closing = ids[3]
prs.part.drop_rel(sample.get(qn("r:id")))
sldIdLst.remove(sample)
sldIdLst.remove(closing)
sldIdLst.append(closing)

prs.core_properties.title = "GENEODE Bioinformatics"
prs.core_properties.author = "Stephen Mburu Mwangi"
prs.save(OUT)
print("saved", OUT, len(prs.slides._sldIdLst))