import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from outlook_reader import fetch_outlook_emails
from template_checker import verify_document_template
from data_extractor import extract_text_from_pdf, parse_pdf_fields
from excel_generator import export_consolidated_excel

def process_emails(
    account_email: str,
    from_date: str = "",
    to_date: str = "",
    output_dir: str = "",
    filename: str = "TongHop_HoSo_DangKy.xlsx",
    limit: int = 100
) -> Dict[str, Any]:
    """
    Main processing function:
    1. Reads Outlook emails by account and date range.
    2. Checks PDF attachments against template01.docx (format, red stamp, QR).
    3. Extracts structured data fields from PDF.
    4. Generates a SINGLE consolidated Excel file with 3 sheets (Báo Cáo Theo Ngày, Tổng Hợp Hồ Sơ, Chi Tiết Email).
    """
    if output_dir and output_dir.lower().endswith(".xlsx"):
        filename = os.path.basename(output_dir)
        output_dir = os.path.dirname(output_dir)

    if not output_dir:
        output_dir = os.path.join(os.getcwd(), "output_excel")
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "="*70)
    print("🚀 QNET-GET-EMAILS: XỬ LÝ EMAIL OUTLOOK & TRÍCH XUẤT HỒ SƠ PDF")
    print("="*70)
    print(f"📧 Tài khoản Outlook : {account_email}")
    print(f"📅 Khoảng thời gian  : Từ {from_date or 'Tất cả'} đến {to_date or 'Tất cả'}")
    print(f"📂 Thư mục kết xuất  : {output_dir}")
    print("="*70 + "\n")

    print("[1/3] 🔍 Đang quét email từ ứng dụng Outlook trên máy tính...")
    emails = fetch_outlook_emails(
        account_email=account_email,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )

    if not emails:
        print("[!] Không tìm thấy email nào phù hợp với tiêu chí tìm kiếm.")
        return {"total_emails": 0, "processed_records": [], "summary_file": None}

    print(f"[✓] Đã tìm thấy {len(emails)} email thỏa mãn điều kiện.\n")

    processed_records = []
    print("[2/3] 📄 Bắt đầu kiểm tra biểu mẫu PDF, nhận diện Dấu đỏ & QR code...")

    for idx, em in enumerate(emails, 1):
        print(f"\n--- Email #{idx}: {em['subject']} ---")
        print(f"    Người gửi : {em['sender']}")
        print(f"    Ngày nhận : {em['date_str']}")

        pdf_list = em.get("pdf_attachments", [])
        if not pdf_list:
            print("    [!] Không có file PDF đính kèm.")
            rec = {
                "email_id": em["email_id"],
                "subject": em["subject"],
                "sender": em["sender"],
                "recipient": em["recipient"],
                "date_str": em["date_str"],
                "body": em["body"],
                "pdf_filename": "Không có",
                "pdf_path": "",
                "validation": {
                    "status": "Không có file PDF",
                    "is_valid": False,
                    "detail": "Email không có file PDF đính kèm",
                    "has_seal": False,
                    "has_qr": False,
                    "qr_value": ""
                },
                "extracted_data": {}
            }
            processed_records.append(rec)
            continue

        for pdf_item in pdf_list:
            pdf_name = pdf_item["filename"]
            pdf_path = pdf_item["local_path"]
            print(f"    📎 Tệp PDF: {pdf_name}")

            if not pdf_path or not os.path.exists(pdf_path):
                print(f"    [!] Tệp PDF chưa được lưu trong cache cục bộ.")
                validation = {
                    "status": "Không tìm thấy file trên máy",
                    "is_valid": False,
                    "detail": f"File {pdf_name} chưa được tải về cache của Outlook",
                    "has_seal": False,
                    "has_qr": False,
                    "qr_value": ""
                }
                extracted_data = {}
            else:
                # 1. Trích xuất text
                pdf_text = extract_text_from_pdf(pdf_path)
                print(f"    [✓] Đã trích xuất nội dung văn bản ({len(pdf_text)} ký tự)")

                # 2. Đối chiếu template01, dấu đỏ, QR
                validation = verify_document_template(pdf_path, pdf_text)
                print(f"    🔍 Đánh giá mẫu: {validation['status']}")
                print(f"       - Dấu đỏ  : {'[CÓ]' if validation['has_seal'] else '[THIẾU]'}")
                print(f"       - Mã QR   : {'[CÓ: ' + validation['qr_value'] + ']' if validation['has_qr'] else '[THIẾU]'}")
                print(f"       - Chi tiết: {validation['detail']}")

                # 3. Trích xuất các trường thông tin
                extracted_data = parse_pdf_fields(pdf_text, email_subject=em["subject"])
                ma_qhns = extracted_data.get("ma_qhns") or "Không rõ"
                ten_dn = extracted_data.get("ten_doanh_nghiep") or "Không rõ"
                print(f"    📊 Trích xuất thông tin:")
                print(f"       - Tên DN  : {ten_dn}")
                print(f"       - Mã QHNS : {ma_qhns}")
                print(f"       - Đại diện: {extracted_data.get('nguoi_dai_dien') or 'N/A'}")

            rec = {
                "email_id": em["email_id"],
                "subject": em["subject"],
                "sender": em["sender"],
                "recipient": em["recipient"],
                "date_str": em["date_str"],
                "body": em["body"],
                "pdf_filename": pdf_name,
                "pdf_path": pdf_path or "",
                "validation": validation,
                "extracted_data": extracted_data
            }
            processed_records.append(rec)

    # Xuất toàn bộ kết quả vào 1 FILE EXCEL DUY NHẤT
    print("\n[3/3] 📊 Đang tổng hợp toàn bộ kết quả vào 1 file Excel duy nhất...")
    summary_file = export_consolidated_excel(processed_records, output_dir, filename=filename)
    print(f"[✓] Đã tạo file Excel tổng hợp thành công: {os.path.basename(summary_file)}")

    print("\n" + "="*70)
    print("🎉 HOÀN TẤT QUÁ TRÌNH XỬ LÝ!")
    print(f"📁 Tệp kết quả: {summary_file}")
    print(f"📊 Tổng số hồ sơ đã xử lý: {len(processed_records)}")
    print("="*70 + "\n")

    return {
        "total_emails": len(emails),
        "processed_records": processed_records,
        "summary_file": summary_file
    }

