#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
TEMPLATE BIÊN SOẠN BỘ BÀI TẬP SGK ĐÃ CHẾ BIẾN LẠI MATHPLUS:
- 100% Đổi mới số liệu & bối cảnh thực tế (CNTT, kinh tế, kỹ thuật...)
- Lời giải chi tiết từng bước, chuẩn sư phạm
- Tạo đồng thời 2 file: Bản Lời giải và Bản Đề bài học sinh
- 100% công thức OMML Math, tuyệt đối không xuất PDF
"""

import os
import sys

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

from mathplus_docx_engine import MathPlusDocxBuilder, audit_docx

def build_exercises(title, subtitle, sections_problems, solved_path, blank_path):
    # 1. Build Solved Document
    builder_solved = MathPlusDocxBuilder(
        title=title,
        subtitle=subtitle + " (LỜI GIẢI CHI TIẾT – ĐỔI SỐ LIỆU & NGHIỆP VỤ MỚI)",
        time_limit=None,
        show_student_info=False,
        is_solved=True
    )
    for sec in sections_problems:
        builder_solved.add_section(sec["title"])
        for prob in sec.get("problems", []):
            builder_solved.add_problem_header(prob["header"], prob["question"])
            builder_solved.add_solution(prob["solution_steps"])

    builder_solved.save(solved_path)
    print(f"Solved document saved: {solved_path}")
    audit_docx(solved_path)

    # 2. Build Blank Student Document
    builder_blank = MathPlusDocxBuilder(
        title=title,
        subtitle=subtitle + " (PHIẾU ĐỀ BÀI TẬP LUYỆN TẬP)",
        time_limit=None,
        show_student_info=True,
        is_solved=False
    )
    for sec in sections_problems:
        builder_blank.add_section(sec["title"])
        for prob in sec.get("problems", []):
            builder_blank.add_problem_header(prob["header"], prob["question"])

    builder_blank.save(blank_path)
    print(f"Blank document saved: {blank_path}")
    audit_docx(blank_path)

    return solved_path, blank_path

if __name__ == "__main__":
    print("Exercise builder template ready.")
