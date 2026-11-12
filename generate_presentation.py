from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

DARK_BG = RGBColor(8, 24, 38)
DARK_CARD = RGBColor(15, 35, 49)
TEAL = RGBColor(57, 197, 188)
SOFT = RGBColor(220, 234, 239)
WHITE = RGBColor(255, 255, 255)
GREY = RGBColor(166, 180, 190)


def add_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG


def add_topbar(slide, number):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.18))
    bar.fill.solid(); bar.fill.fore_color.rgb = TEAL; bar.line.fill.background()
    num = slide.shapes.add_textbox(Inches(12.2), Inches(0.22), Inches(0.8), Inches(0.35))
    tf = num.text_frame
    p = tf.paragraphs[0]
    p.text = number
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.RIGHT


def add_title(slide, title, subtitle=None):
    box = slide.shapes.add_textbox(Inches(0.7), Inches(0.7), Inches(9.5), Inches(0.8))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.LEFT

    if subtitle:
        sbox = slide.shapes.add_textbox(Inches(0.75), Inches(1.2), Inches(7.5), Inches(0.5))
        st = sbox.text_frame
        p2 = st.paragraphs[0]
        p2.text = subtitle
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEAL
        p2.alignment = PP_ALIGN.LEFT


def add_bullets(slide, bullets, left, top, width, height, font_size=20):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 12
    tf.margin_top = 10
    tf.margin_right = 12
    tf.margin_bottom = 10

    for i, text in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = text
        p.level = 0
        p.bullet = True
        p.font.size = Pt(font_size)
        p.font.color.rgb = SOFT
        p.space_after = Pt(8)


def add_card(slide, left, top, width, height, title=None, body=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid(); shape.fill.fore_color.rgb = DARK_CARD; shape.line.color.rgb = TEAL
    tf = shape.text_frame
    tf.margin_left = 12
    tf.margin_top = 12
    tf.margin_right = 12
    tf.margin_bottom = 12
    if title:
        p = tf.paragraphs[0]
        p.text = title
        p.level = 0
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.space_after = Pt(6)
    if body:
        p = tf.paragraphs[1] if len(tf.paragraphs) > 1 else tf.add_paragraph()
        p.text = body
        p.font.size = Pt(12)
        p.font.color.rgb = SOFT
        p.alignment = PP_ALIGN.LEFT


def add_image(slide, path, left, top, width=None, height=None):
    if not path.exists():
        return
    slide.shapes.add_picture(str(path), left, top, width=width, height=height)


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Slide 1: Cover
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_topbar(slide, "SIC AI CAPSTONE")

cover = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(6.5), Inches(2.0))
tf = cover.text_frame
p = tf.paragraphs[0]
p.text = "GENEODE"
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = TEAL
p.alignment = PP_ALIGN.LEFT

p2 = tf.add_paragraph()
p2.text = "Phage Host-Genus Prediction"
p2.font.size = Pt(26)
p2.font.bold = True
p2.font.color.rgb = WHITE

p3 = tf.add_paragraph()
p3.text = "AI-powered decision support for genome-based phage host identification"
p3.font.size = Pt(13)
p3.font.color.rgb = GREY
p3.alignment = PP_ALIGN.LEFT

small = slide.shapes.add_textbox(Inches(0.8), Inches(5.9), Inches(5.0), Inches(0.45))
small_tf = small.text_frame
small_p = small_tf.paragraphs[0]
small_p.text = "Samsung Innovation Campus · AI Training Track"
small_p.font.size = Pt(10)
small_p.font.color.rgb = GREY

# accent panel
panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.6), Inches(2.1), Inches(3.5), Inches(2.3))
panel.fill.solid(); panel.fill.fore_color.rgb = DARK_CARD; panel.line.color.rgb = TEAL
p = panel.text_frame.paragraphs[0]
p.text = "Core result\n0.677\nHonest macro-F1"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.CENTER

# Slide 2: Problem
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_topbar(slide, "01")
add_title(slide, "Problem", "Why host prediction matters")
add_bullets(slide, [
    "Phage therapy depends on matching the right phage to the right bacterial host.",
    "Most sequenced phages have no experimentally confirmed host range.",
    "A genome-only host predictor could speed screening, discovery, and targeted phage selection.",
    "This project turns that challenge into a GENEODE-ready AI module.",
], Inches(0.9), Inches(1.9), Inches(7.0), Inches(3.9), 21)
add_card(slide, Inches(8.9), Inches(2.1), Inches(3.1), Inches(2.5), "Challenge", "Genome-only signal\nNo direct host labels\nNeed reliable validation")

