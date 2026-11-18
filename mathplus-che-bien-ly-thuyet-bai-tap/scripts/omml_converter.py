#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module chuyển đổi công thức Toán học (LaTeX) sang định dạng chuẩn
Microsoft Office Open XML Math (OMML) sử dụng stylesheet XSLT chính thức của Word.
"""

import os
import re
import latex2mathml.converter
import lxml.etree as ET

# Tìm đường dẫn XSLT chuyển đổi MathML -> OMML
DEFAULT_XSLT_PATHS = [
    r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL',
    r'C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL',
    r'C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL',
    r'C:\Program Files\Microsoft Office\Office15\MML2OMML.XSL',
    '/Applications/Microsoft Word.app/Contents/Resources/mathml2omml.xsl',
    '/Applications/Microsoft Word.app/Contents/Resources/MML2OMML.XSL',
    '/Library/Application Support/Microsoft/Office365/MML2OMML.XSL',
    os.path.expanduser('~/.gemini/antigravity/mcp/mathml2omml.xsl')
]

_xslt_transform = None

def get_omml_transform():
    global _xslt_transform
    if _xslt_transform is not None:
        return _xslt_transform
    
    xslt_path = None
    for p in DEFAULT_XSLT_PATHS:
        if os.path.exists(p):
            xslt_path = p
            break
            
    if not xslt_path:
        raise FileNotFoundError(
            "Không tìm thấy file mathml2omml.xsl. Vui lòng kiểm tra cài đặt Microsoft Word trên máy."
        )
        
    xslt_tree = ET.parse(xslt_path)
    _xslt_transform = ET.XSLT(xslt_tree)
    return _xslt_transform

def latex_to_omml(latex_code, display=False):
    """
    Chuyển đổi chuỗi công thức LaTeX sang thẻ XML OMML (lxml Element).
    
    Args:
        latex_code (str): Chuỗi công thức toán dạng LaTeX (ví dụ: r'\\forall x \\in \\mathbb{R}, x^2 \\geq 0')
        display (bool): True nếu là công thức khối (block math trên dòng riêng),
                        False nếu là công thức nội dòng (inline math).
                        
    Returns:
        lxml.etree._Element: Phần tử gốc của OMML (<m:oMath> hoặc <m:oMathPara>)
    """
    transform = get_omml_transform()
    tex = latex_code.strip()
    
    # Chuẩn hóa các tập hợp số
    tex = tex.replace(r'\mathbb R', r'\mathbb{R}').replace(r'\mathbb Z', r'\mathbb{Z}')
    tex = tex.replace(r'\mathbb Q', r'\mathbb{Q}').replace(r'\mathbb N', r'\mathbb{N}')
    tex = tex.replace(r'\mathbb C', r'\mathbb{C}')
    
    # Chuẩn hóa khoảng cách trong MathML
    tex = tex.replace(r'\qquad', r'\ \ \ \ ').replace(r'\quad', r'\ \ ')
    
    # Xử lý môi trường cases / matrix (latex2mathml yêu cầu \cr thay vì \\ để ngắt dòng)
    if r'\begin{cases}' in tex:
        inner = re.search(r'\\begin\{cases\}(.*?)\\end\{cases\}', tex, re.DOTALL)
        if inner:
            inner_content = inner.group(1)
            lines = [l.strip().rstrip('\\').rstrip(',').strip() for l in inner_content.split('\n') if l.strip()]
            if len(lines) == 1:
                lines = [l.strip().rstrip(',').strip() for l in inner_content.split('\\\\') if l.strip()]
            fixed_inner = ' \\cr '.join(lines)
            tex = f"\\begin{{cases}} {fixed_inner} \\end{{cases}}"
            
    # Chuyển đổi LaTeX sang MathML
    mml = latex2mathml.converter.convert(tex, display='block' if display else 'inline')
    dom = ET.fromstring(mml)
    
    # Áp dụng XSLT để sinh ra OMML
    omml = transform(dom).getroot()
    
    # Xóa các phần tử argPr không cần thiết để đảm bảo chuẩn schema ECMA-376 nghiêm ngặt
    for arg_pr in omml.findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}argPr'):
        parent = arg_pr.getparent()
        if parent is not None:
            parent.remove(arg_pr)
            
    return omml
