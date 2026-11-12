from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

NAVY = RGBColor(6, 18, 36)
TEAL = RGBColor(47, 214, 196)
LIGHT = RGBColor(214, 236, 242)
WHITE = RGBColor(255, 255, 255)
GRAY = RGBColor(166, 181, 190)
ACCENT = RGBColor(24, 143, 163)


def add_background(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = NAVY


def add_title(slide, title, subtitle=None):
    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(0.45), Inches(12.0), Inches(0.8))
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
        p.space_after = Pt(8)


def add_note_callout(slide, text, left, top, width, height):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(11)
    p.font.color.rgb = TEAL
    p.alignment = PP_ALIGN.LEFT


def add_image(slide, path, left, top, width=None, height=None):
    if not path.exists():
        return
    if width is None and height is None:
        slide.shapes.add_picture(str(path), left, top)
    else:
        slide.shapes.add_picture(str(path), left, top, width=width, height=height)


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Slide 1 - Title
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "GENEODE Phage Module", "Host-genus prediction from genome composition")

# title accent band
band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(1.8), Inches(12.0), Inches(0.12))
band.fill.solid(); band.fill.fore_color.rgb = TEAL; band.line.fill.background()

# subtitle summary box
box = slide.shapes.add_textbox(Inches(0.9), Inches(2.3), Inches(8.4), Inches(2.2))
tf = box.text_frame
for idx, text in enumerate([
    "A proof-of-concept AI module for predicting the bacterial genus",
    "infected by a phage from genome sequence alone.",
    "", 
    "Built for GENEODE bioinformatics workflows and model validation.",
]):
    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
    p.text = text
    p.font.size = Pt(26 if idx < 2 else 18)
    p.font.bold = idx < 2
    p.font.color.rgb = WHITE if idx < 2 else LIGHT
    p.alignment = PP_ALIGN.LEFT
    p.space_after = Pt(6)

# small metric panel
panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.8), Inches(2.3), Inches(2.5), Inches(1.5))
panel.fill.solid(); panel.fill.fore_color.rgb = RGBColor(12, 36, 51); panel.line.color.rgb = TEAL
panel_tf = panel.text_frame
for idx, text in enumerate(["6", "host genera", "188", "homology clusters", "Macro-F1", "0.677"]):
    p = panel_tf.paragraphs[0] if idx == 0 else panel_tf.add_paragraph()
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(18 if idx % 2 == 0 else 12)
    p.font.bold = idx % 2 == 0
    p.font.color.rgb = WHITE if idx % 2 == 0 else LIGHT
    p.space_after = Pt(0)

# footer note
add_note_callout(slide, "Project scope: phage host prediction, homology-aware validation, and decision support.", Inches(0.9), Inches(6.5), Inches(11.0), Inches(0.55))

# Slide 2 - Problem
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Problem", "Why host prediction matters")
add_bullets(slide, [
    "Antibiotic resistance is growing, and phage therapy depends on matching the right phage to the right bacterium.",
    "Most sequenced phages in public databases have no experimentally confirmed host range.",
    "A fast, sequence-based host predictor would support discovery, screening, and clinical decision support.",
    "This project is a GENEODE-style AI module for that workflow.",
], Inches(0.9), Inches(1.8), Inches(6.8), Inches(4.4), font_size=22)

# side panel
panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.4), Inches(2.0), Inches(3.8), Inches(3.1))
panel.fill.solid(); panel.fill.fore_color.rgb = RGBColor(12, 30, 44); panel.line.color.rgb = TEAL
panel_tf = panel.text_frame
for idx, line in enumerate(["Challenge", "Genome-only signal", "No direct host labels", "Need honest validation"]):
    p = panel_tf.paragraphs[0] if idx == 0 else panel_tf.add_paragraph()
    p.text = line
    p.font.size = Pt(18 if idx == 0 else 14)
    p.font.bold = idx == 0
    p.font.color.rgb = WHITE if idx == 0 else LIGHT
    p.alignment = PP_ALIGN.LEFT
    p.space_after = Pt(10)

