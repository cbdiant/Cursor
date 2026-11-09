#!/usr/bin/env python3
"""Build the Strawberry DNA Extraction science-fair poster slides.

Each slide is letter landscape (11 x 8.5 in) so it prints at actual size
and can be mounted on a tri-fold board.
"""

import math
import os

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

# --- palette ---
CREAM = "FBF7F2"
INK = "2C241F"
MUTED = "5C534C"
BERRY = "A31D36"
BERRY_DEEP = "7C1628"
LEAF = "1B7A4A"
LEAF_DEEP = "145C36"
GOLD = "A56B12"
WHITE = "FFFFFF"
LINE = "E4D9CE"
SOFT_BERRY = "F8ECEC"
SOFT_LEAF = "E6F5ED"
SOFT_BLUE = "E4F0F8"
SOFT_GOLD = "FBF4E6"
ALCOHOL = "D3E6F5"
LIQUID = "F3B0AA"
LIQUID_DEEP = "E5928C"
A_COLOR = "D06A2C"
T_COLOR = "2C6E9B"
G_COLOR = "2C7A4E"
C_COLOR = "A31D36"

FONT = "Arial"
AUTHOR = "Finley Grace DiAntonio"
SW, SH = 11.0, 8.5
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "Strawberry DNA Extraction Science Fair.pptx")
STRAWBERRY_IMG = os.path.join(ROOT, "assets", "strawberry.png")
HELIX_IMG = os.path.join(ROOT, "assets", "dna-helix.png")
MATERIALS_IMG = os.path.join(ROOT, "assets", "materials.png")
ALCOHOL_IMG = os.path.join(ROOT, "assets", "finley-alcohol.png")
SALT_IMG = os.path.join(ROOT, "assets", "salt.png")
FUNNEL_IMG = os.path.join(ROOT, "assets", "funnel-mash.png")
FILTER_IMG = os.path.join(ROOT, "assets", "filter-mash.png")
DRAIN_IMG = os.path.join(ROOT, "assets", "drain-mash.png")
COLLECT_IMG = os.path.join(ROOT, "assets", "collect-liquid.png")
DNA_40X = os.path.join(ROOT, "assets", "dna-40x.jpg")
DNA_100X_A = os.path.join(ROOT, "assets", "dna-100x-a.jpg")
DNA_100X_B = os.path.join(ROOT, "assets", "dna-100x-b.jpg")
DNA_500X = os.path.join(ROOT, "assets", "dna-500x.jpg")
DNA_1000X = os.path.join(ROOT, "assets", "dna-1000x.jpg")
MICRO_ASPECT = 2880 / 2160


def rgb(value):
    return RGBColor.from_string(value)


def set_run(run, font, size, bold, italic, color, spacing):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = rgb(color)
    rPr = run._r.get_or_add_rPr()
    rPr.set("lang", "en-US")
    if spacing is not None:
        rPr.set("spc", str(int(spacing)))
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", font)


def _anchor(tf, anchor):
    tf._txBody.bodyPr.set(
        "anchor", {"top": "t", "middle": "ctr", "bottom": "b"}[anchor]
    )


def fill_shape(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(color)


def no_line(shape):
    shape.line.fill.background()


def add_rect(slide, x, y, w, h, color):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    fill_shape(sh, color)
    no_line(sh)
    return sh


def add_round(slide, x, y, w, h, fill, line=None, line_w=1.25, radius=0.08):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    sh.adjustments[0] = radius
    fill_shape(sh, fill)
    if line is None:
        no_line(sh)
    else:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(line_w)
    return sh


def add_oval(slide, x, y, w, h, fill, line=None, line_w=1.0):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    fill_shape(sh, fill)
    if line is None:
        no_line(sh)
    else:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(line_w)
    return sh


def add_freeform(slide, points, fill, line=None, line_w=1.5):
    x0, y0 = points[0]
    builder = slide.shapes.build_freeform(Inches(x0), Inches(y0))
    builder.add_line_segments(
        [(Inches(x), Inches(y)) for x, y in points[1:]], close=True
    )
    sh = builder.convert_to_shape()
    fill_shape(sh, fill)
    if line is None:
        no_line(sh)
    else:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(line_w)
    return sh


def rich(slide, x, y, w, h, paragraphs, anchor="top", align="left", margins=None):
    """paragraphs: list of {runs, align?, after?, before?, leading?}
    runs: list of {t, size, b, i, c, sp, font}
    """
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    ml, mr, mt, mb = margins or (0.02, 0.02, 0.0, 0.0)
    tf.margin_left = Inches(ml)
    tf.margin_right = Inches(mr)
    tf.margin_top = Inches(mt)
    tf.margin_bottom = Inches(mb)
    _anchor(tf, anchor)
    default_align = {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
    }[align]
    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {
            "left": PP_ALIGN.LEFT,
            "center": PP_ALIGN.CENTER,
            "right": PP_ALIGN.RIGHT,
        }.get(para.get("align"), default_align)
        p.space_before = Pt(para.get("before", 0))
        p.space_after = Pt(para.get("after", 0))
        if "leading" in para:
            p.line_spacing = para["leading"]
        for spec in para["runs"]:
            run = p.add_run()
            run.text = spec["t"]
            set_run(
                run,
                spec.get("font", FONT),
                spec.get("size", 16),
                spec.get("b", False),
                spec.get("i", False),
                spec.get("c", INK),
                spec.get("sp"),
            )
    return box


def plain(
    slide,
    x,
    y,
    w,
    h,
    text,
    size=16,
    bold=False,
    color=INK,
    align="left",
    anchor="top",
    italic=False,
    spacing=None,
    leading=1.0,
    after=0,
    margins=None,
):
    paragraphs = []
    for i, line in enumerate(text.split("\n")):
        paragraphs.append(
            {
                "runs": [
                    {
                        "t": line,
                        "size": size,
                        "b": bold,
                        "i": italic,
                        "c": color,
                        "sp": spacing,
                    }
                ],
                "after": after if i < text.count("\n") else 0,
                "leading": leading,
            }
        )
    return rich(
        slide, x, y, w, h, paragraphs, anchor=anchor, align=align, margins=margins
    )


def stripes(slide):
    add_rect(slide, 0, 0, SW, 0.11, BERRY)
    add_rect(slide, 0, 0.11, SW, 0.055, LEAF)


def new_slide(prs, note):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(CREAM)
    stripes(slide)
    notes = slide.notes_slide.notes_text_frame
    notes.text = note
    return slide


def add_pic(slide, path, x, y, size):
    slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(size), Inches(size))


