import os
import sys
import argparse
import fitz
import ipaddress
import unicodedata
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

def find_tracker_file(search_dirs):
    """Tìm tệp dữ liệu theo dõi IP_CSKCB_INTERNET - VPN.xlsx trong các thư mục khả dĩ."""
    candidate_names = [
        'IP_CSKCB_INTERNET - VPN.xlsx',
        'IP_CSKCB_INTERNET-VPN.xlsx',
        'IP_CSKCB.xlsx'
    ]
    for d in search_dirs:
        if not d or not os.path.exists(d):
            continue
        for name in candidate_names:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
        try:
            for item in os.listdir(d):
                sub = os.path.join(d, item)
                if os.path.isdir(sub):
                    for name in candidate_names:
                        p = os.path.join(sub, name)
                        if os.path.exists(p):
                            return p
        except Exception:
            pass
    return None

def load_tracking_data(tracker_path):
    """Nạp dữ liệu lịch sử từ tệp theo dõi IP_CSKCB_INTERNET - VPN.xlsx."""
    if not tracker_path or not os.path.exists(tracker_path):
        print(f"[CẢNH BÁO] Không tìm thấy tệp theo dõi: {tracker_path}")
        return {}, 27948
    
    print(f"[*] Đang nạp cơ sở dữ liệu theo dõi từ: {tracker_path}")
    wb = openpyxl.load_workbook(tracker_path, data_only=True)
    if 'IP_CSKCB' not in wb.sheetnames:
        print("[LỖI] Tệp theo dõi không có sheet 'IP_CSKCB'")
        return {}, 27948
    
    ws = wb['IP_CSKCB']
    all_history = {}
    batch_start_row = 27948
    
    for r in range(2, ws.max_row + 1):
        ip_val = ws.cell(r, 5).value
        if ip_val:
            ip_clean = str(ip_val).strip()
            if ip_clean not in all_history:
                all_history[ip_clean] = []
            all_history[ip_clean].append({
                'row': r,
                'ma_tinh': ws.cell(r, 1).value,
                'tinh': ws.cell(r, 2).value,
                'ten_cs': ws.cell(r, 3).value,
                'ma_cs': str(ws.cell(r, 4).value).strip() if ws.cell(r, 4).value is not None else '',
                'nha_mang': ws.cell(r, 6).value,
                'dia_chi': ws.cell(r, 7).value,
                'note': ws.cell(r, 8).value,
                'loai': ws.cell(r, 9).value,
                'so_cv': ws.cell(r, 10).value
            })
    
    print(f"[*] Đã nạp thành công {len(all_history)} địa chỉ IP duy nhất từ tập dữ liệu theo dõi.")
    return all_history, batch_start_row

