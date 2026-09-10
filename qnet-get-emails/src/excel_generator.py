import os
import re
from collections import defaultdict
from typing import Dict, Any, List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Styles definition
HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_FONT = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
SUBHEADER_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
SUBHEADER_FONT = Font(name="Segoe UI", size=10, bold=True, color="1F4E78")
REGULAR_FONT = Font(name="Segoe UI", size=10)
BOLD_FONT = Font(name="Segoe UI", size=10, bold=True)
TITLE_FONT = Font(name="Segoe UI", size=14, bold=True, color="1F4E78")

THIN_BORDER = Border(
    left=Side(style="thin", color="D3D3D3"),
    right=Side(style="thin", color="D3D3D3"),
    top=Side(style="thin", color="D3D3D3"),
    bottom=Side(style="thin", color="D3D3D3")
)

VALID_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
VALID_FONT = Font(name="Segoe UI", size=10, bold=True, color="006100")
INVALID_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
INVALID_FONT = Font(name="Segoe UI", size=10, bold=True, color="9C0006")
WARNING_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
WARNING_FONT = Font(name="Segoe UI", size=10, bold=True, color="9C6500")

def clean_cell_value(val: Any) -> Any:
    """Strip illegal control characters that crash openpyxl."""
    if val is None:
        return ""
    if isinstance(val, (int, float, bool)):
        return val
    s = str(val)
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', s).strip()