def main():
    parser = argparse.ArgumentParser(description="Tool đọc mail Outlook, kiểm tra biểu mẫu PDF và xuất Excel")
    parser.add_argument("--account", help="Địa chỉ email tài khoản Outlook (vd: nguyenduchoang1979@outlook.com)")
    parser.add_argument("--from-date", dest="from_date", help="Từ ngày (định dạng YYYY-MM-DD)")
    parser.add_argument("--to-date", dest="to_date", help="Đến ngày (định dạng YYYY-MM-DD)")
    parser.add_argument("--output", dest="output_dir", default="", help="Thư mục xuất file Excel hoặc đường dẫn file .xlsx")
    parser.add_argument("--filename", dest="filename", default="TongHop_HoSo_DangKy.xlsx", help="Tên file Excel kết quả")
    parser.add_argument("--limit", type=int, default=200, help="Số lượng email tối đa cần quét")
    args = parser.parse_args()

    account = args.account
    from_d = args.from_date
    to_d = args.to_date

    # Interactive mode if parameters are missing
    if not account:
        print("\n=== CẤU HÌNH ĐỌC MAIL OUTLOOK ===")
        account = input("Nhập địa chỉ email tài khoản Outlook: ").strip()
        while not account:
            account = input("Vui lòng nhập địa chỉ email hợp lệ: ").strip()

    if from_d is None:
        from_d = input("Nhập Từ Ngày (YYYY-MM-DD, bỏ trống nếu lấy tất cả): ").strip()
    if to_d is None:
        to_d = input("Nhập Đến Ngày (YYYY-MM-DD, bỏ trống nếu lấy tất cả): ").strip()

    process_emails(
        account_email=account,
        from_date=from_d,
        to_date=to_d,
        output_dir=args.output_dir,
        filename=args.filename,
        limit=args.limit
    )

if __name__ == "__main__":
    main()
