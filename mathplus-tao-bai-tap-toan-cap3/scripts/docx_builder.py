#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Engine tạo tài liệu Word (.docx) phiếu bài tập môn Toán chuẩn thương hiệu MathPlus Academy.
Tuân thủ nghiêm ngặt các quy tắc:
1. Phông chữ chuẩn Times New Roman, cỡ chữ tối thiểu 11pt toàn văn bản.
2. Chữ màu đen tuyền 100% (RGBColor(0,0,0)), nền trắng hoàn toàn (không viền đen bên trái).
3. Logo MathPlus nguyên màu thương hiệu tại Header và Top Banner.
4. Thông tin giáo viên Thầy Dũng: 'Thầy Nguyễn Văn Dũng – Hotline: 0977 961 189'.
5. Footer hiển thị thông tin giáo viên, trung tâm và số trang động 'Trang PAGE'.
6. 100% công thức toán học chuyển đổi sang Office Open XML Math (OMML) bản địa gõ được.
7. Phân loại bài tập rõ ràng từ dễ đến khó (Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao).
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

COLOR_BLACK = RGBColor(0, 0, 0)
COLOR_WHITE = RGBColor(255, 255, 255)

def find_mathplus_logo(custom_path=None):
    """Tìm đường dẫn tệp logo MathPlus Academy."""
    candidates = [
        custom_path,
        os.path.join(os.path.dirname(__file__), "..", "resources", "logo.jpg"),
        os.path.join(os.path.dirname(__file__), "..", "resources", "logo.png"),
        r"C:\code\mathplus\public\images\logo.jpg",
        r"C:\code\mathplus\public\images\logo.png",
        "/Volumes/data/code/mathplus/public/images/logo.jpg",
        "/Volumes/data/code/skills/mathplus-add-logo/resources/logo.jpg",
        os.path.join(os.getcwd(), "public", "images", "logo.jpg"),
    ]
    for c in candidates:
        if c and os.path.exists(c) and os.path.isfile(c):
            return os.path.abspath(c)
    return None

def style_cell(cell, bg_color=None, border_color="000000", top="none", bottom="none", left="none", right="none", sz="4"):
    """Thiết lập màu nền và đường viền cho ô theo đúng chuẩn OpenXML ECMA-376."""
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
    """Chèn công thức toán nội dòng (inline) vào đoạn văn bản."""
    try:
        omml = latex_to_omml(latex_code, display=False)
        p._p.append(omml)
    except Exception as e:
        # Nếu lỗi chuyển đổi thì hiển thị mã thô
        r = p.add_run(f" ${latex_code}$ ")
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_BLACK

def add_display_math(doc_or_cell, latex_code, space_before=Pt(2), space_after=Pt(3)):
    """Chèn công thức toán dạng khối (display math) căn giữa."""
    p = doc_or_cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = space_before
    p.paragraph_format.space_after = space_after
    try:
        omml = latex_to_omml(latex_code, display=True)
        p._p.append(omml)
    except Exception as e:
        r = p.add_run(latex_code)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_BLACK
    return p

