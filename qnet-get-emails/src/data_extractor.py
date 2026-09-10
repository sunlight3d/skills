import os
import re
import cv2
import numpy as np
import pymupdf
from typing import Dict, Any, Optional

try:
    from rapidocr_onnxruntime import RapidOCR
    _ocr_engine = RapidOCR()
except Exception:
    _ocr_engine = None

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF file.
    If PDF is text-based and contains core keywords, uses PyMuPDF.
    If PDF is scanned, incomplete (< 400 chars), or lacks key template sections,
    runs RapidOCR on rendered page images to get complete text.
    """
    if not pdf_path or not os.path.exists(pdf_path):
        return ""

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"[!] Error opening PDF {pdf_path}: {e}")
        return ""

    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    
    full_text = "\n".join(pages_text).strip()
    txt_lower = full_text.lower()
    
    has_core_keywords = any(kw in txt_lower for kw in ["đăng ký", "thông tin", "doanh nghiệp", "tài khoản"])

    if len(full_text) > 500 and has_core_keywords:
        doc.close()
        return full_text

    # Otherwise run OCR to obtain all text elements
    ocr_lines = []
    if _ocr_engine is not None:
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
            if pix.n == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            ocr_res, _ = _ocr_engine(img)
            if ocr_res:
                for line in ocr_res:
                    ocr_lines.append(line[1])
    
    doc.close()
    ocr_text = "\n".join(ocr_lines).strip()
    
    if len(ocr_text) > len(full_text):
        return ocr_text
    elif full_text:
        return f"{full_text}\n\n{ocr_text}"
    return ocr_text

def parse_pdf_fields(pdf_text: str, email_subject: str = "") -> Dict[str, Any]:
    """
    Extract structured fields from PDF text according to template01.docx:
    - loai_du_an, doi_tuong_dang_ky
    - ten_doanh_nghiep, ma_qhns, ngay_cap_co_quan_cap, tru_so_chinh, nguoi_dai_dien, chuc_vu_dai_dien, ma_vsic
    - ho_ten_nguoi_quan_ly, chuc_vu_nguoi_quan_ly, don_vi_cong_tac, so_cmnd_cccd, sdt_di_dong, thu_dien_tu
    """
    txt = pdf_text or ""
    lines = [l.strip() for l in txt.splitlines() if l.strip()]

    data = {
        "loai_du_an": "",
        "doi_tuong_dang_ky": "",
        "ten_doanh_nghiep": "",
        "ma_qhns": "",
        "ngay_cap_co_quan_cap": "",
        "tru_so_chinh": "",
        "nguoi_dai_dien": "",
        "chuc_vu_dai_dien": "",
        "ma_vsic": "",
        "ho_ten_nguoi_quan_ly": "",
        "chuc_vu_nguoi_quan_ly": "",
        "don_vi_cong_tac": "",
        "so_cmnd_cccd": "",
        "sdt_di_dong": "",
        "thu_dien_tu": ""
    }

    # 1. Loại dự án
    loai_du_an_list = []
    if re.search(r'Lu[aậ]t\s*DTC|Lu[aậ]t\s*[Đđ]TC', txt, re.I):
        loai_du_an_list.append("Dự án theo Luật ĐTC")
    if re.search(r'Lu[aậ]t\s*PPP', txt, re.I):
        loai_du_an_list.append("Dự án theo Luật PPP")
    if re.search(r'Lu[aậ]t\s*[đd][aầ]u\s*t[uư]', txt, re.I):
        loai_du_an_list.append("Dự án theo Luật đầu tư")
    data["loai_du_an"] = ", ".join(loai_du_an_list) if loai_du_an_list else "Dự án theo Luật đầu tư"

    # Line-by-line parsing for high precision
    for line in lines:
        # Đối tượng đăng ký
        if not data["doi_tuong_dang_ky"] and re.search(r'[ĐđD]oi\s*t[uư]?[oợ]?ng\s*[đd]ang\s*k[yý]', line, re.I):
            m = re.search(r'(?:[ĐđD]oi\s*t[uư]?[oợ]?ng\s*[đd]ang\s*k[yý](?:\s*t[aà]i\s*kho[aả]n)?)\s*[:\s]*(.+)$', line, re.I)
            if m:
                data["doi_tuong_dang_ky"] = m.group(1).strip().strip(".-_ ")

        # 2.1 Tên doanh nghiệp
        if not data["ten_doanh_nghiep"] and re.search(r'2\.1\b', line, re.I):
            val = re.sub(r'^2\.1\.?\s*(?:T[eê]n\s*doanh\s*nghi[eệ]p(?:\s*\(VN\))?)?[:\s]*', '', line, flags=re.I).strip().strip(":-_ \t.")
            if val:
                data["ten_doanh_nghiep"] = val

        # 2.2 Mã số DN (MST) / Mã QHNS
        if not data["ma_qhns"] and (re.search(r'2\.2\b', line, re.I) or re.search(r'(?:MST|M[aã]\s*QHNS)', line, re.I)):
            m = re.search(r'(?:2\.2\.?|M[aã]\s*s[oố6]\s*DN|M[aã]\s*QHNS|MST)[^\d:]*[:\s]*([0-9]{10}(?:-[0-9]{3})?)', line, re.I)
            if m:
                data["ma_qhns"] = m.group(1).strip()

        # 2.3 Ngày cấp & Cơ quan cấp
        if not data["ngay_cap_co_quan_cap"] and re.search(r'2\.3\b', line, re.I):
            val = re.sub(r'^2\.3\.?\s*(?:Ng[aà]y\s*c[aấ]p[^\w:]*&?[^\w:]*C[oơ]\s*quan\s*c[aấ]p)?[:\s]*', '', line, flags=re.I).strip().strip(":-_ \t.")
            if val:
                data["ngay_cap_co_quan_cap"] = val

        # 2.4 Trụ sở chính
        if not data["tru_so_chinh"] and re.search(r'2\.4\b', line, re.I):
            val = re.sub(r'^2\.4\.?\s*(?:Tr[uụ]\s*s[oở]\s*ch[ií]nh)?[:\s]*', '', line, flags=re.I).strip().strip(":-_ \t.")
            if val:
                data["tru_so_chinh"] = val

        # 2.5 Người đại diện pháp luật
        if not data["nguoi_dai_dien"] and re.search(r'2\.5\b', line, re.I):
            val = re.sub(r'^2\.5\.?\s*(?:Ng[uưo][oờ]?i\s*[đd][aạ]i\s*[đd]i[eệ]n\s*ph[aá]p\s*lu[aậ]t)?[:\s]*', '', line, flags=re.I).strip().strip(":-_ \t.")
            if val:
                m_cv = re.search(r'Ch[uứir]+c\s*v[uụ][^\w:]*[:\s]*(.+)$', val, re.I)
                if m_cv:
                    data["chuc_vu_dai_dien"] = m_cv.group(1).strip()
                    data["nguoi_dai_dien"] = val[:m_cv.start()].strip().strip(":-_ \t.,")
                else:
                    data["nguoi_dai_dien"] = val

        # 2.6 Ngành nghề VSIC
        if not data["ma_vsic"] and re.search(r'2\.6\b', line, re.I):
            val = re.sub(r'^2\.6\.?\s*(?:Ng[aà]nh\s*ngh[eề])?\s*(?:\(?M[aã]\s*VSIC\)?)?[:\s]*', '', line, flags=re.I).strip().strip(":-_ \t.")
            if val:
                data["ma_vsic"] = val

        # 3.1 Họ và tên người quản lý
        if not data["ho_ten_nguoi_quan_ly"] and re.search(r'3\.1\b', line, re.I):
            val = re.sub(r'^3\.1\.?\s*(?:H[oọ]\s*v[aà]\s*t[eê]n)?[:\s]*', '', line, flags=re.I).strip().strip(":-_ \t.")
            if val:
                data["ho_ten_nguoi_quan_ly"] = val

        # 3.2 Chức vụ người quản lý
        if not data["chuc_vu_nguoi_quan_ly"] and re.search(r'3\.2\b', line, re.I):
            val = re.sub(r'^3\.2\.?\s*(?:Ch[uứir]+c\s*v[uụ])?[:\s]*', '', line, flags=re.I).strip().strip(":-_ \t.")
            if val:
                data["chuc_vu_nguoi_quan_ly"] = val

        # 3.3 Đơn vị công tác
        if not data["don_vi_cong_tac"] and re.search(r'3\.3\b', line, re.I):
            val = re.sub(r'^3\.3\.?\s*(?:(?:Don\s*vi|[Đđ][oơ]n\s*v[iị])\s*c[oô]ng\s*t[aá]c|Donvicongtac)?[:\s]*', '', line, flags=re.I).strip().strip(":-_ \t.")
            if val:
                data["don_vi_cong_tac"] = val

        # 3.4 Số CMND / CCCD
        if not data["so_cmnd_cccd"] and re.search(r'3\.4\b', line, re.I):
            m = re.search(r'([0-9]{9,12})', line)
            if m:
                data["so_cmnd_cccd"] = m.group(1).strip()

        # 3.5 Điện thoại di động
        if not data["sdt_di_dong"] and re.search(r'3\.5\b', line, re.I):
            m = re.search(r'([0-9]{9,11})', line)
            if m:
                data["sdt_di_dong"] = m.group(1).strip()

        # 3.6 Thư điện tử
        if not data["thu_dien_tu"] and re.search(r'3\.6\b', line, re.I):
            m = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
            if m:
                data["thu_dien_tu"] = m.group(1).strip()

    # Global fallbacks for missing fields
    if not data["ma_qhns"]:
        m_mst_subj = re.search(r'(?:MST|QHNS)[:\s-]*([0-9]{10})', email_subject, re.I)
        if m_mst_subj:
            data["ma_qhns"] = m_mst_subj.group(1).strip()
        else:
            m_any_mst = re.search(r'MST[:\s]*([0-9]{10})', txt, re.I)
            if m_any_mst:
                data["ma_qhns"] = m_any_mst.group(1).strip()

    if not data["ten_doanh_nghiep"]:
        m_name_dn = re.search(r'(?:C[OÔ]NG\s*TY\s*TNHH|C[OÔ]NG\s*TY\s*C[OỔ]\s*PH[AẦ]N)[^\n:]*[:\s]*([^\n]+)', txt, re.I)
        if m_name_dn:
            data["ten_doanh_nghiep"] = m_name_dn.group(0).strip().strip(":-_ \t.")

    if not data["thu_dien_tu"]:
        m_any_mail = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', txt)
        if m_any_mail and not any(k in m_any_mail.group(1) for k in ["mof.gov.vn", "microsoft.com", "outlook.com"]):
            data["thu_dien_tu"] = m_any_mail.group(1).strip()

    return data
