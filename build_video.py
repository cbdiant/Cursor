#!/usr/bin/env python3
"""Narrated science-fair video for Finley Grace DiAntonio.

A cartoon Finley hosts a walk through the whole strawberry DNA project.
Run: python3 build_video.py
Preview stills only: python3 build_video.py --preview
"""

import asyncio
import math
import os
import subprocess
import sys

import edge_tts
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
HOST = os.path.join(ASSETS, "host")
OUT = os.path.join(ROOT, "Finley Strawberry DNA.mp4")
WORK = "/tmp/video"
FPS = 12
W, H = 1280, 720
VOICE = "en-US-AnaNeural"
RATE = "+8%"

CREAM = (251, 247, 242)
INK = (44, 36, 31)
MUTED = (92, 83, 76)
BERRY = (163, 29, 54)
LEAF = (27, 122, 74)
GOLD = (165, 107, 18)
WHITE = (255, 255, 255)
BLUE = (44, 110, 155)
LINE = (228, 217, 206)
SOFT_BERRY = (248, 236, 236)
SOFT_LEAF = (230, 245, 237)
SOFT_BLUE = (228, 240, 248)
SOFT_GOLD = (251, 244, 230)

FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def wrap(draw, text, face, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=face) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def rounded(draw, box, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def cover(im, w, h):
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def contain(im, w, h):
    im = im.convert("RGBA")
    scale = min(w / im.width, h / im.height)
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def paste_round(base, im, box, radius=22):
    x, y, w, h = box
    photo = cover(im, w, h)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    base.paste(photo, (x, y), mask)


def load(name):
    return Image.open(os.path.join(ASSETS, name))


HOSTS = {}


def host(name):
    if name not in HOSTS:
        HOSTS[name] = Image.open(os.path.join(HOST, f"finley-{name}.png")).convert("RGBA")
    return HOSTS[name]


def panel_box():
    return (32, 92, 800, 508)


def draw_title_block(base, kicker, title):
    draw = ImageDraw.Draw(base)
    draw.rectangle((0, 0, W, 12), fill=BERRY)
    draw.rectangle((0, 12, W, 18), fill=LEAF)
    draw.text((32, 28), kicker, font=font(15, True), fill=LEAF)
    draw.text((32, 48), title, font=font(32, True), fill=BERRY)


def caption(base, text):
    draw = ImageDraw.Draw(base)
    y = 612
    rounded(draw, (24, y, W - 24, H - 16), 16, WHITE, LINE, 2)
    face = font(22)
    lines = wrap(draw, text, face, W - 88)
    lines = lines[:3]
    block_h = len(lines) * 28
    ty = y + (H - 16 - y - block_h) / 2 - 1
    for line in lines:
        draw.text((44, ty), line, font=face, fill=INK)
        ty += 28


def place_host(base, pose, t):
    im = host(pose)
    bob = int(7 * math.sin(t * 2.4))
    target_h = 500
    scale = target_h / im.height
    nw, nh = int(im.width * scale), int(im.height * scale)
    sprite = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = W - nw - 8
    y = 600 - nh + bob
    base.alpha_composite(sprite, (x, y))


def card_text(draw, box, title, body, accent, title_size=22, body_size=20):
    x, y, w, h = box
    rounded(draw, (x, y, x + w, y + h), 18, WHITE, LINE, 2)
    draw.rectangle((x, y + 16, x + 8, y + h - 16), fill=accent)
    title_face = font(title_size, True)
    title_lines = wrap(draw, title, title_face, w - 48)
    ty = y + 18
    for line in title_lines:
        draw.text((x + 24, ty), line, font=title_face, fill=accent)
        ty += title_size + 6
    face = font(body_size)
    ty += 8
    for line in wrap(draw, body, face, w - 48):
        if ty > y + h - body_size - 8:
            break
        draw.text((x + 24, ty), line, font=face, fill=INK)
        ty += body_size + 8


def visual_title(base):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    berry = contain(load("strawberry-smile.png"), 340, h - 10)
    base.alpha_composite(berry, (x, y + (h - berry.height) // 2))
    tx = x + 360
    draw.text((tx, y + 70), "SCIENCE FAIR PROJECT", font=font(16, True), fill=LEAF)
    for i, line in enumerate(["Strawberry", "DNA"]):
        draw.text((tx, y + 110 + i * 64), line, font=font(54, True), fill=INK if i == 0 else BERRY)
    draw.text((tx, y + 260), "by Finley Grace DiAntonio", font=font(24, True), fill=INK)
    draw.text((tx, y + 310), "Kitchen supplies. Real DNA.", font=font(22), fill=MUTED)


def visual_words(base, words):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    gap = 16
    cw = (w - gap * (len(words) - 1)) // len(words)
    colors = [BERRY, GOLD, BLUE, LEAF]
    soft = [SOFT_BERRY, SOFT_GOLD, SOFT_BLUE, SOFT_LEAF]
    for i, (big, small) in enumerate(words):
        bx = x + i * (cw + gap)
        rounded(draw, (bx, y, bx + cw, y + h), 22, soft[i % 4], None, 1)
        draw.rectangle((bx, y, bx + cw, y + 12), fill=colors[i % 4])
        face = font(36 if len(big) < 12 else 28, True)
        tw = draw.textlength(big, font=face)
        draw.text((bx + (cw - tw) / 2, y + 150), big, font=face, fill=colors[i % 4])
        face2 = font(20)
        for n, line in enumerate(wrap(draw, small, face2, cw - 36)):
            lw = draw.textlength(line, font=face2)
            draw.text((bx + (cw - lw) / 2, y + 230 + n * 28), line, font=face2, fill=INK)


def visual_quote(base, quote, sub):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    rounded(draw, (x, y, x + w, y + h), 24, WHITE, LINE, 2)
    draw.rectangle((x, y + 28, x + 12, y + h - 28), fill=BERRY)
    face = font(34, True)
    lines = wrap(draw, quote, face, w - 70)
    ty = y + 70
    for line in lines:
        draw.text((x + 40, ty), line, font=face, fill=INK)
        ty += 46
    face2 = font(22)
    for line in wrap(draw, sub, face2, w - 70):
        draw.text((x + 40, ty + 16), line, font=face2, fill=MUTED)
        ty += 30


def visual_dna(base):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    helix = contain(load("dna-helix.png"), 230, h)
    base.alpha_composite(helix, (x + 10, y + (h - helix.height) // 2))
    tx = x + 260
    draw.text((tx, y + 8), "A twisted ladder", font=font(28, True), fill=INK)
    facts = [
        "Sides: sugars and phosphates.",
        "Rungs: four bases.",
        "A always pairs with T.",
        "G always pairs with C.",
    ]
    face = font(22)
    for i, line in enumerate(facts):
        draw.text((tx, y + 58 + i * 34), line, font=face, fill=INK)
    bases = [("A", "Adenine", (208, 106, 44)), ("T", "Thymine", BLUE), ("G", "Guanine", LEAF), ("C", "Cytosine", BERRY)]
    for i, (letter, name, color) in enumerate(bases):
        bx = tx + i * 130
        by = y + 230
        draw.ellipse((bx, by, bx + 54, by + 54), fill=color)
        lw = draw.textlength(letter, font=font(22, True))
        draw.text((bx + (54 - lw) / 2, by + 12), letter, font=font(22, True), fill=WHITE)
        draw.text((bx, by + 62), name, font=font(16), fill=MUTED)


def visual_strawberry(base):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    berry = contain(load("strawberry.png"), 300, h)
    base.alpha_composite(berry, (x, y + (h - berry.height) // 2))
    tx = x + 320
    draw.text((tx, y + 30), "Why a strawberry?", font=font(30, True), fill=BERRY)
    lines = [
        "Soft cells that mash open easily.",
        "Eight copies of DNA in every cell.",
        "Thousands of cells in one berry.",
        "Enough DNA to see without a microscope.",
    ]
    for i, line in enumerate(lines):
        draw.text((tx, y + 100 + i * 48), line, font=font(22), fill=INK)
    draw.text((tx, y + 310), "Source: University of Queensland", font=font(18, True), fill=GOLD)


def visual_reasons(base):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    items = [
        (BERRY, "SOAP", "Breaks open the cells and lets the DNA out."),
        (GOLD, "SALT", "Helps keep proteins separate from the DNA."),
        (BLUE, "COLD ALCOHOL", "DNA will not dissolve, so the strands clump."),
    ]
    gap = 16
    cw = (w - 2 * gap) // 3
    ch = 250
    cy = y + (h - ch) // 2
    for i, (color, title, body) in enumerate(items):
        card_text(draw, (x + i * (cw + gap), cy, cw, ch), title, body, color, 22, 22)


def visual_materials(base):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    photo = load("materials.png")
    paste_round(base, photo, (x, y, 300, h), 20)
    items = [
        "Strawberry and a zip bag",
        "Dish soap, salt, and water",
        "Cup, gauze, rubber band",
        "Small tube and a dropper",
        "Cold rubbing alcohol",
        "An adult helps with the alcohol",
    ]
    for i, line in enumerate(items):
        draw.ellipse((x + 324, y + 18 + i * 72, x + 352, y + 46 + i * 72), fill=BERRY)
        num = str(i + 1)
        nw = draw.textlength(num, font=font(16, True))
        draw.text((x + 338 - nw / 2, y + 22 + i * 72), num, font=font(16, True), fill=WHITE)
        draw.text((x + 366, y + 20 + i * 72), line, font=font(22), fill=INK)


def visual_recipe(base):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    rounded(draw, (x, y, x + w, y + 150), 22, BERRY)
    draw.text((x + 28, y + 28), "DNA EXTRACTING SOLUTION", font=font(16, True), fill=(246, 213, 218))
    draw.text((x + 28, y + 62), "Mix this first", font=font(36, True), fill=WHITE)
    chips = [("1 tablespoon", "dish soap"), ("1 teaspoon", "salt"), ("1 cup", "water")]
    gap = 16
    cw = (w - 2 * gap) // 3
    for i, (amount, name) in enumerate(chips):
        bx = x + i * (cw + gap)
        by = y + 190
        rounded(draw, (bx, by, bx + cw, by + 200), 20, WHITE, LINE, 2)
        aw = draw.textlength(amount, font=font(26, True))
        draw.text((bx + (cw - aw) / 2, by + 48), amount, font=font(26, True), fill=BERRY)
        nw = draw.textlength(name, font=font(24))
        draw.text((bx + (cw - nw) / 2, by + 100), name, font=font(24), fill=INK)
    draw.text((x, y + 420), "Use 2 tablespoons on the strawberry.", font=font(22, True), fill=INK)


def visual_photo(base, filename, headline, lines):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    paste_round(base, load(filename), (x, y, 340, h), 20)
    draw.text((x + 364, y + 16), headline, font=font(28, True), fill=BERRY)
    face = font(22)
    ty = y + 80
    for line in lines:
        for wrapped in wrap(draw, line, face, w - 380):
            draw.text((x + 364, ty), wrapped, font=face, fill=INK)
            ty += 32
        ty += 10


def visual_trio(base, photos, headline):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    draw.text((x, y), headline, font=font(26, True), fill=BERRY)
    gap = 14
    pw = (w - 2 * gap) // 3
    ph = h - 50
    for i, (filename, label) in enumerate(photos):
        bx = x + i * (pw + gap)
        paste_round(base, load(filename), (bx, y + 46, pw, ph - 36), 16)
        tw = draw.textlength(label, font=font(16, True))
        draw.text((bx + (pw - tw) / 2, y + h - 28), label, font=font(16, True), fill=INK)


def visual_tube(base):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    paste_round(base, load("tube-result.jpg"), (x, y, 300, h), 20)
    labels = [
        (BLUE, "Cold alcohol", "Clear layer on top"),
        (BERRY, "Strawberry DNA", "White cloud in the middle"),
        ((196, 90, 82), "Mixture", "Orange layer on the bottom"),
    ]
    for i, (color, title, sub) in enumerate(labels):
        by = y + 30 + i * 140
        draw.ellipse((x + 330, by + 8, x + 358, by + 36), fill=color)
        draw.text((x + 376, by), title, font=font(24, True), fill=INK)
        draw.text((x + 376, by + 36), sub, font=font(20), fill=MUTED)


def visual_micro(base, photos):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    gap = 16
    pw = (w - gap) // 2
    for i, (filename, mag, note) in enumerate(photos):
        bx = x + i * (pw + gap)
        draw.text((bx, y), mag, font=font(26, True), fill=BERRY)
        paste_round(base, load(filename), (bx, y + 42, pw, h - 90), 16)
        face = font(18)
        for n, line in enumerate(wrap(draw, note, face, pw)):
            draw.text((bx, y + h - 40 + n * 22), line, font=face, fill=INK)


def visual_conclusion(base):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    rounded(draw, (x, y, x + w, y + 110), 18, SOFT_LEAF, (201, 230, 212), 2)
    draw.text((x + 24, y + 32), "My hypothesis was supported.", font=font(30, True), fill=(20, 92, 54))
    lessons = [
        (BERRY, "SOAP", "Opens the cells so the DNA can spill out."),
        (GOLD, "SALT", "Separates the DNA from the proteins."),
        (BLUE, "COLD ALCOHOL", "Makes the strands clump so we can see them."),
        (LEAF, "THE BIG IDEA", "DNA is in every living thing, even a strawberry."),
    ]
    gap = 12
    cw = (w - gap) // 2
    ch = (h - 110 - 12 - gap) // 2
    for i, (color, title, body) in enumerate(lessons):
        col, row = i % 2, i // 2
        bx = x + col * (cw + gap)
        by = y + 122 + row * (ch + gap)
        card_text(draw, (bx, by, cw, ch), title, body, color, 20, 20)


def visual_outro(base):
    draw = ImageDraw.Draw(base)
    x, y, w, h = panel_box()
    berry = contain(load("strawberry-smile.png"), 280, h - 40)
    helix = contain(load("helix-smile.png"), 180, h - 20)
    base.alpha_composite(berry, (x + 20, y + (h - berry.height) // 2))
    base.alpha_composite(helix, (x + 300, y + (h - helix.height) // 2))
    draw.text((x + 500, y + 140), "Thanks for", font=font(36, True), fill=INK)
    draw.text((x + 500, y + 190), "watching!", font=font(36, True), fill=BERRY)
    draw.text((x + 500, y + 270), "Finley Grace", font=font(24, True), fill=INK)
    draw.text((x + 500, y + 306), "DiAntonio", font=font(24, True), fill=INK)


VISUALS = {
    "title": visual_title,
    "words": visual_words,
    "quote": visual_quote,
    "dna": visual_dna,
    "strawberry": visual_strawberry,
    "reasons": visual_reasons,
    "materials": visual_materials,
    "recipe": visual_recipe,
    "photo": visual_photo,
    "trio": visual_trio,
    "tube": visual_tube,
    "micro": visual_micro,
    "conclusion": visual_conclusion,
    "outro": visual_outro,
}

SCENES = [
    {
        "id": "intro",
        "kicker": "HELLO",
        "title": "Meet Finley",
        "pose": "smile",
        "visual": "title",
        "args": [],
        "say": "Hi! I'm Finley Grace DiAntonio. This is my science fair project. I extracted DNA from a strawberry, using stuff from the kitchen.",
    },
    {
        "id": "hook",
        "kicker": "THE SUPPLIES",
        "title": "Three kitchen heroes",
        "pose": "talk",
        "visual": "words",
        "args": [[("SOAP", "Bursts the cells"), ("SALT", "Moves proteins aside"), ("ALCOHOL", "Cold, from the freezer")]],
        "say": "Dish soap. Table salt. And cold alcohol that had been sitting in the freezer, waiting for its big moment.",
    },
    {
        "id": "question",
        "kicker": "QUESTION",
        "title": "What I wanted to know",
        "pose": "talk",
        "visual": "quote",
        "args": [
            "Can we extract DNA from a strawberry using household supplies?",
            "Not a fancy lab. Just the kitchen.",
        ],
        "say": "My question was, can we extract DNA from a strawberry using household supplies? Not a fancy lab. Just the kitchen.",
    },
    {
        "id": "hypothesis",
        "kicker": "HYPOTHESIS",
        "title": "My prediction",
        "pose": "smile",
        "visual": "quote",
        "args": [
            "I predict that soap, salt, and cold alcohol will help us see strawberry DNA.",
            "See it, with our actual eyes. That was the whole bet.",
        ],
        "say": "I predicted that soap, salt, and cold alcohol would help us see strawberry DNA. See it, with our actual eyes. That was the whole bet.",
    },
    {
        "id": "dna",
        "kicker": "RESEARCH",
        "title": "What DNA is",
        "pose": "talk",
        "visual": "dna",
        "args": [],
        "say": "DNA stands for deoxyribonucleic acid. It is a double helix, like a twisted ladder. The sides are sugars and phosphates. The rungs are four bases: adenine, thymine, guanine, and cytosine. A always pairs with T, and G always pairs with C.",
    },
    {
        "id": "why",
        "kicker": "RESEARCH",
        "title": "Why a strawberry?",
        "pose": "talk",
        "visual": "strawberry",
        "args": [],
        "say": "Strawberries are perfect for this. The cells are soft and easy to mash, and each cell has eight copies of its DNA. So one berry holds a lot. I learned that from the University of Queensland handout.",
    },
    {
        "id": "why-supplies",
        "kicker": "RESEARCH",
        "title": "Why these supplies?",
        "pose": "talk",
        "visual": "reasons",
        "args": [],
        "say": "Soap bursts the cells open. Salt keeps the proteins away from the DNA. And DNA does not dissolve in cold alcohol, so the strands clump into a white cloud you can see.",
    },
    {
        "id": "materials",
        "kicker": "MATERIALS",
        "title": "What I used",
        "pose": "talk",
        "visual": "materials",
        "args": [],
        "say": "Everything I used was a household supply. A strawberry, a zip bag, dish soap, salt, water, a cup, a filter, a rubber band, a little tube, a dropper, and cold rubbing alcohol. An adult helps with the alcohol. That is the rule.",
    },
    {
        "id": "recipe",
        "kicker": "MATERIALS",
        "title": "The extracting solution",
        "pose": "smile",
        "visual": "recipe",
        "args": [],
        "say": "First I mixed the extracting solution. One tablespoon of dish soap, one teaspoon of salt, and one cup of water. Then I only used two tablespoons on the strawberry. The rest of the cup just stood there looking official.",
    },
    {
        "id": "mash",
        "kicker": "PROCEDURE",
        "title": "Mash, then add salt",
        "pose": "talk",
        "visual": "photo",
        "args": [
            "salt.png",
            "Gentle squishing",
            [
                "Seal one strawberry in a zip bag.",
                "Push out the air and mash gently.",
                "The bag is not a drum.",
                "Add salt to the extraction mixture.",
            ],
        ],
        "say": "I sealed the strawberry in the bag, pushed out the air, and mashed it gently. No pounding. The bag is not a drum. Then I added the salt. Careful squishing is still science.",
    },
    {
        "id": "filter",
        "kicker": "PROCEDURE",
        "title": "Filter the mash",
        "pose": "talk",
        "visual": "trio",
        "args": [
            [
                ("funnel-mash.png", "Funnel"),
                ("filter-mash.png", "Filter"),
                ("collect-liquid.png", "Collect"),
            ],
            "Solids stay out. The liquid goes through.",
        ],
        "say": "I poured the mash through a cloth. The solids stayed out. The pink liquid went into the jar, and I collected it for the next step.",
    },
    {
        "id": "alcohol",
        "kicker": "PROCEDURE",
        "title": "Add the cold alcohol",
        "pose": "talk",
        "visual": "photo",
        "args": [
            "finley-alcohol.png",
            "Slow and steady",
            [
                "Spoon the liquid into a clear tube.",
                "Slide cold alcohol down the side.",
                "Do not tilt the tube.",
                "Do not stir. Just watch.",
            ],
        ],
        "say": "I spooned some liquid into a clear tube and slid cold alcohol down the side. No tilting. No stirring. Then I watched the line where the two liquids meet.",
    },
    {
        "id": "results",
        "kicker": "RESULTS",
        "title": "The DNA shows up",
        "pose": "wow",
        "visual": "tube",
        "args": [],
        "say": "And there it was! Orange strawberry mixture on the bottom. Clear alcohol on top. And right between them, a white thread-like cloud. That cloud is strawberry DNA, from thousands of cells.",
    },
    {
        "id": "micro-low",
        "kicker": "DATA",
        "title": "Under the microscope",
        "pose": "talk",
        "visual": "micro",
        "args": [[
            ("dna-40x.jpg", "40X", "One white clump. Scale bar: 1,000 micrometers."),
            ("dna-100x-a.jpg", "100X", "The clump looks stringy. Scale bar: 250 micrometers."),
        ]],
        "say": "I looked closer with a digital microscope. At 40X, the DNA is one white clump. The scale bar is one thousand micrometers, which is one millimeter. At 100X, that clump looks stringy.",
    },
    {
        "id": "micro-high",
        "kicker": "DATA",
        "title": "Closer and closer",
        "pose": "wow",
        "visual": "micro",
        "args": [[
            ("dna-500x.jpg", "500X", "A thin strand. Scale bar: 50 micrometers."),
            ("dna-1000x.jpg", "1000X", "Closest view. Scale bar: 25 micrometers."),
        ]],
        "say": "At 500X you can see a thin strand. At 1000X it is even closer, and the scale bar is only 25 micrometers. A human hair is about 70 micrometers wide, so these strands are thinner than a hair.",
    },
    {
        "id": "conclusion",
        "kicker": "CONCLUSION",
        "title": "What I learned",
        "pose": "smile",
        "visual": "conclusion",
        "args": [],
        "say": "My hypothesis was supported. Soap, salt, and cold alcohol really did help me see strawberry DNA. Soap opens the cells, salt separates the DNA from proteins, and cold alcohol makes the strands show up.",
    },
    {
        "id": "outro",
        "kicker": "THE END",
        "title": "Thanks for watching",
        "pose": "smile",
        "visual": "outro",
        "args": [],
        "say": "DNA is in every living thing. Even a strawberry. Even you. I'm Finley Grace DiAntonio. The strawberry did not make it. The DNA did. Thanks for watching!",
    },
]


def render_frame(scene, t):
    base = Image.new("RGBA", (W, H), CREAM + (255,))
    draw_title_block(base, scene["kicker"], scene["title"])
    VISUALS[scene["visual"]](base, *scene["args"])
    place_host(base, scene["pose"], t)
    caption(base, scene["say"])
    return base.convert("RGB")


async def synthesize(scene):
    os.makedirs(WORK, exist_ok=True)
    mp3 = os.path.join(WORK, f"{scene['id']}.mp3")
    if not os.path.exists(mp3) or os.path.getsize(mp3) < 1000:
        comm = edge_tts.Communicate(scene["say"], voice=VOICE, rate=RATE)
        await comm.save(mp3)
    return mp3


def audio_seconds(path):
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ],
        text=True,
    ).strip()
    return float(out)


def encode_scene(scene, nframes, mp3, dest):
    pad = nframes / FPS
    wav = os.path.join(WORK, f"{scene['id']}.wav")
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-v", "error", "-i", mp3,
            "-af", f"apad=whole_dur={pad:.3f}",
            "-ar", "44100", "-ac", "2", wav,
        ]
    )
    proc = subprocess.Popen(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
            "-i", "-",
            "-i", wav,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k",
            "-movflags", "+faststart",
            "-shortest", dest,
        ],
        stdin=subprocess.PIPE,
    )
    for i in range(nframes):
        proc.stdin.write(render_frame(scene, i / FPS).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed on {scene['id']}")


def concat(parts, dest):
    listing = os.path.join(WORK, "list.txt")
    with open(listing, "w") as fh:
        for part in parts:
            fh.write(f"file '{part}'\n")
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
            "-i", listing, "-c", "copy", "-movflags", "+faststart", dest,
        ]
    )


async def main():
    preview = "--preview" in sys.argv
    os.makedirs(WORK, exist_ok=True)
    preview_dir = os.path.join(WORK, "preview")
    os.makedirs(preview_dir, exist_ok=True)
    parts = []
    for scene in SCENES:
        print("scene", scene["id"], flush=True)
        if preview:
            frame = render_frame(scene, 0.4)
            frame.save(os.path.join(preview_dir, f"{scene['id']}.jpg"), quality=85)
            continue
        mp3 = await synthesize(scene)
        seconds = audio_seconds(mp3) + 0.35
        nframes = max(FPS, int(round(seconds * FPS)))
        dest = os.path.join(WORK, f"{scene['id']}.mp4")
        encode_scene(scene, nframes, mp3, dest)
        parts.append(dest)
        print("  ", round(seconds, 1), "s", flush=True)
    if preview:
        print(preview_dir)
        return
    concat(parts, OUT)
    print(OUT)


if __name__ == "__main__":
    asyncio.run(main())
