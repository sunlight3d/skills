import os
import re
import cv2
import numpy as np
import pymupdf
from typing import Dict, Any, List

def detect_stamp_in_image(img_bgr: np.ndarray) -> dict:
    """
    Detect presence of red / crimson ink seal/stamp using HSV thresholding.
    Returns:
      {
        "has_seal": bool,
        "red_pixels": int,
        "red_ratio": float,
        "max_contour_area": int
      }
    """
    if img_bgr is None or img_bgr.size == 0:
        return {"has_seal": False, "red_pixels": 0, "red_ratio": 0.0, "max_contour_area": 0}

    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    # Red hues in HSV (0-12 and 155-180)
    lower_red1 = np.array([0, 50, 45])
    upper_red1 = np.array([12, 255, 255])
    lower_red2 = np.array([155, 50, 45])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    red_pixels = int(cv2.countNonZero(mask))
    total_pixels = img_bgr.shape[0] * img_bgr.shape[1]
    red_ratio = red_pixels / total_pixels if total_pixels > 0 else 0

    # Filter connected contours to find stamp shape
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    has_seal_contour = False
    largest_contour_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > largest_contour_area:
            largest_contour_area = area
        if area > 500:
            has_seal_contour = True

    has_seal = has_seal_contour or (red_pixels > 1200)
    return {
        "has_seal": bool(has_seal),
        "red_pixels": red_pixels,
        "red_ratio": round(red_ratio, 5),
        "max_contour_area": int(largest_contour_area)
    }

def detect_qr_in_image(img_bgr: np.ndarray) -> dict:
    """
    Detect QR code in document image using OpenCV QRCodeDetector.
    Checks full page first, then top-right quadrant (standard location for government forms).
    """
    if img_bgr is None or img_bgr.size == 0:
        return {"has_qr": False, "qr_value": "", "bbox": None}

    detector = cv2.QRCodeDetector()
    val, pts, _ = detector.detectAndDecode(img_bgr)
    
    val_str = str(val).strip() if val else ""
    has_qr = bool(val_str)
    bbox = pts.reshape(-1, 2).tolist() if (has_qr and pts is not None and len(pts) > 0) else None
    
    # If not found on full page, search top-right quadrant
    if not has_qr:
        h, w = img_bgr.shape[:2]
        top_right = img_bgr[0:int(0.40 * h), int(0.55 * w):w]
        val_tr, pts_tr, _ = detector.detectAndDecode(top_right)
        val_tr_str = str(val_tr).strip() if val_tr else ""
        if bool(val_tr_str):
            has_qr = True
            val_str = val_tr_str
            if pts_tr is not None and len(pts_tr) > 0:
                pts_tr_adj = pts_tr.reshape(-1, 2)
                pts_tr_adj[:, 0] += int(0.55 * w)
                bbox = pts_tr_adj.tolist()

    return {
        "has_qr": bool(has_qr),
        "qr_value": val_str,
        "bbox": bbox
    }

def check_format_matches_template(pdf_text: str) -> dict:
    """
    Check if the textual structure matches template 'template01.docx'.
    Template requires:
    - Title: PHIẾU ĐĂNG KÝ TÀI KHOẢN / Hệ thống giám sát, đánh giá đầu tư
    - Section 1: Thông tin dự án (Luật ĐTC / PPP / Đầu tư)
    - Section 2: Thông tin doanh nghiệp đăng ký tài khoản (Tên DN, Mã số DN / MST / Mã QHNS, Trụ sở...)
    - Section 3: Thông tin người được giao quản lý, sử dụng tài khoản
    """
    txt_lower = (pdf_text or "").lower()
    
    # Check Section 1
    has_sec1 = bool(re.search(r'1\.\s*th[oô]ng\s*tin\s*d[uự]\s*[aá]n|lu[aậ]t\s*(?:dtc|[đd]tc|ppp|[đd][aầ]u\s*t[uư])|d[oọ]i\s*t[uư][oợ]ng\s*[đd][aă]ng\s*k[yý]', txt_lower))
    # Check Section 2
    has_sec2 = bool(re.search(r'2\.\s*th[oô]ng\s*tin\s*doanh\s*nghi[eệ]p|2\.1\.\s*t[eê]n\s*doanh\s*nghi[eệ]p|m[aã]\s*s[oố]\s*dn|m[aã]\s*qhns', txt_lower))
    # Check Section 3
    has_sec3 = bool(re.search(r'3\.\s*th[oô]ng\s*tin\s*ng[uư][oờ]i|3\.1\.\s*h[oọ]\s*v[aà]\s*t[eê]n', txt_lower))
    # Check Title
    has_title = bool(re.search(r'phi[eế]u\s*[đd][aă]ng\s*k[yý]\s*t[aà]i\s*kho[aả]n|gi[aá]m\s*s[aá]t[,\s]+[đd][aá]nh\s*gi[aá]\s*[đd][aầ]u\s*t[uư]|b[oộ]\s*t[aà]i\s*ch[ií]nh', txt_lower))

    # All key structural sections match template
    matches = (has_sec1 and has_sec2 and has_sec3) or (has_title and (has_sec2 or has_sec3))
    
    missing = []
    if not has_title:
        missing.append("Tiêu đề biểu mẫu (Phiếu đăng ký tài khoản)")
    if not has_sec1:
        missing.append("Mục 1: Thông tin dự án")
    if not has_sec2:
        missing.append("Mục 2: Thông tin doanh nghiệp đăng ký")
    if not has_sec3:
        missing.append("Mục 3: Thông tin người được giao quản lý tài khoản")

    return {
        "matches": matches,
        "has_title": has_title,
        "has_sec1": has_sec1,
        "has_sec2": has_sec2,
        "has_sec3": has_sec3,
        "missing_sections": missing
    }