def brand_icons(slide, x, y, size=0.62, gap=0.08):
    add_pic(slide, STRAWBERRY_IMG, x, y, size)
    add_pic(slide, HELIX_IMG, x + size + gap, y, size)


def photo_card(slide, x, y, w, h, path, kicker, caption, aspect=450 / 600):
    """Photo card. aspect is width divided by height."""
    card(slide, x, y, w, h)
    plain(
        slide,
        x + 0.10,
        y + 0.08,
        w - 0.20,
        0.32,
        kicker,
        size=12,
        bold=True,
        color=BERRY,
        align="center",
        anchor="middle",
        spacing=40,
    )
    caption_h = 0.82
    frame_top = y + 0.46
    frame_h = h - 0.46 - caption_h
    avail_w = w - 0.24
    photo_h = frame_h
    photo_w = photo_h * aspect
    if photo_w > avail_w:
        photo_w = avail_w
        photo_h = photo_w / aspect
    px = x + (w - photo_w) / 2
    py = frame_top + (frame_h - photo_h) / 2
    slide.shapes.add_picture(path, Inches(px), Inches(py), Inches(photo_w), Inches(photo_h))
    plain(
        slide,
        x + 0.12,
        y + h - caption_h,
        w - 0.24,
        caption_h - 0.08,
        caption,
        size=14,
        color=INK,
        align="center",
        anchor="middle",
    )


def header(slide, title):
    icon = 0.62
    gap = 0.08
    icon_x = SW - 0.28 - (icon * 2 + gap)
    brand_icons(slide, icon_x, 0.22, icon, gap)
    plain(
        slide,
        0.40,
        0.22,
        5.15,
        0.58,
        title,
        size=30,
        bold=True,
        color=BERRY,
        anchor="middle",
        margins=(0, 0, 0, 0),
    )
    plain(
        slide,
        icon_x - 2.45,
        0.28,
        2.32,
        0.48,
        AUTHOR,
        size=12,
        bold=True,
        color=INK,
        align="right",
        anchor="middle",
        margins=(0, 0, 0, 0),
    )
    add_rect(slide, 0.42, 0.90, 1.15, 0.045, BERRY)
    add_rect(slide, 1.57, 0.90, 0.34, 0.045, LEAF)


def card(slide, x, y, w, h, fill=WHITE, line=LINE, radius=0.10):
    """radius is the corner radius in inches."""
    adj = min(0.5, radius / min(w, h))
    return add_round(slide, x, y, w, h, fill, line=line, line_w=1.25, radius=adj)


def _arc(cx, cy, r, start_deg, end_deg, n=20):
    pts = []
    for i in range(n + 1):
        deg = start_deg + (end_deg - start_deg) * i / n
        rad = math.radians(deg)
        pts.append((cx + r * math.cos(rad), cy - r * math.sin(rad)))
    return pts


def capped_card(slide, x, y, w, h, cap, cap_h=0.09, corner=0.11, body=WHITE, line=LINE):
    """Rounded card with a color cap that follows the top corners."""
    corner = min(corner, cap_h)
    adj = min(0.5, corner / min(w, h))
    add_round(slide, x, y, w, h, cap, line=line, line_w=1.25, radius=adj)
    inset = 0.016
    left = x + inset
    right = x + w - inset
    top = y + cap_h
    bottom = y + h - inset
    r = max(0.05, corner - inset)
    c_y = bottom - r
    right_cx = right - r
    left_cx = left + r
    pts = [(left, top), (right, top), (right, c_y)]
    pts += _arc(right_cx, c_y, r, 0, -90, 10)[1:]
    pts.append((left_cx, bottom))
    pts += _arc(left_cx, c_y, r, -90, -180, 10)[1:]
    add_freeform(slide, pts, body)


def run(text, size=16, bold=False, color=INK, italic=False, spacing=None):
    return {"t": text, "size": size, "b": bold, "c": color, "i": italic, "sp": spacing}


def para(runs, after=0, before=0, align=None, leading=None):
    item = {"runs": runs, "after": after, "before": before}
    if align:
        item["align"] = align
    if leading:
        item["leading"] = leading
    return item


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