# Slide 3: Approach
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_topbar(slide, "02")
add_title(slide, "Approach", "Data, features, and validation strategy")
add_bullets(slide, [
    "Data: 900 complete phage genomes across 6 host genera from NCBI.",
    "Features: 4-mer frequencies and GC content, chosen to capture host-associated genome composition.",
    "Models: majority baseline, logistic regression, and random forest.",
    "Key method: homology-aware clustering keeps related phages in the same fold to avoid leakage.",
], Inches(0.9), Inches(1.9), Inches(7.2), Inches(3.8), 20)
add_card(slide, Inches(9.0), Inches(2.1), Inches(2.8), Inches(2.6), "Dataset", "900 genomes\n6 genera\n188 clusters\n5-fold CV")

# Slide 4: Validation
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_topbar(slide, "03")
add_title(slide, "Validation", "The difference between honest and leaky evaluation")
add_image(slide, RESULTS / "fig1_validation_comparison.png", Inches(0.7), Inches(1.8), width=Inches(11.8), height=Inches(4.6))
small = slide.shapes.add_textbox(Inches(0.9), Inches(6.6), Inches(11.5), Inches(0.45))
small_tf = small.text_frame
small_p = small_tf.paragraphs[0]
small_p.text = "Random split: 0.921 macro-F1 (leaky). Homology-aware split: 0.677 macro-F1 (honest). Shuffled labels fall to chance."
small_p.font.size = Pt(10)
small_p.font.color.rgb = GREY

# Slide 5: Results
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_topbar(slide, "04")
add_title(slide, "Results", "Performance is meaningful only when leakage is controlled")
add_bullets(slide, [
    "Honest cluster-split macro-F1: 0.677 for logistic regression.",
    "Leaky random split macro-F1: 0.921, showing the inflation caused by close relatives in both sets.",
    "Shuffled-label control stays at chance (~0.16), confirming real signal rather than label memorisation.",
    "The main errors are among genetically related taxa, which is biologically reasonable and not random failure.",
], Inches(0.8), Inches(1.9), Inches(6.0), Inches(3.9), 20)
add_image(slide, RESULTS / "fig2_confusion_matrix.png", Inches(7.2), Inches(2.0), width=Inches(5.2), height=Inches(3.4))

# Slide 6: Helper and roadmap
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_topbar(slide, "05")
add_title(slide, "Helper workflow", "From genome to decision support")
add_bullets(slide, [
    "The model reports a host-genus prediction with confidence and uncertainty bands.",
    "It checks GC deviation, ambiguous bases, ORF-like composition, and novelty against the training set.",
    "This supports discovery, triage, and follow-up experiments rather than acting as a black-box labeler.",
    "The roadmap: protein features, curated host labels, species-level targets, and deeper GENEODE integration.",
], Inches(0.9), Inches(1.9), Inches(6.8), Inches(3.9), 20)
add_card(slide, Inches(8.9), Inches(2.1), Inches(3.1), Inches(2.7), "Outputs", "Top 3 host calls\nConfidence band\nNovelty check\nNext-step guidance")

# Final slide
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_topbar(slide, "06")
add_title(slide, "Takeaway", "A credible AI foundation for phage host prediction")
quote = slide.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.0), Inches(2.2))
qt = quote.text_frame
for idx, line in enumerate([
    "Genome composition can predict host genus from sequence alone.",
    "The key is honest validation: related genomes stay together across folds, so the model is tested on truly unseen phages.",
    "That turns this project from a demonstration into a strong starting point for a real GENEODE module.",
]):
    p = qt.paragraphs[0] if idx == 0 else qt.add_paragraph()
    p.text = line
    p.font.size = Pt(22 if idx == 0 else 18)
    p.font.color.rgb = SOFT
    p.alignment = PP_ALIGN.LEFT
    p.space_after = Pt(8)

output_path = ROOT / "GENEODE_Phage_Presentation_SIC_Style.pptx"
prs.save(str(output_path))
print(f"Saved SIC-style presentation to: {output_path}")