def extract_pdf_records(pdf_dir):
    """Trích xuất danh sách bản ghi đăng ký IP từ tất cả file PDF trong thư mục."""
    pdf_files = sorted([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])
    print(f"[*] Tìm thấy {len(pdf_files)} tệp PDF trong thư mục: {pdf_dir}")
    
    records = []
    for f in pdf_files:
        fpath = os.path.join(pdf_dir, f)
        try:
            doc = fitz.open(fpath)
        except Exception as e:
            print(f"[CẢNH BÁO] Không thể mở file {f}: {e}")
            continue
            
        current_section = 'Thêm mới'
        for page_idx, page in enumerate(doc):
            tables = page.find_tables()
            for tab in tables:
                rows = tab.extract()
                if not rows:
                    continue
                start_row = 0
                first_row_text = ' '.join([str(c) for c in rows[0] if c])
                if any(k in first_row_text.upper() for k in ['STT', 'TT']):
                    start_row = 1
                
                for row in rows[start_row:]:
                    row_str = ' '.join([str(c) for c in row if c]).strip()
                    if not row_str:
                        continue
                    row_lower = unicodedata.normalize('NFC', row_str).lower()
                    if 'thêm mới' in row_lower or 'them moi' in row_lower:
                        current_section = 'Thêm mới'
                        continue
                    if 'hủy' in row_lower or 'huỷ' in row_lower or 'huy' in row_lower:
                        current_section = 'Hủy'
                        continue
                    
                    c_stt = str(row[0]).strip() if len(row) > 0 and row[0] is not None else ''
                    c_ten = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ''
                    c_ma = str(row[2]).strip() if len(row) > 2 and row[2] is not None else ''
                    c_ip = str(row[3]).strip() if len(row) > 3 and row[3] is not None else ''
                    c_mang = str(row[4]).strip() if len(row) > 4 and row[4] is not None else ''
                    c_dc = str(row[5]).strip() if len(row) > 5 and row[5] is not None else ''
                    c_gc = str(row[6]).strip() if len(row) > 6 and row[6] is not None else ''
                    
                    c_ten = unicodedata.normalize('NFC', ' '.join(c_ten.split()))
                    c_ma = unicodedata.normalize('NFC', ' '.join(c_ma.split()))
                    c_ip = unicodedata.normalize('NFC', ' '.join(c_ip.split()))
                    c_mang = unicodedata.normalize('NFC', ' '.join(c_mang.split()))
                    c_dc = unicodedata.normalize('NFC', ' '.join(c_dc.split()))
                    c_gc = unicodedata.normalize('NFC', ' '.join(c_gc.split()))
                    
                    if not c_ip and not c_ten:
                        continue
                    if 'tên cơ sở' in c_ten.lower() or 'tên cskcb' in c_ten.lower():
                        continue
                    
                    records.append({
                        'file': f,
                        'section': current_section,
                        'stt': c_stt,
                        'ten_cs': c_ten,
                        'ma_cs': c_ma,
                        'ip': c_ip,
                        'nha_mang': c_mang,
                        'dia_chi': c_dc,
                        'ghi_chu': c_gc
                    })
    print(f"[*] Đã trích xuất tổng cộng {len(records)} bản ghi từ các tệp PDF.")
    return records, pdf_files

