from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

NAVY = RGBColor(6, 18, 36)
TEAL = RGBColor(52, 214, 196)
LIGHT = RGBColor(224, 238, 242)
WHITE = RGBColor(255, 255, 255)
DARK_PANEL = RGBColor(15, 36, 47)
ACCENT = RGBColor(40, 165, 176)


def add_background(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = NAVY


def add_title(slide, title, subtitle=None):
    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(0.45), Inches(10.5), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.LEFT

    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.75), Inches(1.0), Inches(11.0), Inches(0.5))
        tf2 = sub_box.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = subtitle
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEAL
        p2.alignment = PP_ALIGN.LEFT


def add_bullets(slide, bullets, left, top, width, height, font_size=20):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 8
    tf.margin_top = 8
    tf.margin_right = 8
    tf.margin_bottom = 8
    for i, text in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = text
        p.level = 0
        p.bullet = True
        p.font.size = Pt(font_size)
        p.font.color.rgb = LIGHT
        p.space_after = Pt(6)


def add_note(slide, text, left, top, width, height):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(11)
    p.font.color.rgb = LIGHT
    p.alignment = PP_ALIGN.LEFT


def add_image(slide, path, left, top, width=None, height=None):
    if not path.exists():
        return
    slide.shapes.add_picture(str(path), left, top, width=width, height=height)


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# ---------------------------
# Slide 1: Title
# ---------------------------
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "GENEODE", "Phage host-genus prediction from genome sequence")

band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(1.7), Inches(12.0), Inches(0.12))
band.fill.solid(); band.fill.fore_color.rgb = TEAL; band.line.fill.background()

box = slide.shapes.add_textbox(Inches(0.9), Inches(2.1), Inches(7.0), Inches(2.6))
tf = box.text_frame
lines = [
    "AI-powered decision support for identifying the bacterial genus",
    "a phage infects from its genome alone.",
    "",
    "A proof-of-concept module for the GENEODE bioinformatics platform.",
]
for idx, text in enumerate(lines):
    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
    p.text = text
    p.font.size = Pt(26 if idx < 2 else 18)
    p.font.bold = idx < 2
    p.font.color.rgb = WHITE if idx < 2 else LIGHT
    p.alignment = PP_ALIGN.LEFT
    p.space_after = Pt(8)

panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.2), Inches(2.1), Inches(3.3), Inches(2.2))
panel.fill.solid(); panel.fill.fore_color.rgb = DARK_PANEL; panel.line.color.rgb = TEAL
panel_tf = panel.text_frame
for i, text in enumerate(["6", "host genera", "188", "homology clusters", "0.677", "honest macro-F1"]):
    p = panel_tf.paragraphs[0] if i == 0 else panel_tf.add_paragraph()
    p.text = text
    p.font.size = Pt(18 if i % 2 == 0 else 12)
    p.font.bold = i % 2 == 0
    p.font.color.rgb = WHITE if i % 2 == 0 else LIGHT
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(2)

add_note(slide, "Sequence-only prediction + honest validation = a credible AI module for phage discovery workflows.", Inches(0.9), Inches(6.5), Inches(11.0), Inches(0.5))

# ---------------------------
# Slide 2: Why it matters
# ---------------------------
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Why this matters", "Phage therapy needs fast host identification")
add_bullets(slide, [
    "Antibiotic resistance is accelerating, and phage therapy depends on choosing the right phage for the right bacterial target.",
    "Most phages in public databases do not have experimentally confirmed host ranges.",
    "Genome-only host prediction can accelerate screening, discovery, and decision support in clinical and applied microbiology.",
    "This project turns a bioinformatics problem into a machine-learning module for a broader GENEODE workflow.",
], Inches(0.9), Inches(1.8), Inches(7.2), Inches(4.0), font_size=21)

panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.8), Inches(2.0), Inches(3.6), Inches(2.5))
panel.fill.solid(); panel.fill.fore_color.rgb = DARK_PANEL; panel.line.color.rgb = TEAL
panel_tf = panel.text_frame
for i, text in enumerate(["Clinical need", "Faster triage", "Sequence-first", "Validatable AI"]):
    p = panel_tf.paragraphs[0] if i == 0 else panel_tf.add_paragraph()
    p.text = text
    p.font.size = Pt(18 if i == 0 else 15)
    p.font.bold = i == 0
    p.font.color.rgb = WHITE if i == 0 else LIGHT
    p.alignment = PP_ALIGN.LEFT
    p.space_after = Pt(10)

# ---------------------------
# Slide 3: Approach
# ---------------------------
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Approach", "DNA composition, not explicit host labels")
add_bullets(slide, [
    "Data: 900 complete phage genomes across 6 host genera from NCBI records.",
    "Features: strand-symmetric 4-mer frequencies plus GC content, designed to capture host-associated genome composition.",
    "Models: majority baseline, logistic regression, and random forest.",
    "Critical validation step: cluster-aware grouping prevents near-identical phages from leaking across train and test folds.",
], Inches(0.9), Inches(1.8), Inches(7.1), Inches(4.1), font_size=21)

