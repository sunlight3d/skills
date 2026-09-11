#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_skill.py - Điểm khởi chạy CLI cho kỹ năng qnet-sinh-du-lieu-tu-dong.
Đọc template JSON -> Phân tích schema & ngữ nghĩa -> Sinh dữ liệu tự động -> Thẩm định Validation -> Xuất file.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Thêm thư mục hiện tại vào sys.path để import trực tiếp
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from data_generator import DataGenerator, SchemaAnalyzer, ValidationEngine

# Cấu hình UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def print_banner():
    print("=" * 70)
    print("      QNET SINH DỮ LIỆU TỰ ĐỘNG (DATA GENERATOR & VALIDATOR)")
    print("=" * 70)


def print_schema_summary(fields_meta):
    print("\n📋 CẤU TRÚC VÀ NGỮ NGHĨA PHÁT HIỆN TỪ TEMPLATE:")
    print("-" * 70)
    print(f"{'STT':<4} | {'Tên trường':<18} | {'Kiểu dữ liệu':<14} | {'Ngữ nghĩa suy luận':<20}")
    print("-" * 70)
    for idx, (name, meta) in enumerate(fields_meta.items(), 1):
        print(f"{idx:<4} | {name:<18} | {meta.inferred_type:<14} | {meta.semantic_type:<20}")
    print("-" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Kỹ năng tự động đọc template JSON và sinh dữ liệu kèm validation rules."
    )
    parser.add_argument(
        "-t", "--template",
        default="template.json",
        help="Đường dẫn tới file template JSON mẫu (mặc định: template.json trong thư mục)."
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        help="Số lượng bản ghi cần sinh (mặc định: 10)."
    )
    parser.add_argument(
        "-r", "--rules",
        default=None,
        help="Đường dẫn tới file JSON chứa validation rules hoặc chuỗi JSON cấu hình."
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Đường dẫn file kết quả xuất ra (.json hoặc .csv). Mặc định: generated_data.json."
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv"],
        default="json",
        help="Định dạng xuất file: json (mặc định) hoặc csv."
    )
    parser.add_argument(
        "-p", "--preview",
        action="store_true",
        help="Xem trước phân tích schema và 3 bản ghi mẫu đầu tiên trên terminal."
    )
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=None,
        help="Seed số ngẫu nhiên (dùng khi cần tái lập kết quả kiểm thử)."
    )

    args = parser.parse_args()

    print_banner()

    # Xác định đường dẫn file template
    template_path = Path(args.template)
    if not template_path.is_absolute():
        template_path = CURRENT_DIR / template_path

    if not template_path.exists():
        print(f"❌ [LỖI] Không tìm thấy file template tại: {template_path}")
        sys.exit(1)

    print(f"📂 File template: {template_path.name}")
    print(f"🎯 Số lượng bản ghi cần sinh: {args.count}")

    # Xử lý rules
    user_rules = {}
    if args.rules:
        rules_path = Path(args.rules)
        if not rules_path.is_absolute():
            rules_path = CURRENT_DIR / rules_path

        if rules_path.exists():
            print(f"⚙️  Tải validation rules từ file: {rules_path.name}")
            with open(rules_path, "r", encoding="utf-8") as rf:
                user_rules = json.load(rf)
        else:
            try:
                user_rules = json.loads(args.rules)
                print("⚙️  Áp dụng validation rules từ tham số dòng lệnh.")
            except Exception:
                print(f"⚠️ [Cảnh báo] Không thể đọc rules từ '{args.rules}', sử dụng rules mặc định.")

    # Khởi tạo Generator
    try:
        generator = DataGenerator(template_path=template_path, rules=user_rules, seed=args.seed)
    except Exception as e:
        print(f"❌ [LỖI] Phân tích template thất bại: {e}")
        sys.exit(1)

    print_schema_summary(generator.fields_meta)

    # Sinh dữ liệu
    print(f"\n⚡ Đang tiến hành sinh {args.count} bản ghi và chạy kiểm tra validation...")
    records = generator.generate(args.count)

    # Thẩm định kết quả
    is_valid, dataset_errors = generator.validator.validate_dataset(records)
    if is_valid:
        print("✅ 100% bản ghi đã vượt qua toàn bộ quy tắc thẩm định (Validation PASSED).")
    else:
        print(f"⚠️ Phát hiện {len(dataset_errors)} cảnh báo thẩm định:")
        for err in dataset_errors[:5]:
            print(f"   - [Bản ghi #{err.get('index')}] Cột '{err.get('field')}': {err.get('error')}")

    # Chế độ xem trước
    if args.preview or args.output is None:
        print("\n🔍 XEM TRƯỚC 3 BẢN GHI ĐẦU TIÊN:")
        print("-" * 70)
        preview_samples = records[:3]
        print(json.dumps(preview_samples, ensure_ascii=False, indent=2))
        print("-" * 70)

    # Xác định đường dẫn file xuất
    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = CURRENT_DIR / out_path
    else:
        out_filename = "generated_data.csv" if args.format == "csv" else "generated_data.json"
        out_path = CURRENT_DIR / out_filename

    # Xác định format từ extension của output nếu có
    export_format = args.format
    if out_path.suffix.lower() == ".csv":
        export_format = "csv"
    elif out_path.suffix.lower() == ".json":
        export_format = "json"

    saved_file = generator.export(records, out_path, file_format=export_format)
    print(f"\n💾 Đã lưu thành công {len(records)} bản ghi vào:")
    print(f"   👉 {saved_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
