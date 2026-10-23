#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Engine tạo tài liệu Word (.docx) chuẩn phong cách Trung tâm MathPlus Academy.
Tích hợp:
- Bảng thông tin 2 cột thương hiệu & khung học sinh
- Chuyển đổi công thức toán học LaTeX -> OMML (Word Native Equations)
- Khung bài tập dạng chuẩn & Khung lời giải chi tiết (Solution Box)
- Chèn hình vẽ minh họa (Diagrams / Plots) với chú thích caption
- Bảng tự đánh giá học sinh (Checklist) & Khung nhận xét giáo viên
- Header & Footer trang nhã tự động
- Đảm bảo 100% ECMA-376 OpenXML schema compliance
"""

import os
import re
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from omml_converter import latex_to_omml

# Bảng màu chuẩn MathPlus
COLOR_PRIMARY_NAVY = RGBColor(15, 76, 129)     # #0F4C81 - Xanh Navy chủ đạo
COLOR_DARK_TEXT = RGBColor(34, 34, 34)          # #222222 - Màu chữ dễ đọc
COLOR_MUTED_GRAY = RGBColor(100, 116, 139)      # #64748B - Màu ghi phụ trợ
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_SOLUTION_TITLE = RGBColor(16, 124, 65)    # #107C41 - Xanh lá lời giải
COLOR_CAPTION = RGBColor(71, 85, 105)           # #475569

HEX_PRIMARY_NAVY = "0F4C81"
HEX_LIGHT_BG = "F1F5F9"
HEX_LIGHT_BORDER = "CBD5E1"
HEX_SECTION_BG = "0F4C81"
HEX_SOL_BG = "F8FAFC"
HEX_SOL_BORDER = "0F4C81"

def style_cell(cell, bg_color=None, border_color="CBD5E1", top="none", bottom="none", left="none", right="none", sz="4"):
    """Định kiểu màu nền và đường viền cho ô theo đúng thứ tự schema OpenXML."""
    tcPr = cell._tc.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag.endswith(('tcBorders', 'shd')):
            tcPr.remove(child)
            
    if any(b != 'none' for b in [top, bottom, left, right]):
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="{top}" w:sz="{sz}" w:space="0" w:color="{border_color}"/>'
            f'<w:left w:val="{left}" w:sz="{sz}" w:space="0" w:color="{border_color}"/>'
            f'<w:bottom w:val="{bottom}" w:sz="{sz}" w:space="0" w:color="{border_color}"/>'
            f'<w:right w:val="{right}" w:sz="{sz}" w:space="0" w:color="{border_color}"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)
        
    if bg_color:
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}" w:val="clear"/>')
        tcPr.append(shd)

def add_inline_math(p, latex_code):
    omml = latex_to_omml(latex_code, display=False)
    p._p.append(omml)

def add_display_math(doc_or_cell, latex_code, space_before=Pt(2), space_after=Pt(3)):
    p = doc_or_cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = space_before
    p.paragraph_format.space_after = space_after
    omml = latex_to_omml(latex_code, display=True)
    p._p.append(omml)
    return p

def add_rich_text(p, text, default_font="Times New Roman", default_size=Pt(11),
                  default_color=COLOR_DARK_TEXT, default_bold=False, default_italic=False):
    """Phân tích chuỗi chứa text và công thức toán $...$ rồi thêm run tương ứng."""
    tokens = re.split(r'(\$[^$]+\$)', text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('$') and token.endswith('$'):
            math_code = token[1:-1]
            add_inline_math(p, math_code)
        else:
            run = p.add_run(token)
            run.font.name = default_font
            run.font.size = default_size
            run.font.color.rgb = default_color
            run.font.bold = default_bold
            run.font.italic = default_italic

class MathPlusDocxBuilder:
    def __init__(self, title, subtitle="Năm học 2026 – 2027", time_limit="90 phút", is_solved=False):
        self.doc = Document()
        self.title = title
        self.subtitle = subtitle
        self.time_limit = time_limit
        self.is_solved = is_solved
        self._setup_page()
        self._setup_header_footer()
        self._build_top_banner()

    def _setup_page(self):
        section = self.doc.sections[0]
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(18)
        section.bottom_margin = Mm(18)
        section.left_margin = Mm(20)
        section.right_margin = Mm(18)
        section.different_first_page_header_footer = True
        
        normal_style = self.doc.styles['Normal']
        normal_style.font.name = 'Times New Roman'
        normal_style.font.size = Pt(11)
        normal_style.font.color.rgb = COLOR_DARK_TEXT

    def _setup_header_footer(self):
        section = self.doc.sections[0]
        header = section.header
        p_h = header.paragraphs[0]
        p_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        h_title = f"TRUNG TÂM MATHPLUS ACADEMY  |  {self.title.upper()}"
        if self.is_solved:
            h_title += " (KÈM LỜI GIẢI & HÌNH VẼ)"
        r_h = p_h.add_run(h_title)
        r_h.font.name = "Times New Roman"
        r_h.font.size = Pt(8.5)
        r_h.font.italic = True
        r_h.font.color.rgb = COLOR_MUTED_GRAY

        def setup_ftr(footer_obj):
            p_f = footer_obj.paragraphs[0]
            p_f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p_f.paragraph_format.tab_stops.add_tab_stop(Mm(172), WD_TAB_ALIGNMENT.RIGHT)
            
            r_f1 = p_f.add_run("Giáo viên: Nguyễn Văn Dũng – MathPlus Academy  |  Hotline: 0977 961 189")
            r_f1.font.name = "Times New Roman"
            r_f1.font.size = Pt(8.5)
            r_f1.font.italic = True
            r_f1.font.color.rgb = COLOR_MUTED_GRAY
            
            r_f2 = p_f.add_run("\tTrang ")
            r_f2.font.name = "Times New Roman"
            r_f2.font.size = Pt(8.5)
            r_f2.font.italic = True
            r_f2.font.color.rgb = COLOR_MUTED_GRAY
            
            r_pg = p_f.add_run()
            r_pg.font.name = "Times New Roman"
            r_pg.font.size = Pt(8.5)
            r_pg.font.color.rgb = COLOR_MUTED_GRAY
            fld1 = OxmlElement('w:fldChar')
            fld1.set(qn('w:fldCharType'), 'begin')
            t1 = OxmlElement('w:instrText')
            t1.set(qn('xml:space'), 'preserve')
            t1.text = 'PAGE'
            fld2 = OxmlElement('w:fldChar')
            fld2.set(qn('w:fldCharType'), 'separate')
            fld3 = OxmlElement('w:fldChar')
            fld3.set(qn('w:fldCharType'), 'end')
            r_pg._r.append(fld1)
            r_pg._r.append(t1)
            r_pg._r.append(fld2)
            r_pg._r.append(fld3)

        setup_ftr(section.first_page_footer)
        setup_ftr(section.footer)

    def _build_top_banner(self):
        # 2-column header
        header_table = self.doc.add_table(rows=1, cols=2)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        header_table.autofit = False
        
        # Left
        c_left = header_table.cell(0, 0)
        c_left.width = Mm(65)
        p_l = c_left.paragraphs[0]
        p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_l.paragraph_format.space_before = Pt(0)
        p_l.paragraph_format.space_after = Pt(2)
        p_l.paragraph_format.line_spacing = 1.15
        
        r_l1 = p_l.add_run("TRUNG TÂM MATHPLUS ACADEMY\n")
        r_l1.font.name = "Times New Roman"
        r_l1.font.size = Pt(11.5)
        r_l1.font.bold = True
        r_l1.font.color.rgb = COLOR_PRIMARY_NAVY
        
        r_l2 = p_l.add_run("Bồi dưỡng Toán phổ thông & Luyện thi\n")
        r_l2.font.name = "Times New Roman"
        r_l2.font.size = Pt(9.5)
        r_l2.font.italic = True
        r_l2.font.color.rgb = COLOR_DARK_TEXT
        
        r_l3 = p_l.add_run("Website: mathplus.vn  •  Hotline: 0977 961 189")
        r_l3.font.name = "Times New Roman"
        r_l3.font.size = Pt(8.5)
        r_l3.font.italic = True
        r_l3.font.color.rgb = COLOR_MUTED_GRAY
        
        # Right
        c_right = header_table.cell(0, 1)
        c_right.width = Mm(107)
        p_r = c_right.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_r.paragraph_format.space_before = Pt(0)
        p_r.paragraph_format.space_after = Pt(2)
        p_r.paragraph_format.line_spacing = 1.15
        
        r_r1 = p_r.add_run(f"{self.title.upper()}\n")
        r_r1.font.name = "Times New Roman"
        r_r1.font.size = Pt(12.5)
        r_r1.font.bold = True
        r_r1.font.color.rgb = COLOR_PRIMARY_NAVY
        
        if self.is_solved:
            r_bdg = p_r.add_run("【 ĐỀ BÀI VÀ LỜI GIẢI CHI TIẾT – CÓ HÌNH VẼ 】\n")
            r_bdg.font.name = "Times New Roman"
            r_bdg.font.size = Pt(10)
            r_bdg.font.bold = True
            r_bdg.font.color.rgb = COLOR_SOLUTION_TITLE
            
        r_r2 = p_r.add_run(f"{self.subtitle}  •  Thời gian gợi ý: {self.time_limit}")
        r_r2.font.name = "Times New Roman"
        r_r2.font.size = Pt(9.5)
        r_r2.font.italic = True
        r_r2.font.color.rgb = COLOR_MUTED_GRAY
        
        # Student info box
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(4)
        
        info_t = self.doc.add_table(rows=1, cols=1)
        info_t.alignment = WD_TABLE_ALIGNMENT.CENTER
        info_t.autofit = False
        c_info = info_t.cell(0, 0)
        c_info.width = Mm(172)
        style_cell(c_info, bg_color=HEX_LIGHT_BG, border_color=HEX_LIGHT_BORDER, top="single", bottom="single", left="single", right="single", sz="6")
        
        p_i = c_info.paragraphs[0]
        p_i.paragraph_format.space_before = Pt(3)
        p_i.paragraph_format.space_after = Pt(3)
        p_i.paragraph_format.line_spacing = 1.2
        
        p_i.add_run("Họ và tên học sinh: ").bold = True
        p_i.add_run("……………………………………………………………………    ")
        p_i.add_run("Lớp: ").bold = True
        p_i.add_run("……………………\n")
        p_i.add_run("Ngày làm bài: ").bold = True
        p_i.add_run("………………………………………………    ")
        p_i.add_run("Điểm số / Đánh giá: ").bold = True
        p_i.add_run("………………………………")

    def add_section(self, title, subtitle=None):
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(4)
        p_sp.paragraph_format.space_after = Pt(2)
        
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        c = t.cell(0, 0)
        c.width = Mm(172)
        style_cell(c, bg_color=HEX_SECTION_BG)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_WHITE
        
        if subtitle:
            ps = self.doc.add_paragraph()
            ps.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ps.paragraph_format.space_before = Pt(2)
            ps.paragraph_format.space_after = Pt(6)
            rs = ps.add_run(subtitle)
            rs.font.name = "Times New Roman"
            rs.font.size = Pt(10)
            rs.font.italic = True
            rs.font.color.rgb = COLOR_MUTED_GRAY

    def add_dang(self, dang_title):
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        c = t.cell(0, 0)
        c.width = Mm(172)
        style_cell(c, bg_color="EBF3FA", border_color=HEX_PRIMARY_NAVY, left="single", sz="24")
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.left_indent = Pt(4)
        
        r = p.add_run(dang_title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY_NAVY
        
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(2)

    def add_problem_header(self, num_str, content_str=""):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        r_num = p.add_run(num_str + " ")
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(11)
        r_num.font.bold = True
        r_num.font.color.rgb = COLOR_PRIMARY_NAVY
        
        if content_str:
            add_rich_text(p, content_str)
        return p

    def add_display_equation(self, latex_code):
        return add_display_math(self.doc, latex_code)

    def add_solution(self, solution_steps):
        """
        Thêm khung lời giải chi tiết (Solution Box).
        solution_steps: List of tuples ('title', 'p', 'display_math', 'bullet', 'image', 'caption')
        """
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        c = t.cell(0, 0)
        c.width = Mm(172)
        style_cell(c, bg_color=HEX_SOL_BG, border_color=HEX_SOL_BORDER, left="single", sz="16")
        
        first = True
        for step in solution_steps:
            kind = step[0]
            content = step[1]
            if kind == 'title':
                p = c.paragraphs[0] if first else c.add_paragraph()
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.left_indent = Pt(4)
                r_icon = p.add_run("✎ LỜI GIẢI CHI TIẾT:")
                r_icon.font.name = "Times New Roman"
                r_icon.font.size = Pt(10.5)
                r_icon.font.bold = True
                r_icon.font.color.rgb = COLOR_SOLUTION_TITLE
            elif kind == 'p':
                p = c.paragraphs[0] if first else c.add_paragraph()
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.left_indent = Pt(6)
                p.paragraph_format.line_spacing = 1.15
                add_rich_text(p, content, default_size=Pt(10.5))
            elif kind == 'display_math':
                add_display_math(c, content, space_before=Pt(2), space_after=Pt(2))
            elif kind == 'bullet':
                p = c.paragraphs[0] if first else c.add_paragraph()
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.left_indent = Pt(16)
                p.paragraph_format.line_spacing = 1.15
                r_b = p.add_run("• ")
                r_b.font.bold = True
                r_b.font.color.rgb = COLOR_SOLUTION_TITLE
                add_rich_text(p, content, default_size=Pt(10.5))
            elif kind == 'image':
                img_path = content
                img_w = step[2] if len(step) > 2 else Mm(110)
                p = c.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(2)
                run_img = p.add_run()
                run_img.add_picture(img_path, width=img_w)
            elif kind == 'caption':
                p = c.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(4)
                r_cap = p.add_run(content)
                r_cap.font.name = "Times New Roman"
                r_cap.font.size = Pt(9.5)
                r_cap.font.italic = True
                r_cap.font.color.rgb = COLOR_CAPTION
            first = False
            
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(4)

    def add_self_evaluation(self, criteria_list):
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(2)
        
        self.add_section(
            "PHẦN III. TỰ ĐÁNH GIÁ SAU BUỔI ÔN",
            "Học sinh tự đánh dấu mức độ đạt được và đối chiếu kết quả."
        )
        
        rows_count = len(criteria_list) + 1
        eval_table = self.doc.add_table(rows=rows_count, cols=2)
        eval_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        eval_table.autofit = False
        
        w_col0 = Mm(36)
        w_col1 = Mm(136)
        
        # Header row
        h0 = eval_table.cell(0, 0)
        h1 = eval_table.cell(0, 1)
        h0.width = w_col0
        h1.width = w_col1
        style_cell(h0, bg_color="E2E8F0", border_color=HEX_LIGHT_BORDER, top="single", bottom="single", left="single", right="single")
        style_cell(h1, bg_color="E2E8F0", border_color=HEX_LIGHT_BORDER, top="single", bottom="single", left="single", right="single")
        
        p0 = h0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.add_run("Đánh giá").bold = True
        
        p1 = h1.paragraphs[0]
        p1.add_run("Nội dung kiến thức – Kỹ năng cần đạt").bold = True
        
        for idx, crit in enumerate(criteria_list, start=1):
            c0 = eval_table.cell(idx, 0)
            c1 = eval_table.cell(idx, 1)
            c0.width = w_col0
            c1.width = w_col1
            bg = "F8FAFC" if idx % 2 == 1 else None
            style_cell(c0, bg_color=bg, border_color=HEX_LIGHT_BORDER, top="single", bottom="single", left="single", right="single")
            style_cell(c1, bg_color=bg, border_color=HEX_LIGHT_BORDER, top="single", bottom="single", left="single", right="single")
            
            p0 = c0.paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p0.add_run("☑ Đạt    ☐ Chưa" if self.is_solved else "☐ Đạt    ☐ Chưa").font.size = Pt(9.5)
            
            p1 = c1.paragraphs[0]
            p1.paragraph_format.left_indent = Pt(6)
            p1.add_run(crit).font.size = Pt(10.5)

    def add_teacher_feedback_and_signature(self, teacher_name="Nguyễn Văn Dũng – MathPlus Academy"):
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(2)
        
        rem_table = self.doc.add_table(rows=1, cols=1)
        rem_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        rem_table.autofit = False
        rem_cell = rem_table.cell(0, 0)
        rem_cell.width = Mm(172)
        style_cell(rem_cell, bg_color="FAFAFA", border_color=HEX_LIGHT_BORDER, top="single", bottom="single", left="single", right="single", sz="6")
        
        p_rem = rem_cell.paragraphs[0]
        p_rem.paragraph_format.space_before = Pt(4)
        p_rem.paragraph_format.space_after = Pt(4)
        p_rem.paragraph_format.line_spacing = 1.3
        
        r_rt = p_rem.add_run("Nhận xét của giáo viên bộ môn:\n")
        r_rt.font.bold = True
        r_rt.font.color.rgb = COLOR_PRIMARY_NAVY
        p_rem.add_run("…………………………………………………………………………………………………………………………………………\n")
        p_rem.add_run("…………………………………………………………………………………………………………………………………………\n")
        p_rem.add_run("…………………………………………………………………………………………………………………………………………")
        
        p_sig = self.doc.add_paragraph()
        p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_sig.paragraph_format.space_before = Pt(10)
        p_sig.paragraph_format.space_after = Pt(2)
        
        r_sig1 = p_sig.add_run("Hà Nội, ngày …… tháng …… năm 2026\n")
        r_sig1.font.size = Pt(10)
        r_sig1.font.italic = True
        r_sig1.font.color.rgb = COLOR_MUTED_GRAY
        
        r_sig2 = p_sig.add_run(f"Giáo viên: {teacher_name}")
        r_sig2.font.size = Pt(11)
        r_sig2.font.bold = True
        r_sig2.font.color.rgb = COLOR_PRIMARY_NAVY

    def save(self, filepath):
        # Sửa lỗi zoom percent trong settings.xml để pass 100% ECMA-376 schema
        for elem in self.doc.settings.element.iter():
            if elem.tag.endswith('zoom'):
                elem.set(qn('w:percent'), '100')
                
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.doc.save(filepath)
        return filepath