def add_rich_text(p, text, default_font="Times New Roman", default_size=Pt(11),
                  default_color=COLOR_BLACK, default_bold=False, default_italic=False):
    """
    Phân tích chuỗi chứa văn bản, ký hiệu LaTeX ($...$ hoặc $$...$$) và định dạng markdown (**in đậm**, *in nghiêng*)
    rồi tạo các Run tương ứng có cỡ chữ tối thiểu 11pt, màu đen tuyền.
    """
    effective_size = Pt(11) if default_size < Pt(11) else default_size
    tokens = re.split(r'(\${1,2}[^$]+\${1,2})', text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('$$') and token.endswith('$$') and len(token) > 4:
            math_code = token[2:-2].strip()
            add_inline_math(p, math_code)
        elif token.startswith('$') and token.endswith('$') and len(token) > 2:
            math_code = token[1:-1].strip()
            add_inline_math(p, math_code)
        else:
            md_tokens = re.split(r'(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*)', token)
            for md_tok in md_tokens:
                if not md_tok:
                    continue
                if md_tok.startswith('***') and md_tok.endswith('***') and len(md_tok) > 6:
                    run = p.add_run(md_tok[3:-3])
                    run.font.name = default_font
                    run.font.size = effective_size
                    run.font.color.rgb = COLOR_BLACK
                    run.font.bold = True
                    run.font.italic = True
                elif md_tok.startswith('**') and md_tok.endswith('**') and len(md_tok) > 4:
                    run = p.add_run(md_tok[2:-2])
                    run.font.name = default_font
                    run.font.size = effective_size
                    run.font.color.rgb = COLOR_BLACK
                    run.font.bold = True
                    run.font.italic = default_italic
                elif md_tok.startswith('*') and md_tok.endswith('*') and len(md_tok) > 2:
                    run = p.add_run(md_tok[1:-1])
                    run.font.name = default_font
                    run.font.size = effective_size
                    run.font.color.rgb = COLOR_BLACK
                    run.font.bold = default_bold
                    run.font.italic = True
                else:
                    clean_tok = md_tok.replace('**', '')
                    run = p.add_run(clean_tok)
                    run.font.name = default_font
                    run.font.size = effective_size
                    run.font.color.rgb = COLOR_BLACK
                    run.font.bold = default_bold
                    run.font.italic = default_italic

class MathPlusWorksheetBuilder:
    def __init__(self, topic, grade="12", total_count=20, time_limit="90 phút", is_solved=False, logo_path=None):
        self.doc = Document()
        self.topic = topic
        self.grade = str(grade)
        self.total_count = total_count
        self.time_limit = time_limit
        self.is_solved = is_solved
        self.logo_path = find_mathplus_logo(logo_path)
        
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
        normal_style.font.color.rgb = COLOR_BLACK

    def _setup_header_footer(self):
        section = self.doc.sections[0]
        header = section.header
        p_h = header.paragraphs[0]
        p_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_h.paragraph_format.space_before = Pt(0)
        p_h.paragraph_format.space_after = Pt(0)
        
        # Header ở các trang sau: Logo MathPlus nhỏ + "Trung tâm MathPlus Academy" (in nghiêng 11pt)
        if self.logo_path and os.path.exists(self.logo_path):
            r_logo = p_h.add_run()
            r_logo.add_picture(self.logo_path, width=Mm(7.5))
            
        r_h = p_h.add_run("  Trung tâm MathPlus Academy")
        r_h.font.name = "Times New Roman"
        r_h.font.size = Pt(11)
        r_h.font.italic = True
        r_h.font.color.rgb = COLOR_BLACK

        def setup_ftr(footer_obj):
            p_f = footer_obj.paragraphs[0]
            p_f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p_f.paragraph_format.tab_stops.add_tab_stop(Mm(172), WD_TAB_ALIGNMENT.RIGHT)
            
            r_f1 = p_f.add_run("Giáo viên: Thầy Nguyễn Văn Dũng – MathPlus Academy  |  Hotline: 0977 961 189")
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
        """Tạo Top Banner trang 1 chuyên nghiệp theo chuẩn nhận diện thương hiệu MathPlus."""
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
            
        # Cột trái: Logo và thông tin trung tâm MathPlus Academy
        p_logo = c_left.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(0)
        p_logo.paragraph_format.space_after = Pt(2)
        
        if self.logo_path and os.path.exists(self.logo_path):
            r_img = p_logo.add_run()
            r_img.add_picture(self.logo_path, width=Mm(18.0))
            
        p_name = c_left.add_paragraph()
        p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_name.paragraph_format.space_before = Pt(2)
        p_name.paragraph_format.space_after = Pt(1)
        r_n = p_name.add_run("TRUNG TÂM MATHPLUS ACADEMY")
        r_n.font.name = "Times New Roman"
        r_n.font.size = Pt(11)
        r_n.font.bold = True
        r_n.font.color.rgb = COLOR_BLACK
        
        p_hotline = c_left.add_paragraph()
        p_hotline.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hotline.paragraph_format.space_before = Pt(0)
        p_hotline.paragraph_format.space_after = Pt(2)
        r_h = p_hotline.add_run("Hotline: 0977 961 189  •  mathplus.com.vn")
        r_h.font.name = "Times New Roman"
        r_h.font.size = Pt(11)
        r_h.font.italic = True
        r_h.font.color.rgb = COLOR_BLACK

        # Cột phải: Tiêu đề chuyên đề, giáo viên Thầy Dũng & thông tin học sinh
        p_title = c_right.paragraphs[0]
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_before = Pt(0)
        p_title.paragraph_format.space_after = Pt(2)
        
        suffix = " (ĐÁP ÁN & LỜI GIẢI CHI TIẾT)" if self.is_solved else ""
        r_t = p_title.add_run(f"PHIẾU BÀI TẬP TOÁN {self.grade}{suffix}")
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(12)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_BLACK
        
        p_sub = c_right.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.paragraph_format.space_before = Pt(0)
        p_sub.paragraph_format.space_after = Pt(2)
        r_sub = p_sub.add_run(f"Chuyên đề: {self.topic.upper()}\n(Phân hóa từ Dễ đến Khó – GDPT 2018)")
        r_sub.font.name = "Times New Roman"
        r_sub.font.size = Pt(11)
        r_sub.font.bold = True
        r_sub.font.color.rgb = COLOR_BLACK
        
        p_thay = c_right.add_paragraph()
        p_thay.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_thay.paragraph_format.space_before = Pt(1)
        p_thay.paragraph_format.space_after = Pt(2)
        r_thay = p_thay.add_run("Giáo viên phụ trách: Thầy Nguyễn Văn Dũng – Hotline: 0977 961 189")
        r_thay.font.name = "Times New Roman"
        r_thay.font.size = Pt(11)
        r_thay.font.italic = True
        r_thay.font.bold = True
        r_thay.font.color.rgb = COLOR_BLACK

        # Khung điền thông tin học sinh
        p_hs = c_right.add_paragraph()
        p_hs.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_hs.paragraph_format.space_before = Pt(2)
        p_hs.paragraph_format.space_after = Pt(0)
        r_hs = p_hs.add_run("Họ và tên HS: ................................................ Lớp: ............. Điểm: .........")
        r_hs.font.name = "Times New Roman"
        r_hs.font.size = Pt(11)
        r_hs.font.color.rgb = COLOR_BLACK
        
        # Đường kẻ phân cách nhẹ
        style_cell(c_left, bg_color="FFFFFF", border_color="000000", bottom="single", sz="6")
        style_cell(c_right, bg_color="FFFFFF", border_color="000000", bottom="single", sz="6")
        
        # Thêm khoảng cách sau Top Banner
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(0)

    def add_section_header(self, title, description=""):
        """Thêm tiêu đề phân phần theo mức độ khó (Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao)."""
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        
        run = p.add_run(f"■ {title.upper()}")
        run.font.name = "Times New Roman"
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_BLACK
        
        if description:
            p_desc = self.doc.add_paragraph()
            p_desc.paragraph_format.space_before = Pt(0)
            p_desc.paragraph_format.space_after = Pt(4)
            p_desc.paragraph_format.keep_with_next = True
            r_d = p_desc.add_run(f"({description})")
            r_d.font.name = "Times New Roman"
            r_d.font.size = Pt(11)
            r_d.font.italic = True
            r_d.font.color.rgb = COLOR_BLACK

    def add_question(self, q_index, q_text, options=None, level_name=None):
        """
        Thêm một câu hỏi vào tài liệu.
        options: list gồm 4 lựa chọn ['A. ...', 'B. ...', 'C. ...', 'D. ...'] (nếu trắc nghiệm)
        """
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        
        prefix = f"Câu {q_index}."
        if level_name:
            prefix += f" [{level_name}]"
        
        r_pre = p.add_run(f"{prefix} ")
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_BLACK
        
        add_rich_text(p, q_text)
        
        # Nếu có các phương án lựa chọn A, B, C, D
        if options and len(options) == 4:
            # Kiểm tra độ dài các phương án để xếp 4 cột hoặc 2 cột hoặc 1 dòng
            max_len = max(len(opt) for opt in options)
            if max_len < 25:
                # Xếp thành bảng 1 hàng 4 cột không viền
                tbl = self.doc.add_table(rows=1, cols=4)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                tbl.autofit = False
                widths = [Mm(42), Mm(42), Mm(42), Mm(42)]
                for i in range(4):
                    c = tbl.cell(0, i)
                    c.width = widths[i]
                    style_cell(c, bg_color="FFFFFF")
                    p_opt = c.paragraphs[0]
                    p_opt.paragraph_format.space_before = Pt(1)
                    p_opt.paragraph_format.space_after = Pt(2)
                    add_rich_text(p_opt, options[i])
            elif max_len < 55:
                # Xếp thành bảng 2 hàng 2 cột không viền
                tbl = self.doc.add_table(rows=2, cols=2)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                tbl.autofit = False
                widths = [Mm(85), Mm(85)]
                for r in range(2):
                    for c_idx in range(2):
                        opt_idx = r * 2 + c_idx
                        c = tbl.cell(r, c_idx)
                        c.width = widths[c_idx]
                        style_cell(c, bg_color="FFFFFF")
                        p_opt = c.paragraphs[0]
                        p_opt.paragraph_format.space_before = Pt(1)
                        p_opt.paragraph_format.space_after = Pt(2)
                        add_rich_text(p_opt, options[opt_idx])
            else:
                # Mỗi phương án trên một dòng riêng
                for opt in options:
                    p_opt = self.doc.add_paragraph()
                    p_opt.paragraph_format.left_indent = Mm(6)
                    p_opt.paragraph_format.space_before = Pt(1)
                    p_opt.paragraph_format.space_after = Pt(2)
                    add_rich_text(p_opt, opt)

    def add_solution_box(self, answer_key, solution_steps):
        """
        Thêm khung lời giải chi tiết cho câu hỏi:
        - Nền trắng, KHÔNG có sọc đen bên trái.
        - Phông chữ Times New Roman tối thiểu 11pt, màu đen tuyền.
        """
        tbl = self.doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Mm(172)
        
        # Viền mỏng xung quanh hoặc không viền, nền trắng 100%, không sọc đen viền trái
        style_cell(cell, bg_color="FFFFFF", border_color="000000", top="single", bottom="single", left="none", right="none", sz="4")
        
        p_title = cell.paragraphs[0]
        p_title.paragraph_format.space_before = Pt(3)
        p_title.paragraph_format.space_after = Pt(2)
        
        r_t = p_title.add_run(f"✎ LỜI GIẢI CHI TIẾT  –  ĐÁP ÁN: ")
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(11)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_BLACK
        
        r_ans = p_title.add_run(f"{answer_key}")
        r_ans.font.name = "Times New Roman"
        r_ans.font.size = Pt(11.5)
        r_ans.font.bold = True
        r_ans.font.color.rgb = COLOR_BLACK
        
        for item in solution_steps:
            if isinstance(item, tuple):
                kind, content = item
            else:
                kind, content = 'p', item
                
            if kind == 'display_math':
                add_display_math(cell, content, space_before=Pt(2), space_after=Pt(2))
            else:
                p_step = cell.add_paragraph()
                p_step.paragraph_format.space_before = Pt(1)
                p_step.paragraph_format.space_after = Pt(2)
                if kind == 'bullet':
                    p_step.paragraph_format.left_indent = Mm(4)
                    r_dot = p_step.add_run("• ")
                    r_dot.font.name = "Times New Roman"
                    r_dot.font.size = Pt(11)
                    r_dot.font.bold = True
                    r_dot.font.color.rgb = COLOR_BLACK
                add_rich_text(p_step, content)

    def add_quick_answer_grid(self, answers):
        """
        Thêm bảng đáp án trắc nghiệm nhanh ở đầu file Lời giải chi tiết:
        answers: list các tuple (câu_số, đáp_án, mức_độ)
        """
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run("BẢNG ĐÁP ÁN TRẮC NGHIỆM TỔNG HỢP")
        r.font.name = "Times New Roman"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_BLACK
        
        num_items = len(answers)
        cols = 10 if num_items >= 10 else num_items
        rows = (num_items + cols - 1) // cols
        
        # Bảng câu hỏi & đáp án
        tbl = self.doc.add_table(rows=rows * 2, cols=cols)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        col_w = Mm(172 / cols)
        
        for idx, (q_num, ans_char, _) in enumerate(answers):
            r_block = idx // cols
            c_idx = idx % cols
            row_q = r_block * 2
            row_a = r_block * 2 + 1
            
            # Ô số thứ tự câu
            cell_q = tbl.cell(row_q, c_idx)
            cell_q.width = col_w
            style_cell(cell_q, bg_color="FFFFFF", border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
            p_q = cell_q.paragraphs[0]
            p_q.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_q.paragraph_format.space_before = Pt(1)
            p_q.paragraph_format.space_after = Pt(1)
            rq = p_q.add_run(f"{q_num}")
            rq.font.name = "Times New Roman"
            rq.font.size = Pt(11)
            rq.font.bold = True
            rq.font.color.rgb = COLOR_BLACK
            
            # Ô đáp án
            cell_a = tbl.cell(row_a, c_idx)
            cell_a.width = col_w
            style_cell(cell_a, bg_color="FFFFFF", border_color="000000", top="single", bottom="single", left="single", right="single", sz="4")
            p_a = cell_a.paragraphs[0]
            p_a.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_a.paragraph_format.space_before = Pt(1)
            p_a.paragraph_format.space_after = Pt(1)
            ra = p_a.add_run(f"{ans_char}")
            ra.font.name = "Times New Roman"
            ra.font.size = Pt(11)
            ra.font.bold = True
            ra.font.color.rgb = COLOR_BLACK
            
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(6)
        p_sp.paragraph_format.space_after = Pt(0)

    def save(self, filepath):
        """Lưu tài liệu Word hoàn chỉnh."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        self.doc.save(filepath)
        return filepath
