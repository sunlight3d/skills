#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Engine tạo tài liệu Word (.docx) môn TIẾNG ANH chuẩn phong cách Trung tâm MathPlus Academy.
Quy chuẩn thiết kế:
- Chữ toàn bộ màu ĐEN TUYỀN (RGBColor(0, 0, 0) / #000000), nền trắng hoàn toàn.
- Cỡ chữ toàn văn bản TỐI THIỂU 11pt (Pt(11) / sz=22).
- Khung lời giải chi tiết (Solution Box) KHÔNG có sọc đen bên trái (bỏ hoàn toàn viền trái).
- Chèn Logo MathPlus nguyên màu thương hiệu tại Header đầu trang.
- Header các trang sau chỉ gồm Logo và tên 'Trung tâm MathPlus Academy' (11pt nghiêng).
- Hỗ trợ định dạng bài đọc (Reading Passage), bản dịch toàn văn Tiếng Việt của bài đọc.
- Hỗ trợ giải thích chi tiết từng câu, phân tích ngữ pháp, từ vựng, dẫn chứng trong bài đọc.
- Hỗ trợ gạch chân <u>...</u> (cho bài phát âm, trọng âm, tìm lỗi sai), in đậm **...**, in nghiêng *...*.
- Bảng đáp án nhanh (Quick Answer Key) và bảng tổng hợp từ vựng & cấu trúc (Vocabulary Table).
- Đảm bảo 100% ECMA-376 OpenXML schema compliance.
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

# Bảng màu chuẩn ĐEN TUYỀN - NỀN TRẮNG
COLOR_BLACK = RGBColor(0, 0, 0)             # #000000 - Đen tuyền tuyệt đối
COLOR_DARK_TEXT = RGBColor(0, 0, 0)         # Đen tuyền
COLOR_PRIMARY_NAVY = RGBColor(0, 0, 0)      # Đen tuyền
COLOR_MUTED_GRAY = RGBColor(0, 0, 0)        # Đen tuyền
COLOR_SOLUTION_TITLE = RGBColor(0, 0, 0)    # Đen tuyền
COLOR_CAPTION = RGBColor(0, 0, 0)           # Đen tuyền
COLOR_WHITE = RGBColor(255, 255, 255)

def find_mathplus_logo(custom_path=None):
    """Tìm file logo MathPlus để chèn vào Header, giữ nguyên màu gốc."""
    candidates = [
        custom_path,
        r"C:\code\mathplus\public\images\logo.jpg",
        r"C:\code\mathplus\public\images\logo.png",
        os.path.join(os.path.dirname(__file__), "..", "resources", "logo.jpg"),
        os.path.join(os.path.dirname(__file__), "..", "resources", "logo.png"),
        os.path.join(os.path.dirname(__file__), "..", "..", "mathplus-giai-toan", "resources", "logo.jpg"),
        os.path.join(os.getcwd(), "public", "images", "logo.jpg"),
        os.path.join(os.getcwd(), "public", "images", "logo.png"),
    ]
    for c in candidates:
        if c and os.path.exists(c) and os.path.isfile(c):
            return c
    return None

def style_cell(cell, bg_color=None, border_color="000000", top="none", bottom="none", left="none", right="none", sz="4"):
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
    try:
        omml = latex_to_omml(latex_code, display=False)
        p._p.append(omml)
    except Exception:
        run = p.add_run(f"${latex_code}$")
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_BLACK

def add_display_math(doc_or_cell, latex_code, space_before=Pt(2), space_after=Pt(3)):
    p = doc_or_cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = space_before
    p.paragraph_format.space_after = space_after
    try:
        omml = latex_to_omml(latex_code, display=True)
        p._p.append(omml)
    except Exception:
        run = p.add_run(latex_code)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_BLACK
    return p

def add_rich_text(p, text, default_font="Times New Roman", default_size=Pt(11),
                  default_color=COLOR_BLACK, default_bold=False, default_italic=False, default_underline=False):
    """
    Phân tích chuỗi chứa:
    - <u>...</u> hoặc __...__ (gạch chân - cực kỳ quan trọng cho phát âm, trọng âm, tìm lỗi sai)
    - ***...*** (đậm + nghiêng)
    - **...** (đậm)
    - *...* (nghiêng)
    - $...$ (công thức toán học nếu có)
    Mọi run đều có font size tối thiểu 11pt và màu đen tuyền.
    """
    if text is None:
        return
    text = str(text)
    effective_size = Pt(11) if default_size < Pt(11) else default_size
    
    # Pattern tách các token đặc biệt
    pattern = r'(\$[^$]+\$|<u>.*?</u>|__.*?__|\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*)'
    tokens = re.split(pattern, text)
    
    for token in tokens:
        if not token:
            continue
        
        # 1. Inline math
        if token.startswith('$') and token.endswith('$') and len(token) > 2:
            math_code = token[1:-1].strip()
            add_inline_math(p, math_code)
            
        # 2. Underline <u>...</u> hoặc __...__
        elif (token.startswith('<u>') and token.endswith('</u>') and len(token) >= 7):
            inner = token[3:-4]
            run = p.add_run(inner)
            run.font.name = default_font
            run.font.size = effective_size
            run.font.color.rgb = COLOR_BLACK
            run.font.bold = default_bold
            run.font.italic = default_italic
            run.font.underline = True
        elif (token.startswith('__') and token.endswith('__') and len(token) >= 4):
            inner = token[2:-2]
            run = p.add_run(inner)
            run.font.name = default_font
            run.font.size = effective_size
            run.font.color.rgb = COLOR_BLACK
            run.font.bold = default_bold
            run.font.italic = default_italic
            run.font.underline = True
            
        # 3. Bold Italic ***...***
        elif token.startswith('***') and token.endswith('***') and len(token) > 6:
            run = p.add_run(token[3:-3])
            run.font.name = default_font
            run.font.size = effective_size
            run.font.color.rgb = COLOR_BLACK
            run.font.bold = True
            run.font.italic = True
            run.font.underline = default_underline
            
        # 4. Bold **...**
        elif token.startswith('**') and token.endswith('**') and len(token) > 4:
            run = p.add_run(token[2:-2])
            run.font.name = default_font
            run.font.size = effective_size
            run.font.color.rgb = COLOR_BLACK
            run.font.bold = True
            run.font.italic = default_italic
            run.font.underline = default_underline
            
        # 5. Italic *...*
        elif token.startswith('*') and token.endswith('*') and len(token) > 2:
            run = p.add_run(token[1:-1])
            run.font.name = default_font
            run.font.size = effective_size
            run.font.color.rgb = COLOR_BLACK
            run.font.bold = default_bold
            run.font.italic = True
            run.font.underline = default_underline
            
        # 6. Text thường
        else:
            clean_tok = token.replace('**', '').replace('<u>', '').replace('</u>', '')
            run = p.add_run(clean_tok)
            run.font.name = default_font
            run.font.size = effective_size
            run.font.color.rgb = COLOR_BLACK
            run.font.bold = default_bold
            run.font.italic = default_italic
            run.font.underline = default_underline

class MathPlusDocxBuilder:
    def __init__(self, title, subtitle="Năm học 2026 – 2027", time_limit="60 phút",
                 subject_center="Bồi dưỡng Tiếng Anh & Luyện thi", is_solved=False,
                 logo_path=None, school_name=None, department_name=None,
                 has_header=True, has_footer=True, has_logo=True, **kwargs):
        self.doc = Document()
        self.title = title
        self.subtitle = subtitle
        self.time_limit = time_limit
        self.subject_center = subject_center
        self.is_solved = is_solved
        self.school_name = school_name
        self.department_name = department_name
        self.has_header = has_header
        self.has_footer = has_footer
        self.has_logo = has_logo
        self.logo_path = find_mathplus_logo(logo_path) if has_logo else None
        self._setup_page()
        if self.has_header or self.has_footer:
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
        section.different_first_page_header_footer = True if (self.has_header or self.has_footer) else False
        
        normal_style = self.doc.styles['Normal']
        normal_style.font.name = 'Times New Roman'
        normal_style.font.size = Pt(11)
        normal_style.font.color.rgb = COLOR_BLACK

    def _setup_header_footer(self):
        section = self.doc.sections[0]
        if self.has_header:
            header = section.header
            p_h = header.paragraphs[0]
            p_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p_h.paragraph_format.space_before = Pt(0)
            p_h.paragraph_format.space_after = Pt(0)
            
            # Header ở các trang sau: Chỉ gồm Logo và tên Trung tâm (không viết hoa toàn bộ, 11pt nghiêng)
            if self.has_logo and self.logo_path and os.path.exists(self.logo_path):
                r_logo = p_h.add_run()
                r_logo.add_picture(self.logo_path, width=Mm(7.5))
                
            header_name = f"  {self.school_name}" if self.school_name else "  Trung tâm MathPlus Academy"
            r_h = p_h.add_run(header_name)
            r_h.font.name = "Times New Roman"
            r_h.font.size = Pt(11)
            r_h.font.italic = True
            r_h.font.color.rgb = COLOR_BLACK

        if self.has_footer:
            def setup_ftr(footer_obj):
                p_f = footer_obj.paragraphs[0]
                p_f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                p_f.paragraph_format.tab_stops.add_tab_stop(Mm(172), WD_TAB_ALIGNMENT.RIGHT)
                
                r_f1 = p_f.add_run("Giáo viên: Nguyễn Văn Dũng – MathPlus Academy  |  Hotline: 0977 961 189")
                r_f1.font.name = "Times New Roman"
                r_f1.font.size = Pt(11)
                r_f1.font.italic = True
                r_f1.font.color.rgb = COLOR_BLACK
                
                r_f2 = p_f.add_run("\tTrang ")
                r_f2.font.name = "Times New Roman"
                r_f2.font.size = Pt(11)
                r_f2.font.italic = True
                r_f2.font.color.rgb = COLOR_BLACK
                
                r_pg = p_f.add_run()
                r_pg.font.name = "Times New Roman"
                r_pg.font.size = Pt(11)
                r_pg.font.color.rgb = COLOR_BLACK
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
        header_table = self.doc.add_table(rows=1, cols=2)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        header_table.autofit = False
        
        c_left = header_table.cell(0, 0)
        c_left.width = Mm(78)
        c_right = header_table.cell(0, 1)
        c_right.width = Mm(94)
        
        for c in [c_left, c_right]:
            tcPr = c._tc.get_or_add_tcPr()
            tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))
        
        # Cột trái: Logo (nếu có) + Tên trường/trung tâm
        first_p = c_left.paragraphs[0]
        first_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        first_p.paragraph_format.space_before = Pt(0)
        first_p.paragraph_format.space_after = Pt(2)
        
        if self.has_logo and self.logo_path and os.path.exists(self.logo_path):
            run_logo = first_p.add_run()
            run_logo.add_picture(self.logo_path, width=Mm(18))
            p_l = c_left.add_paragraph()
        else:
            p_l = first_p
            
        p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_l.paragraph_format.space_before = Pt(1)
        p_l.paragraph_format.space_after = Pt(1)
        p_l.paragraph_format.line_spacing = 1.15
        
        org_title = self.school_name if self.school_name else "TRUNG TÂM MATHPLUS ACADEMY"
        r_l1 = p_l.add_run(f"{org_title.upper()}\n")
        r_l1.font.name = "Times New Roman"
        r_l1.font.size = Pt(11)
        r_l1.font.bold = True
        r_l1.font.color.rgb = COLOR_BLACK
        
        dept_title = self.department_name if self.department_name else self.subject_center
        r_l2 = p_l.add_run(f"{dept_title}\n")
        r_l2.font.name = "Times New Roman"
        r_l2.font.size = Pt(11)
        r_l2.font.italic = True
        r_l2.font.color.rgb = COLOR_BLACK
        
        if not self.school_name:
            r_l3 = p_l.add_run("Hotline: 0977 961 189  •  mathplus.com.vn")
            r_l3.font.name = "Times New Roman"
            r_l3.font.size = Pt(11)
            r_l3.font.italic = True
            r_l3.font.color.rgb = COLOR_BLACK
        
        # Cột phải: Tiêu đề đề thi
        p_r = c_right.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_r.paragraph_format.space_before = Pt(0)
        p_r.paragraph_format.space_after = Pt(1)
        p_r.paragraph_format.line_spacing = 1.15
        
        r_r1 = p_r.add_run(f"{self.title.upper()}\n")
        r_r1.font.name = "Times New Roman"
        r_r1.font.size = Pt(12)
        r_r1.font.bold = True
        r_r1.font.color.rgb = COLOR_BLACK
        
        if self.is_solved:
            r_bdg = p_r.add_run("【 ĐỀ BÀI VÀ LỜI GIẢI CHI TIẾT – DỊCH NGHĨA BÀI ĐỌC 】\n")
            r_bdg.font.name = "Times New Roman"
            r_bdg.font.size = Pt(11)
            r_bdg.font.bold = True
            r_bdg.font.color.rgb = COLOR_BLACK
            
        r_r2 = p_r.add_run(f"{self.subtitle}\n")
        r_r2.font.name = "Times New Roman"
        r_r2.font.size = Pt(11)
        r_r2.font.bold = True
        r_r2.font.color.rgb = COLOR_BLACK
        
        r_r3 = p_r.add_run(f"Thời gian làm bài: {self.time_limit}")
        r_r3.font.name = "Times New Roman"
        r_r3.font.size = Pt(11)
        r_r3.font.italic = True
        r_r3.font.color.rgb = COLOR_BLACK
        
        # Khung thông tin học sinh (Nền trắng, viền mảnh đen)
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(4)
        
        info_t = self.doc.add_table(rows=1, cols=1)
        info_t.alignment = WD_TABLE_ALIGNMENT.CENTER
        info_t.autofit = False
        c_info = info_t.cell(0, 0)
        c_info.width = Mm(172)
        style_cell(c_info, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
        
        p_i = c_info.paragraphs[0]
        p_i.paragraph_format.space_before = Pt(3)
        p_i.paragraph_format.space_after = Pt(3)
        p_i.paragraph_format.line_spacing = 1.2
        
        r1 = p_i.add_run("Họ và tên học sinh: ")
        r1.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = COLOR_BLACK
        r1_dot = p_i.add_run("……………………………………………………………………    ")
        r1_dot.font.size = Pt(11)
        r1_dot.font.color.rgb = COLOR_BLACK
        
        r2 = p_i.add_run("Lớp: ")
        r2.bold = True
        r2.font.size = Pt(11)
        r2.font.color.rgb = COLOR_BLACK
        r2_dot = p_i.add_run("……………………\n")
        r2_dot.font.size = Pt(11)
        r2_dot.font.color.rgb = COLOR_BLACK
        
        r3 = p_i.add_run("Ngày làm bài: ")
        r3.bold = True
        r3.font.size = Pt(11)
        r3.font.color.rgb = COLOR_BLACK
        r3_dot = p_i.add_run("………………………………………………    ")
        r3_dot.font.size = Pt(11)
        r3_dot.font.color.rgb = COLOR_BLACK
        
        r4 = p_i.add_run("Điểm số / Đánh giá: ")
        r4.bold = True
        r4.font.size = Pt(11)
        r4.font.color.rgb = COLOR_BLACK
        r4_dot = p_i.add_run("………………………………")
        r4_dot.font.size = Pt(11)
        r4_dot.font.color.rgb = COLOR_BLACK

    def add_section(self, title, subtitle=None):
        """Thêm tiêu đề phần lớn (Nền trắng, viền trên và dưới đen, KHÔNG có sọc đen hai bên)."""
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(2)
        
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        c = t.cell(0, 0)
        c.width = Mm(172)
        style_cell(c, bg_color=None, border_color="000000", top="single", bottom="single", left="none", right="none", sz="6")
        
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_BLACK
        
        if subtitle:
            ps = self.doc.add_paragraph()
            ps.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ps.paragraph_format.space_before = Pt(2)
            ps.paragraph_format.space_after = Pt(6)
            rs = ps.add_run(subtitle)
            rs.font.name = "Times New Roman"
            rs.font.size = Pt(11)
            rs.font.italic = True
            rs.font.color.rgb = COLOR_BLACK

    def add_part_header(self, part_title, part_subtitle=None):
        self.add_section(part_title, part_subtitle)

    def add_instruction(self, instruction_text):
        """Thêm câu lệnh đề bài (in nghiêng, font 11pt, căn đều)."""
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.left_indent = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        
        add_rich_text(p, instruction_text, default_size=Pt(11), default_italic=True, default_color=COLOR_BLACK)

    def add_reading_passage(self, passage_text_or_paras, title="READING PASSAGE", note=None):
        """
        Thêm khung chứa ĐOẠN VĂN BÀI ĐỌC HIỂU (Reading Comprehension / Cloze Test).
        Nền trắng, viền mảnh toàn bộ khung, font 11pt, căn đều hai bên.
        """
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(4)
        p_sp.paragraph_format.space_after = Pt(2)
        
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        c = t.cell(0, 0)
        c.width = Mm(172)
        style_cell(c, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
        
        # Tiêu đề bài đọc
        p_head = c.paragraphs[0]
        p_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_head.paragraph_format.space_before = Pt(4)
        p_head.paragraph_format.space_after = Pt(3)
        
        r_head = p_head.add_run(f"📖 {title.upper()}\n")
        r_head.font.name = "Times New Roman"
        r_head.font.size = Pt(11.5)
        r_head.font.bold = True
        r_head.font.color.rgb = COLOR_BLACK
        
        if note:
            r_note = p_head.add_run(f"({note})")
            r_note.font.name = "Times New Roman"
            r_note.font.size = Pt(11)
            r_note.font.italic = True
            r_note.font.color.rgb = COLOR_BLACK
            
        # Thêm nội dung các đoạn văn
        if isinstance(passage_text_or_paras, str):
            paras = [p.strip() for p in passage_text_or_paras.split('\n') if p.strip()]
        else:
            paras = passage_text_or_paras
            
        for para in paras:
            p = c.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.left_indent = Pt(8)
            p.paragraph_format.right_indent = Pt(8)
            p.paragraph_format.line_spacing = 1.15
            add_rich_text(p, para, default_size=Pt(11), default_color=COLOR_BLACK)

    def add_reading_translation(self, translation_text_or_paras, title="BẢN DỊCH TIẾNG VIỆT TOÀN VĂN BÀI ĐỌC"):
        """
        Thêm BẢN DỊCH TIẾNG VIỆT của bài đọc hiểu.
        YÊU CẦU BẮT BUỘC: Nếu có bài đọc thì phải dịch trọn vẹn sang tiếng Việt.
        Nền trắng, viền trên và dưới đơn mảnh, font 11pt, căn đều, giúp học sinh nắm vững ngữ nghĩa.
        """
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(2)
        
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        c = t.cell(0, 0)
        c.width = Mm(172)
        # Nền trắng, viền trên dưới mảnh, KHÔNG có sọc đen hai bên
        style_cell(c, bg_color=None, border_color="000000", top="single", bottom="single", left="none", right="none", sz="4")
        
        p_head = c.paragraphs[0]
        p_head.paragraph_format.space_before = Pt(4)
        p_head.paragraph_format.space_after = Pt(3)
        p_head.paragraph_format.left_indent = Pt(6)
        
        r_head = p_head.add_run(f"🌐 {title.upper()}:")
        r_head.font.name = "Times New Roman"
        r_head.font.size = Pt(11.5)
        r_head.font.bold = True
        r_head.font.color.rgb = COLOR_BLACK
        
        if isinstance(translation_text_or_paras, str):
            paras = [p.strip() for p in translation_text_or_paras.split('\n') if p.strip()]
        else:
            paras = translation_text_or_paras
            
        for para in paras:
            p = c.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.left_indent = Pt(10)
            p.paragraph_format.right_indent = Pt(8)
            p.paragraph_format.line_spacing = 1.15
            add_rich_text(p, para, default_size=Pt(11), default_color=COLOR_BLACK)

    def add_question(self, num_str, content_str="", options=None):
        """
        Thêm câu hỏi trắc nghiệm hoặc tự luận tiếng Anh.
        - num_str: e.g. "Question 1:" hoặc "Câu 1."
        - content_str: Nội dung câu hỏi (hỗ trợ <u>gạch chân</u>, **in đậm**)
        - options: dict {'A': '...', 'B': '...', 'C': '...', 'D': '...'} hoặc list [('A', '...'), ...]
        Tự động bố cục các phương án: 4 cột / 2 cột x 2 hàng / 4 hàng tùy theo độ dài phương án.
        """
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        r_num = p.add_run(num_str + " ")
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(11.5)
        r_num.font.bold = True
        r_num.font.color.rgb = COLOR_BLACK
        
        if content_str:
            add_rich_text(p, content_str, default_size=Pt(11), default_color=COLOR_BLACK)
            
        # Thêm các phương án nếu có
        if options:
            if isinstance(options, dict):
                opt_items = list(options.items())
            else:
                opt_items = options
                
            # Đánh giá độ dài text phương án
            max_len = max(len(str(val)) for _, val in opt_items) if opt_items else 0
            total_len = sum(len(str(val)) for _, val in opt_items) if opt_items else 0
            
            # 1. Nếu rất ngắn (ví dụ: các từ đơn trong bài ngữ âm/từ vựng): xếp 4 phương án trên 1 dòng
            if len(opt_items) == 4 and max_len <= 18 and total_len <= 65:
                p_opts = self.doc.add_paragraph()
                p_opts.paragraph_format.space_before = Pt(1)
                p_opts.paragraph_format.space_after = Pt(3)
                p_opts.paragraph_format.left_indent = Pt(12)
                p_opts.paragraph_format.line_spacing = 1.15
                
                # Chia tab hoặc dùng khoảng cách đều
                for idx, (label, text_val) in enumerate(opt_items):
                    r_lbl = p_opts.add_run(f"**{label}.** ")
                    add_rich_text(p_opts, str(text_val), default_size=Pt(11), default_color=COLOR_BLACK)
                    if idx < 3:
                        p_opts.add_run(" " * 8)
                        
            # 2. Nếu độ dài trung bình: xếp 2 hàng x 2 cột (A - B trên hàng 1, C - D trên hàng 2)
            elif len(opt_items) == 4 and max_len <= 45:
                # Hàng 1: A và B
                p_row1 = self.doc.add_paragraph()
                p_row1.paragraph_format.space_before = Pt(1)
                p_row1.paragraph_format.space_after = Pt(2)
                p_row1.paragraph_format.left_indent = Pt(12)
                p_row1.paragraph_format.line_spacing = 1.15
                
                # Tab stop tại giữa trang (Mm(85))
                p_row1.paragraph_format.tab_stops.add_tab_stop(Mm(85), WD_TAB_ALIGNMENT.LEFT)
                add_rich_text(p_row1, f"**{opt_items[0][0]}.** ", default_size=Pt(11), default_color=COLOR_BLACK)
                add_rich_text(p_row1, str(opt_items[0][1]), default_size=Pt(11), default_color=COLOR_BLACK)
                p_row1.add_run("\t")
                add_rich_text(p_row1, f"**{opt_items[1][0]}.** ", default_size=Pt(11), default_color=COLOR_BLACK)
                add_rich_text(p_row1, str(opt_items[1][1]), default_size=Pt(11), default_color=COLOR_BLACK)
                
                # Hàng 2: C và D
                p_row2 = self.doc.add_paragraph()
                p_row2.paragraph_format.space_before = Pt(1)
                p_row2.paragraph_format.space_after = Pt(3)
                p_row2.paragraph_format.left_indent = Pt(12)
                p_row2.paragraph_format.line_spacing = 1.15
                p_row2.paragraph_format.tab_stops.add_tab_stop(Mm(85), WD_TAB_ALIGNMENT.LEFT)
                add_rich_text(p_row2, f"**{opt_items[2][0]}.** ", default_size=Pt(11), default_color=COLOR_BLACK)
                add_rich_text(p_row2, str(opt_items[2][1]), default_size=Pt(11), default_color=COLOR_BLACK)
                p_row2.add_run("\t")
                add_rich_text(p_row2, f"**{opt_items[3][0]}.** ", default_size=Pt(11), default_color=COLOR_BLACK)
                add_rich_text(p_row2, str(opt_items[3][1]), default_size=Pt(11), default_color=COLOR_BLACK)
                
            # 3. Nếu dài: mỗi phương án 1 dòng riêng biệt
            else:
                for label, text_val in opt_items:
                    p_opt = self.doc.add_paragraph()
                    p_opt.paragraph_format.space_before = Pt(1)
                    p_opt.paragraph_format.space_after = Pt(2)
                    p_opt.paragraph_format.left_indent = Pt(12)
                    p_opt.paragraph_format.line_spacing = 1.15
                    add_rich_text(p_opt, f"**{label}.** ", default_size=Pt(11), default_color=COLOR_BLACK)
                    add_rich_text(p_opt, str(text_val), default_size=Pt(11), default_color=COLOR_BLACK)
                    
        return p

    def add_solution(self, solution_steps):
        """
        Thêm khung lời giải chi tiết (Solution Box) - Nền trắng, KHÔNG CÓ SỌC ĐEN BÊN TRÁI, font >= 11pt.
        Tuân thủ tuyệt đối quy chuẩn: style_cell(c, bg_color=None, top="none", bottom="none", left="none", right="none").
        """
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        c = t.cell(0, 0)
        c.width = Mm(172)
        # BỎ HOÀN TOÀN SỌC ĐEN BÊN TRÁI (left="none")
        style_cell(c, bg_color=None, top="none", bottom="none", left="none", right="none")
        
        first = True
        for step in solution_steps:
            kind = step[0]
            content = step[1] if len(step) > 1 else ""
            
            p = c.paragraphs[0] if first else c.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            
            if kind == 'title':
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.left_indent = Pt(6)
                r_icon = p.add_run(content if content else "✎ LỜI GIẢI CHI TIẾT & DỊCH NGHĨA:")
                r_icon.font.name = "Times New Roman"
                r_icon.font.size = Pt(11.5)
                r_icon.font.bold = True
                r_icon.font.color.rgb = COLOR_BLACK
                
            elif kind == 'key':
                # Đáp án đúng: e.g. "Đáp án đúng: C"
                p.paragraph_format.left_indent = Pt(8)
                r_k = p.add_run("► ")
                r_k.font.bold = True
                r_k.font.color.rgb = COLOR_BLACK
                add_rich_text(p, f"**{content}**", default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'translate_q':
                # Dịch nghĩa câu hỏi
                p.paragraph_format.left_indent = Pt(10)
                r_tq = p.add_run("• ")
                r_tq.font.bold = True
                add_rich_text(p, f"**Dịch câu:** {content}", default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'translate_opts':
                # Dịch nghĩa các phương án A, B, C, D
                p.paragraph_format.left_indent = Pt(10)
                r_to = p.add_run("• ")
                r_to.font.bold = True
                add_rich_text(p, f"**Nghĩa các lựa chọn:** {content}", default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'grammar':
                # Cấu trúc / Quy tắc ghi nhớ
                p.paragraph_format.left_indent = Pt(10)
                r_gm = p.add_run("• ")
                r_gm.font.bold = True
                add_rich_text(p, f"**Cấu trúc / Quy tắc:** {content}", default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'explain':
                # Giải thích chi tiết vì sao chọn
                p.paragraph_format.left_indent = Pt(10)
                r_ex = p.add_run("• ")
                r_ex.font.bold = True
                add_rich_text(p, f"**Giải thích chi tiết:** {content}", default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'evidence':
                # Dẫn chứng trong bài đọc
                p.paragraph_format.left_indent = Pt(10)
                r_ev = p.add_run("• ")
                r_ev.font.bold = True
                add_rich_text(p, f"**Dẫn chứng trong bài đọc:** *\"{content}\"*", default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'eliminate':
                # Phân tích phương án gây nhiễu
                p.paragraph_format.left_indent = Pt(10)
                r_el = p.add_run("• ")
                r_el.font.bold = True
                add_rich_text(p, f"**Loại trừ phương án:** {content}", default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'vocab':
                # Từ vựng mở rộng
                p.paragraph_format.left_indent = Pt(10)
                r_vc = p.add_run("• ")
                r_vc.font.bold = True
                add_rich_text(p, f"**Từ vựng cần nhớ:** {content}", default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'p':
                p.paragraph_format.left_indent = Pt(8)
                add_rich_text(p, content, default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'bullet':
                p.paragraph_format.left_indent = Pt(14)
                r_b = p.add_run("• ")
                r_b.font.bold = True
                r_b.font.size = Pt(11)
                r_b.font.color.rgb = COLOR_BLACK
                add_rich_text(p, content, default_size=Pt(11), default_color=COLOR_BLACK)
                
            elif kind == 'image':
                img_path = content
                img_w = step[2] if len(step) > 2 else Mm(110)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(2)
                run_img = p.add_run()
                run_img.add_picture(img_path, width=img_w)
                
            elif kind == 'caption':
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(4)
                r_cap = p.add_run(content)
                r_cap.font.name = "Times New Roman"
                r_cap.font.size = Pt(11)
                r_cap.font.italic = True
                r_cap.font.color.rgb = COLOR_BLACK
                
            first = False
            
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(4)

    def add_solution_box(self, key, explanation=None, translation=None,
                         options_meaning=None, grammar=None, evidence=None,
                         eliminate=None, vocab=None, title=None, extra_steps=None):
        """
        Helper tiện dụng tạo khung lời giải chuẩn tiếng Anh bao gồm đầy đủ các mục giải thích.
        """
        sol_steps = [('title', title or "✎ LỜI GIẢI CHI TIẾT & DỊCH NGHĨA:")]
        if key:
            sol_steps.append(('key', f"Đáp án đúng: {key}"))
        if translation:
            sol_steps.append(('translate_q', translation))
        if options_meaning:
            sol_steps.append(('translate_opts', options_meaning))
        if grammar:
            sol_steps.append(('grammar', grammar))
        if explanation:
            sol_steps.append(('explain', explanation))
        if evidence:
            sol_steps.append(('evidence', evidence))
        if eliminate:
            sol_steps.append(('eliminate', eliminate))
        if vocab:
            sol_steps.append(('vocab', vocab))
            
        if extra_steps:
            for st in extra_steps:
                if isinstance(st, tuple):
                    sol_steps.append(st)
                elif isinstance(st, str):
                    clean_st = st.lstrip('• ').strip() if st.strip().startswith('•') else st
                    kind = 'bullet' if st.strip().startswith('•') else 'p'
                    sol_steps.append((kind, clean_st))
                    
        self.add_solution(sol_steps)

    def add_quick_answer_key(self, answers_dict_or_list):
        """
        Thêm bảng tổng hợp đáp án nhanh (Quick Answer Key) ở đầu hoặc cuối tài liệu.
        Bảng chia thành các khối 10 câu/hàng tiện theo dõi.
        """
        if isinstance(answers_dict_or_list, dict):
            items = list(answers_dict_or_list.items())
        else:
            items = answers_dict_or_list
            
        if not items:
            return
            
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(2)
        
        self.add_section("BẢNG ĐÁP ÁN NHANH (QUICK ANSWER KEY)", "Dành cho học sinh và giáo viên tra cứu đối chiếu.")
        
        # Chia thành từng nhóm 10 câu
        chunk_size = 10
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            cols = len(chunk) + 1  # 1 cột nhãn + các cột câu hỏi
            
            t = self.doc.add_table(rows=2, cols=cols)
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.autofit = False
            
            w_label = Mm(22)
            w_col = Mm((172 - 22) / len(chunk))
            
            # Cột nhãn hàng 1: Câu
            c_h1 = t.cell(0, 0)
            c_h1.width = w_label
            style_cell(c_h1, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
            p = c_h1.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run("Câu")
            r.bold = True
            r.font.size = Pt(11)
            
            # Cột nhãn hàng 2: Đ/A
            c_h2 = t.cell(1, 0)
            c_h2.width = w_label
            style_cell(c_h2, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
            p = c_h2.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run("Đ/A")
            r.bold = True
            r.font.size = Pt(11)
            
            # Điền các câu hỏi
            for col_idx, (q_num, ans) in enumerate(chunk, start=1):
                # Ô số câu
                c_q = t.cell(0, col_idx)
                c_q.width = w_col
                style_cell(c_q, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
                p = c_q.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                # Rút gọn nhãn câu nếu dài (ví dụ "Question 1" -> "1")
                q_short = re.sub(r'^(Question|Câu)\s*', '', str(q_num), flags=re.IGNORECASE).rstrip(':').rstrip('.')
                r = p.add_run(q_short)
                r.bold = True
                r.font.size = Pt(11)
                
                # Ô đáp án
                c_a = t.cell(1, col_idx)
                c_a.width = w_col
                style_cell(c_a, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
                p = c_a.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(str(ans))
                r.bold = True
                r.font.size = Pt(11)
                
            p_space = self.doc.add_paragraph()
            p_space.paragraph_format.space_before = Pt(2)
            p_space.paragraph_format.space_after = Pt(2)

    def add_vocabulary_table(self, vocab_items):
        """
        Thêm Bảng Tổng Hợp Từ Vựng & Cấu Trúc Trọng Tâm (Vocabulary & Structures).
        vocab_items: list các tuple hoặc dict:
        (Từ vựng, Phiên âm IPA, Loại từ, Nghĩa tiếng Việt, Ví dụ / Collocation)
        """
        if not vocab_items:
            return
            
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(2)
        
        self.add_section("TỪ VỰNG & CẤU TRÚC TRỌNG TÂM (KEY VOCABULARY)", "Các từ vựng, cụm từ vựng và cấu trúc ngữ pháp cần ghi nhớ.")
        
        rows_count = len(vocab_items) + 1
        t = self.doc.add_table(rows=rows_count, cols=5)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        
        w_stt = Mm(12)
        w_word = Mm(36)
        w_ipa = Mm(32)
        w_pos = Mm(20)
        w_mean = Mm(72)
        
        widths = [w_stt, w_word, w_ipa, w_pos, w_mean]
        headers = ["STT", "Từ vựng / Cụm từ", "Phiên âm (IPA)", "Loại từ", "Nghĩa & Ví dụ minh họa"]
        
        # Header hàng 0
        for col_idx, (w, h_text) in enumerate(zip(widths, headers)):
            c = t.cell(0, col_idx)
            c.width = w
            style_cell(c, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(h_text)
            r.bold = True
            r.font.size = Pt(11)
            r.font.color.rgb = COLOR_BLACK
            
        # Data rows
        for row_idx, item in enumerate(vocab_items, start=1):
            if isinstance(item, dict):
                stt = str(row_idx)
                word = item.get('word', '')
                ipa = item.get('ipa', '')
                pos = item.get('pos', '')
                mean = item.get('meaning', '')
                if item.get('example'):
                    mean += f" (VD: {item.get('example')})"
            else:
                stt = str(row_idx)
                word = item[0] if len(item) > 0 else ''
                ipa = item[1] if len(item) > 1 else ''
                pos = item[2] if len(item) > 2 else ''
                mean = item[3] if len(item) > 3 else ''
                if len(item) > 4 and item[4]:
                    mean += f" (VD: {item[4]})"
                    
            row_data = [stt, word, ipa, pos, mean]
            aligns = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
            
            for col_idx, (w, val, align) in enumerate(zip(widths, row_data, aligns)):
                c = t.cell(row_idx, col_idx)
                c.width = w
                style_cell(c, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
                p = c.paragraphs[0]
                p.alignment = align
                p.paragraph_format.line_spacing = 1.15
                if col_idx == 1:
                    # Word in bold
                    r = p.add_run(val)
                    r.bold = True
                    r.font.size = Pt(11)
                else:
                    add_rich_text(p, val, default_size=Pt(11), default_color=COLOR_BLACK)

    def add_self_evaluation(self, criteria_list):
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(2)
        
        self.add_section(
            "PHẦN ĐÁNH GIÁ KẾT QUẢ VÀ NĂNG LỰC",
            "Học sinh tự đánh dấu mức độ đạt được và đối chiếu kết quả."
        )
        
        rows_count = len(criteria_list) + 1
        eval_table = self.doc.add_table(rows=rows_count, cols=2)
        eval_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        eval_table.autofit = False
        
        w_col0 = Mm(36)
        w_col1 = Mm(136)
        
        h0 = eval_table.cell(0, 0)
        h1 = eval_table.cell(0, 1)
        h0.width = w_col0
        h1.width = w_col1
        style_cell(h0, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
        style_cell(h1, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
        
        p0 = h0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run("Đánh giá")
        r0.bold = True
        r0.font.size = Pt(11)
        r0.font.color.rgb = COLOR_BLACK
        
        p1 = h1.paragraphs[0]
        r1 = p1.add_run("Nội dung kỹ năng & Mục tiêu cần đạt")
        r1.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = COLOR_BLACK
        
        for idx, crit in enumerate(criteria_list, start=1):
            c0 = eval_table.cell(idx, 0)
            c1 = eval_table.cell(idx, 1)
            c0.width = w_col0
            c1.width = w_col1
            style_cell(c0, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
            style_cell(c1, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
            
            p0 = c0.paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_box = p0.add_run("☑ Đạt    ☐ Chưa" if self.is_solved else "☐ Đạt    ☐ Chưa")
            r_box.font.size = Pt(11)
            r_box.font.color.rgb = COLOR_BLACK
            
            p1 = c1.paragraphs[0]
            p1.paragraph_format.left_indent = Pt(6)
            r_text = p1.add_run(crit)
            r_text.font.size = Pt(11)
            r_text.font.color.rgb = COLOR_BLACK

    def add_teacher_feedback_and_signature(self, teacher_name="Nguyễn Văn Dũng – MathPlus Academy"):
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(2)
        
        rem_table = self.doc.add_table(rows=1, cols=1)
        rem_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        rem_table.autofit = False
        rem_cell = rem_table.cell(0, 0)
        rem_cell.width = Mm(172)
        style_cell(rem_cell, bg_color=None, border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
        
        p_rem = rem_cell.paragraphs[0]
        p_rem.paragraph_format.space_before = Pt(4)
        p_rem.paragraph_format.space_after = Pt(4)
        p_rem.paragraph_format.line_spacing = 1.3
        
        r_rt = p_rem.add_run("Nhận xét của giáo viên bộ môn:\n")
        r_rt.font.bold = True
        r_rt.font.size = Pt(11.5)
        r_rt.font.color.rgb = COLOR_BLACK
        
        r_dots = p_rem.add_run(
            "…………………………………………………………………………………………………………………………………………\n"
            "…………………………………………………………………………………………………………………………………………\n"
            "…………………………………………………………………………………………………………………………………………"
        )
        r_dots.font.size = Pt(11)
        r_dots.font.color.rgb = COLOR_BLACK
        
        p_sig = self.doc.add_paragraph()
        p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_sig.paragraph_format.space_before = Pt(10)
        p_sig.paragraph_format.space_after = Pt(2)
        
        r_sig1 = p_sig.add_run("Hà Nội, ngày …… tháng …… năm 2026\n")
        r_sig1.font.size = Pt(11)
        r_sig1.font.italic = True
        r_sig1.font.color.rgb = COLOR_BLACK
        
        r_sig2 = p_sig.add_run(f"Giáo viên: {teacher_name}")
        r_sig2.font.size = Pt(11.5)
        r_sig2.font.bold = True
        r_sig2.font.color.rgb = COLOR_BLACK

    def save(self, filepath):
        for elem in self.doc.settings.element.iter():
            if elem.tag.endswith('zoom'):
                elem.set(qn('w:percent'), '100')
                
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        self.doc.save(filepath)
        return filepath