def slide_title(prs):
    s = new_slide(
        prs,
        "Mount at the top of the CENTER panel. Print landscape, letter, actual size.",
    )
    plain(
        s,
        1.95,
        1.08,
        7.10,
        0.32,
        "SCIENCE FAIR PROJECT",
        size=13,
        bold=True,
        color=LEAF,
        align="center",
        anchor="middle",
        spacing=240,
    )
    add_pic(s, STRAWBERRY_IMG, 0.32, 1.48, 1.72)
    add_pic(s, HELIX_IMG, 8.96, 1.48, 1.72)
    plain(
        s,
        2.05,
        1.48,
        6.90,
        0.82,
        "Strawberry DNA",
        size=48,
        bold=True,
        color=INK,
        align="center",
        anchor="middle",
    )
    plain(
        s,
        2.05,
        2.28,
        6.90,
        0.78,
        "Extraction",
        size=48,
        bold=True,
        color=BERRY,
        align="center",
        anchor="middle",
    )
    add_rect(s, 4.55, 3.18, 1.90, 0.05, BERRY)
    plain(
        s,
        2.05,
        3.32,
        6.90,
        0.62,
        "Pulling DNA out of a strawberry\nwith soap, salt, and cold alcohol.",
        size=16,
        color=MUTED,
        align="center",
        anchor="top",
        leading=1.08,
    )
    plain(
        s,
        2.05,
        3.98,
        6.90,
        0.40,
        AUTHOR,
        size=20,
        bold=True,
        color=INK,
        align="center",
        anchor="middle",
    )

    labels = [
        (BERRY, "SOAP", "Breaks the cells open"),
        (GOLD, "SALT", "Separates the DNA"),
        (T_COLOR, "COLD ALCOHOL", "Makes the DNA visible"),
    ]
    w, gap = 3.05, 0.18
    total = 3 * w + 2 * gap
    x0 = (SW - total) / 2
    y = 4.92
    h = 1.70
    for i, (accent, name, detail) in enumerate(labels):
        x = x0 + i * (w + gap)
        capped_card(s, x, y, w, h, accent, cap_h=0.09, corner=0.11)
        plain(
            s,
            x + 0.12,
            y + 0.22,
            w - 0.24,
            0.38,
            name,
            size=14,
            bold=True,
            color=accent,
            align="center",
            anchor="middle",
            spacing=140,
        )
        plain(
            s,
            x + 0.16,
            y + 0.66,
            w - 0.32,
            0.72,
            detail,
            size=16,
            color=INK,
            align="center",
            anchor="top",
        )
    plain(
        s,
        0.5,
        6.82,
        10.0,
        0.36,
        "All living things have DNA. This experiment makes strawberry DNA visible.",
        size=14,
        color=MUTED,
        align="center",
        anchor="middle",
    )


def slide_question(prs):
    s = new_slide(prs, "Mount on the LEFT panel, top.")
    header(s, "Question")
    card(s, 0.40, 1.18, 10.20, 2.35)
    add_rect(s, 0.40, 1.36, 0.10, 1.99, BERRY)
    plain(
        s,
        0.70,
        1.30,
        9.70,
        2.10,
        "Can we extract DNA from a strawberry\nusing household supplies?",
        size=32,
        bold=True,
        color=INK,
        align="center",
        anchor="middle",
        leading=1.05,
    )

    blocks = [
        (
            BERRY,
            SOFT_BERRY,
            "IN EVERY CELL",
            "DNA is the instruction molecule inside every living thing, including a strawberry.",
        ),
        (
            LEAF,
            SOFT_LEAF,
            "THOUSANDS OF CELLS",
            "DNA in one cell is too small to see. A mashed strawberry releases DNA from thousands of cells.",
        ),
        (
            T_COLOR,
            SOFT_BLUE,
            "HOUSEHOLD SUPPLIES",
            "The test uses only soap, salt, and cold alcohol. If they work, the DNA should show up.",
        ),
    ]
    y, h, gap = 3.75, 4.30, 0.18
    w = (10.20 - 2 * gap) / 3
    for i, (accent, bg, title, body) in enumerate(blocks):
        x = 0.40 + i * (w + gap)
        card(s, x, y, w, h, fill=WHITE)
        # Group is centered in the card so the lower half is not empty.
        add_oval(s, x + (w - 0.62) / 2, y + 0.78, 0.62, 0.62, accent)
        plain(
            s,
            x + (w - 0.62) / 2,
            y + 0.78,
            0.62,
            0.62,
            str(i + 1),
            size=20,
            bold=True,
            color=WHITE,
            align="center",
            anchor="middle",
            margins=(0, 0, 0, 0),
        )
        plain(
            s,
            x + 0.18,
            y + 1.58,
            w - 0.36,
            0.55,
            title,
            size=14,
            bold=True,
            color=accent,
            align="center",
            anchor="middle",
            spacing=80,
        )
        plain(
            s,
            x + 0.24,
            y + 2.22,
            w - 0.48,
            1.45,
            body,
            size=16,
            color=INK,
            align="center",
            anchor="top",
            leading=1.15,
        )