# Slide 3 - Approach
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Approach", "Data, features, and models")
add_bullets(slide, [
    "Data: 900 complete phage genomes from NCBI, sampled across 6 host genera.",
    "Features: strand-symmetric 4-mer frequencies plus GC content.",
    "Models: majority baseline, logistic regression, and random forest.",
    "Validation: homology-aware cluster split instead of random split, plus shuffled-label negative control.",
], Inches(0.9), Inches(1.8), Inches(7.0), Inches(4.2), font_size=22)

# stats box
stats = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.6), Inches(2.1), Inches(3.8), Inches(2.9))
stats.fill.solid(); stats.fill.fore_color.rgb = RGBColor(11, 38, 42); stats.line.color.rgb = TEAL
stats_tf = stats.text_frame
for idx, line in enumerate(["6 genera", "900 genomes", "188 clusters", "5-fold CV"]):
    p = stats_tf.paragraphs[0] if idx == 0 else stats_tf.add_paragraph()
    p.text = line
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(8)

# Slide 4 - Validation
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Validation", "The honest comparison matters")
add_image(slide, RESULTS / "fig1_validation_comparison.png", Inches(0.7), Inches(1.8), width=Inches(11.8), height=Inches(4.9))
add_note_callout(slide, "Random split inflates the score because near-identical phages appear in both train and test. The homology-aware split prevents that leakage.", Inches(0.9), Inches(6.7), Inches(11.0), Inches(0.5))

# Slide 5 - Results
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Results", "Key model performance")
add_bullets(slide, [
    "Honest cluster-split macro-F1: 0.677 for logistic regression.",
    "Leaky random split macro-F1: 0.921, showing the inflation caused by related-phage leakage.",
    "Shuffled-label control drops to chance level, confirming the pipeline is not overfitting labels.",
    "Mycobacterium and Staphylococcus are the most distinctive; Enterobacteriaceae genera remain the hardest cases.",
], Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.0), font_size=21)
add_image(slide, RESULTS / "fig2_confusion_matrix.png", Inches(7.0), Inches(2.1), width=Inches(5.5), height=Inches(3.8))

# Slide 6 - Limits and roadmap
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Limits and next steps", "From proof of concept to GENEODE module")
add_bullets(slide, [
    "Weak labels come from NCBI record titles, not curated host-range data.",
    "Current scope is genus-level prediction, not strain-level identification.",
    "Composition-only features limit performance on closely related taxa.",
    "Next: protein-level features, receptor-binding proteins, Evo 2 embeddings, and curated host-range labels.",
], Inches(0.9), Inches(1.8), Inches(6.7), Inches(4.2), font_size=21)
# example small panel for roadmap
panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.2), Inches(2.2), Inches(3.9), Inches(2.8))
panel.fill.solid(); panel.fill.fore_color.rgb = RGBColor(12, 36, 51); panel.line.color.rgb = TEAL
p = panel.text_frame.paragraphs[0]
p.text = "Roadmap\n• Held-out test set\n• Protein features\n• Species-level labels\n• GENEODE integration"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

# Slide 7 - closing
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide)
add_title(slide, "Takeaway", "A truthful, validated module for phage host prediction")
box = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.4), Inches(2.3))
tf = box.text_frame
for idx, text in enumerate([
    "This project shows that genome composition can predict host genus from sequence alone.",
    "The honest evaluation is the key point: cluster-aware validation and shuffled controls prevent inflated claims.",
    "The next step is a stronger, biology-aware model integrated into the GENEODE platform.",
]):
    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
    p.text = text
    p.font.size = Pt(25)
    p.font.color.rgb = LIGHT
    p.alignment = PP_ALIGN.LEFT
    p.space_after = Pt(12)

output_path = ROOT / "GENEODE_Phage_Presentation.pptx"
prs.save(str(output_path))
print(f"Saved presentation to: {output_path}")