def validate_records(raw_records, all_history, batch_start_row):
    """Kiểm tra validation theo 3 tiêu chí: Định dạng IP, IP Public, Trùng lặp dữ liệu."""
    evaluated = []
    
    for idx, r in enumerate(raw_records, 1):
        ip_str = r['ip']
        errors = []
        warnings = []
        
        # 1. Định dạng IP
        is_valid_format = False
        ip_format_status = 'ĐẠT'
        ip_format_note = 'Đúng định dạng IPv4 chuẩn (4 octet)'
        
        if not ip_str:
            is_valid_format = False
            ip_format_status = 'LỖI'
            ip_format_note = 'Thiếu địa chỉ IP (để trống)'
            errors.append('Không có địa chỉ IP')
        else:
            octets = ip_str.split('.')
            if len(octets) != 4:
                is_valid_format = False
                ip_format_status = 'LỖI'
                ip_format_note = f'Sai số lượng octet: {len(octets)} octet (chuẩn phải là 4)'
                errors.append(ip_format_note)
            else:
                format_err = None
                for oct_i, oct_val in enumerate(octets, 1):
                    if not oct_val.isdigit():
                        format_err = f"Octet {oct_i} '{oct_val}' không phải là chữ số"
                        break
                    val_int = int(oct_val)
                    if val_int < 0 or val_int > 255:
                        format_err = f"Octet {oct_i} ({val_int}) vượt giới hạn hợp lệ 0-255"
                        break
                if format_err:
                    is_valid_format = False
                    ip_format_status = 'LỖI'
                    ip_format_note = f'Lỗi cú pháp IP: {format_err}'
                    errors.append(ip_format_note)
                else:
                    is_valid_format = True

        # 2. Chuẩn IP Public
        is_public = False
        ip_public_status = 'ĐẠT'
        ip_public_note = 'IP Public toàn cầu hợp lệ'
        
        if is_valid_format:
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                if ip_obj.is_private:
                    ip_public_status = 'LỖI'
                    ip_public_note = f'IP Private nội bộ ({ip_str}), không được phép cấp IP Public'
                    errors.append(ip_public_note)
                elif ip_obj.is_loopback:
                    ip_public_status = 'LỖI'
                    ip_public_note = f'Địa chỉ Loopback ({ip_str})'
                    errors.append(ip_public_note)
                elif ip_obj.is_link_local:
                    ip_public_status = 'LỖI'
                    ip_public_note = f'Địa chỉ Link-local ({ip_str})'
                    errors.append(ip_public_note)
                elif ip_obj.is_multicast:
                    ip_public_status = 'LỖI'
                    ip_public_note = f'Địa chỉ Multicast ({ip_str})'
                    errors.append(ip_public_note)
                elif ip_obj.is_reserved:
                    ip_public_status = 'LỖI'
                    ip_public_note = f'Địa chỉ Reserved ({ip_str})'
                    errors.append(ip_public_note)
                elif not ip_obj.is_global:
                    ip_public_status = 'LỖI'
                    ip_public_note = f'Không phải IP Public toàn cầu ({ip_str})'
                    errors.append(ip_public_note)
                else:
                    is_public = True
            except Exception as e:
                ip_public_status = 'LỖI'
                ip_public_note = f'Lỗi phân tích IP: {str(e)}'
                errors.append(ip_public_note)
        else:
            ip_public_status = 'K.XÁC ĐỊNH'
            ip_public_note = 'Không thể kiểm tra do định dạng IP sai'

        # 3. Kiểm tra trùng lặp với CSDL theo dõi
        tracked_matches = all_history.get(ip_str, [])
        prior_matches = [m for m in tracked_matches if m['row'] < batch_start_row]
        batch_matches = [m for m in tracked_matches if m['row'] >= batch_start_row]
        
        dup_status = 'ĐẠT'
        dup_details = []
        
        if not r['ma_cs']:
            warnings.append('Hồ sơ thiếu Mã cơ sở KCB')

        if r['section'] == 'Thêm mới':
            if prior_matches:
                dup_status = 'BỊ TRÙNG'
                for m in prior_matches:
                    info = f"Dòng {m['row']} - CSKCB: {m['ten_cs']} (Mã: {m['ma_cs']}), Tỉnh: {m['tinh']}, CV: {m['so_cv']}"
                    dup_details.append(info)
                if any(m['ma_cs'] == r['ma_cs'] for m in prior_matches):
                    msg = f"Trùng lặp: IP đã được cấp trước đó cho chính đơn vị này ({'; '.join(dup_details)})"
                else:
                    msg = f"Xung đột IP: IP này đã thuộc đơn vị khác đăng ký trước đó ({'; '.join(dup_details)})"
                errors.append(msg)
            else:
                if batch_matches:
                    dup_status = 'ĐÃ GHI NHẬN ĐỢT NÀY'
                    m_info = [f"Dòng {m['row']} (CV: {m['so_cv']})" for m in batch_matches]
                    dup_details.append(f"Đã có trong dữ liệu ghi nhận đợt T9/2026: {', '.join(m_info)}")
                else:
                    dup_status = 'CHƯA TỒN TẠI (MỚI 100%)'
                    dup_details.append("IP hoàn toàn mới, chưa từng có trong toàn bộ hệ thống theo dõi")
        
        elif r['section'] == 'Hủy':
            if prior_matches:
                matched_unit = [m for m in prior_matches if m['ma_cs'] == r['ma_cs']]
                if matched_unit:
                    dup_status = 'ĐẠT (HỢP LỆ ĐỂ HỦY)'
                    dup_details.append(f"Khớp đơn vị sở hữu trong lịch sử: Dòng {matched_unit[0]['row']} (Mã: {matched_unit[0]['ma_cs']})")
                else:
                    dup_status = 'SAI LỆCH ĐƠN VỊ'
                    other_units = [f"Dòng {m['row']} thuộc CSKCB '{m['ten_cs']}' (Mã: {m['ma_cs']}, Tỉnh: {m['tinh']}, CV: {m['so_cv']})" for m in prior_matches]
                    msg = f"Bất thường khi Hủy: IP này trong hệ thống trước đó thuộc đơn vị khác: {'; '.join(other_units)}"
                    errors.append(msg)
                    dup_details.append(msg)
            else:
                dup_status = 'CHƯA CÓ LỊCH SỬ CŨ'
                if batch_matches:
                    dup_details.append(f"Được ghi nhận tại dòng {batch_matches[0]['row']} đợt này")
                else:
                    warnings.append("IP xin hủy chưa từng xuất hiện trong dữ liệu lịch sử")

        if errors:
            final_validation = 'FAILED'
            final_reason = ' | '.join(errors)
            if warnings:
                final_reason += f" (Cảnh báo: {', '.join(warnings)})"
        else:
            final_validation = 'PASSED'
            if warnings:
                final_reason = f"Đạt yêu cầu IP (Lưu ý: {', '.join(warnings)})"
            else:
                final_reason = 'Đạt đầy đủ các tiêu chí validation'

        evaluated.append({
            'stt': idx,
            'file': r['file'],
            'section': r['section'],
            'stt_pdf': r['stt'],
            'ten_cs': r['ten_cs'],
            'ma_cs': r['ma_cs'],
            'ip': r['ip'],
            'nha_mang': r['nha_mang'],
            'dia_chi': r['dia_chi'],
            'ghi_chu_pdf': r['ghi_chu'],
            'format_status': ip_format_status,
            'format_note': ip_format_note,
            'public_status': ip_public_status,
            'public_note': ip_public_note,
            'dup_status': dup_status,
            'dup_detail': ' | '.join(dup_details) if dup_details else 'Không có',
            'validation': final_validation,
            'reason': final_reason
        })
    return evaluated