def slide_hypothesis(prs):
    s = new_slide(prs, "Mount on the LEFT panel, under Question.")
    header(s, "Hypothesis")
    card(s, 0.40, 1.18, 10.20, 3.05)
    plain(
        s,
        0.70,
        1.32,
        9.60,
        0.36,
        "MY PREDICTION",
        size=13,
        bold=True,
        color=BERRY,
        align="center",
        anchor="middle",
        spacing=220,
    )
    plain(
        s,
        0.70,
        1.75,
        9.60,
        2.20,
        "I predict that soap, salt, and cold alcohol\nwill help us see strawberry DNA.",
        size=28,
        bold=True,
        color=INK,
        align="center",
        anchor="middle",
        leading=1.08,
    )

    blocks = [
        (BERRY, "SOAP", "Breaks open the strawberry cells and lets the DNA out."),
        (GOLD, "SALT", "Helps keep proteins separate from the DNA."),
        (T_COLOR, "COLD ALCOHOL", "Makes the DNA clump into strands we can see."),
    ]
    y, h, gap = 4.45, 3.60, 0.18
    w = (10.20 - 2 * gap) / 3
    for i, (accent, title, body) in enumerate(blocks):
        x = 0.40 + i * (w + gap)
        capped_card(s, x, y, w, h, accent, cap_h=0.09, corner=0.11)
        plain(
            s,
            x + 0.20,
            y + 0.95,
            w - 0.40,
            0.50,
            title,
            size=16,
            bold=True,
            color=accent,
            align="center",
            anchor="middle",
            spacing=100,
        )
        plain(
            s,
            x + 0.26,
            y + 1.58,
            w - 0.52,
            1.40,
            body,
            size=18,
            color=INK,
            align="center",
            anchor="top",
            leading=1.15,
        )


def slide_research(prs):
    s = new_slide(prs, "Mount on the LEFT panel, under Hypothesis.")
    header(s, "Research and Sources")

    # Left: DNA summary
    card(s, 0.38, 1.16, 5.35, 6.95)
    plain(
        s,
        0.58,
        1.30,
        4.95,
        0.40,
        "WHAT DNA IS",
        size=13,
        bold=True,
        color=BERRY,
        spacing=120,
        anchor="middle",
    )
    rich(
        s,
        0.58,
        1.78,
        4.95,
        3.55,
        [
            para([run("DNA stands for deoxyribonucleic acid.", 15)], after=8, leading=1.08),
            para(
                [
                    run("Shape. ", 15, bold=True),
                    run("It is a long molecule in a double helix — two spirals, like a twisted ladder.", 15),
                ],
                after=8,
                leading=1.08,
            ),
            para(
                [
                    run("Sides. ", 15, bold=True),
                    run("Sugars and phosphates make the backbone of each spiral.", 15),
                ],
                after=8,
                leading=1.08,
            ),
            para(
                [
                    run("Rungs. ", 15, bold=True),
                    run("Four bases connect the spirals: adenine (A), thymine (T), guanine (G), and cytosine (C).", 15),
                ],
                after=8,
                leading=1.08,
            ),
            para(
                [
                    run("Job. ", 15, bold=True),
                    run("Genes are made of DNA. It holds the instructions for making proteins, like a recipe book for a living thing.", 15),
                ],
                after=0,
                leading=1.08,
            ),
        ],
        margins=(0.04, 0.08, 0.0, 0.0),
    )

    # Base-pair chips
    bases = [
        ("A", "Adenine", A_COLOR),
        ("T", "Thymine", T_COLOR),
        ("G", "Guanine", G_COLOR),
        ("C", "Cytosine", C_COLOR),
    ]
    chip_w = 1.05
    chip_gap = 0.12
    row_w = 4 * chip_w + 3 * chip_gap
    bx0 = 0.38 + (5.35 - row_w) / 2
    by = 5.45
    for i, (letter, name, color) in enumerate(bases):
        x = bx0 + i * (chip_w + chip_gap)
        add_oval(s, x + (chip_w - 0.48) / 2, by, 0.48, 0.48, color)
        plain(
            s,
            x + (chip_w - 0.48) / 2,
            by,
            0.48,
            0.48,
            letter,
            size=16,
            bold=True,
            color=WHITE,
            align="center",
            anchor="middle",
            margins=(0, 0, 0, 0),
        )
        plain(
            s,
            x,
            by + 0.52,
            chip_w,
            0.32,
            name,
            size=11,
            color=MUTED,
            align="center",
            anchor="top",
        )
    plain(
        s,
        0.58,
        6.40,
        4.95,
        0.70,
        "A always pairs with T.\nG always pairs with C.",
        size=14,
        bold=True,
        color=INK,
        align="center",
        leading=1.15,
    )
    plain(
        s,
        0.58,
        7.15,
        4.95,
        0.70,
        "All living things have DNA — people, plants, animals, and strawberries.",
        size=14,
        color=INK,
        align="center",
        leading=1.12,
    )

    # Right stack
    right_x, right_w = 5.90, 4.72
    blocks = [
        (
            1.16,
            2.15,
            LEAF,
            "WHY A STRAWBERRY?",
            [
                "Strawberry cells are soft and easy to mash open.",
                "Each cell has eight copies of its DNA, so there is a lot to collect.",
                "DNA from thousands of cells can be seen without a microscope.",
            ],
        ),
        (
            3.45,
            2.35,
            BERRY,
            "WHY THESE SUPPLIES?",
            [
                "Dish soap bursts the cells open and releases the DNA.",
                "Salt keeps the proteins separate from the DNA.",
                "DNA does not dissolve in cold alcohol, so the strands clump and become visible.",
            ],
        ),
    ]
    for y, h, accent, title, lines in blocks:
        card(s, right_x, y, right_w, h)
        add_rect(s, right_x, y + 0.16, 0.09, h - 0.32, accent)
        plain(
            s,
            right_x + 0.24,
            y + 0.10,
            right_w - 0.40,
            0.34,
            title,
            size=13,
            bold=True,
            color=accent,
            anchor="middle",
            spacing=80,
        )
        body = "\n".join("•  " + line for line in lines)
        plain(
            s,
            right_x + 0.24,
            y + 0.48,
            right_w - 0.42,
            h - 0.60,
            body,
            size=14,
            color=INK,
            leading=1.08,
            after=6,
        )

    # Source
    y, h = 5.94, 2.17
    card(s, right_x, y, right_w, h, fill=SOFT_GOLD, line="E7D7B8")
    add_rect(s, right_x, y + 0.16, 0.09, h - 0.32, GOLD)
    plain(
        s,
        right_x + 0.24,
        y + 0.08,
        right_w - 0.40,
        0.30,
        "SOURCE",
        size=13,
        bold=True,
        color=GOLD,
        anchor="middle",
        spacing=120,
    )
    rich(
        s,
        right_x + 0.24,
        y + 0.40,
        right_w - 0.42,
        1.65,
        [
            para([run("Strawberry DNA Extraction", 15, bold=True)], after=2),
            para([run("Institute for Molecular Bioscience", 13)], after=0),
            para([run("The University of Queensland", 13)], after=4),
            para([run("www.imb.uq.edu.au", 13, bold=True, color=BERRY)], after=0),
        ],
    )


