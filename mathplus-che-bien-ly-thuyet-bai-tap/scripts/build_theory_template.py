#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
TEMPLATE BIÊN SOẠN BÀI GIẢNG LÝ THUYẾT CHUYÊN SÂU MATHPLUS:
- 100% Công thức chuẩn khung SGK
- Giải mã từ viết tắt, thuật ngữ tiếng Anh
- Ví dụ đổi 100% số liệu & nghiệp vụ thực tế
- Tích hợp hình vẽ minh họa 300 DPI
- 100% công thức OMML Math, không xuất PDF
"""

import os
import sys

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

from mathplus_docx_engine import (
    MathPlusDocxBuilder,
    add_heading_1,
    add_heading_2,
    add_heading_3,
    add_p,
    add_bullet_point,
    add_sgk_box,
    add_callout,
    add_example_box,
    add_figure_box,
    audit_docx
)

def build_theory(lesson_title, subtitle, sections_data, output_docx_path):
    builder = MathPlusDocxBuilder(
        title=lesson_title,
        subtitle=subtitle,
        time_limit=None,
        show_student_info=False,
        is_solved=True
    )
    doc = builder.doc

    for sec in sections_data:
        add_heading_1(doc, sec["title"])
        for part in sec.get("parts", []):
            if "heading_2" in part:
                add_heading_2(doc, part["heading_2"])
            if "sgk_box" in part:
                add_sgk_box(doc, part["sgk_box"]["title"], part["sgk_box"]["lines"])
            if "callout" in part:
                add_callout(doc, part["callout"]["title"], part["callout"]["lines"], box_type=part["callout"].get("type", "ghi_nho"))
            if "examples" in part:
                for ex in part["examples"]:
                    add_example_box(doc, ex["title"], ex["problem"], ex["solution"])
            if "figure" in part:
                fig = part["figure"]
                add_figure_box(doc, fig["path"], fig["caption"], fig.get("explanation"))

    builder.save(output_docx_path)
    print(f"Theory saved: {output_docx_path}")
    audit_docx(output_docx_path)
    return output_docx_path

if __name__ == "__main__":
    print("Theory builder template ready.")
