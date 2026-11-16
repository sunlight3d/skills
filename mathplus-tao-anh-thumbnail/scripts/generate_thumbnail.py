#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MathPlus YouTube Thumbnail Generator
Style: MathPlus Signature Emerald & Gold (Chuẩn Nhận Diện Thương Hiệu MathPlus Academy)
Resolution: 1280x720 (16:9, High CTR YouTube Standard)
"""

import os
import sys
import argparse
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import numpy as np

W, H = 1280, 720
FONT_BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT_REGULAR = '/System/Library/Fonts/Supplemental/Arial.ttf'

SKILL_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = SKILL_DIR / 'resources'
DEFAULT_TEACHER = RESOURCES_DIR / 'thay_hoang_master.png'


def draw_bullet(draw, cx, cy, r, color):
    """Vẽ chấm tròn bullet sắc nét"""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def draw_star(draw, cx, cy, r_outer, r_inner, color):
    """Vẽ ngôi sao 5 cánh vector rực rỡ"""
    points = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        angle = i * np.pi / 5 - np.pi / 2
        x = cx + r * np.cos(angle)
        y = cy + r * np.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=color)


def prepare_teacher_portrait(img_path):
    """
    Chuẩn bị ảnh chân dung thầy giáo:
    - Nếu là ảnh chưa xóa phông (.heic, .jpg), gọi Apple Vision để tách nền chuẩn xác
    - Căn chỉnh tỷ lệ đầu, cổ, vai hoàn hảo trong khung tròn 530x530
    """
    if not os.path.exists(img_path):
        if os.path.exists(DEFAULT_TEACHER):
            img_path = str(DEFAULT_TEACHER)
        else:
            raise FileNotFoundError(f"Không tìm thấy ảnh chân dung: {img_path}")

    src = Image.open(img_path)
    src = ImageOps.exif_transpose(src).convert('RGBA')

    # Nếu ảnh chưa có kênh alpha trong suốt
    alpha = np.array(src.split()[-1])
    is_transparent = np.any(alpha < 250)

    if not is_transparent:
        print("Ảnh gốc chưa tách nền, đang bóc tách tự động bằng Apple Vision...")
        import subprocess
        mask_tmp = f"/tmp/mask_{os.getpid()}.png"
        script_path = str(SKILL_DIR / 'scripts' / 'cutout_person.swift')
        cmd = ['swift', script_path, str(img_path), mask_tmp]
        subprocess.run(cmd, check=True)
        
        real_mask_path = mask_tmp + ".mask.png"
        if os.path.exists(real_mask_path):
            mask_im = Image.open(real_mask_path).convert('L')
            src.putalpha(mask_im)
            if os.path.exists(real_mask_path):
                os.remove(real_mask_path)

    # Nâng nhẹ độ sáng và tương phản tự nhiên (giữ 100% texture da thật)
    enh = ImageEnhance.Brightness(src).enhance(1.06)
    enh = ImageEnhance.Contrast(enh).enhance(1.05)

    # Tìm khung người chính xác
    alpha_arr = np.array(enh.split()[-1])
    coords = np.argwhere(alpha_arr > 30)
    if len(coords) > 0:
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
    else:
        y_min, x_min, y_max, x_max = 0, 0, enh.height, enh.width

    center_x = (x_min + x_max) // 2
    head_w = x_max - x_min
    box_side = int(head_w * 1.15)
    top_y = max(0, y_min - int(box_side * 0.08))

    crop_box = (
        max(0, center_x - box_side // 2),
        top_y,
        min(enh.width, center_x + box_side // 2),
        min(enh.height, top_y + box_side)
    )
    cropped = enh.crop(crop_box)
    if cropped.width != cropped.height:
        sq = Image.new('RGBA', (box_side, box_side), (0, 0, 0, 0))
        sq.paste(cropped, ((box_side - cropped.width) // 2, (box_side - cropped.height)))
        cropped = sq

    t_circle_size = 530
    t_resized = cropped.resize((t_circle_size, t_circle_size), Image.Resampling.LANCZOS)

    mask = Image.new('L', (t_circle_size, t_circle_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((6, 6, t_circle_size - 6, t_circle_size - 6), fill=255)

    return Image.composite(t_resized, Image.new('RGBA', (t_circle_size, t_circle_size), (0, 0, 0, 0)), mask), t_circle_size


def split_title_smart(title_str):
    """Tự động phân tách tiêu đề thành 2 dòng: Dòng 1 (Trắng) và Dòng 2 (Vàng)"""
    title_str = title_str.strip()
    words = title_str.split()
    if len(words) <= 2:
        return words[0].upper(), (words[1].upper() if len(words) > 1 else "")

    # Mẫu chuyên đề phổ biến
    lower = title_str.lower()
    if "giới hạn" in lower and "dãy số" in lower:
        return "GIỚI HẠN", "DÃY SỐ"
    if "giới hạn" in lower and "hàm số" in lower:
        return "GIỚI HẠN", "HÀM SỐ"
    if "hàm số" in lower and "liên tục" in lower:
        return "HÀM SỐ", "LIÊN TỤC"
    if "khảo sát" in lower:
        return "KHẢO SÁT", " ".join(words[2:]).upper() if len(words) > 2 else "HÀM SỐ"
    if "nguyên hàm" in lower:
        return "NGUYÊN HÀM", "TÍCH PHÂN"
    if "tích phân" in lower:
        return "TÍCH PHÂN", "ỨNG DỤNG"
    if "hình học" in lower:
        return "HÌNH HỌC", "KHÔNG GIAN"
    if "khoảng cách" in lower:
        return "KHOẢNG CÁCH", "TRONG KHÔNG GIAN"
    if "góc" in lower and "không gian" in lower:
        return "GÓC TRONG", "KHÔNG GIAN"

    # Chia đôi cân bằng
    mid = len(words) // 2
    return " ".join(words[:mid]).upper(), " ".join(words[mid:]).upper()


def build_thumbnail(
    curriculum="TOÁN 11 - KẾT NỐI TRI THỨC",
    subtitle="BÀI 15: CHUYÊN ĐỀ",
    title_l1="GIỚI HẠN",
    title_l2="DÃY SỐ",
    bullets=None,
    hook="NẮM TRỌN ĐIỂM 9 - 10",
    slogan="Bám sát cấu trúc đề thi mới nhất • Tự tin giành điểm tối đa!",
    teacher_badge="THẦY HOÀNG • MATHPLUS",
    teacher_img=None,
    output_path="thumbnail.png"
):
    """Sinh ảnh thumbnail chuẩn phong cách MathPlus Emerald & Gold"""
    if bullets is None:
        bullets = [
            "3 Dạng Vô Định Trọng Tâm (∞ - ∞,  ∞ / ∞)",
            "Tuyệt Kỹ Nhân Liên Hợp Căn Bậc 2, Bậc 3",
            "Kỹ Thuật Bấm Máy Casio & Tự Luận Điểm 10"
        ]

    # 1. NỀN GRADIENT XANH LỤC BẢO ĐẬM (MATHPLUS EMERALD)
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    for y in range(H):
        ty = y / H
        for x in range(W):
            tx = x / W
            r = int(5 * (1 - tx) + 12 * tx)
            g = int(24 * (1 - tx) + 48 * tx + 14 * (1 - ty))
            b = int(12 * (1 - tx) + 24 * tx)
            arr[y, x] = [r, g, b, 255]

    base = Image.fromarray(arr, 'RGBA')
    draw = ImageDraw.Draw(base)

    # 2. LƯỚI TỌA ĐỘ TOÁN HỌC (CYBER MATH GRID)
    for x in range(0, W, 45):
        draw.line([(x, 0), (x, H)], fill=(0, 230, 118, 14), width=1)
    for y in range(0, H, 45):
        draw.line([(0, y), (W, y)], fill=(0, 230, 118, 14), width=1)

    # 3. HÀO QUANG DẠ QUANG PHÍA SAU THẦY GIÁO (RADIAL GLOW)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([720, 30, 1320, 670], fill=(0, 200, 83, 85))
    glow_draw.ellipse([790, 90, 1260, 610], fill=(255, 214, 0, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(65))
    base = Image.alpha_composite(base, glow)
    draw = ImageDraw.Draw(base)

    # 4. CHÂN DUNG THẦY HOÀNG VỚI VIỀN HÀO QUANG KÉP
    teacher_path = teacher_img or str(DEFAULT_TEACHER)
    t_framed, t_size = prepare_teacher_portrait(teacher_path)

    tx_pos = 715
    ty_pos = 65

    # Viền ngoài phát sáng: Vàng kim
    for r_off in range(16, 0, -2):
        alpha = int(15 + (16 - r_off) * 14)
        draw.ellipse([tx_pos - r_off, ty_pos - r_off, tx_pos + t_size + r_off, ty_pos + t_size + r_off],
                     outline=(255, 214, 0, alpha), width=2)
    # Viền trong sắc nét: Xanh lục bảo
    for r_off in range(6, 0, -1):
        alpha = int(70 + (6 - r_off) * 30)
        draw.ellipse([tx_pos - r_off, ty_pos - r_off, tx_pos + t_size + r_off, ty_pos + t_size + r_off],
                     outline=(0, 230, 118, alpha), width=2)

    base.paste(t_framed, (tx_pos, ty_pos), t_framed)

    # 5. HUY HIỆU TÊN THẦY (TEACHER BRAND BADGE)
    f_badge = ImageFont.truetype(FONT_BOLD, 24)
    nb_w, nb_h = 360, 48
    nb_x = tx_pos + (t_size - nb_w) // 2 - 10
    nb_y = ty_pos + t_size - 42
    draw.rounded_rectangle([nb_x + 4, nb_y + 4, nb_x + nb_w + 4, nb_y + nb_h + 4], radius=12, fill=(0, 0, 0, 200))
    draw.rounded_rectangle([nb_x, nb_y, nb_x + nb_w, nb_y + nb_h], radius=12, fill=(27, 94, 32, 245), outline=(255, 214, 0, 255), width=2)
    
    text_bbox = draw.textbbox((0, 0), teacher_badge, font=f_badge)
    text_w = text_bbox[2] - text_bbox[0]
    badge_tx = nb_x + (nb_w - text_w) // 2
    draw.text((badge_tx, nb_y + 10), teacher_badge, font=f_badge, fill=(255, 255, 255, 255))

    # 6. CỘT THÔNG TIN BÊN TRÁI (HIGH CTR STACK)
    # Tag 1: Bộ Sách & Lớp (Curriculum Tag - Red Pill)
    f_top = ImageFont.truetype(FONT_BOLD, 24)
    top_bbox = draw.textbbox((0, 0), curriculum, font=f_top)
    pill_w = max(420, (top_bbox[2] - top_bbox[0]) + 40)
    draw.rounded_rectangle([52, 42, 52 + pill_w, 90], radius=8, fill=(0, 0, 0, 180))
    draw.rounded_rectangle([50, 40, 50 + pill_w, 88], radius=8, fill=(211, 47, 47, 245), outline=(255, 205, 210, 255), width=2)
    draw.text((70, 51), curriculum, font=f_top, fill=(255, 255, 255, 255))

    # Tag 2: Tên Bài / Chuyên đề (Subtitle)
    f_sub = ImageFont.truetype(FONT_BOLD, 40)
    draw.text((54, 116), subtitle, font=f_sub, fill=(0, 0, 0, 240))
    draw.text((50, 112), subtitle, font=f_sub, fill=(224, 242, 241, 255))

    # Tag 3: TIÊU ĐỀ LỚN KHỔNG LỒ (Massive 2-Line Title)
    f_title = ImageFont.truetype(FONT_BOLD, 78)
    draw.text((56, 178), title_l1, font=f_title, fill=(0, 0, 0, 255))
    draw.text((50, 172), title_l1, font=f_title, fill=(255, 255, 255, 255))

    draw.text((56, 268), title_l2, font=f_title, fill=(0, 0, 0, 255))
    draw.text((50, 262), title_l2, font=f_title, fill=(255, 214, 0, 255))

    # Tag 4: HỘP TRỌNG TÂM DẠNG BÀI (Feature Card Glassmorphism)
    f_feat = ImageFont.truetype(FONT_BOLD, 26)
    box_x, box_y, box_w, box_h = 50, 365, 650, 142
    feat_bg = Image.new('RGBA', (box_w, box_h), (8, 36, 20, 210))
    base.paste(feat_bg, (box_x, box_y), feat_bg)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=10, outline=(0, 230, 118, 180), width=2)

    bullet_colors = [
        ((0, 230, 118, 255), (255, 255, 255, 255)),
        ((255, 214, 0, 255), (255, 238, 88, 255)),
        ((129, 199, 132, 255), (224, 242, 241, 255))
    ]

    for i, b_text in enumerate(bullets[:3]):
        dot_col, text_col = bullet_colors[i]
        item_y = box_y + 15 + i * 42
        draw_bullet(draw, box_x + 28, item_y + 13, 6, dot_col)
        draw.text((box_x + 46, item_y), b_text, font=f_feat, fill=text_col)

    # Tag 5: NÚT KÊU GỌI HÀNH ĐỘNG CAM RỰC RỠ (Hook Button)
    f_hook = ImageFont.truetype(FONT_BOLD, 36)
    hook_bbox = draw.textbbox((0, 0), hook, font=f_hook)
    hook_w = max(520, (hook_bbox[2] - hook_bbox[0]) + 110)
    
    draw.rounded_rectangle([53, 533, 53 + hook_w, 618], radius=12, fill=(0, 0, 0, 200))
    draw.rounded_rectangle([50, 530, 50 + hook_w, 615], radius=12, fill=(255, 111, 0, 245), outline=(255, 224, 130, 255), width=3)
    draw_star(draw, 85, 572, 16, 7, (255, 255, 255, 255))
    draw.text((115, 549), hook, font=f_hook, fill=(255, 255, 255, 255))

    # Tag 6: SLOGAN CHÂN TRANG
    f_bot = ImageFont.truetype(FONT_BOLD, 22)
    draw.text((52, 648), slogan, font=f_bot, fill=(200, 230, 201, 230))

    # 7. XUẤT FILE CHUẨN ĐỊNH DẠNG YOUTUBE
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    base.convert('RGB').save(output_path, quality=95)
    print(f"SUCCESS: Thumbnail đã được tạo thành công tại: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Tạo ảnh Thumbnail YouTube chuẩn MathPlus Emerald & Gold")
    parser.add_argument('--curriculum', default="TOÁN 11 - KẾT NỐI TRI THỨC", help="Tên bộ sách và lớp (vd: TOÁN 11 - KẾT NỐI TRI THỨC)")
    parser.add_argument('--subtitle', default="BÀI 15: CHUYÊN ĐỀ", help="Tên bài học hoặc chuyên đề (vd: BÀI 15: CHUYÊN ĐỀ)")
    parser.add_argument('--title', help="Tiêu đề bài học đầy đủ (vd: 'Giới Hạn Dãy Số')")
    parser.add_argument('--title-l1', help="Tiêu đề Dòng 1 - Chữ trắng (vd: GIỚI HẠN)")
    parser.add_argument('--title-l2', help="Tiêu đề Dòng 2 - Chữ vàng (vd: DÃY SỐ)")
    parser.add_argument('--bullets', help="3 ý trọng tâm phân tách bằng dấu gạch đứng '|'")
    parser.add_argument('--hook', default="NẮM TRỌN ĐIỂM 9 - 10", help="Nội dung nút cam (vd: NẮM TRỌN ĐIỂM 9 - 10)")
    parser.add_argument('--slogan', default="Bám sát cấu trúc đề thi mới nhất • Tự tin giành điểm tối đa!", help="Slogan chân trang")
    parser.add_argument('--teacher-badge', default="THẦY HOÀNG • MATHPLUS", help="Nhãn tên thầy giáo")
    parser.add_argument('--teacher-img', help="Đường dẫn file ảnh chân dung")
    parser.add_argument('--output', default="thumbnail_mathplus.png", help="Đường dẫn lưu file ảnh xuất ra")
    parser.add_argument('--video-folder', help="Thư mục video (tự động đọc youtube_metadata.txt nếu có)")

    args = parser.parse_args()

    # Nếu truyền --video-folder, thử tự động đọc thông tin từ file metadata hoặc video
    if args.video_folder and os.path.isdir(args.video_folder):
        vdir = Path(args.video_folder)
        meta_files = list(vdir.glob("*metadata*.txt"))
        if meta_files:
            content = meta_files[0].read_text(encoding='utf-8')
            for line in content.splitlines():
                if line.startswith("Tiêu đề video:") or line.startswith("Tiêu đề:"):
                    raw_title = line.split(":", 1)[1].strip()
                    if not args.title and not args.title_l1:
                        if "Bài" in raw_title:
                            parts = raw_title.split("Bài")
                            sub_part = "BÀI " + parts[1].split(":")[0].strip() + ": CHUYÊN ĐỀ"
                            args.subtitle = sub_part
                            if ":" in parts[1]:
                                main_t = parts[1].split(":")[1].split("|")[0].strip()
                                args.title = main_t
        if args.output == "thumbnail_mathplus.png":
            args.output = str(vdir / "thumbnail_mathplus.png")

    # Xử lý tiêu đề
    if args.title and (not args.title_l1 or not args.title_l2):
        l1, l2 = split_title_smart(args.title)
        args.title_l1 = args.title_l1 or l1
        args.title_l2 = args.title_l2 or l2

    l1 = args.title_l1 or "GIỚI HẠN"
    l2 = args.title_l2 or "DÃY SỐ"

    bullet_list = None
    if args.bullets:
        bullet_list = [b.strip() for b in args.bullets.split('|') if b.strip()]

    build_thumbnail(
        curriculum=args.curriculum,
        subtitle=args.subtitle,
        title_l1=l1,
        title_l2=l2,
        bullets=bullet_list,
        hook=args.hook,
        slogan=args.slogan,
        teacher_badge=args.teacher_badge,
        teacher_img=args.teacher_img,
        output_path=args.output
    )


if __name__ == '__main__':
    main()