stats = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.8), Inches(2.1), Inches(3.5), Inches(2.8))
stats.fill.solid(); stats.fill.fore_color.rgb = DARK_PANEL; stats.line.color.rgb = TEAL
stats_tf = stats.text_frame
for i, text in enumerate(["900 genomes", "6 genera", "188 clusters", "5-fold CV"]):
    p = stats_tf.paragraphs[0] if i == 0 else stats_tf.add_paragraph()
    p.text = text
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(8)

# ---------------------------
# Slide 4: Validation is the core story
# ---------------------------
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Validation", "This is where the science becomes credible")
add_image(slide, RESULTS / "fig1_validation_comparison.png", Inches(0.7), Inches(1.8), width=Inches(11.9), height=Inches(4.6))
add_note(slide, "Random split: 0.921 macro-F1 (leaky). Homology-aware split: 0.677 macro-F1 (honest). Shuffled labels fall to chance.", Inches(0.9), Inches(6.6), Inches(11.3), Inches(0.5))

# ---------------------------
# Slide 5: Results
# ---------------------------
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Results", "Performance is meaningful when leakage is controlled")
add_bullets(slide, [
    "Honest cluster-split logistic regression: macro-F1 = 0.677; balanced accuracy = 0.667.",
    "Naive random split gives 0.921 because near-identical phages appear on both sides of the divide.",
    "Shuffled-label control sits at chance (~0.16), confirming the model is learning real signal rather than dataset artifacts.",
    "The hardest confusions are among closely related taxa, which is biologically sensible and not random failure.",
], Inches(0.8), Inches(1.8), Inches(6.0), Inches(4.1), font_size=21)
add_image(slide, RESULTS / "fig2_confusion_matrix.png", Inches(7.2), Inches(2.0), width=Inches(5.3), height=Inches(3.5))

# ---------------------------
# Slide 6: Product and helper workflow
# ---------------------------
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "GENEODE helper workflow", "From prediction to decision support")
add_bullets(slide, [
    "Load a phage genome, inspect quality and composition, and generate a host-genus prediction with confidence.",
    "The helper reports soft checks: GC deviation, ambiguous bases, ORF-like composition, and novelty against the training set.",
    "It ranks the top candidate genera, highlights uncertainty, and recommends next steps based on evidence rather than a single raw label.",
    "This makes the model useful as a discovery and triage tool, not just as a benchmark.",
], Inches(0.9), Inches(1.8), Inches(7.0), Inches(4.0), font_size=20)

panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.8), Inches(2.0), Inches(3.6), Inches(2.9))
panel.fill.solid(); panel.fill.fore_color.rgb = DARK_PANEL; panel.line.color.rgb = TEAL
p = panel.text_frame.paragraphs[0]
p.text = "Outputs\n• Top 3 host calls\n• Confidence band\n• Novelty check\n• Suggested next steps"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

# ---------------------------
# Slide 7: Limits and roadmap
# ---------------------------
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Limits and roadmap", "What is needed to turn this into a real product")
add_bullets(slide, [
    "Current labels are weak: they are based on NCBI record titles rather than curated host-range data.",
    "The model predicts genus, not strain; species-level decisions need more biology and deeper evidence.",
    "Composition-only features limit performance on closely related taxa and distant phages.",
    "Next steps: protein-level signals, receptor-binding features, Evo 2 embeddings, curated host-range labels, and a held-out benchmark set.",
], Inches(0.9), Inches(1.8), Inches(7.2), Inches(4.1), font_size=20)

panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.8), Inches(2.0), Inches(3.5), Inches(2.6))
panel.fill.solid(); panel.fill.fore_color.rgb = DARK_PANEL; panel.line.color.rgb = TEAL
p = panel.text_frame.paragraphs[0]
p.text = "Roadmap\n• Protein features\n• Targeted host data\n• Species-level model\n• GENEODE integration"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

# ---------------------------
# Final closing slide
# ---------------------------
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Takeaway", "A honest, validated foundation for AI-assisted phage host prediction")
box = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.0), Inches(2.8))
tf = box.text_frame
for idx, text in enumerate([
    "This project demonstrates that genome composition can predict the host genus of a phage from sequence alone.",
    "The key differentiator is honest validation: the model is tested on genetically distinct relatives, not near-duplicates.",
    "That makes the work a credible starting point for a much stronger, biology-aware GENEODE module.",
]):
    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
    p.text = text
    p.font.size = Pt(24)
    p.font.color.rgb = LIGHT
    p.alignment = PP_ALIGN.LEFT
    p.space_after = Pt(12)

output_path = ROOT / "GENEODE_Phage_Presentation.pptx"
prs.save(str(output_path))
print(f"Saved polished presentation to: {output_path}")
