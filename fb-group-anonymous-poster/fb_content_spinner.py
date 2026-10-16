#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Post Content Spinner
Tạo các biến thể nội dung tự nhiên, không trùng lặp cho bài đăng Facebook Groups.
"""

import random
import json
import argparse
from typing import List, Dict

# Ma trận các thành phần câu để ghép thành bài viết tự nhiên
GREETINGS = [
    "Chào các bố mẹ ạ!",
    "Chào cả nhà mình ạ,",
    "Em chào các bố mẹ trong nhóm,",
    "Em chào mọi người ạ,",
    "Chào các mẹ thông thái,",
    "Em chào các anh/chị phụ huynh ạ,",
    "Chào các bậc phụ huynh trong nhóm ạ!",
]

INTRO_STYLES = [
    # Style 1: Tâm tình mẹ lo lắng
    "{greet}\n\nĐợt này vào năm học mới, em thấy 2 bé nhà em ({grade1} và {grade2}) bị đuối {subject} quá. Các con tiếp thu hơi chậm nên trên lớp nhiều bài chưa theo kịp các bạn, để lâu em sợ con bị hổng kiến thức rồi sinh ra chán học.",
    
    # Style 2: Thực tế, thẳng thắn
    "{greet}\n\nEm đang cần tìm lớp học {subject} cho 2 bạn nhà em (1 bạn {grade1}, 1 bạn {grade2}). Tình hình là lực học của 2 con hiện tại hơi yếu, tiếp thu chậm nên cần người giảng kỹ từng bước, không chạy theo tiến độ đại trà.",
    
    # Style 3: Con tự ti/ngợp ở lớp đông
    "{greet}\n\nNhà em có 2 bạn ({grade1} và {grade2}), môn {subject} của các con khá đuối. Tính các bạn lại hơi rụt rè nên đi học các lớp đông học sinh là bị ngợp, không dám hỏi bài thầy cô.",
    
    # Style 4: Ngắn gọn, súc tích
    "{greet}\n\nEm ngoi lên nhờ các bố mẹ tư vấn giúp em với ạ. Nhà em có 2 bé ({grade1} và {grade2}), lực học {subject} hơi yếu nên muốn tìm lớp học thêm để củng cố lại kiến thức căn bản.",
]

REQUIREMENTS = [
    # Option A: Dạy chậm, nhóm nhỏ
    "Em muốn tìm lớp quy mô **nhóm nhỏ (tầm 4–8 bạn)** hoặc thầy/cô kèm sát, dạy chậm, kiên nhẫn với học sinh mất gốc để giúp con lấy lại nền tảng và sự tự tin.",
    
    # Option B: Gạch đầu dòng
    "Mong muốn của em:\n- Lớp nhóm nhỏ ít học sinh để thầy/cô có thời gian chữa bài kỹ cho từng bạn.\n- Thầy/cô dạy nhiệt tình, giảng giải dễ hiểu, kiên nhẫn kéo các bạn học chậm lên.",
    
    # Option C: Kèm sát từng bước
    "Tiêu chí của em là cần thầy cô giảng bài thật kỹ, kiên nhẫn chỉ từng bước một và không đặt nặng áp lực điểm số ngay từ đầu, chỉ cần con hiểu bản chất bài học.",
    
    # Option D: Ghép nhóm
    "Em ưu tiên lớp nhóm nhỏ ít người. Bố mẹ nào quanh khu này có con cùng độ tuổi và học lực muốn **ghép nhóm 3–5 bạn** cùng học thì nhắn em lập nhóm chung luôn nhé ạ!",
]

LOCATIONS = [
    "Em tìm lớp quanh khu vực **{location}** (hoặc bán kính lân cận) để tiện đưa đón các con.",
    "Khu vực ưu tiên: Trục **{location}** hoặc các tuyến đường gần đó ạ.",
    "Em đang tìm quanh mạn **{location}** hoặc lân cận Đống Đa/Hai Bà Trưng cho gần nhà.",
    "Bố mẹ nào biết lớp/thầy cô quanh khu vực **{location}** không ạ?",
]

CALL_TO_ACTIONS = [
    "Bố mẹ nào có con từng học thấy thầy cô nào dạy có tâm và tiến bộ thì chia sẻ hoặc cho em xin contact với ạ! Em cảm ơn cả nhà nhiều!",
    "Bố mẹ nào trong nhóm có kinh nghiệm hoặc đang cho con theo học lớp ổn áp quanh khu này thì giới thiệu giúp em với ạ. Em xin cảm ơn!",
    "Rất mong nhận được chia sẻ thực tế từ các phụ huynh đã có con theo học. Em xin chân thành cảm ơn cả nhà ạ!",
    "Mẹ nào biết địa chỉ nào uy tín chỉ giúp em với nha. Em cảm ơn các bố mẹ nhiều ạ!",
]

PS_NOTES = [
    "\n\n*(Em xin phép chỉ xin review thực tế từ các phụ huynh, các bên trung tâm vui lòng không spam ạ)*",
    "\n\n*(Em xin review thật từ các bố mẹ ạ, trung tâm quảng cáo xin đừng spam bài em nhé)*",
    "",
    "\n\n*(Em cảm ơn và chúc các bé luôn học tốt ạ!)*",
]


def generate_spin_post(
    subject: str = "Toán",
    grade1: str = "lớp 8",
    grade2: str = "lớp 10",
    location: str = "Xã Đàn, Giải Phóng",
    style_index: int = None,
    include_ps: bool = True
) -> str:
    """Sinh ra 1 bài viết ngẫu nhiên theo ma trận nội dung."""
    greet = random.choice(GREETINGS)
    intro_template = INTRO_STYLES[style_index % len(INTRO_STYLES)] if style_index is not None else random.choice(INTRO_STYLES)
    intro = intro_template.format(
        greet=greet,
        subject=subject,
        grade1=grade1,
        grade2=grade2
    )
    
    req = random.choice(REQUIREMENTS)
    loc_template = random.choice(LOCATIONS)
    loc = loc_template.format(location=location)
    cta = random.choice(CALL_TO_ACTIONS)
    ps = random.choice(PS_NOTES) if include_ps else ""
    
    parts = [intro, req, loc, cta]
    full_post = "\n\n".join(parts) + ps
    return full_post


def generate_variants(
    count: int = 5,
    subject: str = "Toán",
    grade1: str = "lớp 8",
    grade2: str = "lớp 10",
    location: str = "Xã Đàn, Giải Phóng"
) -> List[Dict[str, str]]:
    """Sinh N bài viết biến thể khác nhau, đảm bảo tính đa dạng."""
    variants = []
    used_hashes = set()
    
    for i in range(count):
        for _ in range(50): # thử tối đa 50 lần để không trùng
            post = generate_spin_post(
                subject=subject,
                grade1=grade1,
                grade2=grade2,
                location=location,
                style_index=i
            )
            h = hash(post)
            if h not in used_hashes:
                used_hashes.add(h)
                variants.append({
                    "id": i + 1,
                    "title": f"Biến thể {i + 1}",
                    "content": post
                })
                break
                
    return variants


def main():
    parser = argparse.ArgumentParser(description="Sinh nội dung bài đăng Facebook Groups tự nhiên, đa dạng")
    parser.add_argument("--count", type=int, default=5, help="Số lượng bài viết biến thể cần sinh")
    parser.add_argument("--subject", type=str, default="Toán", help="Môn học (ví dụ: Toán, Tiếng Anh, Văn)")
    parser.add_argument("--grade1", type=str, default="lớp 8", help="Lớp bé thứ nhất (ví dụ: lớp 8)")
    parser.add_argument("--grade2", type=str, default="lớp 10", help="Lớp bé thứ hai (ví dụ: lớp 10)")
    parser.add_argument("--location", type=str, default="Xã Đàn, Giải Phóng", help="Khu vực tìm kiếm")
    parser.add_argument("--export-json", type=str, default=None, help="Đường dẫn file JSON để lưu kết quả")
    
    args = parser.parse_args()
    
    variants = generate_variants(
        count=args.count,
        subject=args.subject,
        grade1=args.grade1,
        grade2=args.grade2,
        location=args.location
    )
    
    if args.export_json:
        with open(args.export_json, "w", encoding="utf-8") as f:
            json.dump(variants, f, ensure_ascii=False, indent=2)
        print(f"[+] Đã xuất {len(variants)} biến thể ra file: {args.export_json}")
    else:
        print(f"=== TỔNG HỢP {len(variants)} BIẾN THỂ BÀI ĐĂNG TỰ NHIÊN ===")
        for v in variants:
            print(f"\n------------------- {v['title']} -------------------")
            print(v['content'])
            print("-------------------------------------------------------")


if __name__ == "__main__":
    main()
