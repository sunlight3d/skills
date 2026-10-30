#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pptx_insert_slides.py

A utility script to insert beautifully designed, 100% native editable PowerPoint (.pptx)
slides into an existing presentation at any specified slide position.

Key Features:
- Dynamic Color Tone Detection (Auto Palette Extraction):
    * Scans existing slides (Slide 1, Slide 2, and slide adjacent to insertion point).
    * Extracts brand primary, secondary accents, and dark/light mode from native shapes,
      fonts, and slide images.
    * Adapts cards, borders, badges, and text colors dynamically to match the presentation's
      exact aesthetic (e.g., Navy/Blue, Forest Green/Orange, Tech Dark Mode, etc.).
- 100% Native PowerPoint Shapes & TextFrames (No screenshots/images).
- Fully editable: Edit text, change colors, resize shapes directly in Microsoft PowerPoint.
- Typography Standard: Font size >= 22pt everywhere for high legibility and presentation standards.
- Concise Content: Clean cards and concise bullet points preventing text overflow.
- Flexible Layouts:
    * '2_column': 2 comparison/parallel cards + bottom summary card
    * 'grid_2x2': 4 categorical cards arranged in a 2x2 grid
    * 'stacked_rows': 3-4 horizontal cards with badges and descriptions
"""

import os
import sys
import io
import json
import shutil
import colorsys
import argparse
from collections import Counter
from typing import List, Dict, Any, Optional, Tuple

try:
    import pptx
    from pptx import Presentation
    from pptx.util import Pt
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
except ImportError:
    print("Error: python-pptx is required. Install via: pip install python-pptx")
    sys.exit(1)

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def hex_to_rgb(hex_str: str) -> RGBColor:
    """Convert hex string (e.g. '#004C7E' or '004C7E') to RGBColor."""
    s = hex_str.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) == 6:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        return RGBColor(r, g, b)
    return RGBColor(0, 119, 182)


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


class PresentationPalette:
    """Encapsulates the detected color palette of the target presentation."""
    def __init__(self, is_dark_mode: bool, primary: RGBColor, accent: RGBColor,
                 card_bg: RGBColor, text_title: RGBColor, text_body: RGBColor,
                 border_subtle: RGBColor, alert_red: RGBColor,
                 status_orange: RGBColor, success_green: RGBColor):
        self.is_dark_mode = is_dark_mode
        self.primary = primary
        self.accent = accent
        self.card_bg = card_bg
        self.text_title = text_title
        self.text_body = text_body
        self.border_subtle = border_subtle
        self.alert_red = alert_red
        self.status_orange = status_orange
        self.success_green = success_green

    def summary(self) -> str:
        mode_str = "DARK" if self.is_dark_mode else "LIGHT"
        return (f"Mode: {mode_str} | Primary: {rgb_to_hex(self.primary)} | "
                f"Accent: {rgb_to_hex(self.accent)} | CardBg: {rgb_to_hex(self.card_bg)}")


def detect_presentation_palette(prs: Presentation, target_slide_idx: int) -> PresentationPalette:
    """
    Inspects several slides (Slide 1, Slide 2, and the slide adjacent to target)
    to dynamically extract the presentation's color tone and mode.
    """
    total = len(prs.slides)
    if total == 0:
        return _fallback_palette(False, "#004C7E", "#0077B6")

    # Sample slides: Slide 1 (Cover), Slide 2 (Agenda/Overview), and Slide around target
    sample_indices = set([0])
    if total > 1:
        sample_indices.add(1)
    adj_idx = max(0, min(target_slide_idx - 1, total - 1))
    sample_indices.add(adj_idx)
    if target_slide_idx < total:
        sample_indices.add(target_slide_idx)

    extracted_colors = []
    bg_luminances = []
    header_colors = []

    for s_idx in sorted(list(sample_indices)):
        s = prs.slides[s_idx]

        # 1. Native Shapes, Texts & Fills
        for shp in s.shapes:
            if shp.has_text_frame:
                for p in shp.text_frame.paragraphs:
                    for r in p.runs:
                        try:
                            if r.font.color and r.font.color.type == pptx.enum.dml.MSO_COLOR_TYPE.RGB:
                                c = r.font.color.rgb
                                extracted_colors.append((c[0], c[1], c[2]))
                        except Exception:
                            pass
            if shp.shape_type in [MSO_SHAPE.RECTANGLE, MSO_SHAPE.ROUNDED_RECTANGLE]:
                try:
                    if shp.fill and shp.fill.type == pptx.enum.dml.MSO_COLOR_TYPE.RGB:
                        fc = shp.fill.fore_color.rgb
                        extracted_colors.append((fc[0], fc[1], fc[2]))
                except Exception:
                    pass

            # 2. Slide Pictures / Image-based slides
            if HAS_PIL and shp.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
                try:
                    img = Image.open(io.BytesIO(shp.image.blob)).convert("RGB")
                    w, h = img.size

                    # Sample 4 corners + center for background tone
                    corners = [
                        img.getpixel((int(w * 0.05), int(h * 0.05))),
                        img.getpixel((int(w * 0.95), int(h * 0.05))),
                        img.getpixel((int(w * 0.5), int(h * 0.5))),
                        img.getpixel((int(w * 0.05), int(h * 0.95))),
                        img.getpixel((int(w * 0.95), int(h * 0.95))),
                    ]
                    for px in corners:
                        lum = (0.299 * px[0] + 0.587 * px[1] + 0.114 * px[2]) / 255.0
                        bg_luminances.append(lum)

                    # Sample header region (y: 3% to 20%)
                    hdr = img.crop((int(w * 0.04), int(h * 0.03), int(w * 0.96), int(h * 0.20)))
                    hdr_small = hdr.resize((120, 36))
                    for px in list(hdr_small.getdata()):
                        h_val, s_val, v_val = colorsys.rgb_to_hsv(px[0] / 255.0, px[1] / 255.0, px[2] / 255.0)
                        if s_val > 0.22 and 0.12 < v_val < 0.96:
                            header_colors.append(px)
                            extracted_colors.append(px)
                except Exception:
                    pass

    # Determine Light vs Dark Mode
    avg_bg_lum = sum(bg_luminances) / len(bg_luminances) if bg_luminances else 0.85
    is_dark = avg_bg_lum < 0.45

    # Group colors by Hue buckets to find dominant brand themes
    def find_top_hues(colors_list):
        buckets = Counter()
        rep_color = {}
        for c in colors_list:
            h_val, s_val, v_val = colorsys.rgb_to_hsv(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)
            if s_val > 0.18:
                bucket = int(h_val * 16) % 16
                buckets[bucket] += 1
                if bucket not in rep_color:
                    rep_color[bucket] = c
                else:
                    curr_c = rep_color[bucket]
                    curr_v = colorsys.rgb_to_hsv(curr_c[0]/255.0, curr_c[1]/255.0, curr_c[2]/255.0)[2]
                    # On dark mode prefer brighter representative; on light mode prefer rich contrast
                    if is_dark and v_val > curr_v:
                        rep_color[bucket] = c
                    elif not is_dark and 0.2 < v_val < 0.7 and v_val < curr_v:
                        rep_color[bucket] = c
        return [rep_color[b] for b, _ in buckets.most_common(4) if b in rep_color]

    top_hues = find_top_hues(header_colors if header_colors else extracted_colors)

    if top_hues:
        primary_rgb = top_hues[0]
        primary_col = RGBColor(primary_rgb[0], primary_rgb[1], primary_rgb[2])
    else:
        primary_col = RGBColor(0, 76, 126) if not is_dark else RGBColor(56, 189, 248)

    if len(top_hues) > 1:
        accent_rgb = top_hues[1]
        accent_col = RGBColor(accent_rgb[0], accent_rgb[1], accent_rgb[2])
    else:
        # Generate complementary/analogous accent
        pr, pg, pb = primary_col[0] / 255.0, primary_col[1] / 255.0, primary_col[2] / 255.0
        h, s, v = colorsys.rgb_to_hsv(pr, pg, pb)
        new_h = (h + 0.12) % 1.0
        ar, ag, ab = colorsys.hsv_to_rgb(new_h, min(1.0, s * 1.1), min(1.0, v * 1.2))
        accent_col = RGBColor(int(ar * 255), int(ag * 255), int(ab * 255))

    return _construct_palette(is_dark, primary_col, accent_col)


def _construct_palette(is_dark: bool, primary: RGBColor, accent: RGBColor) -> PresentationPalette:
    if is_dark:
        card_bg = RGBColor(24, 32, 47)         # Deep slate navy
        text_title = RGBColor(255, 255, 255)   # Crisp white
        text_body = RGBColor(226, 232, 240)    # Soft slate white
        border_subtle = RGBColor(51, 65, 85)   # Muted border
        alert_red = RGBColor(248, 113, 113)    # Bright coral red
        status_orange = RGBColor(251, 146, 60) # Bright amber orange
        success_green = RGBColor(74, 222, 128) # Bright emerald green
    else:
        card_bg = RGBColor(248, 250, 252)      # Soft off-white
        text_title = primary                   # Brand title
        text_body = RGBColor(30, 41, 59)       # High contrast charcoal
        border_subtle = RGBColor(203, 213, 225)# Crisp subtle gray
        alert_red = RGBColor(220, 38, 38)      # Classic red
        status_orange = RGBColor(234, 88, 12)  # Rich orange
        success_green = RGBColor(21, 128, 61)  # Forest green

    return PresentationPalette(
        is_dark_mode=is_dark,
        primary=primary,
        accent=accent,
        card_bg=card_bg,
        text_title=text_title,
        text_body=text_body,
        border_subtle=border_subtle,
        alert_red=alert_red,
        status_orange=status_orange,
        success_green=success_green
    )


def _fallback_palette(is_dark: bool, primary_hex: str, accent_hex: str) -> PresentationPalette:
    return _construct_palette(is_dark, hex_to_rgb(primary_hex), hex_to_rgb(accent_hex))


def add_header(slide, category: str, title: str, font_name: str, width: float, palette: PresentationPalette):
    """Add category & title header textbox at top of slide with harmonized colors."""
    header_box = slide.shapes.add_textbox(Pt(50), Pt(24), Pt(width - 100), Pt(76))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.alignment = PP_ALIGN.CENTER
    p_cat.font.size = Pt(22)
    p_cat.font.bold = True
    p_cat.font.name = font_name
    p_cat.font.color.rgb = palette.accent

    p_tit = tf.add_paragraph()
    p_tit.text = title.upper()
    p_tit.alignment = PP_ALIGN.CENTER
    p_tit.font.size = Pt(34)
    p_tit.font.bold = True
    p_tit.font.name = font_name
    p_tit.font.color.rgb = palette.text_title
    p_tit.space_before = Pt(4)


def build_slide_2_column(slide, slide_data: Dict[str, Any], font_name: str,
                         width: float, height: float, palette: PresentationPalette):
    """Build a 2-column comparison/parallel slide with an optional bottom summary card."""
    add_header(slide, slide_data.get("category", ""), slide_data.get("title", ""), font_name, width, palette)

    has_bottom = "bottom_card" in slide_data and slide_data["bottom_card"]
    card_h = 380 if has_bottom else 560
    card_w = (width - 130) / 2
    x_left = 50
    x_right = x_left + card_w + 30
    y_cards = 115

    # 1. Left Card
    left = slide_data.get("left_card", {})
    c_left = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Pt(x_left), Pt(y_cards), Pt(card_w), Pt(card_h))
    bg_l = hex_to_rgb(left["bg_color"]) if "bg_color" in left else palette.card_bg
    br_l = hex_to_rgb(left["border_color"]) if "border_color" in left else palette.primary
    c_left.fill.solid(); c_left.fill.fore_color.rgb = bg_l
    c_left.line.color.rgb = br_l; c_left.line.width = Pt(2.5)

    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = Pt(24)
    tf_l.margin_top = tf_l.margin_bottom = Pt(16)

    p_lh = tf_l.paragraphs[0]
    p_lh.text = f"{left.get('badge', '')} {left.get('title', '')}".strip()
    p_lh.font.size = Pt(25)
    p_lh.font.bold = True
    p_lh.font.name = font_name
    p_lh.font.color.rgb = br_l

    for item in left.get("items", []):
        p = tf_l.add_paragraph()
        p.space_before = Pt(10)
        _render_card_item(p, item, font_name, br_l, palette)

    # 2. Right Card
    right = slide_data.get("right_card", {})
    c_right = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Pt(x_right), Pt(y_cards), Pt(card_w), Pt(card_h))
    bg_r = hex_to_rgb(right["bg_color"]) if "bg_color" in right else palette.card_bg
    br_r = hex_to_rgb(right["border_color"]) if "border_color" in right else palette.success_green
    c_right.fill.solid(); c_right.fill.fore_color.rgb = bg_r
    c_right.line.color.rgb = br_r; c_right.line.width = Pt(2.5)

    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = Pt(24)
    tf_r.margin_top = tf_r.margin_bottom = Pt(16)

    p_rh = tf_r.paragraphs[0]
    p_rh.text = f"{right.get('badge', '')} {right.get('title', '')}".strip()
    p_rh.font.size = Pt(25)
    p_rh.font.bold = True
    p_rh.font.name = font_name
    p_rh.font.color.rgb = br_r

    for item in right.get("items", []):
        p = tf_r.add_paragraph()
        p.space_before = Pt(10)
        _render_card_item(p, item, font_name, br_r, palette)

    # 3. Bottom Card (if present)
    if has_bottom:
        bot = slide_data["bottom_card"]
        c_bot = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Pt(50), Pt(515), Pt(width - 100), Pt(175))
        bg_b = hex_to_rgb(bot["bg_color"]) if "bg_color" in bot else palette.card_bg
        br_b = hex_to_rgb(bot["border_color"]) if "border_color" in bot else palette.accent
        c_bot.fill.solid(); c_bot.fill.fore_color.rgb = bg_b
        c_bot.line.color.rgb = br_b; c_bot.line.width = Pt(2)

        tf_b = c_bot.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_right = Pt(24)
        tf_b.margin_top = tf_b.margin_bottom = Pt(14)

        p_bh = tf_b.paragraphs[0]
        p_bh.text = bot.get("title", "")
        p_bh.font.size = Pt(24)
        p_bh.font.bold = True
        p_bh.font.name = font_name
        p_bh.font.color.rgb = palette.primary

        for item in bot.get("items", []):
            p = tf_b.add_paragraph()
            p.space_before = Pt(6)
            if isinstance(item, str):
                r = p.add_run(); r.text = item; r.font.size = Pt(22); r.font.name = font_name; r.font.color.rgb = palette.text_body
            else:
                _render_card_item(p, item, font_name, br_b, palette)


def build_slide_grid_2x2(slide, slide_data: Dict[str, Any], font_name: str,
                         width: float, height: float, palette: PresentationPalette):
    """Build a 2x2 grid slide containing 4 distinct categorized cards matching presentation tone."""
    add_header(slide, slide_data.get("category", ""), slide_data.get("title", ""), font_name, width, palette)

    cards = slide_data.get("cards", [])
    if len(cards) < 4:
        while len(cards) < 4:
            cards.append({"title": f"Mục {len(cards)+1}", "items": []})

    card_w = (width - 130) / 2
    row1_y = 112
    row1_h = 280
    row2_y = 405
    row2_h = 288

    positions = [
        (50, row1_y, card_w, row1_h),
        (50 + card_w + 30, row1_y, card_w, row1_h),
        (50, row2_y, card_w, row2_h),
        (50 + card_w + 30, row2_y, card_w, row2_h)
    ]

    default_borders = [palette.alert_red, palette.status_orange, palette.accent, palette.primary]

    for i in range(4):
        c_info = cards[i]
        x, y, w, h = positions[i]

        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Pt(x), Pt(y), Pt(w), Pt(h))
        bg_col = hex_to_rgb(c_info["bg_color"]) if "bg_color" in c_info else palette.card_bg
        br_col = hex_to_rgb(c_info["border_color"]) if "border_color" in c_info else default_borders[i]
        shape.fill.solid(); shape.fill.fore_color.rgb = bg_col
        shape.line.color.rgb = br_col; shape.line.width = Pt(2.5)

        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Pt(22)
        tf.margin_top = tf.margin_bottom = Pt(14)

        badge_text = c_info.get("badge", "").strip()
        card_title = c_info.get("title", "").strip()
        full_title = f"{badge_text}: {card_title}" if badge_text else card_title

        p_h = tf.paragraphs[0]
        p_h.text = full_title
        p_h.font.size = Pt(24)
        p_h.font.bold = True
        p_h.font.name = font_name
        p_h.font.color.rgb = br_col

        for item in c_info.get("items", []):
            p = tf.add_paragraph()
            p.space_before = Pt(8)
            _render_card_item(p, item, font_name, br_col, palette)


def build_slide_stacked_rows(slide, slide_data: Dict[str, Any], font_name: str,
                             width: float, height: float, palette: PresentationPalette):
    """Build a stacked horizontal rows layout (3 or 4 rows)."""
    add_header(slide, slide_data.get("category", ""), slide_data.get("title", ""), font_name, width, palette)

    rows = slide_data.get("rows", [])
    count = min(len(rows), 4)
    if count == 0:
        return

    row_h = (580 - (count - 1) * 16) / count
    y_start = 115
    default_borders = [palette.primary, palette.success_green, palette.status_orange, palette.alert_red]

    for i in range(count):
        r_info = rows[i]
        y = y_start + i * (row_h + 16)

        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Pt(50), Pt(y), Pt(width - 100), Pt(row_h))
        bg_col = hex_to_rgb(r_info["bg_color"]) if "bg_color" in r_info else palette.card_bg
        br_col = hex_to_rgb(r_info["border_color"]) if "border_color" in r_info else default_borders[i % 4]
        shape.fill.solid(); shape.fill.fore_color.rgb = bg_col
        shape.line.color.rgb = br_col; shape.line.width = Pt(2)

        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Pt(24)
        tf.margin_top = tf.margin_bottom = Pt(12)

        p = tf.paragraphs[0]
        badge = r_info.get("badge", "").strip()
        title = r_info.get("title", "").strip()
        if badge:
            r1 = p.add_run(); r1.text = f"[{badge}] "; r1.font.bold = True; r1.font.size = Pt(24); r1.font.name = font_name; r1.font.color.rgb = br_col
        if title:
            r2 = p.add_run(); r2.text = f"{title}: "; r2.font.bold = True; r2.font.size = Pt(24); r2.font.name = font_name; r2.font.color.rgb = palette.primary

        desc = r_info.get("desc", "") or r_info.get("text", "")
        if desc:
            r3 = p.add_run(); r3.text = desc; r3.font.size = Pt(22); r3.font.name = font_name; r3.font.color.rgb = palette.text_body


def _render_card_item(paragraph, item: Any, font_name: str, accent_color: RGBColor, palette: PresentationPalette):
    """Render a card item with label, text, and optional highlighted runs (all font >= 22pt)."""
    if isinstance(item, str):
        r = paragraph.add_run()
        r.text = item
        r.font.size = Pt(22)
        r.font.name = font_name
        r.font.color.rgb = palette.text_body
        return

    label = item.get("label", "")
    text = item.get("text", "")
    highlight = item.get("highlight", "")

    if label:
        r_lbl = paragraph.add_run()
        r_lbl.text = label
        r_lbl.font.bold = True
        r_lbl.font.size = Pt(22)
        r_lbl.font.name = font_name
        r_lbl.font.color.rgb = palette.text_title if palette.is_dark_mode else RGBColor(0, 0, 0)

    if highlight and highlight in text:
        parts = text.split(highlight, 1)
        if parts[0]:
            r0 = paragraph.add_run(); r0.text = parts[0]; r0.font.size = Pt(22); r0.font.name = font_name; r0.font.color.rgb = palette.text_body
        rh = paragraph.add_run()
        rh.text = highlight
        rh.font.bold = True
        rh.font.size = Pt(22)
        rh.font.name = font_name
        rh.font.color.rgb = hex_to_rgb(item["highlight_color"]) if "highlight_color" in item else accent_color
        if parts[1]:
            r1 = paragraph.add_run(); r1.text = parts[1]; r1.font.size = Pt(22); r1.font.name = font_name; r1.font.color.rgb = palette.text_body
    else:
        r_txt = paragraph.add_run()
        r_txt.text = text
        r_txt.font.size = Pt(22)
        r_txt.font.name = font_name
        r_txt.font.color.rgb = palette.text_body


def insert_slides(pptx_path: str, after_slide: int, slides_data: List[Dict[str, Any]],
                  output_path: Optional[str] = None, font_name: str = "Segoe UI",
                  theme_override: Optional[str] = None) -> str:
    """
    Insert native editable slides after the given 1-based slide index,
    automatically extracting and matching the color tone of the presentation.
    """
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"PPTX file not found: {pptx_path}")

    target_output = output_path or pptx_path

    # Auto-backup if in-place update
    if target_output == pptx_path:
        bak_path = pptx_path + ".bak"
        if not os.path.exists(bak_path):
            shutil.copy2(pptx_path, bak_path)
            print(f"[Backup] Created backup: {bak_path}")

    prs = Presentation(pptx_path)
    total_slides_before = len(prs.slides)
    slide_w_pt = prs.slide_width / Pt(1)
    slide_h_pt = prs.slide_height / Pt(1)

    # 1. Color Tone Detection across existing slides
    print(f"\n[Color Tone Analysis] Scanning slides in '{os.path.basename(pptx_path)}' around slide {after_slide}...")
    if theme_override:
        palette = _fallback_palette(False, theme_override, theme_override)
        print(f"  -> Using manual theme override: {theme_override}")
    else:
        palette = detect_presentation_palette(prs, after_slide)
        print(f"  -> {palette.summary()}")

    # 2. Insert slides
    insert_idx = max(0, min(after_slide, total_slides_before))
    blank_layout = prs.slide_layouts[6]
    sldIdLst = prs.slides._sldIdLst

    new_slide_elements = []

    for s_idx, s_data in enumerate(slides_data):
        slide = prs.slides.add_slide(blank_layout)
        layout_type = s_data.get("layout", "2_column").lower()

        if layout_type in ["2_column", "2_col", "columns"]:
            build_slide_2_column(slide, s_data, font_name, slide_w_pt, slide_h_pt, palette)
        elif layout_type in ["grid_2x2", "2x2", "grid"]:
            build_slide_grid_2x2(slide, s_data, font_name, slide_w_pt, slide_h_pt, palette)
        elif layout_type in ["stacked_rows", "rows", "stacked"]:
            build_slide_stacked_rows(slide, s_data, font_name, slide_w_pt, slide_h_pt, palette)
        else:
            build_slide_2_column(slide, s_data, font_name, slide_w_pt, slide_h_pt, palette)

        elem = sldIdLst[-1]
        new_slide_elements.append(elem)

    # Reorder slides into position
    for elem in new_slide_elements:
        sldIdLst.remove(elem)

    for i, elem in enumerate(new_slide_elements):
        sldIdLst.insert(insert_idx + i, elem)

    prs.save(target_output)
    print(f"SUCCESS: Inserted {len(slides_data)} editable slide(s) after slide {after_slide}.")
    print(f"Saved to: {target_output}\n")
    return target_output


def main():
    parser = argparse.ArgumentParser(
        description="Insert 100% native editable PowerPoint slides matching existing presentation color tone, font >= 22pt."
    )
    parser.add_argument("pptx", help="Path to input PowerPoint (.pptx) file")
    parser.add_argument("--after-slide", "-a", type=int, required=True,
                        help="1-based slide index after which new slides are inserted (e.g. 10)")
    parser.add_argument("--content", "-c", type=str,
                        help="Path to JSON file containing slides definition")
    parser.add_argument("--json-str", "-j", type=str,
                        help="Direct JSON string containing slides definition")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Destination .pptx path (default: overwrite input in-place with .bak backup)")
    parser.add_argument("--font", "-f", type=str, default="Segoe UI",
                        help="Font family for slides (default: 'Segoe UI')")
    parser.add_argument("--theme-color", type=str, default=None,
                        help="Optional manual hex primary color override (e.g. '#7FBD42' or '#004C7E')")

    args = parser.parse_args()

    slides_data = None
    if args.content:
        with open(args.content, "r", encoding="utf-8") as f:
            slides_data = json.load(f)
    elif args.json_str:
        slides_data = json.loads(args.json_str)
    else:
        if not sys.stdin.isatty():
            slides_data = json.load(sys.stdin)
        else:
            print("Error: Either --content <file.json> or --json-str '<json>' must be provided.")
            sys.exit(1)

    if isinstance(slides_data, dict):
        slides_data = [slides_data]

    insert_slides(
        pptx_path=args.pptx,
        after_slide=args.after_slide,
        slides_data=slides_data,
        output_path=args.output,
        font_name=args.font,
        theme_override=args.theme_color
    )


if __name__ == "__main__":
    main()