def export_excel_report(evaluated_records, pdf_files, all_history, output_path):
    """Xuất báo cáo Excel với đầy đủ text wrapping, auto-height và bôi đỏ bản ghi FAILED."""
    wb = openpyxl.Workbook()
    FONT_NAME = 'Arial'
    
    font_title = Font(name=FONT_NAME, size=13, bold=True, color='1F4E78')
    font_subtitle = Font(name=FONT_NAME, size=10, italic=True, color='595959')
    font_header = Font(name=FONT_NAME, size=10, bold=True, color='FFFFFF')
    font_data = Font(name=FONT_NAME, size=9)
    font_bold = Font(name=FONT_NAME, size=9, bold=True)
    
    fill_header = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
    fill_header_sec = PatternFill(start_color='2F5597', end_color='2F5597', fill_type='solid')
    fill_failed = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
    font_failed = Font(name=FONT_NAME, size=9, bold=True, color='9C0006')
    fill_passed = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
    font_passed = Font(name=FONT_NAME, size=9, bold=True, color='006100')
    fill_zebra = PatternFill(start_color='F9F9F9', end_color='F9F9F9', fill_type='solid')
    
    thin_side = Side(border_style='thin', color='D9D9D9')
    border_cell = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    border_failed = Border(
        left=Side(border_style='thin', color='FF8080'),
        right=Side(border_style='thin', color='FF8080'),
        top=Side(border_style='thin', color='FF8080'),
        bottom=Side(border_style='thin', color='FF8080')
    )

    # ----------------- SHEET 1: KetQua_Validation_ChiTiet -----------------
    ws1 = wb.active
    ws1.title = 'KetQua_Validation_ChiTiet'
    
    ws1['A1'] = "BÁO CÁO KẾT QUẢ KIỂM TRA VÀ ĐỐI CHIẾU ĐỊA CHỈ IP CSKCB TỪ CÁC TỆP PDF"
    ws1['A1'].font = font_title
    ws1['A2'] = "Tiêu chí thẩm định: 1. Chuẩn IP Public | 2. Chuẩn định dạng IPv4 | 3. Kiểm tra trùng lặp với CSDL theo dõi"
    ws1['A2'].font = font_subtitle
    
    headers1 = [
        "STT", "Tên tệp PDF nguồn", "Mục yêu cầu", "STT PDF", "Tên cơ sở KCB",
        "Mã CSKCB", "Địa chỉ IP", "Nhà mạng", "Địa chỉ sử dụng", "Ghi chú PDF",
        "1. Định dạng IP", "2. IP Public", "3. Đối chiếu CSDL theo dõi",
        "Kết quả Validation", "Chi tiết lý do & Cảnh báo"
    ]
    
    row_start = 4
    for col_idx, h in enumerate(headers1, 1):
        cell = ws1.cell(row=row_start, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = border_cell
    ws1.row_dimensions[row_start].height = 28
    
    for row_offset, r in enumerate(evaluated_records):
        cur_row = row_start + 1 + row_offset
        is_fail = (r['validation'] == 'FAILED')
        
        row_values = [
            r['stt'],
            r['file'],
            r['section'],
            r['stt_pdf'],
            r['ten_cs'],
            r['ma_cs'],
            r['ip'],
            r['nha_mang'],
            r['dia_chi'],
            r['ghi_chu_pdf'],
            f"{r['format_status']}: {r['format_note']}",
            f"{r['public_status']}: {r['public_note']}",
            f"{r['dup_status']} ({r['dup_detail']})",
            r['validation'],
            r['reason']
        ]
        
        for c_idx, val in enumerate(row_values, 1):
            cell = ws1.cell(row=cur_row, column=c_idx, value=val)
            cell.border = border_failed if is_fail else border_cell
            
            # Text wrapping cho tất cả các cột
            if c_idx in [1, 3, 4, 6, 7]:
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            elif c_idx in [11, 12, 14]:
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
            
            if is_fail:
                cell.fill = fill_failed
                if c_idx in [1, 7, 14, 15]:
                    cell.font = font_failed
                else:
                    cell.font = Font(name=FONT_NAME, size=9, color='9C0006')
            else:
                if row_offset % 2 == 1:
                    cell.fill = fill_zebra
                cell.font = font_data
                if c_idx == 14:
                    cell.fill = fill_passed
                    cell.font = font_passed
        
        # Auto-height: không đặt cố định height để Excel tự động co giãn theo số dòng wrap
        ws1.row_dimensions[cur_row].height = None

    # ----------------- SHEET 2: TongHop_ThongKe -----------------
    ws2 = wb.create_sheet(title='TongHop_ThongKe')
    ws2['A1'] = "BẢNG TỔNG HỢP VÀ ĐÁNH GIÁ THỐNG KÊ VALIDATION"
    ws2['A1'].font = font_title
    ws2['A2'] = "Dữ liệu thẩm định từ các tệp PDF đăng ký địa chỉ IP"
    ws2['A2'].font = font_subtitle
    
    ws2['A4'] = "CHỈ SỐ TỔNG QUAN"
    ws2['A4'].font = Font(name=FONT_NAME, size=11, bold=True, color='1F4E78')
    
    passed_cnt = sum(1 for r in evaluated_records if r['validation'] == 'PASSED')
    failed_cnt = sum(1 for r in evaluated_records if r['validation'] == 'FAILED')
    total_cnt = len(evaluated_records)
    
    metrics = [
        ("Tổng số tệp PDF tiếp nhận", len(pdf_files)),
        ("Tổng số bản ghi địa chỉ IP trích xuất", total_cnt),
        ("Số bản ghi yêu cầu 'Thêm mới'", sum(1 for r in evaluated_records if r['section'] == 'Thêm mới')),
        ("Số bản ghi yêu cầu 'Hủy'", sum(1 for r in evaluated_records if r['section'] == 'Hủy')),
        ("Số bản ghi HỢP LỆ (PASSED)", passed_cnt),
        ("Số bản ghi KHÔNG ĐẠT (FAILED - BÔI ĐỎ)", failed_cnt),
        ("Tỷ lệ không đạt", f"{(failed_cnt / total_cnt * 100):.1f}%" if total_cnt > 0 else "0%")
    ]
    
    for idx, (lbl, val) in enumerate(metrics, 5):
        c_lbl = ws2.cell(row=idx, column=1, value=lbl)
        c_val = ws2.cell(row=idx, column=2, value=val)
        c_lbl.font = font_data
        c_lbl.border = border_cell
        c_lbl.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        c_val.font = font_bold
        c_val.alignment = Alignment(horizontal='center', vertical='center')
        c_val.border = border_cell
        if "FAILED" in lbl:
            c_lbl.fill = fill_failed
            c_lbl.font = font_failed
            c_val.fill = fill_failed
            c_val.font = font_failed
        elif "PASSED" in lbl:
            c_lbl.fill = fill_passed
            c_lbl.font = font_passed
            c_val.fill = fill_passed
            c_val.font = font_passed
        elif idx % 2 == 1:
            c_lbl.fill = fill_zebra
            c_val.fill = fill_zebra
        ws2.row_dimensions[idx].height = None

    # Bảng tiêu chí
    ws2['A14'] = "KẾT QUẢ ĐÁNH GIÁ THEO TỪNG TIÊU CHÍ"
    ws2['A14'].font = Font(name=FONT_NAME, size=11, bold=True, color='1F4E78')
    
    crit_headers = ["STT", "Tiêu chí kiểm tra", "Số lượng Đạt", "Số lượng Lỗi / Vi phạm", "Đánh giá chi tiết"]
    for c_idx, h in enumerate(crit_headers, 1):
        c = ws2.cell(row=15, column=c_idx, value=h)
        c.font = font_header
        c.fill = fill_header_sec
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = border_cell
    ws2.row_dimensions[15].height = 25
    
    format_pass = sum(1 for r in evaluated_records if r['format_status'] == 'ĐẠT')
    public_pass = sum(1 for r in evaluated_records if r['public_status'] == 'ĐẠT')
    dup_fail = sum(1 for r in evaluated_records if any(k in r['reason'] for k in ['Trùng lặp', 'Xung đột', 'Bất thường', 'SAI LỆCH']))
    
    crit_rows = [
        (1, "1. Chuẩn định dạng IP (IPv4 4-octet, 0-255)", format_pass, total_cnt - format_pass, "Tất cả địa chỉ IP trích xuất đều đúng cú pháp IPv4 chuẩn."),
        (2, "2. Chuẩn IP Public (không cho phép IP Private/Local)", public_pass, total_cnt - public_pass, "Tất cả địa chỉ IP đều là IP Public toàn cầu hợp lệ."),
        (3, "3. Trùng lặp với dữ liệu đăng ký trước đó", total_cnt - dup_fail, dup_fail, "Phát hiện các bản ghi trùng lặp IP đã cấp hoặc sai lệch đơn vị khi hủy."),
        (4, "4. Tính đầy đủ hồ sơ (Mã cơ sở KCB)", sum(1 for r in evaluated_records if r['ma_cs']), sum(1 for r in evaluated_records if not r['ma_cs']), "Kiểm tra sự hiện diện của Mã CSKCB trong hồ sơ.")
    ]
    
    for r_offset, r_data in enumerate(crit_rows):
        cur_r = 16 + r_offset
        for c_i, val in enumerate(r_data, 1):
            cell = ws2.cell(row=cur_r, column=c_i, value=val)
            cell.font = font_data
            cell.border = border_cell
            if c_i in [1, 3, 4]:
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
            if c_i == 4 and val > 0:
                cell.fill = fill_failed
                cell.font = font_failed
        ws2.row_dimensions[cur_r].height = None

    # Bảng các bản ghi Failed
    ws2['A22'] = "DANH SÁCH BẢN GHI VALIDATION FAILED (CẦN XỬ LÝ / TỪ CHỐI)"
    ws2['A22'].font = Font(name=FONT_NAME, size=11, bold=True, color='9C0006')
    
    fail_hdrs = ["STT", "Tên tệp PDF", "Mục", "Tên cơ sở KCB", "Mã CSKCB", "Địa chỉ IP", "Lý do Validation FAILED & Chi tiết vi phạm"]
    for c_idx, h in enumerate(fail_hdrs, 1):
        c = ws2.cell(row=23, column=c_idx, value=h)
        c.font = font_header
        c.fill = PatternFill(start_color='C00000', end_color='C00000', fill_type='solid')
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = border_cell
    ws2.row_dimensions[23].height = 25
    
    failed_list = [r for r in evaluated_records if r['validation'] == 'FAILED']
    for f_idx, r in enumerate(failed_list, 1):
        cur_r = 24 + f_idx
        f_vals = [f_idx, r['file'], r['section'], r['ten_cs'], r['ma_cs'] if r['ma_cs'] else '(BỊ THIẾU)', r['ip'], r['reason']]
        for c_i, val in enumerate(f_vals, 1):
            cell = ws2.cell(row=cur_r, column=c_i, value=val)
            cell.fill = fill_failed
            cell.font = font_failed if c_i in [1, 6, 7] else Font(name=FONT_NAME, size=9, color='9C0006')
            cell.border = border_failed
            if c_i in [1, 3, 5, 6]:
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        ws2.row_dimensions[cur_r].height = None

    # ----------------- SHEET 3: TraCuu_LichSu_CSDL -----------------
    ws3 = wb.create_sheet(title='TraCuu_LichSu_CSDL')
    ws3['A1'] = "TRA CỨU CHI TIẾT DÒNG DỮ LIỆU ĐỐI CHIẾU TRONG FILE THEO DÕI HỆ THỐNG"
    ws3['A1'].font = font_title
    ws3['A2'] = "Sheet IP_CSKCB trong tệp theo dõi hệ thống (đối chiếu cho từng địa chỉ IP thẩm định)"
    ws3['A2'].font = font_subtitle
    
    headers3 = [
        'STT', 'Địa chỉ IP', 'Dòng trong file theo dõi', 'Tỉnh / Thành phố',
        'Tên CSKCB trong CSDL', 'Mã CSKCB', 'Nhà mạng', 'Địa chỉ đơn vị',
        'Loại (Add/Hủy)', 'Số Công văn', 'Phân loại dữ liệu', 'Ghi chú đối chiếu'
    ]
    
    for c_idx, h in enumerate(headers3, 1):
        c = ws3.cell(row=4, column=c_idx, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = border_cell
    ws3.row_dimensions[4].height = 28
    
    cur_r = 5
    stt_c = 1
    unique_ips = []
    for r in evaluated_records:
        if r['ip'] and r['ip'] not in unique_ips:
            unique_ips.append(r['ip'])
            
    for ip in unique_ips:
        matches = all_history.get(ip, [])
        if matches:
            for m in matches:
                is_prior = (m['row'] < 27948)
                phan_loai = 'Dữ liệu lịch sử trước đây (row < 27948)' if is_prior else 'Đợt cập nhật tiếp nhận gần đây (row >= 27948)'
                ghichu = 'CẢNH BÁO: Đã tồn tại trong hệ thống trước đợt T9/2026' if is_prior else 'Đã nhập vào cuối file theo dõi'
                
                r_data = [
                    stt_c, ip, m['row'], m['tinh'], m['ten_cs'], m['ma_cs'],
                    m['nha_mang'], m['dia_chi'], m['loai'], m['so_cv'], phan_loai, ghichu
                ]
                for c_i, val in enumerate(r_data, 1):
                    cell = ws3.cell(row=cur_r, column=c_i, value=val)
                    cell.border = border_cell
                    if is_prior:
                        cell.fill = fill_failed
                        cell.font = font_failed if c_i in [2, 11, 12] else Font(name=FONT_NAME, size=9, color='9C0006')
                    else:
                        if cur_r % 2 == 1:
                            cell.fill = fill_zebra
                        cell.font = font_data
                    if c_i in [1, 2, 3, 6, 9, 10]:
                        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                    else:
                        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
                ws3.row_dimensions[cur_r].height = None
                cur_r += 1
                stt_c += 1
        else:
            r_data = [
                stt_c, ip, 'Không tìm thấy', '-', '-', '-', '-', '-', '-', '-',
                'Chưa có trong hệ thống (Mới hoàn toàn)', 'IP mới 100%, chưa từng xuất hiện trong tập theo dõi'
            ]
            for c_i, val in enumerate(r_data, 1):
                cell = ws3.cell(row=cur_r, column=c_i, value=val)
                cell.font = font_passed if c_i in [2, 11, 12] else font_data
                cell.fill = fill_passed if c_i in [11, 12] else fill_zebra
                cell.border = border_cell
                if c_i in [1, 2, 3]:
                    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                else:
                    cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
            ws3.row_dimensions[cur_r].height = None
            cur_r += 1
            stt_c += 1

    # Điều chỉnh độ rộng cột tối ưu
    ws1.column_dimensions['A'].width = 6
    ws1.column_dimensions['B'].width = 26
    ws1.column_dimensions['C'].width = 12
    ws1.column_dimensions['D'].width = 8
    ws1.column_dimensions['E'].width = 35
    ws1.column_dimensions['F'].width = 12
    ws1.column_dimensions['G'].width = 16
    ws1.column_dimensions['H'].width = 18
    ws1.column_dimensions['I'].width = 35
    ws1.column_dimensions['J'].width = 12
    ws1.column_dimensions['K'].width = 22
    ws1.column_dimensions['L'].width = 22
    ws1.column_dimensions['M'].width = 35
    ws1.column_dimensions['N'].width = 16
    ws1.column_dimensions['O'].width = 45

    ws2.column_dimensions['A'].width = 36
    ws2.column_dimensions['B'].width = 28
    ws2.column_dimensions['C'].width = 14
    ws2.column_dimensions['D'].width = 22
    ws2.column_dimensions['E'].width = 14
    ws2.column_dimensions['F'].width = 16
    ws2.column_dimensions['G'].width = 50

    ws3.column_dimensions['A'].width = 6
    ws3.column_dimensions['B'].width = 16
    ws3.column_dimensions['C'].width = 14
    ws3.column_dimensions['D'].width = 16
    ws3.column_dimensions['E'].width = 36
    ws3.column_dimensions['F'].width = 12
    ws3.column_dimensions['G'].width = 16
    ws3.column_dimensions['H'].width = 35
    ws3.column_dimensions['I'].width = 14
    ws3.column_dimensions['J'].width = 22
    ws3.column_dimensions['K'].width = 30
    ws3.column_dimensions['L'].width = 45

    wb.save(output_path)
    print(f"[*] Xuất báo cáo Excel thành công: {output_path}")

def run_filter(pdf_dir, tracker_path=None, output_path=None):
    """Hàm wrapper chạy toàn bộ quy trình kiểm tra và tạo báo cáo."""
    if not os.path.exists(pdf_dir):
        raise FileNotFoundError(f"Không tìm thấy thư mục: {pdf_dir}")
    
    if not output_path:
        output_path = os.path.join(pdf_dir, 'KetQua_KiemTra_IP_CSKCB.xlsx')
    
    if not tracker_path:
        tracker_path = find_tracker_file([
            pdf_dir,
            os.path.dirname(pdf_dir),
            os.getcwd()
        ])
    
    all_history, batch_start_row = load_tracking_data(tracker_path)
    raw_records, pdf_files = extract_pdf_records(pdf_dir)
    evaluated_records = validate_records(raw_records, all_history, batch_start_row)
    export_excel_report(evaluated_records, pdf_files, all_history, output_path)
    return output_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Skill qnet-filter-pdf: Đọc PDF hồ sơ đăng ký IP, kiểm tra định dạng, IP Public, trùng lặp và xuất Excel.")
    parser.add_argument('--input-dir', '-i', required=True, help="Thư mục chứa các tệp PDF cần kiểm tra")
    parser.add_argument('--tracker-file', '-t', default=None, help="Đường dẫn tệp Excel theo dõi hệ thống (IP_CSKCB_INTERNET - VPN.xlsx)")
    parser.add_argument('--output', '-o', default=None, help="Đường dẫn tệp Excel báo cáo đầu ra")
    
    args = parser.parse_args()
    out = run_filter(args.input_dir, args.tracker_file, args.output)
    print(f"[HOÀN TẤT] File kết quả: {out}")
