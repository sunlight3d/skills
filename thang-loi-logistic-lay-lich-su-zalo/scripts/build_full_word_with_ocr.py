#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import os
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def generate_word_document(
    chat_entries,
    output_dir="/Users/hoangnd/Downloads/Lich_Su_Chat_COLE_KHOA_HOC_UNG_DUNG_AI_LOGISTIC",
    doc_filename="Lich_Su_Chat_COLE_KHOA_HOC_UNG_DUNG_AI_LOGISTIC.docx"
):
    os.makedirs(output_dir, exist_ok=True)
    
    ocr_data = {
        "Anh_01_DanhSach_HocVien_ThangLoi_1.jpg": {
            "title": "Bảng danh sách học viên Công ty Cổ phần Dịch vụ Logistics Thắng Lợi (Phần 1)",
            "details": [
                "Dòng 11: Bộ phận Kế toán | Đặng Thu Hằng | Nhân viên | SĐT: 0365974981 | Email: acc01@thangloilogistics.vn",
                "Dòng 12: Bộ phận Kế toán | Bùi Huyền Trang | Nhân viên | SĐT: 0962378832 | Email: acc08@thangloilogistics.vn",
                "Dòng 13: Bộ phận Kế toán | Ngô Thị Uyên | Nhân viên | SĐT: 0374150526 | Email: acc02@thangloilogistics.vn",
                "Dòng 14: Bộ phận Kế toán | Phùng Kim Chi | Nhân viên | SĐT: 0932319495 | Email: kimchi@thangloilogistics.vn",
                "Dòng 15: Bộ phận Tờ khai | Ngô Dịu Hương | Nhân viên | SĐT: 0962862000 | Email: doc13@thangloilogistics.vn",
                "Dòng 16: Bộ phận Tờ khai | Trần Thanh Thủy | Nhân viên | SĐT: 0971575557 | Email: thuytran@thangloilogistics.vn",
                "Dòng 17 (Đang highlight): Bộ phận Tờ khai | Phạm Hồng Quân | Nhân viên | SĐT: 0796008822 | Email: doc7@thangloilogistics.vn",
                "Dòng 18: Bộ phận Tờ khai | Hỏa Thị Thanh Xuân | Nhân viên | SĐT: 0981491819 | Email: doc4@thangloilogistics.vn",
                "Dòng 19: Bộ phận Tờ khai | Phạm Thùy Dương | Nhân viên | SĐT: 0986866777 | Email: duongpham@thangloilogistics.vn",
                "Dòng 20: Bộ phận Tờ khai | Nguyễn Thúy Uyển Nhi | Nhân viên | SĐT: 0965475532 | Email: minguyen@thangloilogistics.vn",
                "Dòng 21: Bộ phận Tờ khai | Vũ Thị Thương Huyền | Nhân viên | SĐT: 0983270335 | Email: doc6@thangloilogistics.vn",
                "Dòng 22: Bộ phận Tờ khai | Nguyễn Thị Phương Lan | Nhân viên | SĐT: 0976377127 | Email: lannguyen@thangloilogistics.vn",
                "Dòng 23: Bộ phận Tờ khai | Phạm Thị May | Nhân viên | SĐT: 0343197894 | Email: doc1@thangloilogistics.vn"
            ]
        },
        "Anh_02_Loi_DoiMatKhau_LMS.jpg": {
            "title": "Ảnh chụp màn hình lỗi giao diện đổi mật khẩu trên hệ thống COLE LMS",
            "details": [
                "Đường dẫn truy cập: https://lms.cole.vn/student-portal/profile?tab=password",
                "Tài khoản học viên đang thao tác: Nguyễn Thị Nhài (Học viên)",
                "Thông báo lỗi: 'COLE LMS - Trang đang gặp sự cố. Hệ thống chưa mở được màn hình này. Bạn có thể thử tải lại trang, hoặc quay về trang chủ để tiếp tục làm việc.'",
                "Mã lỗi kỹ thuật (JavaScript Error): NotFoundError: Failed to execute 'insertBefore' on 'Node': The node before which the new node is to be inserted is not a child of this node.",
                "Hotline hỗ trợ kỹ thuật hiển thị: 0869 810 635 / 0862 085 989",
                "Thời điểm ghi nhận trên máy: 13:23 CH ngày 20/11/2026"
            ]
        },
        "Anh_03_DanhSach_HocVien_ThangLoi_2.jpg": {
            "title": "Bảng danh sách học viên Thắng Lợi Logistics bổ sung lãnh đạo tham gia khóa học (Phần 2)",
            "details": [
                "Dòng 23: Bộ phận Tờ khai | Nguyễn Nam Anh | Nhân viên | SĐT: 0989380284 | Email: doc11@thangloilogistics.vn",
                "Dòng 24: Bộ phận Tờ khai | Nguyễn Thị Trà My | Nhân viên | SĐT: 0962081236 | Email: mynguyen@thangloilogistics.vn",
                "Dòng 25: Bộ phận Tờ khai | Dương Thị Hương | Nhân viên | SĐT: 0948891589 | Email: huongduong@thangloilogistics.vn",
                "Dòng 26: Bộ phận Tờ khai | Vũ Thị Như Huệ | Nhân viên | SĐT: 0979549864 | Email: doc12@thangloilogistics.vn",
                "Dòng 27: Chi nhánh Hà Nam | Nguyễn Hữu Dũng | Nhân viên | SĐT: 0915557828 | Email: ophanam@thangloilogistics.vn",
                "Dòng 28: Chi nhánh Hà Nam | Đinh Quốc Huy | Nhân viên | SĐT: 0902910333 | Email: vncs04@thangloilogistics.vn",
                "Dòng 29: Sau thông quan | Nguyễn Thị Nhài | Nhân viên | SĐT: 0333639729 | Email: nhainguyen@thangloilogistics.vn",
                "Dòng 30: Sau thông quan | Hồ Diễm Ly | Nhân viên | SĐT: 0762186207 | Email: diemly@thangloilogistics.vn",
                "Dòng 31: Bộ phận Tờ khai | Hoàng Trọng Nghĩa | Nhân viên | SĐT: 0968986048 | Email: doc8@thangloilogistics.vn",
                "Dòng 32: Bộ phận Kế toán | Phạm Thị Lự | Kế toán trưởng (KTT) | SĐT: 0942709898 | Email: lupham@thangloilogistics.vn",
                "Dòng 33: Bộ phận Tờ khai | Nguyễn Quỳnh Hương | Nhân viên | SĐT: 0354235589 | Email: doc9@thangloilogistics.vn",
                "Dòng 34: Chi nhánh Hải Phòng | Lê Thị Phương Thúy | Nhân viên | SĐT: 0949026215 | Email: acc7@thangloilogistics.vn",
                "Dòng 35: Chi nhánh Hải Phòng | Phan Thùy Dung | Nhân viên | SĐT: 0911022863 | Email: acc6@thangloilogistics.vn",
                "Dòng 36 (Khoanh viền đỏ bổ sung): Ban Giám đốc | Ngô Minh Hải | Giám đốc | SĐT: 0912317585 | Email: hai.ngo@thangloilogistics.vn"
            ]
        },
        "Anh_04_Slide_KhaiMac_KhoaHoc.jpg": {
            "title": "Slide bài giảng khai mạc khóa đào tạo ứng dụng AI",
            "details": [
                "Đơn vị tổ chức: Trung tâm Đào tạo COLE (Logo COLE)",
                "Chương trình: KHÓA ĐÀO TẠO DOANH NGHIỆP: Ứng dụng AI trong nghiệp vụ Logistics",
                "Doanh nghiệp đào tạo: Dành cho Công ty CP Dịch vụ Logistics Thắng Lợi",
                "Giảng viên giảng dạy: Thầy Nguyễn Đức Hoàng",
                "Năm đào tạo: Trung tâm Đào tạo COLE · 2026"
            ]
        },
        "Anh_05_RustDesk_DoHongHanh.jpg": {
            "title": "Thông tin kết nối điều khiển máy tính từ xa RustDesk (Đỗ Hồng Hạnh)",
            "details": [
                "Phần mềm: RustDesk Remote Desktop",
                "ID kết nối từ xa: 465 159 518",
                "Mật khẩu một lần (One-time password): 57qjsv",
                "Mục đích: Cho phép Giảng viên kết nối trực tiếp vào máy tính của học viên để hỗ trợ thực hành trên dữ liệu thực tế."
            ]
        },
        "Anh_06_RustDesk_Remote.jpg": {
            "title": "Thông tin kết nối điều khiển máy tính từ xa RustDesk (Máy học viên thứ 2)",
            "details": [
                "Phần mềm: RustDesk Remote Desktop",
                "ID kết nối từ xa: 80 703 179",
                "Mật khẩu một lần (One-time password): 4vzihw",
                "Trạng thái: Ready, chờ giảng viên kết nối hỗ trợ kỹ thuật."
            ]
        },
        "Anh_07_Teams_PhongCho_DoHongHanh.jpg": {
            "title": "Thông báo phòng chờ Microsoft Teams (Học viên Đỗ Hồng Hạnh)",
            "details": [
                "Ứng dụng: Microsoft Teams",
                "Nội dung thông báo: 'Xin chào ĐỖ HỒNG HẠNH_ĐIỀU HÀNH. Khi cuộc họp bắt đầu, sẽ có người cho bạn vào. Cuộc họp trong Microsoft Teams.'",
                "Thời điểm: 08:31 sáng ngày 22/11/2026 (Học viên đang đợi admin duyệt vào phòng học)."
            ]
        },
        "Anh_08_Teams_PhongCho_NguyenDucHoang.jpg": {
            "title": "Thông báo phòng chờ Microsoft Teams (Giảng viên Nguyễn Đức Hoàng)",
            "details": [
                "Ứng dụng: Microsoft Teams meeting",
                "Nội dung thông báo: 'Hi, Nguyen Duc Hoang. Someone will let you in when the meeting starts. Microsoft Teams meeting.'",
                "Thiết bị âm thanh đã kết nối: Yeti Stereo Microphone (Microphone bật, Camera chưa kết nối).",
                "Ghi chú: Giảng viên cũng bị giữ ở phòng chờ do phía điều phối gặp sự cố cấp quyền duyệt."
            ]
        },
        "Anh_09_Teams_PhongCho_LeVanDien.jpg": {
            "title": "Thông báo phòng chờ Microsoft Teams (Học viên Lê Văn Diễn)",
            "details": [
                "Ứng dụng: Microsoft Teams",
                "Nội dung thông báo: 'Xin chào Lê Văn Diễn. Khi cuộc họp bắt đầu, sẽ có người cho bạn vào. Cuộc họp trong Microsoft Teams.'",
                "Thời điểm: 08:32 sáng ngày 22/11/2026."
            ]
        },
        "Anh_10_Teams_PhongCho_VietAnh.jpg": {
            "title": "Màn hình ứng dụng Microsoft Teams trên di động (Học viên Việt Anh)",
            "details": [
                "Ứng dụng: Microsoft Teams Mobile",
                "Thời gian trên máy: 08:38",
                "Nội dung thông báo: 'Cuộc họp. Xin chào Việt Anh, một thành viên của cuộc họp sẽ sớm cho phép bạn tham gia.'",
                "Tình trạng thiết bị: Micro đang tắt, Video đang tắt."
            ]
        },
        "Anh_11_Teams_PhongCho_PhamAnhTai.jpg": {
            "title": "Màn hình ứng dụng Microsoft Teams trên iPhone (Học viên Phạm Anh Tài)",
            "details": [
                "Ứng dụng: Microsoft Teams trên iOS",
                "Thời gian trên máy: 08:39",
                "Nội dung thông báo: 'Cuộc họp. Một người nào đó trong cuộc họp sẽ sớm cho phép bạn vào.'",
                "Avatar hiển thị: T (Thangloi Logistics)."
            ]
        },
        "Anh_12_Teams_PhongCho_PhamAnhTai_2.jpg": {
            "title": "Màn hình ứng dụng Microsoft Teams trên iPhone (Học viên Phạm Anh Tài - Nhắc lại)",
            "details": [
                "Thời gian trên máy: 08:50",
                "Trạng thái: Vẫn đang ở phòng chờ Teams trước khi chuyển sang link Google Meet dự phòng của Giảng viên."
            ]
        }
    }

    attached_txt_path = os.path.join(output_dir, "File_DinhKem_01_Note_Bai_Hoc_Ngay_21_11_2026.txt")
    attached_file_content = ""
    if os.path.exists(attached_txt_path):
        with open(attached_txt_path, "r", encoding="utf-8") as f:
            attached_file_content = f.read()

    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    COLOR_NAVY = RGBColor(31, 78, 121)
    COLOR_BLUE = RGBColor(47, 85, 151)
    COLOR_TEACHER = RGBColor(180, 40, 40)
    COLOR_COLE = RGBColor(25, 111, 61)
    COLOR_STUDENT = RGBColor(46, 64, 83)
    COLOR_GRAY = RGBColor(108, 117, 125)
    COLOR_DARK = RGBColor(33, 37, 41)

    def set_cell_shading(cell, color_hex):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def set_cell_borders(cell, top="none", bottom="none", left="none", right="none", 
                         color="CCCCCC", sz="4"):
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
        for b_name, b_val in borders.items():
            b_elm = OxmlElement(f'w:{b_name}')
            b_elm.set(qn('w:val'), b_val)
            if b_val != "none":
                b_elm.set(qn('w:sz'), sz)
                b_elm.set(qn('w:space'), '0')
                b_elm.set(qn('w:color'), color)
            tcBorders.append(b_elm)
        tcPr.append(tcBorders)

    # 1. Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("BÁO CÁO LỊCH SỬ HỘI THOẠI & DỮ LIỆU ĐÍNH KÈM NHÓM ZALO")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("COLE_KHÓA HỌC ỨNG DỤNG AI TRONG NGHIỆP VỤ LOGISTIC")
    r_sub.bold = True
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(12.5)
    r_sub.font.color.rgb = COLOR_BLUE

    # 2. Metadata Box Table
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    col_widths = [Inches(2.2), Inches(4.6)]
    for row in meta_table.rows:
        for idx_w, width in enumerate(col_widths):
            row.cells[idx_w].width = width

    meta_data = [
        ("Tên nhóm Zalo:", "COLE_KHÓA HỌC ỨNG DỤNG AI TRONG NGHIỆP VỤ LOGISTIC"),
        ("Đơn vị đào tạo & Tổ chức:", "Trung tâm Đào tạo COLE"),
        ("Doanh nghiệp tham gia:", "Công ty Cổ phần Dịch vụ Logistics Thắng Lợi"),
        ("Giảng viên phụ trách:", "Thầy Nguyễn Đức Hoàng (Kỹ sư ĐHBK HN, Chuyên gia AI/Data)"),
        ("Điều phối khóa học:", "Hiền Quách & Cole (Hỗ trợ học viên, LMS, Lớp học)"),
        ("Quy mô & Thư mục đính kèm:", "42 thành viên • Toàn bộ 12 ảnh & 1 file đính kèm lưu tại thư mục cùng tên")
    ]

    for row_idx, (label, val) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        c0 = row.cells[0]
        set_cell_shading(c0, "F0F4F8")
        set_cell_margins(c0, top=70, bottom=70, left=120, right=100)
        set_cell_borders(c0, top="single", bottom="single", left="single", right="single", color="D0D7DE", sz="4")
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = "Arial"
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = COLOR_NAVY
        
        c1 = row.cells[1]
        set_cell_shading(c1, "FFFFFF" if row_idx % 2 == 0 else "F9FAFC")
        set_cell_margins(c1, top=70, bottom=70, left=120, right=100)
        set_cell_borders(c1, top="single", bottom="single", left="single", right="single", color="D0D7DE", sz="4")
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.name = "Arial"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 3. Pinned Info
    pin_table = doc.add_table(rows=1, cols=1)
    pin_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    pin_table.autofit = False
    pin_cell = pin_table.rows[0].cells[0]
    pin_cell.width = Inches(6.8)
    set_cell_shading(pin_cell, "EBF3FA")
    set_cell_margins(pin_cell, top=140, bottom=140, left=180, right=180)
    set_cell_borders(pin_cell, top="single", bottom="single", left="single", right="single", color="2F5597", sz="12")

    p_pin_title = pin_cell.paragraphs[0]
    p_pin_title.paragraph_format.space_before = Pt(0)
    p_pin_title.paragraph_format.space_after = Pt(6)
    r_pin_h = p_pin_title.add_run("📌 THÔNG TIN QUAN TRỌNG & NỘI DUNG GHIM ĐẦU NHÓM")
    r_pin_h.bold = True
    r_pin_h.font.name = "Arial"
    r_pin_h.font.size = Pt(11)
    r_pin_h.font.color.rgb = COLOR_NAVY

    pin_bullets = [
        ("🗓️ Lịch học chính thức: ", "08:00 – 10:00 sáng Thứ Bảy & Chủ nhật hằng tuần."),
        ("💻 Hệ thống học tập LMS: ", "https://lms.cole.vn/student-portal"),
        ("👤 Tài khoản & Mật khẩu mặc định: ", "Tên đăng nhập: Email đăng ký • Mật khẩu mặc định: ColeVN2026 (yêu cầu đổi mật khẩu sau lần đăng nhập đầu tiên)."),
        ("📖 Video hướng dẫn đăng nhập LMS: ", "https://drive.google.com/file/d/1ckU9EXOAyWxGWsm2LDcpYyrheRAPZGm_/view"),
        ("🎥 Video ghi hình & Note buổi học Bài 1 (21/11): ", "https://drive.google.com/drive/u/0/folders/1GboKYAyuypXyqzbHgsAwhTgMu8OiXKlf"),
        ("📂 Thư mục tài liệu thực hành Bài 2 (22/11): ", "https://drive.google.com/drive/u/0/folders/1TbdsMg5AcgZL9VkQ99_Tpka4HTOmHW3i"),
        ("🔗 Kênh học trực tuyến Microsoft Teams: ", "https://teams.microsoft.com/meet/45218490918599?p=pErSz0CN9OxUTfktfR (ID: 452 184 909 185 99 | Mã: pT9tj2m6)"),
        ("🔗 Kênh học dự phòng Google Meet: ", "https://meet.google.com/xnm-veor-szs")
    ]

    for label, val in pin_bullets:
        p_b = pin_cell.add_paragraph()
        p_b.paragraph_format.space_before = Pt(2)
        p_b.paragraph_format.space_after = Pt(2)
        p_b.paragraph_format.left_indent = Inches(0.2)
        r_lbl = p_b.add_run(label)
        r_lbl.bold = True
        r_lbl.font.name = "Arial"
        r_lbl.font.size = Pt(9.5)
        r_lbl.font.color.rgb = COLOR_NAVY
        r_val = p_b.add_run(val)
        r_val.font.name = "Arial"
        r_val.font.size = Pt(9.5)
        r_val.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    def get_sender_style(sender_name):
        if "Nguyễn Đức Hoàng" in sender_name or "Nguyen Duc Hoang" in sender_name:
            return "Thầy Nguyễn Đức Hoàng [Giảng viên]", COLOR_TEACHER, "Giảng viên"
        elif sender_name in ["Hiền Quách", "Cole"]:
            return f"{sender_name} [Ban tổ chức COLE]", COLOR_COLE, "Ban tổ chức"
        else:
            return f"{sender_name} [Học viên Thắng Lợi Logistics]", COLOR_STUDENT, "Học viên"

    def insert_ocr_box(cell, ocr_info, img_filename):
        ocr_tbl = cell.add_table(rows=1, cols=1)
        ocr_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        ocr_tbl.autofit = False
        oc = ocr_tbl.rows[0].cells[0]
        oc.width = Inches(6.5)
        set_cell_shading(oc, "FFFDF5")
        set_cell_margins(oc, top=80, bottom=80, left=120, right=120)
        set_cell_borders(oc, top="single", bottom="single", left="single", right="single", color="E0A800", sz="6")
        
        p_h = oc.paragraphs[0]
        p_h.paragraph_format.space_before = Pt(0)
        p_h.paragraph_format.space_after = Pt(3)
        r_h = p_h.add_run(f"🔍 THÔNG TIN TRÍCH XUẤT TỪ HÌNH ẢNH ({img_filename})")
        r_h.bold = True
        r_h.font.name = "Arial"
        r_h.font.size = Pt(9)
        r_h.font.color.rgb = RGBColor(160, 100, 0)
        
        p_t = oc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(1)
        p_t.paragraph_format.space_after = Pt(2)
        r_t = p_t.add_run(f"Nội dung: {ocr_info['title']}")
        r_t.bold = True
        r_t.font.name = "Arial"
        r_t.font.size = Pt(9)
        r_t.font.color.rgb = COLOR_DARK
        
        for detail in ocr_info["details"]:
            p_d = oc.add_paragraph()
            p_d.paragraph_format.space_before = Pt(1)
            p_d.paragraph_format.space_after = Pt(1)
            p_d.paragraph_format.left_indent = Inches(0.15)
            r_d = p_d.add_run(f"• {detail}")
            r_d.font.name = "Arial"
            r_d.font.size = Pt(8.5)
            r_d.font.color.rgb = COLOR_DARK

    def insert_file_box(cell, filename, content):
        f_tbl = cell.add_table(rows=1, cols=1)
        f_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        f_tbl.autofit = False
        fc = f_tbl.rows[0].cells[0]
        fc.width = Inches(6.5)
        set_cell_shading(fc, "F4F8FA")
        set_cell_margins(fc, top=90, bottom=90, left=130, right=130)
        set_cell_borders(fc, top="single", bottom="single", left="single", right="single", color="1F4E79", sz="8")
        
        p_h = fc.paragraphs[0]
        p_h.paragraph_format.space_before = Pt(0)
        p_h.paragraph_format.space_after = Pt(4)
        r_h = p_h.add_run(f"📎 TỆP ĐÍNH KÈM ĐÃ TẢI VỀ THƯ MỤC: {filename}")
        r_h.bold = True
        r_h.font.name = "Arial"
        r_h.font.size = Pt(9.5)
        r_h.font.color.rgb = COLOR_NAVY
        
        p_c = fc.add_paragraph()
        p_c.paragraph_format.space_before = Pt(2)
        p_c.paragraph_format.space_after = Pt(2)
        r_c = p_c.add_run("Nội dung chi tiết trong file:")
        r_c.bold = True
        r_c.italic = True
        r_c.font.name = "Arial"
        r_c.font.size = Pt(8.5)
        r_c.font.color.rgb = COLOR_GRAY
        
        for line in content.split("\n"):
            if not line.strip(): continue
            p_l = fc.add_paragraph()
            p_l.paragraph_format.space_before = Pt(1)
            p_l.paragraph_format.space_after = Pt(1)
            p_l.paragraph_format.left_indent = Inches(0.15)
            r_l = p_l.add_run(line.strip())
            r_l.font.name = "Courier New"
            r_l.font.size = Pt(8)
            r_l.font.color.rgb = COLOR_DARK

    image_schedule = {
        19: "Anh_01_DanhSach_HocVien_ThangLoi_1.jpg",
        27: "Anh_02_Loi_DoiMatKhau_LMS.jpg",
        43: "Anh_03_DanhSach_HocVien_ThangLoi_2.jpg",
        54: "Anh_04_Slide_KhaiMac_KhoaHoc.jpg",
        72: "Anh_05_RustDesk_DoHongHanh.jpg",
        87: "Anh_06_RustDesk_Remote.jpg",
        114: "Anh_07_Teams_PhongCho_DoHongHanh.jpg",
        116: "Anh_08_Teams_PhongCho_NguyenDucHoang.jpg",
        118: "Anh_09_Teams_PhongCho_LeVanDien.jpg",
        124: "Anh_10_Teams_PhongCho_VietAnh.jpg",
        126: "Anh_11_Teams_PhongCho_PhamAnhTai.jpg",
        132: "Anh_12_Teams_PhongCho_PhamAnhTai_2.jpg"
    }

    # 4. Render Timeline Entries
    for idx, e in enumerate(chat_entries):
        if e["type"] == "DATE":
            doc.add_paragraph().paragraph_format.space_after = Pt(4)
            d_table = doc.add_table(rows=1, cols=1)
            d_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            d_cell = d_table.rows[0].cells[0]
            d_cell.width = Inches(6.8)
            set_cell_shading(d_cell, "1F4E79")
            set_cell_margins(d_cell, top=100, bottom=100, left=150, right=150)
            set_cell_borders(d_cell, top="none", bottom="none", left="none", right="none")
            
            pd = d_cell.paragraphs[0]
            pd.alignment = WD_ALIGN_PARAGRAPH.LEFT
            pd.paragraph_format.space_before = Pt(0)
            pd.paragraph_format.space_after = Pt(0)
            rd = pd.add_run(f"📅  {e['date'].upper()}")
            rd.bold = True
            rd.font.name = "Arial"
            rd.font.size = Pt(11)
            rd.font.color.rgb = RGBColor(255, 255, 255)
            doc.add_paragraph().paragraph_format.space_after = Pt(4)
            
        elif e["type"] == "SYS":
            p_sys = doc.add_paragraph()
            p_sys.paragraph_format.space_before = Pt(2)
            p_sys.paragraph_format.space_after = Pt(3)
            p_sys.paragraph_format.left_indent = Inches(0.4)
            
            r_time = p_sys.add_run(f"[{e['time']}] ")
            r_time.font.name = "Arial"
            r_time.font.size = Pt(8.5)
            r_time.font.color.rgb = COLOR_GRAY
            
            r_ico = p_sys.add_run("⚙️ ")
            r_ico.font.size = Pt(8.5)
            
            r_txt = p_sys.add_run(e["text"])
            r_txt.font.name = "Arial"
            r_txt.font.size = Pt(9)
            r_txt.italic = True
            r_txt.font.color.rgb = COLOR_GRAY
            
        elif e["type"] == "MSG":
            sender_label, sender_color, role_type = get_sender_style(e["sender"])
            
            m_table = doc.add_table(rows=1, cols=1)
            m_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            m_table.autofit = False
            m_cell = m_table.rows[0].cells[0]
            m_cell.width = Inches(6.8)
            
            if role_type == "Giảng viên":
                set_cell_shading(m_cell, "FDF8F7")
                set_cell_borders(m_cell, left="single", top="single", right="single", bottom="single", color="E8C4C4", sz="6")
            elif role_type == "Ban tổ chức":
                set_cell_shading(m_cell, "F4FAF6")
                set_cell_borders(m_cell, left="single", top="single", right="single", bottom="single", color="BFE2CD", sz="6")
            else:
                set_cell_shading(m_cell, "FAFBFC")
                set_cell_borders(m_cell, left="single", top="single", right="single", bottom="single", color="E1E4E8", sz="4")
                
            set_cell_margins(m_cell, top=80, bottom=80, left=140, right=140)
            
            p_head = m_cell.paragraphs[0]
            p_head.paragraph_format.space_before = Pt(0)
            p_head.paragraph_format.space_after = Pt(2)
            
            r_sname = p_head.add_run(sender_label)
            r_sname.bold = True
            r_sname.font.name = "Arial"
            r_sname.font.size = Pt(10)
            r_sname.font.color.rgb = sender_color
            
            r_sp = p_head.add_run("   •   ")
            r_sp.font.name = "Arial"
            r_sp.font.size = Pt(8.5)
            r_sp.font.color.rgb = COLOR_GRAY
            
            r_stime = p_head.add_run(f"Thời gian: {e['time']}")
            r_stime.font.name = "Arial"
            r_stime.font.size = Pt(8.5)
            r_stime.font.color.rgb = COLOR_GRAY
            
            if e.get("quote"):
                p_q = m_cell.add_paragraph()
                p_q.paragraph_format.space_before = Pt(2)
                p_q.paragraph_format.space_after = Pt(3)
                p_q.paragraph_format.left_indent = Inches(0.2)
                
                rq_lbl = p_q.add_run(f"↳ Trả lời @{e['quote']['sender']}: ")
                rq_lbl.bold = True
                rq_lbl.font.name = "Arial"
                rq_lbl.font.size = Pt(8.5)
                rq_lbl.font.color.rgb = COLOR_GRAY
                
                rq_txt = p_q.add_run(f'"{e["quote"]["snippet"]}"')
                rq_txt.italic = True
                rq_txt.font.name = "Arial"
                rq_txt.font.size = Pt(8.5)
                rq_txt.font.color.rgb = COLOR_GRAY
                
            p_body = m_cell.add_paragraph()
            p_body.paragraph_format.space_before = Pt(2)
            p_body.paragraph_format.space_after = Pt(2)
            
            msg_text = e["text"]
            lines = msg_text.split("\n")
            for l_idx, line in enumerate(lines):
                line_str = line.strip()
                if not line_str: continue
                if l_idx > 0:
                    p_line = m_cell.add_paragraph()
                    p_line.paragraph_format.space_before = Pt(1)
                    p_line.paragraph_format.space_after = Pt(1)
                else:
                    p_line = p_body
                    
                parts = re.split(r'(https?://[^\s]+)', line_str)
                for part in parts:
                    if re.match(r'https?://[^\s]+', part):
                        r_link = p_line.add_run(part)
                        r_link.font.name = "Arial"
                        r_link.font.size = Pt(9.5)
                        r_link.font.color.rgb = RGBColor(0, 102, 204)
                        r_link.underline = True
                    else:
                        r_text = p_line.add_run(part)
                        r_text.font.name = "Arial"
                        r_text.font.size = Pt(9.5)
                        r_text.font.color.rgb = COLOR_DARK
                        
            if idx in image_schedule:
                img_fname = image_schedule[idx]
                img_full_path = os.path.join(output_dir, img_fname)
                if os.path.exists(img_full_path):
                    p_img = m_cell.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(6)
                    p_img.paragraph_format.space_after = Pt(2)
                    run_img = p_img.add_run()
                    run_img.add_picture(img_full_path, width=Inches(5.0))
                    
                    p_cap = m_cell.add_paragraph()
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_cap.paragraph_format.space_before = Pt(1)
                    p_cap.paragraph_format.space_after = Pt(4)
                    r_cap = p_cap.add_run(f"📸 Hình ảnh: {img_fname}")
                    r_cap.italic = True
                    r_cap.font.name = "Arial"
                    r_cap.font.size = Pt(8.5)
                    r_cap.font.color.rgb = COLOR_GRAY
                    
                    if img_fname in ocr_data:
                        insert_ocr_box(m_cell, ocr_data[img_fname], img_fname)
                        
            if idx == 100 and attached_file_content:
                insert_file_box(m_cell, "File_DinhKem_01_Note_Bai_Hoc_Ngay_21_11_2026.txt", attached_file_content)
                
            if e.get("reactions"):
                p_react = m_cell.add_paragraph()
                p_react.paragraph_format.space_before = Pt(3)
                p_react.paragraph_format.space_after = Pt(0)
                r_rx = p_react.add_run(f"Cảm xúc: {'  |  '.join(e['reactions'])}")
                r_rx.font.name = "Arial"
                r_rx.font.size = Pt(8.5)
                r_rx.font.color.rgb = RGBColor(160, 80, 80)
                
            doc.add_paragraph().paragraph_format.space_after = Pt(2)

    target_docx = os.path.join(output_dir, doc_filename)
    doc.save(target_docx)
    return target_docx

if __name__ == "__main__":
    with open("/Users/hoangnd/.gemini/antigravity/brain/449aabe8-7dba-474b-984b-e173e65ebfaf/scratch/parsed_chat_clean.json", "r", encoding="utf-8") as f:
        entries = json.load(f)
    generate_word_document(entries)