def verify_document_template(pdf_path: str, pdf_text: str = "") -> dict:
    """
    Main verification function:
    Compares PDF with template01.docx.
    Rules:
    - Đúng format + Dấu đỏ + QR => 'Hợp lệ (Đúng mẫu + Dấu đỏ + QR)'
    - Đúng format nhưng thiếu dấu đỏ => 'Đúng format nhưng thiếu dấu đỏ'
    - Đúng format nhưng thiếu QR => 'Đúng format nhưng thiếu QR'
    - Đúng format nhưng thiếu cả dấu đỏ và QR => 'Đúng format nhưng thiếu cả dấu đỏ và QR'
    - Sai format => 'Sai format' (kèm chi tiết phần thiếu)
    """
    if not pdf_path or not os.path.exists(pdf_path):
        return {
            "status": "Không có file PDF",
            "is_valid": False,
            "detail": "Không tìm thấy tệp PDF đính kèm.",
            "is_match_format": False,
            "has_qr": False,
            "qr_value": "",
            "has_seal": False,
            "format_details": {}
        }

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        return {
            "status": "Lỗi đọc PDF",
            "is_valid": False,
            "detail": f"Không thể mở file PDF: {e}",
            "is_match_format": False,
            "has_qr": False,
            "qr_value": "",
            "has_seal": False,
            "format_details": {}
        }

    # Extract text if not provided
    if not pdf_text:
        pages_txt = []
        for p in doc:
            pages_txt.append(p.get_text())
        pdf_text = "\n".join(pages_txt)

    # 1. Check Format Match
    fmt_check = check_format_matches_template(pdf_text)
    is_match_format = fmt_check["matches"]

    # 2. Render Page(s) to image (at 200 DPI) for visual inspection (QR & Stamp)
    has_qr = False
    qr_value = ""
    has_seal = False
    stamp_info = {}

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        pix = page.get_pixmap(dpi=200)
        img_bgr = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
        if pix.n == 4:
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2BGR)
        elif pix.n == 3:
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGB2BGR)
        elif pix.n == 1:
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2BGR)

        # Check QR code
        if not has_qr:
            qr_res = detect_qr_in_image(img_bgr)
            if qr_res["has_qr"]:
                has_qr = True
                qr_value = qr_res["qr_value"]

        # Check Red Stamp / Seal
        if not has_seal:
            seal_res = detect_stamp_in_image(img_bgr)
            if seal_res["has_seal"]:
                has_seal = True
                stamp_info = seal_res

    doc.close()

    # Apply Business Rules:
    # 1. Không đúng format
    if not is_match_format:
        missing_desc = ", ".join(fmt_check["missing_sections"]) if fmt_check["missing_sections"] else "Không khớp biểu mẫu Mẫu 1"
        return {
            "status": "Sai format",
            "is_valid": False,
            "detail": f"Văn bản không đúng format biểu mẫu chuẩn template01.docx (Thiếu: {missing_desc}).",
            "is_match_format": False,
            "has_qr": has_qr,
            "qr_value": qr_value,
            "has_seal": has_seal,
            "format_details": fmt_check
        }

    # 2. Đúng format nhưng thiếu cả dấu đỏ và QR
    if not has_seal and not has_qr:
        return {
            "status": "Đúng format nhưng thiếu cả dấu đỏ và QR",
            "is_valid": False,
            "detail": "Đúng format biểu mẫu chuẩn nhưng thiếu cả con dấu đỏ xác nhận và mã QR hệ thống.",
            "is_match_format": True,
            "has_qr": False,
            "qr_value": "",
            "has_seal": False,
            "format_details": fmt_check
        }

    # 3. Đúng format nhưng thiếu dấu đỏ
    if not has_seal:
        qr_info = f" (Mã QR: {qr_value})" if qr_value else ""
        return {
            "status": "Đúng format nhưng thiếu dấu đỏ",
            "is_valid": False,
            "detail": f"Đúng format biểu mẫu chuẩn{qr_info} nhưng thiếu con dấu mộc đỏ của đơn vị/doanh nghiệp.",
            "is_match_format": True,
            "has_qr": has_qr,
            "qr_value": qr_value,
            "has_seal": False,
            "format_details": fmt_check
        }

    # 4. Đúng format nhưng thiếu QR
    if not has_qr:
        return {
            "status": "Đúng format nhưng thiếu QR",
            "is_valid": False,
            "detail": "Đúng format biểu mẫu chuẩn và có dấu mộc đỏ, nhưng thiếu mã QR xác thực của hệ thống.",
            "is_match_format": True,
            "has_qr": False,
            "qr_value": "",
            "has_seal": True,
            "format_details": fmt_check
        }

    # 5. Đầy đủ cả 3: Format + Dấu đỏ + QR
    return {
        "status": "Hợp lệ (Đúng mẫu + Dấu đỏ + QR)",
        "is_valid": True,
        "detail": f"Văn bản hoàn toàn hợp lệ: đúng format chuẩn template01.docx, có con dấu mộc đỏ và mã QR ({qr_value}).",
        "is_match_format": True,
        "has_qr": True,
        "qr_value": qr_value,
        "has_seal": True,
        "format_details": fmt_check
    }
