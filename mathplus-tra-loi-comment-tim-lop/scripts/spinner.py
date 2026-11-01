#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MathPlus Trả Lời Comment Tìm Lớp - Comment Spinner
Sinh lời bình luận thiên biến vạn hoá giới thiệu Thầy Dũng Toán (0977961189).
Đảm bảo 100% văn phong đời thường tự nhiên, số điện thoại nguyên bản dễ copy/gọi, KHÔNG markdown.
"""

import random
import re
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PHONE_VARIANTS = [
    "0977961189 (Zalo)",
    "0977961189 (Zalo thầy Dũng)",
    "0977961189",
    "0977961189 ạ",
    "0977961189 (có Zalo)",
]

# Các mẫu câu mở đầu / xưng hô
GREETINGS = [
    "Bạn",
    "Mẹ",
    "Mom",
    "Bác",
    "Chị",
    "Bố mẹ",
    "Nhà mình",
]

# Các mẫu câu hoàn chỉnh đa dạng góc nhìn
COMMENT_TEMPLATES = [
    # Mẫu 1: Trực tiếp, súc tích chuẩn prompt
    "{greet} thử hỏi thầy Dũng Toán nhé, thầy hay dạy ở Xã Đàn, Hồ Đắc Di. Lớp nhóm nhỏ kèm sát từng bạn dạy rất có tâm. Số đt của thầy: {phone}",

    # Mẫu 2: Phụ huynh có con từng học chia sẻ
    "Bé nhà mình trước cũng học lớp Toán thầy Dũng ở mạn Hồ Đắc Di, Xã Đàn. Thầy giảng kỹ từng bước và sát sao bài vở lắm. {greet} thử liên hệ thầy xem sao nhé: {phone}",

    # Mẫu 3: Dành cho học sinh mất gốc / học chậm
    "Nếu con đang bị hổng kiến thức thì {greet} thử nhắn thầy Dũng Toán xem ạ. Thầy chuyên dạy khu Xã Đàn, Hồ Đắc Di, kiên nhẫn giảng kỹ bản chất giúp con lấy lại gốc nhanh. Số Zalo thầy: {phone}",

    # Mẫu 4: Giới thiệu địa bàn Đống Đa / Hồ Đắc Di
    "Quanh khu Xã Đàn - Hồ Đắc Di thì {greet} thử tham khảo lớp thầy Dũng Toán xem sao. Thầy dạy nhiệt tình, có tâm và phương pháp dễ hiểu lắm. Sđt liên hệ thầy: {phone}",

    # Mẫu 5: Ôn thi / rèn nền tảng
    "{greet} thử tham khảo lớp thầy Dũng Toán ở Hồ Đắc Di, Xã Đàn nhé. Thầy kèm nhóm nhỏ chắc kiến thức và rèn phương pháp làm bài bản lắm. Số Zalo thầy Dũng: {phone}",

    # Mẫu 6: Nhóm nhỏ kèm sát
    "{greet} thử hỏi thầy Dũng Toán xem thầy còn slot không nhé. Thầy chuyên dạy Toán ở khu Xã Đàn, Hồ Đắc Di, nhóm ít bạn nên con không bị ngợp. Số điện thoại thầy: {phone}",

    # Mẫu 7: Tự nhiên, ngắn gọn
    "{greet} nhắn hỏi thầy Dũng Toán ở mạn Hồ Đắc Di hoặc Xã Đàn xem nhé, thầy dạy dễ hiểu và nhiệt tình. Số đt Zalo: {phone}",

    # Mẫu 8: Giúp con tiến bộ
    "Con nhà mình đợt trước cũng đuối toán, sau theo học thầy Dũng ở Hồ Đắc Di thấy tiến bộ và tự tin hẳn. {greet} thử alo hoặc nhắn Zalo thầy xem nhé: {phone}",

    # Mẫu 9: Thầy kèm kiên nhẫn
    "{greet} thử liên hệ thầy Dũng Toán nhé, thầy hay dạy lớp ở Xã Đàn, Hồ Đắc Di. Thầy kiên nhẫn chỉ từng bước cho học sinh lắm. Sđt: {phone}",

    # Mẫu 10: Lời khuyên chân thành
    "Khu Đống Đa mạn Xã Đàn, Hồ Đắc Di thì {greet} cứ nhắn thầy Dũng Toán nhé, thầy dạy có tâm và sát sao học sinh lắm ạ. Số Zalo của thầy: {phone}",
]


def strip_all_markdown(text: str) -> str:
    """Loại bỏ triệt để mọi dấu vết markdown."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = text.replace("**", "").replace("*", "")
    text = re.sub(r"__(.*?)__", r"\1", text)
    return text.strip()


def generate_comment(template_idx: int = None) -> str:
    """Sinh ra 1 lời bình luận tự nhiên, số điện thoại chuẩn copy."""
    greet = random.choice(GREETINGS)
    phone = random.choice(PHONE_VARIANTS)
    tmpl = COMMENT_TEMPLATES[template_idx % len(COMMENT_TEMPLATES)] if template_idx is not None else random.choice(COMMENT_TEMPLATES)
    raw = tmpl.format(greet=greet, phone=phone)
    return strip_all_markdown(raw)


def generate_comment_variants(count: int = 5) -> list[str]:
    """Sinh ra N lời bình luận khác nhau hoàn toàn."""
    comments = []
    shuffled_indices = list(range(len(COMMENT_TEMPLATES)))
    random.shuffle(shuffled_indices)
    
    for i in range(count):
        idx = shuffled_indices[i % len(shuffled_indices)]
        comment = generate_comment(template_idx=idx)
        comments.append(comment)
    return comments


if __name__ == "__main__":
    variants = generate_comment_variants(5)
    for i, c in enumerate(variants, 1):
        print(f"[{i}] {c}")
        assert "0977961189" in c, "Thiếu số điện thoại chuẩn!"
        assert "**" not in c, "Vẫn dính ký tự **!"
        print("-" * 50)
    print("XÁC NHẬN: 100% bình luận tự nhiên, số đt chuẩn dễ copy, không markdown.")