def slide_materials(prs):
    s = new_slide(prs, "Mount on the CENTER panel, under the title.")
    header(s, "Materials")

    left = [
        ("Strawberries", "The cells the DNA comes from"),
        ("Zip-close sandwich bag", "For mashing without a mess"),
        ("Dish soap", "Bursts the cells open"),
        ("Table salt", "Separates DNA from proteins"),
        ("Water", "The base of the extracting solution"),
        ("Plastic cup", "Catches the filtered liquid"),
    ]
    right = [
        ("Gauze or coffee filter", "Strains out the solids"),
        ("Rubber band", "Holds the filter on the cup"),
        ("Test tube or small cup", "Where the DNA shows up"),
        ("Spoon or dropper", "Moves the liquid and the alcohol"),
        ("Cold rubbing alcohol", "Kept in the freezer until use"),
        ("Paper towels", "For spills and cleanup"),
    ]

    def draw_items(items, x, start):
        top, row_h, col_w = 1.16, 0.78, 2.95
        for i, (name, why) in enumerate(items):
            y = top + i * row_h
            add_oval(s, x, y + 0.08, 0.26, 0.26, BERRY)
            plain(
                s,
                x,
                y + 0.08,
                0.26,
                0.26,
                str(start + i),
                size=10,
                bold=True,
                color=WHITE,
                align="center",
                anchor="middle",
                margins=(0, 0, 0, 0),
            )
            plain(
                s,
                x + 0.34,
                y + 0.00,
                col_w - 0.38,
                0.32,
                name,
                size=13,
                bold=True,
                color=INK,
                anchor="middle",
            )
            plain(
                s,
                x + 0.34,
                y + 0.30,
                col_w - 0.38,
                0.32,
                why,
                size=11,
                color=MUTED,
                anchor="top",
            )

    draw_items(left, 0.36, 1)
    draw_items(right, 3.32, 7)

    card(s, 6.42, 1.16, 4.20, 4.88)
    plain(
        s,
        6.58,
        1.24,
        3.88,
        0.28,
        "OUR SUPPLIES",
        size=12,
        bold=True,
        color=BERRY,
        align="center",
        anchor="middle",
        spacing=120,
    )
    photo_h = 4.22
    photo_w = photo_h * (450 / 600)
    photo_x = 6.42 + (4.20 - photo_w) / 2
    s.shapes.add_picture(
        MATERIALS_IMG, Inches(photo_x), Inches(1.58), Inches(photo_w), Inches(photo_h)
    )

    # Recipe banner
    add_round(s, 0.40, 6.22, 10.20, 1.92, BERRY, radius=0.08)
    plain(
        s,
        0.60,
        6.32,
        9.80,
        0.28,
        "MIX THIS FIRST",
        size=12,
        bold=True,
        color="F6D5DA",
        align="center",
        spacing=180,
        anchor="middle",
    )
    plain(
        s,
        0.60,
        6.58,
        9.80,
        0.36,
        "DNA extracting solution",
        size=20,
        bold=True,
        color=WHITE,
        align="center",
        anchor="middle",
    )
    chips = [
        ("1 tablespoon", "dish soap"),
        ("1 teaspoon", "salt"),
        ("1 cup", "water"),
    ]
    cw, cg = 2.55, 0.28
    total = 3 * cw + 2 * cg
    x0 = (SW - total) / 2
    for i, (amount, name) in enumerate(chips):
        x = x0 + i * (cw + cg)
        add_round(s, x, 7.05, cw, 0.88, WHITE, radius=0.12)
        plain(
            s,
            x + 0.08,
            7.08,
            cw - 0.16,
            0.40,
            amount,
            size=15,
            bold=True,
            color=BERRY,
            align="center",
            anchor="middle",
        )
        plain(
            s,
            x + 0.08,
            7.44,
            cw - 0.16,
            0.40,
            name,
            size=14,
            color=INK,
            align="center",
            anchor="middle",
        )


