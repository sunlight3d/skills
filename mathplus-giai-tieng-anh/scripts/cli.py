#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Runner cho skill mathplus-giai-tieng-anh.
Cho phép tạo khung tài liệu Word môn Tiếng Anh và kiểm tra engine từ dòng lệnh:
  python3 cli.py --help
"""

import os
import sys
import argparse

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from mathplus_docx_engine import MathPlusDocxBuilder

def main():
    parser = argparse.ArgumentParser(description="MathPlus Giải Tiếng Anh CLI - Biên soạn đề thi, lời giải chi tiết & dịch nghĩa bài đọc chuẩn MathPlus")
    parser.add_argument("--title", default="ĐỀ KHẢO SÁT CHẤT LƯỢNG MÔN TIẾNG ANH", help="Tiêu đề phiếu bài tập / đề thi")
    parser.add_argument("--subtitle", default="Năm học 2026 – 2027", help="Năm học / học kỳ")
    parser.add_argument("--time-limit", default="60 phút", help="Thời gian làm bài")
    parser.add_argument("--output", default="output_english.docx", help="Đường dẫn file Word đầu ra")
    parser.add_argument("--solved", action="store_true", help="Xuất bản có lời giải chi tiết và dịch nghĩa")
    args = parser.parse_args()

    builder = MathPlusDocxBuilder(
        title=args.title,
        subtitle=args.subtitle,
        time_limit=args.time_limit,
        subject_center="Bồi dưỡng Tiếng Anh & Luyện thi",
        is_solved=args.solved
    )
    
    out_path = builder.save(args.output)
    print(f"Tạo file Word Tiếng Anh thành công: {out_path}")

if __name__ == "__main__":
    main()