def export_consolidated_excel(
    all_records: List[Dict[str, Any]],
    output_dir: str,
    filename: str = "TongHop_HoSo_DangKy.xlsx"
) -> str:
    """
    Export all email records and extracted PDF data into a SINGLE consolidated Excel file.
    Sheet 1: 'Báo Cáo Theo Ngày' (Thống kê số lượng email & phân loại hồ sơ theo ngày)
    Sheet 2: 'Tổng Hợp Hồ Sơ' (All extracted fields + template validation)
    Sheet 3: 'Chi Tiết Email' (Source email metadata and body preview)
    """
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, filename)

    wb = openpyxl.Workbook()

    # -------------------------------------------------------------
    # Sheet 1: Báo Cáo Theo Ngày (Thống kê số lượng email & hồ sơ)
    # -------------------------------------------------------------
    ws0 = wb.active
    ws0.title = "Báo Cáo Theo Ngày"
    ws0.views.sheetView[0].showGridLines = True

    # Title
    ws0.merge_cells("A1:J1")
    ws0["A1"] = "BẢNG BÁO CÁO THỐNG KÊ SỐ LƯỢNG EMAIL & HỒ SƠ THEO NGÀY"
    ws0["A1"].font = TITLE_FONT
    ws0["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws0.row_dimensions[1].height = 32

    daily_headers = [
        "STT",
        "Ngày nhận",
        "Tổng số Email",
        "Email có tệp PDF",
        "Email không có PDF",
        "Hồ sơ Hợp lệ",
        "Đúng format, thiếu QR",
        "Đúng format, thiếu Dấu đỏ",
        "Sai format biểu mẫu",
        "Tỷ lệ hợp lệ (%)"
    ]
    ws0.append([clean_cell_value(h) for h in daily_headers])
    h0_row = 2
    ws0.row_dimensions[h0_row].height = 28
    for col_idx in range(1, len(daily_headers) + 1):
        col_letter = get_column_letter(col_idx)
        cell = ws0[f"{col_letter}{h0_row}"]
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Group by date (YYYY-MM-DD)
    daily_stats = defaultdict(lambda: {
        "total": 0, "with_pdf": 0, "without_pdf": 0,
        "valid": 0, "missing_qr": 0, "missing_seal": 0, "invalid_format": 0
    })

    for rec in all_records:
        d_str = (rec.get("date_str") or "Không rõ")[:10]
        daily_stats[d_str]["total"] += 1
        pdf = rec.get("pdf_filename")
        has_pdf = bool(rec.get("pdf_path")) or (pdf and pdf not in ["", "Không có", "(Không có đính kèm PDF)"])
        val = rec.get("validation", {})
        status = val.get("status", "")
        if has_pdf:
            daily_stats[d_str]["with_pdf"] += 1
            if val.get("is_valid"):
                daily_stats[d_str]["valid"] += 1
            elif "thiếu qr" in status.lower():
                daily_stats[d_str]["missing_qr"] += 1
            elif "thiếu dấu đỏ" in status.lower():
                daily_stats[d_str]["missing_seal"] += 1
            elif "sai format" in status.lower():
                daily_stats[d_str]["invalid_format"] += 1
        else:
            daily_stats[d_str]["without_pdf"] += 1

    sorted_dates = sorted(daily_stats.keys(), reverse=True)

    tot_total = 0
    tot_with_pdf = 0
    tot_without_pdf = 0
    tot_valid = 0
    tot_missing_qr = 0
    tot_missing_seal = 0
    tot_invalid_format = 0

    for i, d in enumerate(sorted_dates, 1):
        s = daily_stats[d]
        tot_total += s["total"]
        tot_with_pdf += s["with_pdf"]
        tot_without_pdf += s["without_pdf"]
        tot_valid += s["valid"]
        tot_missing_qr += s["missing_qr"]
        tot_missing_seal += s["missing_seal"]
        tot_invalid_format += s["invalid_format"]

        rate_str = f"{(s['valid'] / s['with_pdf'] * 100):.1f}%" if s["with_pdf"] > 0 else "0.0%"
        row_data = [
            i,
            d,
            s["total"],
            s["with_pdf"],
            s["without_pdf"],
            s["valid"],
            s["missing_qr"],
            s["missing_seal"],
            s["invalid_format"],
            rate_str
        ]
        ws0.append(row_data)
        r = ws0.max_row
        for col_idx in range(1, len(row_data) + 1):
            col_letter = get_column_letter(col_idx)
            cell = ws0[f"{col_letter}{r}"]
            cell.font = REGULAR_FONT
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            if col_idx == 6 and s["valid"] > 0:
                cell.fill = VALID_FILL
                cell.font = VALID_FONT
            elif col_idx == 9 and s["invalid_format"] > 0:
                cell.fill = INVALID_FILL
                cell.font = INVALID_FONT
            elif col_idx in [7, 8] and row_data[col_idx - 1] > 0:
                cell.fill = WARNING_FILL
                cell.font = WARNING_FONT

    # Total row
    tot_rate_str = f"{(tot_valid / tot_with_pdf * 100):.1f}%" if tot_with_pdf > 0 else "0.0%"
    tot_row_data = [
        "",
        "TỔNG CỘNG",
        tot_total,
        tot_with_pdf,
        tot_without_pdf,
        tot_valid,
        tot_missing_qr,
        tot_missing_seal,
        tot_invalid_format,
        tot_rate_str
    ]
    ws0.append(tot_row_data)
    tot_r = ws0.max_row
    for col_idx in range(1, len(tot_row_data) + 1):
        col_letter = get_column_letter(col_idx)
        cell = ws0[f"{col_letter}{tot_r}"]
        cell.fill = SUBHEADER_FILL
        cell.font = SUBHEADER_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Column widths for Sheet 0
    ws0.column_dimensions["A"].width = 8
    ws0.column_dimensions["B"].width = 16
    ws0.column_dimensions["C"].width = 18
    ws0.column_dimensions["D"].width = 18
    ws0.column_dimensions["E"].width = 20
    ws0.column_dimensions["F"].width = 16
    ws0.column_dimensions["G"].width = 22
    ws0.column_dimensions["H"].width = 24
    ws0.column_dimensions["I"].width = 22
    ws0.column_dimensions["J"].width = 18

    # -------------------------------------------------------------
    # Sheet 2: Tổng Hợp Hồ Sơ & Kết Quả Đối Chiếu
    # -------------------------------------------------------------
    ws1 = wb.create_sheet(title="Tổng Hợp Hồ Sơ")
    ws1.views.sheetView[0].showGridLines = True

    # Title
    ws1.merge_cells("A1:X1")
    ws1["A1"] = "BẢNG TỔNG HỢP KIỂM ĐỊNH BIỂU MẪU & TRÍCH XUẤT HỒ SƠ ĐĂNG KÝ TÀI KHOẢN (OUTLOOK)"
    ws1["A1"].font = TITLE_FONT
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 32

    headers = [
        "STT",
        "Thời gian nhận",
        "Tiêu đề Email",
        "Người gửi",
        "Tên tệp PDF",
        "Đánh giá biểu mẫu",
        "Dấu đỏ",
        "Mã QR",
        "Tên doanh nghiệp (VN)",
        "Mã QHNS / MST",
        "Loại dự án",
        "Đối tượng đăng ký",
        "Ngày cấp & Cơ quan cấp",
        "Trụ sở chính",
        "Người đại diện pháp luật",
        "Chức vụ đại diện",
        "Ngành nghề (Mã VSIC)",
        "Người quản lý tài khoản",
        "Chức vụ người quản lý",
        "Đơn vị công tác",
        "Số CMND / CCCD",
        "Điện thoại di động",
        "Email",
        "Chi tiết đánh giá biểu mẫu"
    ]

    ws1.append([clean_cell_value(h) for h in headers])
    h_row = 2
    ws1.row_dimensions[h_row].height = 28
    
    for col_idx in range(1, len(headers) + 1):
        col_letter = get_column_letter(col_idx)
        cell = ws1[f"{col_letter}{h_row}"]
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for i, rec in enumerate(all_records, 1):
        extracted = rec.get("extracted_data", {})
        validation = rec.get("validation", {})
        
        status_str = validation.get("status", "Chưa kiểm tra")
        has_seal_str = "Có" if validation.get("has_seal") else "Không"
        
        qr_val = validation.get("qr_value", "")
        has_qr_str = f"Có ({qr_val})" if validation.get("has_qr") else "Không"

        row_data = [
            i,
            clean_cell_value(rec.get("date_str", "")),
            clean_cell_value(rec.get("subject", "")),
            clean_cell_value(rec.get("sender", "")),
            clean_cell_value(rec.get("pdf_filename", "")),
            clean_cell_value(status_str),
            has_seal_str,
            has_qr_str,
            clean_cell_value(extracted.get("ten_doanh_nghiep", "")),
            clean_cell_value(extracted.get("ma_qhns", "")),
            clean_cell_value(extracted.get("loai_du_an", "")),
            clean_cell_value(extracted.get("doi_tuong_dang_ky", "")),
            clean_cell_value(extracted.get("ngay_cap_co_quan_cap", "")),
            clean_cell_value(extracted.get("tru_so_chinh", "")),
            clean_cell_value(extracted.get("nguoi_dai_dien", "")),
            clean_cell_value(extracted.get("chuc_vu_dai_dien", "")),
            clean_cell_value(extracted.get("ma_vsic", "")),
            clean_cell_value(extracted.get("ho_ten_nguoi_quan_ly", "")),
            clean_cell_value(extracted.get("chuc_vu_nguoi_quan_ly", "")),
            clean_cell_value(extracted.get("don_vi_cong_tac", "")),
            clean_cell_value(extracted.get("so_cmnd_cccd", "")),
            clean_cell_value(extracted.get("sdt_di_dong", "")),
            clean_cell_value(extracted.get("thu_dien_tu", "")),
            clean_cell_value(validation.get("detail", ""))
        ]
        ws1.append(row_data)
        r = ws1.max_row
        # Do not set row_dimensions[r].height to let Excel auto-fit height for wrapped text

        for col_idx in range(1, len(row_data) + 1):
            col_letter = get_column_letter(col_idx)
            cell = ws1[f"{col_letter}{r}"]
            cell.font = REGULAR_FONT
            cell.border = THIN_BORDER
            
            # Alignments with wrap_text=True
            if col_idx in [1, 2, 7, 8, 10, 21, 22]:
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            else:
                cell.alignment = Alignment(vertical="center", wrap_text=True)

        # Color highlight evaluation column (Col F = Col 6)
        cell_status = ws1[f"F{r}"]
        is_valid = validation.get("is_valid", False)
        if is_valid:
            cell_status.fill = VALID_FILL
            cell_status.font = VALID_FONT
        elif "Sai format" in status_str:
            cell_status.fill = INVALID_FILL
            cell_status.font = INVALID_FONT
        elif "thiếu" in status_str.lower():
            cell_status.fill = WARNING_FILL
            cell_status.font = WARNING_FONT

        # Highlight seal and QR
        ws1[f"G{r}"].font = VALID_FONT if validation.get("has_seal") else BOLD_FONT
        ws1[f"H{r}"].font = VALID_FONT if validation.get("has_qr") else BOLD_FONT

    # Auto-adjust column widths for Sheet 1
    for col in ws1.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len and len(val_str) < 60:
                max_len = len(val_str)
        ws1.column_dimensions[col_letter].width = max(max_len + 3, 12)

    ws1.column_dimensions["C"].width = 35  # Subject
    ws1.column_dimensions["E"].width = 30  # PDF filename
    ws1.column_dimensions["F"].width = 25  # Evaluation
    ws1.column_dimensions["I"].width = 32  # Enterprise name
    ws1.column_dimensions["N"].width = 35  # Headquarters
    ws1.column_dimensions["X"].width = 45  # Detail

    # -------------------------------------------------------------
    # Sheet 2: Chi Tiết Email Nguồn
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="Chi Tiết Email")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"] = "DANH SÁCH CHI TIẾT EMAIL NGUỒN TỪ OUTLOOK"
    ws2["A1"].font = TITLE_FONT
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 30

    email_headers = ["STT", "Thời gian nhận", "Tiêu đề Email", "Người gửi", "Người nhận", "Tệp PDF", "Nội dung thư (Preview)"]
    ws2.append([clean_cell_value(h) for h in email_headers])
    h2_row = 2
    ws2.row_dimensions[h2_row].height = 26
    for col_idx in range(1, len(email_headers) + 1):
        col_letter = get_column_letter(col_idx)
        cell = ws2[f"{col_letter}{h2_row}"]
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for i, rec in enumerate(all_records, 1):
        row_mail = [
            i,
            clean_cell_value(rec.get("date_str", "")),
            clean_cell_value(rec.get("subject", "")),
            clean_cell_value(rec.get("sender", "")),
            clean_cell_value(rec.get("recipient", "")),
            clean_cell_value(rec.get("pdf_filename", "")),
            clean_cell_value(rec.get("body", ""))
        ]
        ws2.append(row_mail)
        r = ws2.max_row
        # Do not set row_dimensions[r].height to let Excel auto-fit height for wrapped text
        for col_idx in range(1, len(row_mail) + 1):
            col_letter = get_column_letter(col_idx)
            cell = ws2[f"{col_letter}{r}"]
            cell.font = REGULAR_FONT
            cell.border = THIN_BORDER
            if col_idx in [1, 2]:
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            else:
                cell.alignment = Alignment(vertical="center", wrap_text=True)

    for col in ws2.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len and len(val_str) < 70:
                max_len = len(val_str)
        ws2.column_dimensions[col_letter].width = max(max_len + 3, 15)

    ws2.column_dimensions["C"].width = 35
    ws2.column_dimensions["G"].width = 60

    wb.save(out_path)
    return out_path