def slide_procedure(prs):
    s = new_slide(prs, "Mount on the CENTER panel, under Materials.")
    header(s, "Procedure")
    plain(
        s,
        0.42,
        1.00,
        10.1,
        0.32,
        "Use 2 tablespoons of the DNA extracting solution from the Materials list.",
        size=14,
        color=MUTED,
        anchor="middle",
    )

    steps = [
        "Seal one strawberry in a zip-close bag. Push out most of the air.",
        "Mash it gently in your hand. Do not pound the bag on the table.",
        "Add 2 tablespoons of the DNA extracting solution.",
        "Keep mashing until the strawberry looks soupy.",
        "Cover a cup with gauze or a coffee filter. Hold it with a rubber band.",
        "Pour the mixture through so only the liquid goes into the cup.",
        "Spoon some liquid into a clear test tube or small cup.",
        "Add a spoonful of cold alcohol. Do not tilt the tube or mix.",
        "Watch the line where the strawberry liquid meets the alcohol.",
    ]
    cols, rows = 2, 5
    left, top = 0.36, 1.40
    grid_w, grid_h = 6.05, 5.55
    gap_x, gap_y = 0.14, 0.08
    col_w = (grid_w - gap_x) / cols
    row_h = (grid_h - gap_y * (rows - 1)) / rows
    for i, text in enumerate(steps):
        c = 0 if i < 5 else 1
        r = i if i < 5 else i - 5
        x = left + c * (col_w + gap_x)
        y = top + r * (row_h + gap_y)
        circle = 0.34
        add_oval(s, x, y + (row_h - circle) / 2, circle, circle, BERRY)
        plain(
            s,
            x,
            y + (row_h - circle) / 2,
            circle,
            circle,
            str(i + 1),
            size=13,
            bold=True,
            color=WHITE,
            align="center",
            anchor="middle",
            margins=(0, 0, 0, 0),
        )
        plain(
            s,
            x + 0.42,
            y,
            col_w - 0.46,
            row_h,
            text,
            size=13,
            color=INK,
            anchor="middle",
            leading=1.02,
        )

    card(s, 6.58, 1.40, 4.04, 5.55)
    plain(
        s,
        6.72,
        1.48,
        3.76,
        0.30,
        "FINLEY ADDS THE ALCOHOL",
        size=11,
        bold=True,
        color=BERRY,
        align="center",
        anchor="middle",
        spacing=60,
    )
    photo_h = 4.36
    photo_w = photo_h * (450 / 600)
    photo_x = 6.58 + (4.04 - photo_w) / 2
    s.shapes.add_picture(
        ALCOHOL_IMG, Inches(photo_x), Inches(1.84), Inches(photo_w), Inches(photo_h)
    )
    plain(
        s,
        6.72,
        6.26,
        3.76,
        0.58,
        "Finley adds the cold alcohol with a dropper so the two liquids stay in layers.",
        size=12,
        color=INK,
        align="center",
        anchor="middle",
    )

    add_round(s, 0.38, 7.12, 10.24, 1.05, SOFT_GOLD, line="E7D7B8", radius=0.08)
    add_rect(s, 0.38, 7.28, 0.09, 0.73, GOLD)
    plain(
        s,
        0.64,
        7.20,
        9.80,
        0.32,
        "ADULT HELP",
        size=12,
        bold=True,
        color=GOLD,
        spacing=140,
        anchor="middle",
    )
    plain(
        s,
        0.64,
        7.50,
        9.80,
        0.55,
        "Ask an adult to pour the alcohol. Do not drink it. Keep it in the freezer until you use it. Pounding the bag can break the DNA.",
        size=14,
        color=INK,
        anchor="top",
    )


def slide_mixing(prs):
    s = new_slide(
        prs,
        "Mount on the RIGHT panel, top, above Collect and Drain.",
    )
    header(s, "Mixing and Filtering")
    items = [
        (
            SALT_IMG,
            "ADDING THE SALT",
            "Finley adds salt to the extraction mixture.",
        ),
        (
            FUNNEL_IMG,
            "FUNNEL THE MASH",
            "Finley funnels the mash through the cloth.",
        ),
        (
            FILTER_IMG,
            "FILTER THE MASH",
            "Finley filters the mash and keeps the solids out.",
        ),
    ]
    gap = 0.14
    x0, y, h = 0.36, 1.16, 6.15
    w = (10.28 - gap * 2) / 3
    for i, (path, kicker, caption) in enumerate(items):
        photo_card(s, x0 + i * (w + gap), y, w, h, path, kicker, caption)
    plain(
        s,
        0.40,
        7.48,
        10.20,
        0.55,
        "Salt is stirred into the soap and water first. Then the mashed strawberry is poured and pressed through the cloth.",
        size=15,
        color=INK,
        align="center",
        anchor="middle",
    )


def slide_collect(prs):
    s = new_slide(
        prs,
        "Mount on the RIGHT panel, under Mixing and Filtering. Read left to right: the mash drains, then Finley collects the liquid.",
    )
    header(s, "Drain and Collect")
    items = [
        (
            DRAIN_IMG,
            "DRAIN THE MASH",
            "The mash drains through the cloth into the jar.",
        ),
        (
            COLLECT_IMG,
            "COLLECT THE LIQUID",
            "Finley collects the filtered liquid for the next step.",
        ),
    ]
    gap = 0.18
    x0, y, h = 0.36, 1.16, 6.90
    w = (10.28 - gap) / 2
    for i, (path, kicker, caption) in enumerate(items):
        photo_card(s, x0 + i * (w + gap), y, w, h, path, kicker, caption)


