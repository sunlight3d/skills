#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Runner cho skill mathplus-giai-toan.
Cho phép chạy trực tiếp từ dòng lệnh:
  python3 cli.py --help
"""

import os
import sys
import argparse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from mathplus_docx_engine import MathPlusDocxBuilder
from omml_converter import latex_to_omml
import math_plotter

def main():
    parser = argparse.ArgumentParser(description="MathPlus Giải Toán CLI - Biên soạn đề thi & lời giải chuẩn OMML")
    parser.add_argument("--title", default="PHIẾU ÔN TẬP TOÁN HỌC", help="Tiêu đề phiếu bài tập")
    parser.add_argument("--subtitle", default="Năm học 2026 – 2027", help="Năm học / học kỳ")
    parser.add_argument("--time-limit", default="90 phút", help="Thời gian làm bài")
    parser.add_argument("--output", default="output.docx", help="Đường dẫn file Word đầu ra")
    parser.add_argument("--solved", action="store_true", help="Xuất bản có lời giải chi tiết")
    args = parser.parse_args()

    builder = MathPlusDocxBuilder(
        title=args.title,
        subtitle=args.subtitle,
        time_limit=args.time_limit,
        is_solved=args.solved
    )
    
    out_path = builder.save(args.output)
    print(f"Tạo file Word thành công: {out_path}")

if __name__ == "__main__":
    main()
