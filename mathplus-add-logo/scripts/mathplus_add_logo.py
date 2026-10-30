#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mathplus_add_logo.py: Bộ công cụ tự động chèn Logo MathPlus Academy và thông tin Thầy Dũng
vào tài liệu Word (.docx) hoặc PDF (.pdf).

Chức năng:
1. Hỗ trợ đầu vào .docx và .pdf (đơn lẻ hoặc hàng loạt cả thư mục).
2. Tự động chuyển đổi PDF sang DOCX giữ nguyên công thức, bảng, hình ảnh và định dạng.
3. Chèn nhận diện thương hiệu MathPlus Academy:
   - Header trang sau: Logo MathPlus (nguyên màu) + "Trung tâm MathPlus Academy".
   - Footer tất cả các trang: "Giáo viên: Thầy Nguyễn Văn Dũng – MathPlus Academy | Hotline: 0977 961 189" + Đánh số trang tự động.
   - Top Banner trang đầu: Khung nhận diện thương hiệu hoặc thay thế khung trường cũ thông minh.
4. Bảo toàn 100% nội dung gốc của tài liệu.
"""

import os
import sys
import argparse
import glob
from pathlib import Path

# Cấu hình encoding chuẩn utf-8 cho console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DEFAULT_CENTER_NAME = "Trung tâm MathPlus Academy"
DEFAULT_SUBTITLE = "Bồi dưỡng Toán & Luyện thi Chuyên / Đại học"
DEFAULT_TEACHER = "Thầy Nguyễn Văn Dũng"
DEFAULT_HOTLINE = "0977 961 189"
DEFAULT_WEBSITE = "mathplus.com.vn"

COLOR_BLACK = RGBColor(0, 0, 0)
COLOR_BRAND_GREEN = RGBColor(15, 138, 60) # #0F8A3C

ORG_KEYWORDS = [
    "trường", "sở gd", "phòng gd", "bộ gd", "ubnd", "thpt", "thcs",
    "đại học", "khoa", "toán học", "học viện", "trung tâm", "viện", "tổ tự nhiên"
]

def find_logo_path(custom_path=None):
    """Tìm file logo MathPlus (ưu tiên file tùy chọn -> resources -> public/images)."""
    candidates = [
        custom_path,
        os.path.join(os.path.dirname(__file__), "..", "resources", "logo.jpg"),
        os.path.join(os.path.dirname(__file__), "..", "resources", "logo.png"),
        r"C:\code\mathplus\public\images\logo.jpg",
        r"C:\code\mathplus\public\images\logo.png",
        os.path.join(os.getcwd(), "public", "images", "logo.jpg"),
    ]
    for c in candidates:
        if c and os.path.exists(c) and os.path.isfile(c):
            return os.path.abspath(c)
    return None

def convert_pdf_to_docx(pdf_path, temp_docx_path):
    """Chuyển đổi file PDF sang DOCX sử dụng pdf2docx."""
    print(f"[*] Đang chuyển đổi PDF sang DOCX: {os.path.basename(pdf_path)}...")
    from pdf2docx import Converter
    cv = Converter(pdf_path)
    cv.convert(temp_docx_path)
    cv.close()
    print(f"[+] Chuyển đổi PDF hoàn tất: {temp_docx_path}")
    return temp_docx_path

def add_page_number_field(run):
    """Thêm trường đánh số trang tự động PAGE vào Run."""
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    t1 = OxmlElement('w:instrText')
    t1.set(qn('xml:space'), 'preserve')
    t1.text = 'PAGE'
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'separate')
    fld3 = OxmlElement('w:fldChar')
    fld3.set(qn('w:fldCharType'), 'end')
    run._r.append(fld1)
    run._r.append(t1)
    run._r.append(fld2)
    run._r.append(fld3)

def add_numpages_field(run):
    """Thêm trường tổng số trang NUMPAGES vào Run."""
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    t1 = OxmlElement('w:instrText')
    t1.set(qn('xml:space'), 'preserve')
    t1.text = 'NUMPAGES'
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'separate')
    fld3 = OxmlElement('w:fldChar')
    fld3.set(qn('w:fldCharType'), 'end')
    run._r.append(fld1)
    run._r.append(t1)
    run._r.append(fld2)
    run._r.append(fld3)

def clear_header_or_footer(obj):
    """Xóa sạch bảng biểu và các đoạn văn bản trong header/footer cũ."""
    for tbl in list(obj.tables):
        tbl._element.getparent().remove(tbl._element)
    for p in list(obj.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    if obj.paragraphs:
        obj.paragraphs[0].text = ""

def remove_leading_old_headers(doc):
    """
    Xóa các dòng header cũ ở đầu văn bản (dòng trống, Họ và tên, Lớp, v.v.)
    trước khi chèn banner mới để tránh trùng lặp.
    """
    to_delete = []
    for idx, p in enumerate(doc.paragraphs[:10]):
        text = p.text.strip().lower()
        if not text:
            to_delete.append(p)
            continue
        if any(kw in text for kw in ["họ và tên", "họ  và tên"]):
            to_delete.append(p)
            continue
        if text.startswith("lớp") and ("t7" in text or "t8" in text or "tuần" in text or "…" in text or "..." in text or len(text) < 30):
            to_delete.append(p)
            continue
        break
        
    for p in to_delete:
        p._p.getparent().remove(p._p)

def format_footer(footer_obj, section=None, teacher_name=DEFAULT_TEACHER, hotline=DEFAULT_HOTLINE, center_name=DEFAULT_CENTER_NAME):
    """Tạo Footer chuẩn nhận diện MathPlus và thông tin Thầy Dũng."""
    clear_header_or_footer(footer_obj)
        
    p_f = footer_obj.paragraphs[0] if footer_obj.paragraphs else footer_obj.add_paragraph()
    p_f.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_f.paragraph_format.space_before = Pt(2)
    p_f.paragraph_format.space_after = Pt(0)
    
    # Tính toán vị trí tab stop sát lề phải của văn bản
    tab_pos = Mm(185)
    if section:
        try:
            tab_pos = section.page_width - section.left_margin - section.right_margin
        except Exception:
            pass
            
    try:
        p_f.paragraph_format.tab_stops.clear_all()
    except Exception:
        pass
    p_f.paragraph_format.tab_stops.add_tab_stop(tab_pos, WD_TAB_ALIGNMENT.RIGHT)
    
    # Đoạn text bên trái
    r_left = p_f.add_run(f"Giáo viên: {teacher_name} – {center_name}  |  Hotline: {hotline}")
    r_left.font.name = "Times New Roman"
    r_left.font.size = Pt(10.5)
    r_left.font.italic = True
    r_left.font.color.rgb = COLOR_BLACK
    
    # Nhảy tab sang phải và đánh số trang
    r_tab = p_f.add_run("\tTrang ")
    r_tab.font.name = "Times New Roman"
    r_tab.font.size = Pt(10.5)
    r_tab.font.italic = True
    r_tab.font.color.rgb = COLOR_BLACK
    
    # Trường số trang
    r_pg = p_f.add_run()
    r_pg.font.name = "Times New Roman"
    r_pg.font.size = Pt(10.5)
    r_pg.font.bold = True
    r_pg.font.color.rgb = COLOR_BLACK
    add_page_number_field(r_pg)

def format_subsequent_header(header_obj, logo_path, center_name=DEFAULT_CENTER_NAME):
    """Tạo Header ở các trang sau: Logo MathPlus + Tên Trung tâm (nghiêng, 10.5pt)."""
    clear_header_or_footer(header_obj)
        
    p_h = header_obj.paragraphs[0] if header_obj.paragraphs else header_obj.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_h.paragraph_format.space_before = Pt(0)
    p_h.paragraph_format.space_after = Pt(2)
    
    if logo_path and os.path.exists(logo_path):
        r_logo = p_h.add_run()
        try:
            r_logo.add_picture(logo_path, width=Mm(7.5))
        except Exception as e:
            print(f"[!] Cảnh báo chèn ảnh logo header: {e}")
            
    r_h = p_h.add_run(f"  {center_name}")
    r_h.font.name = "Times New Roman"
    r_h.font.size = Pt(10.5)
    r_h.font.italic = True
    r_h.font.color.rgb = COLOR_BLACK

def format_first_page_header(header_obj, logo_path, center_name=DEFAULT_CENTER_NAME, hotline=DEFAULT_HOTLINE):
    """Tạo Header ở trang đầu nếu không dùng Top Banner."""
    clear_header_or_footer(header_obj)
    p_h = header_obj.paragraphs[0] if header_obj.paragraphs else header_obj.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_h.paragraph_format.space_before = Pt(0)
    p_h.paragraph_format.space_after = Pt(2)
    
    if logo_path and os.path.exists(logo_path):
        r_logo = p_h.add_run()
        try:
            r_logo.add_picture(logo_path, width=Mm(9.0))
        except Exception:
            pass
            
    r_h = p_h.add_run(f"  {center_name}  •  Hotline: {hotline}")
    r_h.font.name = "Times New Roman"
    r_h.font.size = Pt(11)
    r_h.font.bold = True
    r_h.font.color.rgb = COLOR_BLACK

def populate_left_branding_cell(cell, logo_path, hotline=DEFAULT_HOTLINE, extra_text=None):
    """Điền nhận diện MathPlus vào ô bên trái của bảng banner."""
    for p in list(cell.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    if cell.paragraphs:
        cell.paragraphs[0].text = ""
        
    p_logo = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(0)
    p_logo.paragraph_format.space_after = Pt(2)
    
    if logo_path and os.path.exists(logo_path):
        r_l = p_logo.add_run()
        try:
            r_l.add_picture(logo_path, width=Mm(18.0))
        except Exception as e:
            print(f"[!] Lỗi chèn ảnh logo: {e}")
            
    p_info = cell.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_info.paragraph_format.space_before = Pt(1)
    p_info.paragraph_format.space_after = Pt(1)
    p_info.paragraph_format.line_spacing = 1.15
    
    r_name = p_info.add_run("TRUNG TÂM MATHPLUS ACADEMY\n")
    r_name.font.name = "Times New Roman"
    r_name.font.size = Pt(11)
    r_name.font.bold = True
    r_name.font.color.rgb = COLOR_BLACK
    
    r_sub = p_info.add_run("Bồi dưỡng Toán & Luyện thi Chuyên / ĐH\n")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_BLACK
    
    r_contact = p_info.add_run(f"Hotline: {hotline}  •  {DEFAULT_WEBSITE}")
    r_contact.font.name = "Times New Roman"
    r_contact.font.size = Pt(10)
    r_contact.font.italic = True
    r_contact.font.color.rgb = COLOR_BLACK
    
    if extra_text and extra_text.strip():
        p_extra = cell.add_paragraph()
        p_extra.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_extra.paragraph_format.space_before = Pt(2)
        p_extra.paragraph_format.space_after = Pt(0)
        p_extra.paragraph_format.line_spacing = 1.15
        r_ex = p_extra.add_run(extra_text.strip())
        r_ex.font.name = "Times New Roman"
        r_ex.font.size = Pt(10.5)
        r_ex.font.bold = True
        r_ex.font.color.rgb = COLOR_BLACK

def check_and_replace_existing_header_table(doc, logo_path, teacher_name=DEFAULT_TEACHER, hotline=DEFAULT_HOTLINE):
    """
    Kiểm tra xem trong tài liệu có các bảng tiêu đề trường/sở cũ hay không (quét qua tất cả bảng).
    Nếu có: Thay thế ô bên trái bằng logo và thông tin MathPlus, bảo tồn thông tin đề bài (Đề 1, Đề 2...),
    và bổ sung thông tin Thầy Dũng vào ô bên phải.
    Trả về True nếu có ít nhất 1 bảng được chuyển đổi.
    """
    if len(doc.tables) == 0:
        return False
        
    converted_count = 0
    for tbl in doc.tables:
        if len(tbl.rows) >= 1 and len(tbl.columns) >= 2:
            cell_0 = tbl.cell(0, 0)
            cell_0_text = cell_0.text.lower()
            if any(kw in cell_0_text for kw in ORG_KEYWORDS) or "ubnd" in cell_0_text or "phòng gd" in cell_0_text or "sở gd" in cell_0_text:
                converted_count += 1
                print(f"[*] Phát hiện bảng tiêu đề tổ chức ({converted_count}): Chuyển đổi sang nhận diện MathPlus...")
                
                # Trích xuất các dòng không thuộc tên trường/sở để bảo toàn nội dung đề thi (ví dụ: Đề 1, Đề 2, số câu hỏi...)
                raw_lines = [l.strip() for l in cell_0.text.split("\n") if l.strip()]
                extra_lines = []
                for l in raw_lines:
                    l_lower = l.lower()
                    if not any(kw in l_lower for kw in ORG_KEYWORDS) and "ubnd" not in l_lower and "cộng hòa" not in l_lower and "độc lập" not in l_lower:
                        extra_lines.append(l)
                extra_text = "\n".join(extra_lines) if extra_lines else None
                
                c_left = tbl.cell(0, 0)
                c_right = tbl.cell(0, 1)
                
                c_left.width = Mm(78)
                c_right.width = Mm(94)
                
                for c in [c_left, c_right]:
                    tcPr = c._tc.get_or_add_tcPr()
                    tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))
                    
                populate_left_branding_cell(c_left, logo_path, hotline=hotline, extra_text=extra_text)
                
                c_right_text = c_right.text
                if teacher_name not in c_right_text:
                    p_teacher = c_right.add_paragraph()
                    p_teacher.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_teacher.paragraph_format.space_before = Pt(3)
                    p_teacher.paragraph_format.space_after = Pt(1)
                    r_t = p_teacher.add_run(f"Giáo viên phụ trách: {teacher_name} – Hotline: {hotline}")
                    r_t.font.name = "Times New Roman"
                    r_t.font.size = Pt(10.5)
                    r_t.font.bold = True
                    r_t.font.color.rgb = COLOR_BLACK
                    
    return converted_count > 0

def check_and_replace_existing_header_paragraphs(doc, logo_path, teacher_name=DEFAULT_TEACHER, hotline=DEFAULT_HOTLINE, file_path=""):
    """
    Kiểm tra xem ở đầu văn bản có tiêu đề trường/sở ở dạng các đoạn văn bản (paragraphs)
    hoặc tiêu đề đáp án bên thứ ba (ví dụ TOANMATH) hay không.
    Nếu có: Thay thế bằng bảng nhận diện thương hiệu MathPlus.
    """
    if not doc.paragraphs:
        return False
        
    folder_name = os.path.basename(os.path.dirname(os.path.abspath(file_path))).lower()
    grade_str = ""
    for g in ["6", "7", "8", "9", "10", "11", "12"]:
        if f"toan{g}" in folder_name or f"lop{g}" in folder_name:
            grade_str = g
            break

    # Trường hợp 1: Tiêu đề 2 cột dạng Section ở các đoạn văn bản đầu (P0..P7)
    has_org = False
    sectPr_idx = -1
    for idx, p in enumerate(doc.paragraphs[:12]):
        t = p.text.strip().lower()
        if any(kw in t for kw in ORG_KEYWORDS):
            has_org = True
        pPr = p._p.pPr
        if pPr is not None and pPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sectPr') is not None:
            sectPr_idx = idx
            break
        if "bài i" in t or "bài 1" in t or "phần i" in t:
            break
            
    if has_org and sectPr_idx != -1:
        print(f"[*] Phát hiện tiêu đề trường/sở dạng 2 cột section (đoạn 0..{sectPr_idx}). Chuyển đổi sang MathPlus...")
        split_idx = -1
        for i in range(sectPr_idx + 1):
            txt = doc.paragraphs[i].text.strip().lower()
            if "đề kiểm tra" in txt or "kiểm tra" in txt or "khảo sát" in txt:
                split_idx = i
                break
        if split_idx == -1:
            split_idx = (sectPr_idx + 1) // 2

        left_paras = [doc.paragraphs[i].text.strip() for i in range(split_idx) if doc.paragraphs[i].text.strip()]
        right_paras = [doc.paragraphs[i].text.strip() for i in range(split_idx, sectPr_idx + 1) if doc.paragraphs[i].text.strip()]

        extra_lines = []
        for l in left_paras:
            l_lower = l.lower()
            if not any(kw in l_lower for kw in ORG_KEYWORDS) and "ubnd" not in l_lower:
                extra_lines.append(l)
        extra_text = "\n".join(extra_lines) if extra_lines else None

        delete_count = sectPr_idx + 1
        if delete_count < len(doc.paragraphs) and not doc.paragraphs[delete_count].text.strip():
            delete_count += 1
            
        for _ in range(delete_count):
            p = doc.paragraphs[0]
            p._p.getparent().remove(p._p)

        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        c_left = tbl.cell(0, 0)
        c_right = tbl.cell(0, 1)
        c_left.width = Mm(78)
        c_right.width = Mm(94)

        for c in [c_left, c_right]:
            tcPr = c._tc.get_or_add_tcPr()
            tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))

        populate_left_branding_cell(c_left, logo_path, hotline=hotline, extra_text=extra_text)

        p_r = c_right.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_r.paragraph_format.space_before = Pt(0)
        p_r.paragraph_format.space_after = Pt(1)
        p_r.paragraph_format.line_spacing = 1.15

        for i, line in enumerate(right_paras):
            r = p_r.add_run(line + "\n")
            r.font.name = "Times New Roman"
            if i == 0:
                r.font.size = Pt(11.5)
                r.font.bold = True
            elif "môn" in line.lower():
                r.font.size = Pt(11)
                r.font.bold = True
            else:
                r.font.size = Pt(10.5)
                r.font.italic = True

        r_t = p_r.add_run(f"Giáo viên phụ trách: {teacher_name} – Hotline: {hotline}")
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(10.5)
        r_t.font.bold = True

        p_sep = doc.add_paragraph()
        p_sep.paragraph_format.space_before = Pt(4)
        p_sep.paragraph_format.space_after = Pt(8)
        body = doc._body._element
        first_el = body[0]
        first_el.addprevious(tbl._tbl)
        first_el.addprevious(p_sep._p)
        return True

    # Trường hợp 2: Tiêu đề Đáp án bên thứ ba (ví dụ TOANMATH, AI & THCS)
    p0_text = doc.paragraphs[0].text.strip() if doc.paragraphs else ""
    if "đáp án" in p0_text.lower() or "toanmath" in p0_text.lower():
        print(f"[*] Phát hiện tiêu đề Đáp án ở đoạn đầu. Chuyển đổi sang MathPlus...")
        doc.paragraphs[0]._p.getparent().remove(doc.paragraphs[0]._p)

        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        c_left = tbl.cell(0, 0)
        c_right = tbl.cell(0, 1)
        c_left.width = Mm(78)
        c_right.width = Mm(94)

        for c in [c_left, c_right]:
            tcPr = c._tc.get_or_add_tcPr()
            tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))

        populate_left_branding_cell(c_left, logo_path, hotline=hotline)

        p_r = c_right.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_r.paragraph_format.space_before = Pt(0)
        p_r.paragraph_format.space_after = Pt(1)
        p_r.paragraph_format.line_spacing = 1.15

        subj_title = f"MÔN: TOÁN {grade_str}" if grade_str else "MÔN: TOÁN"
        lines = [
            ("ĐÁP ÁN VÀ LỜI GIẢI CHI TIẾT\n", True, Pt(12)),
            (f"{subj_title}\n", True, Pt(11)),
            ("ĐỀ KIỂM TRA GIỮA HỌC KÌ I\n", False, Pt(10.5)),
            ("Năm học 2026 - 2027\n", False, Pt(10)),
            (f"Giáo viên phụ trách: {teacher_name} – Hotline: {hotline}", True, Pt(10.5))
        ]
        for line_txt, is_bold, sz in lines:
            r = p_r.add_run(line_txt)
            r.font.name = "Times New Roman"
            r.font.size = sz
            r.font.bold = is_bold
            if not is_bold:
                r.font.italic = True

        p_sep = doc.add_paragraph()
        p_sep.paragraph_format.space_before = Pt(4)
        p_sep.paragraph_format.space_after = Pt(8)
        body = doc._body._element
        first_el = body[0]
        first_el.addprevious(tbl._tbl)
        first_el.addprevious(p_sep._p)
        return True

    return False

def insert_top_banner_table(doc, logo_path, teacher_name=DEFAULT_TEACHER, hotline=DEFAULT_HOTLINE,
                            center_name=DEFAULT_CENTER_NAME, doc_title=None):
    """
    Chèn bảng Top Banner nhận diện thương hiệu MathPlus vào ngay vị trí đầu tiên của tài liệu.
    """
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    c_left = table.cell(0, 0)
    c_left.width = Mm(78)
    c_right = table.cell(0, 1)
    c_right.width = Mm(94)
    
    for c in [c_left, c_right]:
        tcPr = c._tc.get_or_add_tcPr()
        tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))
        
    populate_left_branding_cell(c_left, logo_path, hotline=hotline)
    
    p_r1 = c_right.paragraphs[0]
    p_r1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_r1.paragraph_format.space_before = Pt(0)
    p_r1.paragraph_format.space_after = Pt(2)
    p_r1.paragraph_format.line_spacing = 1.2
    
    if doc_title:
        r_t = p_r1.add_run(f"{doc_title.upper()}\n")
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(12)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_BLACK
        
    r_info1 = p_r1.add_run("Họ và tên: ..............................................................  Lớp: .........\n")
    r_info1.font.name = "Times New Roman"
    r_info1.font.size = Pt(11)
    r_info1.font.color.rgb = COLOR_BLACK
    
    r_info2 = p_r1.add_run("Trường: ...................................................................  Điểm: ........\n")
    r_info2.font.name = "Times New Roman"
    r_info2.font.size = Pt(11)
    r_info2.font.color.rgb = COLOR_BLACK
    
    r_teacher = p_r1.add_run(f"Giáo viên phụ trách: {teacher_name} ({hotline})")
    r_teacher.font.name = "Times New Roman"
    r_teacher.font.size = Pt(11)
    r_teacher.font.bold = True
    r_teacher.font.color.rgb = COLOR_BLACK
    
    p_sep = doc.add_paragraph()
    p_sep.paragraph_format.space_before = Pt(4)
    p_sep.paragraph_format.space_after = Pt(8)
    
    body = doc._body._element
    if len(body) > 2:
        first_orig_el = body[0]
        first_orig_el.addprevious(table._tbl)
        first_orig_el.addprevious(p_sep._p)

def process_docx_file(input_path, output_path, logo_path, teacher_name=DEFAULT_TEACHER,
                      hotline=DEFAULT_HOTLINE, center_name=DEFAULT_CENTER_NAME,
                      mode="full", add_banner=True):
    """
    Xử lý file DOCX:
    - Chèn / cập nhật Header ở tất cả các section.
    - Chèn / cập nhật Footer ở tất cả các section.
    - Chèn hoặc thay thế Top Banner trang 1.
    """
    print(f"[*] Đang xử lý file Word: {os.path.basename(input_path)}")
    doc = Document(input_path)
    
    replaced_banner = False
    if add_banner and mode in ("full", "banner_only"):
        replaced_banner = check_and_replace_existing_header_table(
            doc, logo_path, teacher_name=teacher_name, hotline=hotline
        )
        if not replaced_banner:
            replaced_banner = check_and_replace_existing_header_paragraphs(
                doc, logo_path, teacher_name=teacher_name, hotline=hotline, file_path=input_path
            )
        if not replaced_banner:
            remove_leading_old_headers(doc)
            insert_top_banner_table(doc, logo_path, teacher_name=teacher_name, hotline=hotline, center_name=center_name)
            
    for i, section in enumerate(doc.sections):
        if i == 0:
            section.different_first_page_header_footer = True
        else:
            section.different_first_page_header_footer = False
            section.header.is_linked_to_previous = True
            section.footer.is_linked_to_previous = True
        
        # 1. Header các trang sau
        if mode in ("full", "header_footer", "header_only"):
            format_subsequent_header(section.header, logo_path, center_name=center_name)
            if not add_banner:
                format_first_page_header(section.first_page_header, logo_path, center_name=center_name, hotline=hotline)
            else:
                clear_header_or_footer(section.first_page_header)
                    
        # 2. Footer ở tất cả các trang
        if mode in ("full", "header_footer", "footer_only"):
            format_footer(section.footer, section=section, teacher_name=teacher_name, hotline=hotline, center_name=center_name)
            if i == 0:
                format_footer(section.first_page_footer, section=section, teacher_name=teacher_name, hotline=hotline, center_name=center_name)
            
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    print(f"[+] Đã lưu file Word thương hiệu MathPlus: {output_path}")
    return output_path

def add_mathplus_branding(input_path, output_path=None, logo_path=None,
                          teacher_name=DEFAULT_TEACHER, hotline=DEFAULT_HOTLINE,
                          center_name=DEFAULT_CENTER_NAME, mode="full"):
    """
    Hàm tổng điều phối: nhận diện .pdf hoặc .docx, chuyển đổi và chèn nhận diện MathPlus.
    """
    input_path = os.path.abspath(input_path)
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Không tìm thấy file: {input_path}")
        
    logo_file = find_logo_path(logo_path)
    if not logo_file:
        print("[!] Chú ý: Không tìm thấy file logo MathPlus, tiếp tục với text nhận diện.")
    else:
        print(f"[*] Sử dụng logo MathPlus tại: {logo_file}")
        
    ext = os.path.splitext(input_path)[1].lower()
    
    if not output_path:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_dir = os.path.dirname(input_path)
        output_path = os.path.join(output_dir, f"{base_name}_mathplus.docx")
    else:
        output_path = os.path.abspath(output_path)
        if os.path.isdir(output_path):
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_path, f"{base_name}_mathplus.docx")
            
    temp_docx = None
    try:
        if ext == ".pdf":
            temp_docx = output_path + ".temp.docx"
            convert_pdf_to_docx(input_path, temp_docx)
            target_input_docx = temp_docx
        elif ext in (".docx", ".doc"):
            target_input_docx = input_path
        else:
            raise ValueError(f"Định dạng file không được hỗ trợ: {ext}. Chỉ hỗ trợ .docx và .pdf.")
            
        res = process_docx_file(
            input_path=target_input_docx,
            output_path=output_path,
            logo_path=logo_file,
            teacher_name=teacher_name,
            hotline=hotline,
            center_name=center_name,
            mode=mode,
            add_banner=(mode in ("full", "banner_only"))
        )
        return res
    finally:
        if temp_docx and os.path.exists(temp_docx):
            try:
                os.remove(temp_docx)
            except Exception:
                pass

def main():
    parser = argparse.ArgumentParser(
        description="MathPlus Add Logo: Tự động chèn Logo MathPlus và thông tin Thầy Dũng vào tài liệu Word và PDF."
    )
    parser.add_argument("-i", "--input", required=True, help="Đường dẫn file (.docx, .pdf) hoặc thư mục chứa các file.")
    parser.add_argument("-o", "--output", default=None, help="Đường dẫn file Word đầu ra hoặc thư mục đầu ra.")
    parser.add_argument("--logo", default=None, help="Đường dẫn file logo MathPlus tùy chọn.")
    parser.add_argument("--teacher", default=DEFAULT_TEACHER, help=f"Tên giáo viên (mặc định: {DEFAULT_TEACHER}).")
    parser.add_argument("--hotline", default=DEFAULT_HOTLINE, help=f"Hotline trung tâm (mặc định: {DEFAULT_HOTLINE}).")
    parser.add_argument("--center", default=DEFAULT_CENTER_NAME, help=f"Tên trung tâm (mặc định: {DEFAULT_CENTER_NAME}).")
    parser.add_argument(
        "--mode",
        choices=["full", "header_footer", "banner_only", "footer_only"],
        default="full",
        help="Chế độ chèn nhận diện: 'full' (Banner + Header + Footer), 'header_footer', 'banner_only', 'footer_only'."
    )
    
    args = parser.parse_args()
    
    target_input = os.path.abspath(args.input)
    if os.path.isdir(target_input):
        files = glob.glob(os.path.join(target_input, "*.docx")) + glob.glob(os.path.join(target_input, "*.pdf"))
        files = [f for f in files if not f.endswith("_mathplus.docx")]
        print(f"[*] Tìm thấy {len(files)} file cần xử lý trong thư mục {target_input}")
        for idx, f in enumerate(files, 1):
            print(f"\n[{idx}/{len(files)}] Đang xử lý: {os.path.basename(f)}")
            try:
                add_mathplus_branding(
                    input_path=f,
                    output_path=args.output,
                    logo_path=args.logo,
                    teacher_name=args.teacher,
                    hotline=args.hotline,
                    center_name=args.center,
                    mode=args.mode
                )
            except Exception as e:
                print(f"[!] Lỗi khi xử lý {f}: {e}")
    else:
        add_mathplus_branding(
            input_path=target_input,
            output_path=args.output,
            logo_path=args.logo,
            teacher_name=args.teacher,
            hotline=args.hotline,
            center_name=args.center,
            mode=args.mode
        )

if __name__ == "__main__":
    main()