def slide_results(prs):
    s = new_slide(prs, "Mount on the RIGHT panel, under Collect and Drain.")
    header(s, "Results")

    card(s, 0.38, 1.16, 4.85, 6.95)
    plain(
        s,
        0.52,
        1.28,
        4.55,
        0.36,
        "IN THE TUBE",
        size=13,
        bold=True,
        color=BERRY,
        align="center",
        spacing=120,
        anchor="middle",
    )

    # Test tube geometry, in inches
    left, top, width, height = 1.05, 1.85, 1.72, 4.85
    r = width / 2
    cx = left + r
    cy = top + height - r  # center of the bottom curve
    right = left + width

    glass = [(left, top), (left, cy)]
    glass += _arc(cx, cy, r, 180, 360, 24)[1:]
    glass += [(right, top)]
    add_freeform(s, glass, WHITE, line=INK, line_w=1.75)
    # rim
    add_rect(s, left, top - 0.03, width, 0.06, INK)

    inset = 0.09
    il, iw = left + inset, width - 2 * inset
    ir = il + iw
    inner_r = iw / 2
    icx = il + inner_r
    # Keep the inner bottom curve inside the glass
    icy = cy
    interface = top + 2.15

    # Strawberry liquid: interface down through the rounded bottom
    liquid = [(il, interface), (il, icy)]
    liquid += _arc(icx, icy, inner_r, 180, 360, 24)[1:]
    liquid += [(ir, interface)]
    add_freeform(s, liquid, LIQUID)

    # Alcohol layer
    add_rect(s, il, top + 0.12, iw, interface - (top + 0.12), ALCOHOL)
    # surface line
    add_rect(s, il, top + 0.12, iw, 0.025, "F7FBFE")

    # DNA cloud — white threads at the interface, drifting up
    clouds = [
        (cx - 0.34, interface - 0.02, 0.42, 0.20),
        (cx - 0.02, interface - 0.16, 0.36, 0.18),
        (cx - 0.22, interface + 0.06, 0.50, 0.16),
        (cx + 0.16, interface - 0.04, 0.30, 0.15),
        (cx - 0.16, interface - 0.32, 0.26, 0.14),
        (cx + 0.08, interface - 0.40, 0.20, 0.12),
        (cx - 0.30, interface - 0.22, 0.22, 0.12),
    ]
    for x, y, w, h in clouds:
        add_oval(s, x, y, w, h, WHITE, line="8EA0B0", line_w=0.75)

    # Labels to the right of the tube, inside the card
    labels = [
        (2.95, top + 0.55, T_COLOR, "Cold alcohol", "Top layer"),
        (2.95, interface - 0.28, BERRY, "DNA", "White strands"),
        (2.95, interface + 0.85, "C45A52", "Strawberry liquid", "Bottom layer"),
    ]
    for x, y, color, title, sub in labels:
        add_oval(s, x, y + 0.08, 0.16, 0.16, color)
        plain(s, x + 0.24, y - 0.02, 1.85, 0.28, title, size=13, bold=True, color=INK, anchor="middle")
        plain(s, x + 0.24, y + 0.24, 1.85, 0.26, sub, size=12, color=MUTED, anchor="top")

    plain(
        s,
        0.55,
        6.85,
        4.50,
        1.05,
        "The two liquids stay apart.\nThe DNA appears on the line between them.",
        size=13,
        color=MUTED,
        align="center",
        leading=1.12,
    )

    findings = [
        ("1", "Two layers"),
        ("2", "A white cloud"),
        ("3", "It floats up"),
        ("4", "This is the DNA"),
    ]
    bodies = [
        "The strawberry liquid stayed on the bottom. The cold alcohol stayed on top.",
        "A white, thread-like cloud formed on the line where the two liquids met.",
        "The threads clumped together and rose into the alcohol layer.",
        "That white cloud is strawberry DNA, gathered from thousands of cells.",
    ]
    fx, fw = 5.42, 5.20
    fy, gap = 1.16, 0.14
    fh = (6.95 - 3 * gap) / 4
    for i, ((num, title), body) in enumerate(zip(findings, bodies)):
        y = fy + i * (fh + gap)
        card(s, fx, y, fw, fh)
        add_oval(s, fx + 0.16, y + (fh - 0.42) / 2, 0.42, 0.42, BERRY)
        plain(
            s,
            fx + 0.16,
            y + (fh - 0.42) / 2,
            0.42,
            0.42,
            num,
            size=16,
            bold=True,
            color=WHITE,
            align="center",
            anchor="middle",
            margins=(0, 0, 0, 0),
        )
        plain(
            s,
            fx + 0.72,
            y + 0.10,
            fw - 0.90,
            0.36,
            title,
            size=16,
            bold=True,
            color=INK,
            anchor="middle",
        )
        plain(
            s,
            fx + 0.72,
            y + 0.48,
            fw - 0.90,
            fh - 0.58,
            body,
            size=14,
            color=MUTED,
            anchor="top",
            leading=1.05,
        )


