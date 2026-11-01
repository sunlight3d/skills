#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MathPlus Seeding - Content Spinner
Sinh biến thể bài viết 100% tự nhiên bằng văn phong đời thường của phụ huynh trên Facebook.
TUYỆT ĐỐI KHÔNG dùng định dạng Markdown (**in đậm**, *nghiêng*, dấu sao) để tránh lộ dấu vết AI.
"""

import random
import re
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from typing import List, Optional

GREETINGS = [
    "Chào các mẹ ạ,",
    "Em chào cả nhà mình ạ,",
    "Chào các bậc phụ huynh trong nhóm ạ,",
    "Các mẹ thông thái ơi,",
    "Em chào các bố mẹ ạ,",
    "Chào các mom trong nhóm ạ,",
    "Em chào các anh chị phụ huynh ạ,",
]

OPENINGS = [
    # Mẫu 1: Con lên cấp 3 ngợp kiến thức, đuối môn Toán
    "{greet}\n\nĐợt này vào năm học mới, em thấy 2 bạn nhà em (1 bạn học lớp 10, 1 bạn học lớp 11) bắt đầu có dấu hiệu đuối môn Toán quá. Lên cấp 3 lượng kiến thức nặng và trừu tượng hơn hẳn cấp 2 nên các con hơi ngợp, học trên lớp nhiều chỗ chưa kịp hiểu sâu mà bài tập về nhà dồn dập.",

    # Mẫu 2: Tâm lý con sợ học Toán, điểm kiểm tra giảm
    "{greet}\n\nEm ngoi lên nhờ các mẹ tư vấn giúp em với ạ. Nhà em có 2 bạn học lớp 10 và lớp 11, lực học môn Toán của các con chỉ ở mức trung bình khá thôi. Đợt này làm bài kiểm tra điểm số không được như ý nên con bắt đầu có tâm lý sợ học Toán và thiếu tự tin.",

    # Mẫu 3: Bạn lớp 10 mới chuyển cấp, bạn lớp 11 chuẩn bị thi
    "{greet}\n\nCác mẹ ơi em cần tìm lớp Toán 10 và 11 cho các bạn nhà mình ạ. Bạn lớp 10 thì mới chuyển cấp còn bỡ ngỡ với cách học THPT, còn bạn lớp 11 thì năm sau thi tốt nghiệp rồi nên em muốn tìm thầy cô rèn giũa, củng cố nền tảng sớm.",

    # Mẫu 4: Con rụt rè, không hợp lớp đông lò luyện
    "{greet}\n\nEm đang đau đầu tìm lớp học thêm Toán cho 2 bạn nhà em (lớp 10 và lớp 11). Tính các con nhà em hơi rụt rè, đi học mấy lớp lò đông 30 - 40 bạn là bị ngợp, không dám giơ tay hỏi bài thầy cô bao giờ, chỗ nào chưa hiểu là cứ để trôi đi.",

    # Mẫu 5: Tiếp thu hơi chậm, cần giảng chắc bản chất
    "{greet}\n\nNhà em có 2 bạn học lớp 10 và lớp 11, sức học môn Toán tiếp thu hơi chậm một chút nên em không dám cho theo các lớp đại trà chạy nhanh theo tiến độ. Em muốn tìm nơi dạy chắc căn bản trước.",
]

REQUIREMENTS = [
    # Nhóm nhỏ 5-8 bạn (văn phong đời thường)
    "Em muốn tìm lớp quy mô nhóm nhỏ khoảng 5 đến 8 bạn hoặc thầy cô dạy có tâm, kiên nhẫn giảng kỹ từng bước, chữa bài chi tiết để giúp các con hiểu bản chất bài toán và lấy lại tự tin.",

    # Tiêu chí ngắn gọn tự nhiên
    "Tiêu chí của em là lớp nhóm nhỏ vừa phải để giáo viên sát sao được từng học sinh. Thầy cô dạy nhiệt tình, phương pháp dễ hiểu, không tạo áp lực điểm số dồn dập ngay từ đầu mà kéo dần các bạn lên.",

    # Chữa bài kỹ, không áp lực
    "Em ưu tiên thầy cô kèm sát, giảng chậm chắc, giải thích cặn kẽ và có định hướng làm bài bản từ trắc nghiệm đến tự luận, chấm chữa bài cẩn thận cho từng bạn.",

    # Ngỏ ý ghép nhóm chung
    "Em muốn tìm lớp nhóm nhỏ ít bạn để thầy cô theo sát. Bố mẹ nào quanh khu này có con học lớp 10 hoặc 11 muốn ghép nhóm cùng học tầm 3 đến 5 bạn thì nhắn em lập nhóm chung luôn nhé ạ!",
]

LOCATIONS = [
    "Nhà em ở khu vực Đống Đa, ưu tiên tìm lớp mạn Phạm Ngọc Thạch, Kim Liên hoặc Xã Đàn cho tiện các con tự đi lại hoặc tiện đưa đón.",

    "Em đang tìm lớp quanh trục Phạm Ngọc Thạch, Chùa Bộc hoặc khu vực quận Đống Đa để các bạn tự đạp xe đi học được cho gần.",

    "Khu vực ưu tiên: Quanh Phạm Ngọc Thạch hoặc các tuyến đường lân cận quận Đống Đa ạ.",

    "Bố mẹ nào biết lớp hoặc thầy cô dạy tốt quanh khu Đống Đa, Phạm Ngọc Thạch chỉ giúp em với ạ.",
]

CLOSINGS = [
    "Mẹ nào có con từng học thấy thầy cô nào dạy có tâm, phương pháp hay và con tiến bộ thì cho em xin thông tin hoặc review với ạ. Em xin cảm ơn cả nhà nhiều!",

    "Bố mẹ nào trong nhóm có kinh nghiệm chia sẻ giúp em với nha. Em xin chân thành cảm ơn các mẹ ạ!",

    "Rất mong nhận được lời khuyên và chia sẻ thực tế từ các phụ huynh đi trước. Em cảm ơn cả nhà nhiều ạ!",

    "Mẹ nào biết lớp uy tín chỉ giúp em với nhé. Em chúc các con luôn học tốt ạ!",
]

PS_NOTES = [
    "\n\nP/s: Em xin review thực tế từ phụ huynh ạ, các bên trung tâm vui lòng không spam bài em nhé.",
    "\n\nP/s: Em chỉ xin kinh nghiệm thật từ các bố mẹ thôi ạ, em cảm ơn.",
    "",
    "\n\nEm xin cảm ơn các bố mẹ nhiều ạ!",
]


def strip_all_markdown(text: str) -> str:
    """Loại bỏ triệt để mọi ký tự markdown hoặc ký tự lạ để văn bản 100% tự nhiên."""
    # Bỏ **in đậm** và *nghiêng*
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = text.replace("**", "").replace("*", "")
    text = re.sub(r"__(.*?)__", r"\1", text)
    return text.strip()


def generate_post(
    greeting_idx: Optional[int] = None,
    opening_idx: Optional[int] = None,
    req_idx: Optional[int] = None,
    loc_idx: Optional[int] = None,
    closing_idx: Optional[int] = None,
    include_ps: bool = True
) -> str:
    """Tạo 1 bài đăng ngẫu nhiên với nội dung hoàn toàn tự nhiên không markdown."""
    greet = GREETINGS[greeting_idx % len(GREETINGS)] if greeting_idx is not None else random.choice(GREETINGS)
    opening_tmpl = OPENINGS[opening_idx % len(OPENINGS)] if opening_idx is not None else random.choice(OPENINGS)
    opening = opening_tmpl.format(greet=greet)

    req = REQUIREMENTS[req_idx % len(REQUIREMENTS)] if req_idx is not None else random.choice(REQUIREMENTS)
    loc = LOCATIONS[loc_idx % len(LOCATIONS)] if loc_idx is not None else random.choice(LOCATIONS)
    closing = CLOSINGS[closing_idx % len(CLOSINGS)] if closing_idx is not None else random.choice(CLOSINGS)
    ps = random.choice(PS_NOTES) if include_ps else ""

    raw_post = f"{opening}\n\n{req}\n\n{loc}\n\n{closing}{ps}"
    return strip_all_markdown(raw_post)


def generate_variants(count: int = 2) -> List[str]:
    """Sinh ra N biến thể bài đăng không trùng lặp và không có ký tự markdown."""
    posts = []
    used_openings = set()

    for i in range(count):
        avail_openings = [idx for idx in range(len(OPENINGS)) if idx not in used_openings]
        op_idx = random.choice(avail_openings) if avail_openings else i % len(OPENINGS)
        used_openings.add(op_idx)

        post = generate_post(
            opening_idx=op_idx,
            req_idx=i % len(REQUIREMENTS),
            loc_idx=i % len(LOCATIONS),
            closing_idx=i % len(CLOSINGS)
        )
        posts.append(post)
    return posts


if __name__ == "__main__":
    variants = generate_variants(2)
    for idx, v in enumerate(variants, 1):
        print(f"=== BIẾN THỂ {idx} ===")
        print(v)
        assert "**" not in v, "Vẫn còn dấu ** trong bài viết!"
        assert "*" not in v, "Vẫn còn dấu * trong bài viết!"
        print("-" * 50)
    print("XÁC NHẬN: 100% không còn dấu ** hay ký tự Markdown nào!")