def slide_data(prs):
    s = new_slide(
        prs,
        "Mount with Results. This slide is the 40X overview and the two 100X views.",
    )
    header(s, "Data and Pictures")
    items = [
        (
            DNA_40X,
            "40X",
            "The whole DNA clump. Scale bar: 1,000 micrometers.",
        ),
        (
            DNA_100X_A,
            "100X",
            "The clump looks stringy. Scale bar: 250 micrometers.",
        ),
        (
            DNA_100X_B,
            "100X",
            "Another 100X view of the strands. Scale bar: 250 micrometers.",
        ),
    ]
    gap = 0.14
    x0, y, h = 0.32, 1.14, 4.55
    w = (10.36 - gap * 2) / 3
    for i, (path, kicker, caption) in enumerate(items):
        photo_card(
            s, x0 + i * (w + gap), y, w, h, path, kicker, caption, aspect=MICRO_ASPECT
        )
    card(s, 0.32, 5.88, 10.36, 1.85)
    plain(
        s,
        0.52,
        5.96,
        9.96,
        0.30,
        "WHAT THE PICTURES SHOW",
        size=13,
        bold=True,
        color=BERRY,
        spacing=80,
        anchor="middle",
    )
    plain(
        s,
        0.52,
        6.28,
        9.96,
        1.30,
        "These are digital microscope photos of the DNA Finley collected. At 40X it is one white clump. At 100X that clump is made of many thin strands. The blue line in each photo is a scale bar. 1,000 micrometers equals 1 millimeter.",
        size=16,
        color=INK,
        anchor="top",
        leading=1.05,
    )


def slide_magnification(prs):
    s = new_slide(
        prs,
        "Mount after Data and Pictures. This slide is the 500X and 1000X views.",
    )
    header(s, "Higher Magnification")
    items = [
        (
            DNA_500X,
            "500X",
            "A thin strand up close. Scale bar: 50 micrometers.",
        ),
        (
            DNA_1000X,
            "1000X",
            "The closest view of a strand. Scale bar: 25 micrometers.",
        ),
    ]
    gap = 0.16
    x0, y, h = 0.32, 1.14, 5.05
    w = (10.36 - gap) / 2
    for i, (path, kicker, caption) in enumerate(items):
        photo_card(
            s, x0 + i * (w + gap), y, w, h, path, kicker, caption, aspect=MICRO_ASPECT
        )
    card(s, 0.32, 6.38, 10.36, 1.72, fill=SOFT_LEAF, line="C9E6D4")
    plain(
        s,
        0.52,
        6.48,
        9.96,
        1.48,
        "At 500X and 1000X a thin strand stands out from the clump. The scale bars are 50 and 25 micrometers. A human hair is about 70 micrometers wide, so these strands are thinner than a hair.",
        size=16,
        color=INK,
        anchor="middle",
        leading=1.08,
    )


def slide_conclusion(prs):
    s = new_slide(prs, "Mount on the RIGHT panel, under Results. The right panel, top to bottom: Mixing and Filtering, Collect and Drain, Results, Conclusion.")
    header(s, "Conclusion")

    add_round(s, 0.40, 1.18, 10.20, 1.25, SOFT_LEAF, line="C9E6D4", radius=0.08)
    add_rect(s, 0.40, 1.34, 0.10, 0.93, LEAF)
    plain(
        s,
        0.70,
        1.18,
        9.70,
        1.25,
        "My hypothesis was supported.",
        size=28,
        bold=True,
        color=LEAF_DEEP,
        anchor="middle",
    )

    plain(
        s,
        0.45,
        2.55,
        10.10,
        1.05,
        "I predicted that soap, salt, and cold alcohol would help us see strawberry DNA. The white, thread-like strands in the alcohol showed that this happened.",
        size=18,
        color=INK,
        align="left",
        anchor="top",
        leading=1.15,
    )

    plain(
        s,
        0.42,
        3.68,
        10.1,
        0.32,
        "WHAT I LEARNED",
        size=13,
        bold=True,
        color=BERRY,
        spacing=140,
        anchor="middle",
    )

    lessons = [
        (BERRY, "SOAP", "Soap breaks the cell membrane, the outer layer of each cell, so the DNA can spill out."),
        (GOLD, "SALT", "Salt helps keep the DNA separate from the proteins that were packed in the cell with it."),
        (T_COLOR, "COLD ALCOHOL", "DNA does not dissolve in cold alcohol, so the strands clump into a cloud we can see."),
        (LEAF, "THE BIG IDEA", "DNA is in every living thing. Household supplies can make the DNA inside a strawberry visible."),
    ]
    gap_x, gap_y = 0.16, 0.14
    cw = (10.20 - gap_x) / 2
    ch = 1.85
    top = 4.10
    for i, (accent, title, body) in enumerate(lessons):
        col, row = i % 2, i // 2
        x = 0.40 + col * (cw + gap_x)
        y = top + row * (ch + gap_y)
        card(s, x, y, cw, ch)
        add_rect(s, x, y + 0.16, 0.09, ch - 0.32, accent)
        plain(
            s,
            x + 0.26,
            y + 0.28,
            cw - 0.42,
            0.36,
            title,
            size=13,
            bold=True,
            color=accent,
            anchor="middle",
            spacing=100,
        )
        plain(
            s,
            x + 0.26,
            y + 0.68,
            cw - 0.44,
            0.95,
            body,
            size=15,
            color=INK,
            anchor="top",
            leading=1.08,
        )


def build():
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)
    prs.core_properties.title = "Strawberry DNA Extraction"
    prs.core_properties.author = AUTHOR
    prs.core_properties.subject = (
        "Science fair poster slides. Print landscape, letter, actual size, one slide per page."
    )
    prs.core_properties.category = "Science Fair"
    slide_title(prs)
    slide_question(prs)
    slide_hypothesis(prs)
    slide_research(prs)
    slide_materials(prs)
    slide_procedure(prs)
    slide_mixing(prs)
    slide_collect(prs)
    slide_results(prs)
    slide_data(prs)
    slide_magnification(prs)
    slide_conclusion(prs)
    # Drop unused empty layout slide if the default template added none — it doesn't.
    prs.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
