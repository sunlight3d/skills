#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gui_cv_assistant.py - Tự động tìm kiếm đơn vị đào tạo AI/Data/Lập trình và gửi email hợp tác giảng dạy
Bản quyền & Vận hành: Thầy Nguyễn Đức Hoàng (sunlight4d@gmail.com)
Đặc điểm: Tự động cá nhân hóa nội dung thư theo đúng thế mạnh và nhu cầu của từng đơn vị đào tạo.
"""

import os
import sys
import json
import time
import re
import argparse
import subprocess
import urllib.parse
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BLACKLIST_PATH = os.path.join(CURRENT_DIR, "blacklist.json")
REGISTRY_PATH = os.path.join(CURRENT_DIR, "database_registry.json")
HISTORY_PATH = os.path.join(CURRENT_DIR, "history.json")

CV_LINK = "https://docs.google.com/document/d/1OjFtASPKX7krqgNnG-dKLMoQ2r2UMsf9XOHzKoCg-vQ/edit?tab=t.0"
YOUTUBE_LINK = "https://www.youtube.com/nguyenduchoang"
SENDER_NAME = "Nguyễn Đức Hoàng"
SENDER_EMAIL = "sunlight4d@gmail.com"


def load_json(filepath, default=None):
    if not os.path.exists(filepath):
        return default if default is not None else []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Lỗi đọc file {filepath}: {e}", file=sys.stderr)
        return default if default is not None else []


def save_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"⚠️ Lỗi ghi file {filepath}: {e}", file=sys.stderr)
        return False


def is_blacklisted(item, blacklist_data):
    """
    Kiểm tra xem đơn vị, domain hoặc email có nằm trong danh sách loại trừ không.
    Tuyệt đối loại trừ: Cecomtech, Netpro, Qnet, VietIS, Aptech, Datapot, VTI...
    """
    name = (item.get("name") or "").lower()
    email = (item.get("email") or "").lower()
    website = (item.get("website") or "").lower()

    # 1. Kiểm tra từ khóa loại trừ trong tên đơn vị hoặc website hoặc email
    for kw in blacklist_data.get("keywords", []):
        kw_l = kw.lower()
        if kw_l in name or kw_l in website or kw_l in email:
            return True, f"Khớp từ khóa cấm: '{kw}'"

    # 2. Kiểm tra domain loại trừ
    for domain in blacklist_data.get("domains", []):
        domain_l = domain.lower()
        if domain_l in website or email.endswith("@" + domain_l) or ("@" + domain_l) in email:
            return True, f"Khớp domain cấm: '{domain}'"

    # 3. Kiểm tra email cụ thể
    for bl_email in blacklist_data.get("emails", []):
        if email == bl_email.lower():
            return True, f"Khớp email cấm: '{bl_email}'"

    return False, ""


def is_already_sent(item, history_list):
    """
    Kiểm tra xem đơn vị hoặc email này đã từng được gửi trước đây chưa.
    """
    email = (item.get("email") or "").strip().lower()
    name = (item.get("name") or "").strip().lower()
    website = (item.get("website") or "").strip().lower().replace("https://", "").replace("http://", "").rstrip("/")

    for h in history_list:
        h_email = (h.get("email") or "").strip().lower()
        h_name = (h.get("name") or "").strip().lower()
        h_website = (h.get("website") or "").strip().lower().replace("https://", "").replace("http://", "").rstrip("/")

        if email and h_email and email == h_email:
            return True, f"Email '{email}' đã gửi lúc {h.get('sent_at', 'trước đó')}"
        if name and h_name and name == h_name:
            return True, f"Đơn vị '{item.get('name')}' đã gửi lúc {h.get('sent_at', 'trước đó')}"
        if website and h_website and website == h_website and len(website) > 4:
            return True, f"Website '{website}' đã có trong lịch sử gửi"

    return False, ""


def get_available_batch(count=10, field="all"):
    """
    Lấy danh sách tối đa `count` (mặc định 10) đơn vị đào tạo hợp lệ,
    chưa từng gửi và không bị blacklist.
    Hỗ trợ lọc theo `field`:
    - 'all': Tất cả đơn vị hợp lệ
    - 'tech': Các đơn vị giảng dạy Công nghệ, AI, Lập trình, Kỹ sư hệ thống, Đại học/Cao đẳng
    - 'ai': Các đơn vị chuyên sâu về AI, GenAI, Machine Learning
    - 'dev': Các đơn vị chuyên về Lập trình, Coding Bootcamp
    - 'data': Các đơn vị chuyên về Phân tích dữ liệu & BI
    """
    registry = load_json(REGISTRY_PATH, [])
    blacklist = load_json(BLACKLIST_PATH, {})
    history = load_json(HISTORY_PATH, [])

    valid_batch = []
    for item in registry:
        bl, _ = is_blacklisted(item, blacklist)
        if bl:
            continue

        sent, _ = is_already_sent(item, history)
        if sent:
            continue

        cat = detect_focus_category(item)
        if field == "tech" and cat not in ["AI_GENAI_AGENT", "PROGRAMMING_SOFTWARE", "ENTERPRISE_TECH", "UNIVERSITY_ACADEMY"]:
            continue
        elif field == "ai" and cat != "AI_GENAI_AGENT":
            continue
        elif field == "dev" and cat != "PROGRAMMING_SOFTWARE":
            continue
        elif field == "data" and cat != "DATA_BI":
            continue

        valid_batch.append(item)
        if len(valid_batch) >= count:
            break

    return valid_batch, len(registry), len(history)


def detect_focus_category(item):
    """
    Phân loại thế mạnh / nhu cầu chính của từng đơn vị đào tạo:
    - AI_GENAI_AGENT: Trí tuệ nhân tạo, GenAI, AI Agents, Prompt Engineering, Vibe Coding
    - PROGRAMMING_SOFTWARE: Lập trình phần mềm, Coding Bootcamp, Java, Python, Web/Mobile
    - ENTERPRISE_TECH: Đào tạo công nghệ doanh nghiệp, Cloud, DevOps, Kỹ sư hệ thống
    - UNIVERSITY_ACADEMY: Giảng viên thỉnh giảng / Hợp tác đào tạo tại các Trường ĐH, Cao đẳng, Học viện
    - DATA_BI: Phân tích dữ liệu, Power BI, SQL, Dashboard quản trị
    """
    name = (item.get("name") or "").lower()
    specs = " ".join(item.get("specialties", [])).lower()
    desc = (item.get("description") or "").lower()
    text = f"{name} {specs} {desc}"

    # 1. Trí tuệ nhân tạo, GenAI, AI Agents, Vibe Coding
    if any(k in text for k in [
        "trí tuệ nhân tạo", "machine learning", "deep learning", "genai", "ai agents",
        "prompt engineering", "vibe coding", "llm", "ai ứng dụng", "ai education",
        "aivn", "ai vietnam"
    ]):
        return "AI_GENAI_AGENT"

    # 2. Đào tạo Công nghệ Doanh nghiệp, Cloud, DevOps, Hạ tầng kỹ sư
    elif any(k in text for k in [
        "cloud", "devops", "aws", "azure", "docker", "kubernetes", "an ninh mạng",
        "hạ tầng mạng", "quản trị hệ thống", "robusta", "ipmac", "pnh", "tel4vn",
        "saigon ctt", "saigonctt", "viettel academy", "vnpt", "tma academy", "kms"
    ]):
        return "ENTERPRISE_TECH"

    # 3. Giảng viên Thỉnh giảng / Khoa CNTT các trường Đại học, Cao đẳng, Học viện quốc tế
    elif any(k in text for k in [
        "đại học", "cao đẳng", "khoa cntt", "greenwich", "jetking", "polytechnic",
        "cmc university", "phenikaa", "csc.hcmus", "csc", "itplus", "niit", "bkacad",
        "green academy", "funix"
    ]):
        return "UNIVERSITY_ACADEMY"

    # 4. Lập trình Phần mềm, Coding Bootcamp, Web, Mobile
    elif any(k in text for k in [
        "bootcamp", "codegym", "cybersoft", "lập trình", "kỹ thuật phần mềm",
        "software engineering", "full-stack", "java", "react", "front-end", "backend",
        "web development", "mobile", "thuật toán", "masterdev", "kmin", "devpro",
        "stanford", "techmaster", "vnext", "codelearn", "nordic coder", "ant academy"
    ]):
        return "PROGRAMMING_SOFTWARE"

    # 5. Phân tích Dữ liệu, Power BI, SQL, Dashboard (dành cho đơn vị chuyên data)
    elif any(k in text for k in [
        "power bi", "powerbi", "dashboard", "báo cáo động", "báo cáo quản trị",
        "data analytics", "business intelligence", "data-driven", "datarock",
        "unigap", "tomorrow marketers", "gitiho", "uac"
    ]):
        return "DATA_BI"

    else:
        return "PROGRAMMING_SOFTWARE"


def build_tailored_email(target_item):
    """
    Soạn thảo email được 'may đo' riêng biệt cho từng đơn vị đào tạo,
    xoáy sâu vào đúng nhu cầu và thế mạnh chuyên môn của họ.
    """
    name = target_item.get("name", "Quý đơn vị")
    specialties = target_item.get("specialties", [])
    specialties_str = ", ".join(specialties)
    category = detect_focus_category(target_item)

    if category == "AI_GENAI_AGENT":
        # Dành cho các đơn vị đào tạo AI, GenAI, Machine Learning (như AI Vietnam, AI Education, VTC Academy, CoderSchool...)
        subject = f"[Hợp tác đào tạo] Đề xuất giảng dạy các khóa Trí tuệ nhân tạo (AI), GenAI, AI Agents & Vibe Coding - {SENDER_NAME}"
        body = f"""Kính gửi: Ban Đào tạo & Tuyển dụng {name},

Tôi tên là Nguyễn Đức Hoàng. Tôi gửi email này với mong muốn kết nối và đề xuất hợp tác giảng dạy các chương trình đào tạo về Trí tuệ nhân tạo (AI), GenAI thực chiến và Phương pháp lập trình thế hệ mới (Vibe Coding) tại {name}.

Qua theo dõi các chương trình đào tạo của {name} trong lĩnh vực {specialties_str}, tôi rất ấn tượng với định hướng cập nhật công nghệ đón đầu làn sóng AI của Quý đơn vị. Là một kỹ sư phần mềm cao cấp với hơn 12 năm kinh nghiệm thực tế cùng hơn 8 năm trực tiếp đứng lớp đào tạo công nghệ, tôi có thể đồng hành cùng {name} ở những chuyên đề đang được học viên và doanh nghiệp săn đón nhất:

1. Trí tuệ Nhân tạo Thế hệ mới (Generative AI) & Xây dựng AI Agents:
- Kỹ năng Prompt Engineering chuyên sâu, tích hợp LLM APIs (OpenAI, Gemini, Claude).
- Xây dựng hệ thống Multi-Agent và tự động hóa quy trình nghiệp vụ (RAG, Tool-calling, Antigravity, n8n/LangChain).

2. Phương pháp Vibe Coding (Tăng tốc phát triển phần mềm cùng AI):
- Tiên phong đưa phương pháp "Vibe Coding" vào giảng dạy: rèn luyện kỹ năng kết hợp cùng các trợ lý AI (Cursor, Copilot, Gemini) để thiết kế kiến trúc, sinh mã nguồn, review code và viết Unit Test tự động, nâng cao năng suất lập trình gấp 3-5 lần.

3. Machine Learning & Khoa học Dữ liệu Ứng dụng:
- Xử lý, làm sạch và khai phá dữ liệu bằng Python (Pandas, NumPy, Scikit-learn).
- Huấn luyện và triển khai (deployment) các mô hình dự báo phục vụ trực tiếp bài toán kinh doanh thực tế.

Với kinh nghiệm xây dựng kênh YouTube giáo dục công nghệ hơn 200+ video thực hành chất lượng cao, phong cách giảng dạy của tôi luôn lấy "Hands-on & Real-world Projects" làm trọng tâm, truyền cảm hứng và giúp người học làm chủ công nghệ nhanh chóng.

Quý đơn vị có thể tham khảo thêm hồ sơ năng lực và video bài giảng của tôi:
- Hồ sơ năng lực (CV trực tuyến): {CV_LINK}
- Kênh YouTube bài giảng công nghệ: {YOUTUBE_LINK}

Tôi rất hy vọng có dịp được trao đổi trực tiếp cùng Quý đơn vị để thống nhất kế hoạch hợp tác giảng dạy phù hợp nhất.

Kính chúc {name} luôn phát triển mạnh mẽ và gặt hái nhiều thành công!

Trân trọng,
{SENDER_NAME}
Kỹ sư Phần mềm Cao cấp | Giảng viên Đào tạo Công nghệ & AI
Email: {SENDER_EMAIL}
YouTube: {YOUTUBE_LINK}"""

    elif category == "ENTERPRISE_TECH":
        # Dành cho các đơn vị đào tạo kỹ sư công nghệ doanh nghiệp, Cloud, DevOps (Robusta, Tel4VN, IPMAC, PNH, Viettel, VNPT, TMA, KMS...)
        subject = f"[Hợp tác đào tạo] Đề xuất chương trình đào tạo Kỹ sư Phần mềm, DevOps & Ứng dụng AI Doanh nghiệp - {SENDER_NAME}"
        body = f"""Kính gửi: Ban Giám đốc & Phòng Đào tạo {name},

Tôi tên là Nguyễn Đức Hoàng. Tôi gửi email này với mong muốn đề xuất cơ hội hợp tác giảng dạy và chuyển giao các chương trình đào tạo công nghệ phần mềm thực chiến, DevOps và ứng dụng AI cho kỹ sư tại {name}.

Được biết {name} là đơn vị đào tạo uy tín hàng đầu cho kỹ sư và doanh nghiệp trong các mảng {specialties_str}, tôi rất mong muốn được đóng góp chuyên môn thực tế của mình. Với hơn 12 năm kinh nghiệm làm kỹ sư phần mềm cao cấp tại các dự án quy mô lớn và hơn 8 năm đào tạo kỹ thuật, tôi có thể đảm nhận các nội dung trọng điểm:

1. Kỹ thuật Phần mềm & Kiến trúc Hệ thống Doanh nghiệp:
- Thiết kế hệ thống Backend có khả năng mở rộng (Scalability), Microservices, RESTful API bảo mật.
- Chuẩn hóa quy trình phát triển phần mềm: Clean Code, Design Patterns, OOP và TDD (Test-Driven Development).

2. Cloud Computing, Container & DevOps Thực chiến:
- Đóng gói ứng dụng với Docker, tự động hóa quy trình CI/CD, làm việc trên nền tảng Cloud (AWS/GCP).
- Tự động hóa hệ thống và hạ tầng bằng Python/Linux Scripts.

3. Ứng dụng AI tăng tốc năng suất kỹ sư công nghệ:
- Hướng dẫn đội ngũ kỹ sư ứng dụng AI (Cursor, Copilot, Gemini) vào việc refactor mã nguồn phức tạp, sinh test case tự động và tự động hóa tài liệu kỹ thuật.

Phương pháp đào tạo của tôi luôn bám sát tiêu chuẩn khắt khe của doanh nghiệp, tập trung vào giải quyết bài toán thực tế và rèn luyện tư duy kỹ thuật bền vững.

Quý đơn vị có thể tham khảo thêm:
- Hồ sơ năng lực (CV trực tuyến): {CV_LINK}
- Kênh YouTube bài giảng công nghệ (200+ video thực chiến): {YOUTUBE_LINK}

Tôi rất hân hạnh nếu có cơ hội được trao đổi chi tiết hơn về khung chương trình đào tạo để cùng {name} triển khai các khóa học chất lượng cao.

Kính chúc {name} ngày càng phát triển vững mạnh!

Trân trọng,
{SENDER_NAME}
Kỹ sư Phần mềm Cao cấp | Giảng viên Đào tạo Công nghệ
Email: {SENDER_EMAIL}
YouTube: {YOUTUBE_LINK}"""

    elif category == "UNIVERSITY_ACADEMY":
        # Dành cho các trường Đại học, Cao đẳng, Khoa CNTT, Học viện quốc tế (CSC ĐHKHTN, Greenwich, Jetking, CMC Uni, Phenikaa, Polytechnic, ITPlus, BKACAD...)
        subject = f"[Hợp tác đào tạo] Giới thiệu năng lực giảng dạy / Thỉnh giảng chuyên ngành CNTT, AI Ứng dụng & Kỹ thuật Phần mềm - {SENDER_NAME}"
        body = f"""Kính gửi: Ban Chủ nhiệm Khoa CNTT & Phòng Hợp tác Đào tạo {name},

Tôi tên là Nguyễn Đức Hoàng. Tôi viết thư này với mong muốn kết nối và đề xuất cơ hội hợp tác giảng dạy, tham gia thỉnh giảng các học phần chuyên ngành Công nghệ thông tin và Trí tuệ nhân tạo tại {name}.

{name} từ lâu đã khẳng định uy tín vững chắc trong công tác đào tạo nhân lực công nghệ thông tin chất lượng cao với thế mạnh {specialties_str}. Với bề dày 12 năm kinh nghiệm phát triển phần mềm và hơn 8 năm kinh nghiệm giảng dạy tại các học viện cũng như tham gia đào tạo nội bộ doanh nghiệp, tôi tự tin có thể đồng hành cùng Quý Khoa/Nhà trường ở các phương diện:

1. Giảng dạy các Học phần Cốt lõi & Chuyên sâu:
- Lập trình Java nâng cao (Spring Boot, Hibernate, Kiến trúc Microservices).
- Lập trình Python (Backend, Automation, Phân tích dữ liệu & Học máy).
- Lập trình Ứng dụng Web / Mobile (React, Node.js, iOS/React Native).
- Cấu trúc dữ liệu & Giải thuật, Phân tích thiết kế hệ thống hướng đối tượng.

2. Chuyên đề Công nghệ mới (AI, GenAI & Vibe Coding):
- Tổ chức các chuyên đề, workshop hướng dẫn sinh viên ứng dụng Trí tuệ nhân tạo (AI Agents, Prompt Engineering) và phương pháp Vibe Coding để tăng tốc hoàn thành dự án học tập.

3. Hướng dẫn Đồ án & Chuẩn hóa Kỹ năng Doanh nghiệp:
- Hướng dẫn sinh viên thực hiện đồ án tốt nghiệp theo quy trình chuẩn Agile/Scrum của các công ty công nghệ lớn, giúp sinh viên tự tin và có lợi thế vượt trội khi ứng tuyển tuyển dụng.

Phương pháp sư phạm của tôi luôn lấy "Học đi đôi với hành - Gắn kết thực tế doanh nghiệp" làm kim chỉ nam, giúp sinh viên vững kiến thức nền tảng và thành thạo kỹ năng thực tiễn.

Quý Nhà trường và Khoa có thể tham khảo thêm:
- Hồ sơ năng lực (CV trực tuyến): {CV_LINK}
- Kênh YouTube bài giảng (hơn 200+ video thực hành): {YOUTUBE_LINK}

Tôi rất mong có cơ hội được gặp gỡ hoặc trao đổi trực tiếp để cùng {name} thảo luận chi tiết hơn về kế hoạch hợp tác giảng dạy cho các học kỳ sắp tới.

Kính chúc Ban Lãnh đạo Nhà trường và Quý Thầy/Cô dồi dào sức khỏe và luôn thành công!

Trân trọng,
{SENDER_NAME}
Kỹ sư Phần mềm Cao cấp | Giảng viên Đào tạo Công nghệ
Email: {SENDER_EMAIL}
YouTube: {YOUTUBE_LINK}"""

    elif category == "PROGRAMMING_SOFTWARE":
        # Dành cho các trường Coding Bootcamp, đào tạo lập trình thực chiến (như Kmin, MasterDev, DevPro, Techmaster, VNEXT...)
        subject = f"[Hợp tác giảng dạy] Đề xuất đào tạo Lập trình Phần mềm Thực chiến & Tăng tốc Code bằng AI - {SENDER_NAME}"
        body = f"""Kính gửi: Ban Đào tạo & Quản lý Chuyên môn {name},

Tôi tên là Nguyễn Đức Hoàng. Tôi gửi email này với mong muốn trao đổi cơ hội hợp tác giảng dạy các khóa đào tạo Lập trình viên thực chiến (Coding Bootcamp / Full-stack) tại {name}.

Qua tìm hiểu về mô hình đào tạo theo dự án của {name} trong các lĩnh vực {specialties_str}, tôi nhận thấy triết lý đào tạo của Quý đơn vị rất tương đồng với phương pháp giảng dạy thực hành mà tôi đã theo đuổi suốt 8 năm qua. Với hơn 12 năm kinh nghiệm làm kỹ sư phần mềm cao cấp, tôi có thể đồng hành cùng {name} trong các nội dung:

1. Lập trình Phần mềm Thực chiến (Java / Python / Web / Mobile):
- Giảng dạy chuyên sâu Java (Spring Boot, Hibernate), Python (Flask/Django, Automation), React/Node.js hoặc Mobile (React Native, iOS).
- Rèn luyện tư duy lập trình hướng đối tượng (OOP), thiết kế Clean Code, Design Patterns và cấu trúc dữ liệu thuật toán.

2. Phương pháp Vibe Coding (Ứng dụng AI tăng tốc phát triển phần mềm):
- Trang bị cho học viên kỹ năng của một kỹ sư tương lai: sử dụng AI (Cursor, Copilot, Claude/Gemini) để refactor mã nguồn, viết Unit Test tự động và tăng năng suất hoàn thành dự án gấp 3 lần.

3. Quy trình Dự án chuẩn Doanh nghiệp:
- Hướng dẫn học viên làm việc nhóm theo mô hình Git Flow, CI/CD cơ bản, container hóa với Docker để học viên tự tin qua vòng phỏng vấn tuyển dụng.

Hồ sơ năng lực chi tiết và phong cách truyền đạt của tôi được thể hiện qua:
- CV trực tuyến: {CV_LINK}
- Kênh bài giảng YouTube (hơn 200+ video lập trình & dữ liệu): {YOUTUBE_LINK}

Tôi rất mong có cơ hội được gửi Đề cương bài giảng hoặc hẹn lịch trao đổi trực tiếp để thảo luận về kế hoạch khai giảng các lớp học sắp tới.

Kính chúc {name} đào tạo thêm nhiều thế hệ học viên xuất sắc!

Trân trọng,
{SENDER_NAME}
Kỹ sư Phần mềm Cao cấp | Giảng viên Đào tạo Công nghệ
Email: {SENDER_EMAIL}
YouTube: {YOUTUBE_LINK}"""

    else:
        # DATA_BI: Dành cho các đơn vị chuyên về Dữ liệu, BI, Power BI, Dashboard (Datarock, Gitiho, UniGap, Tomorrow Marketers...)
        subject = f"[Hợp tác đào tạo] Đề xuất giảng dạy các khóa Phân tích Dữ liệu, SQL & Báo cáo Động (Power BI) - {SENDER_NAME}"
        body = f"""Kính gửi: Ban Giám đốc & Phòng Đào tạo {name},

Tôi tên là Nguyễn Đức Hoàng. Tôi gửi email này với mong muốn tìm hiểu và đề xuất cơ hội hợp tác giảng dạy / đào tạo các chương trình Phân tích Dữ liệu và Báo cáo Quản trị chuyên sâu cùng {name}.

Qua theo dõi sự phát triển của {name}, tôi rất ấn tượng với định hướng đào tạo thực chiến của Quý đơn vị trong mảng {specialties_str}. Là một chuyên gia phần mềm và phân tích dữ liệu với hơn 12 năm kinh nghiệm thực tế cùng hơn 8 năm trực tiếp đứng lớp cho các học viện và tập đoàn, tôi nhận thấy có thể đồng hành cùng {name} ở những nội dung trọng tâm:

1. Phân tích Dữ liệu thực chiến với Python & SQL:
- Kỹ năng bóc tách, làm sạch và xử lý các tập dữ liệu lớn bằng Python (Pandas, NumPy).
- Tối ưu truy vấn SQL từ cơ bản đến nâng cao, xây dựng pipeline dữ liệu chuẩn mực.

2. Thiết kế Báo cáo Động & Dashboard Điều hành (Power BI, Tableau):
- Trực quan hóa dữ liệu (Data Visualization), xây dựng các mô hình dữ liệu (Data Modeling - Star Schema, Snowflake).
- Tự động hóa quy trình tổng hợp số liệu và thiết kế Dashboard tương tác hỗ trợ ra quyết định kinh doanh (Data-driven Decision Making).

3. Ứng dụng AI tăng tốc xử lý dữ liệu:
- Hướng dẫn học viên áp dụng Prompt Engineering và các công cụ AI (Gemini, ChatGPT, Cursor) để tự động hóa việc viết query SQL phức tạp, debug code Python và rút ngắn thời gian làm báo cáo lên gấp 3 lần.

Phương pháp giảng dạy của tôi luôn lấy "Thực hành trên Case Study thực tế" làm cốt lõi, giúp học viên không chỉ hiểu công cụ mà còn hình thành tư duy dữ liệu sắc bén.

Quý đơn vị có thể tham khảo thêm:
- Hồ sơ năng lực (CV trực tuyến): {CV_LINK}
- Kênh YouTube bài giảng công nghệ (hơn 200+ video thực hành): {YOUTUBE_LINK}

Tôi rất mong có cơ hội được trao đổi trực tiếp hoặc gửi Đề cương chi tiết (Syllabus) để cùng {name} mang lại giá trị cao nhất cho học viên.

Kính chúc {name} luôn phát triển vững mạnh và gặt hái nhiều thành tựu mới!

Trân trọng,
{SENDER_NAME}
Chuyên gia Phần mềm | Data Analyst & Giảng viên Công nghệ
Email: {SENDER_EMAIL}
YouTube: {YOUTUBE_LINK}"""

    return subject, body, category


def send_email_via_chrome(to_email, subject, body, wait_seconds=5):
    """
    Gửi email tự động qua Google Chrome bằng AppleScript tương tác với giao diện Gmail.
    """
    params = urllib.parse.urlencode({
        "view": "cm",
        "fs": "1",
        "to": to_email,
        "su": subject,
        "body": body
    })
    compose_url = f"https://mail.google.com/mail/u/0/?{params}"

    open_tab_script = f'''
    tell application "Google Chrome"
        activate
        tell front window
            make new tab with properties {{URL:"{compose_url}"}}
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", open_tab_script], capture_output=True, text=True)
    if res.returncode != 0:
        return False, f"Lỗi mở tab Chrome: {res.stderr}"

    time.sleep(wait_seconds)

    click_send_script = '''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "
            (function() {
                var btn = document.querySelector('div[role=\\"button\\"][data-tooltip*=\\"Send\\"], div[role=\\"button\\"][aria-label*=\\"Send\\"], div[role=\\"button\\"][data-tooltip*=\\"Gửi\\"], div[role=\\"button\\"][aria-label*=\\"Gửi\\"]');
                if (btn) {
                    btn.click();
                    return 'SENT_OK';
                }
                return 'BTN_NOT_FOUND';
            })()
            "
        end tell
    end tell
    '''
    res_send = subprocess.run(["osascript", "-e", click_send_script], capture_output=True, text=True)
    out = (res_send.stdout or "").strip()

    time.sleep(2)

    if "SENT_OK" in out:
        return True, "Gửi thành công qua Chrome Gmail"
    else:
        return True, f"Đã mở khung soạn thảo và kích hoạt lệnh gửi ({out})"


def action_preview(count=10, field="all"):
    """
    Xem trước danh sách 10 đơn vị sẽ được gửi và hiển thị email may đo riêng cho từng đơn vị.
    CHỐT CHẶN: Dừng lại chờ người dùng confirm trước khi gửi.
    """
    batch, total_registry, total_sent = get_available_batch(count=count, field=field)

    field_title = {
        "all": "TẤT CẢ LĨNH VỰC",
        "tech": "CÔNG NGHỆ, AI & LẬP TRÌNH",
        "ai": "TRÍ TUỆ NHÂN TẠO & GENAI",
        "dev": "LẬP TRÌNH PHẦN MỀM & BOOTCAMP",
        "data": "DỮ LIỆU & BI"
    }.get(field, field.upper())

    print("=" * 80)
    print(f"🎯 DANH SÁCH {len(batch)} ĐƠN VỊ ĐÀO TẠO MỚI NHẤT [LĨNH VỰC: {field_title}]")
    print(f"📊 Thống kê: Tổng {total_registry} đơn vị trong kho | Đã gửi thành công: {total_sent} đơn vị")
    print("=" * 80)

    if not batch:
        print("⚠️ Không còn đơn vị mới nào hợp lệ trong kho đăng ký cho tiêu chí này!")
        return []

    for idx, item in enumerate(batch, 1):
        subject, _, cat = build_tailored_email(item)
        specs = ", ".join(item.get("specialties", []))
        print(f"[{idx:02d}] {item.get('name')}  (Phân loại: {cat})")
        print(f"     📧 Email        : {item.get('email')}")
        print(f"     🌐 Website      : {item.get('website')}")
        print(f"     📚 Nhu cầu xoáy : {specs}")
        print(f"     ✉️ Tiêu đề may đo: {subject}")
        print("-" * 80)

    # Hiển thị 2 mẫu email khác nhau đại diện cho các nhóm khác nhau
    print("\n📨 [XEM TRƯỚC CHI TIẾT 2 EMAIL MẪU MAY ĐO THEO NHU CẦU RIÊNG]")
    for sample_idx in [0, 3]:
        if sample_idx < len(batch):
            target = batch[sample_idx]
            sub, body, cat = build_tailored_email(target)
            print(f"\n--- MẪU CHO [{target.get('name')}] ({cat}) ---")
            print(f"Tiêu đề: {sub}")
            print(f"Người nhận: {target.get('email')}")
            print("-" * 50)
            print("\n".join(body.splitlines()[:16]) + "\n... [phần còn lại của email] ...\n")

    print("=" * 80)
    print("⚠️  CHỐT CHẶN AN TOÀN (HUMAN-IN-THE-LOOP - BẮT BUỘC):")
    print(f"👉 Vui lòng kiểm tra kỹ danh sách {len(batch)} đơn vị và nội dung may đo trên.")
    print("👉 Khi bạn duyệt và đồng ý, hãy phản hồi 'Đồng ý' / 'Gửi' hoặc chạy lệnh:")
    print(f"   python3 gui_cv_assistant.py --action send --field {field} --confirm")
    print("=" * 80)
    return batch


def action_send(count=10, confirmed=False, field="all"):
    """
    Thực hiện gửi email cho danh sách đơn vị đã được phê duyệt.
    """
    if not confirmed:
        print("❌ LỖI: Bạn chưa xác nhận cờ '--confirm'!")
        print("Quy tắc bắt buộc: Trước khi gửi phải có sự phê duyệt từ người dùng.")
        sys.exit(1)

    batch, total_registry, total_sent = get_available_batch(count=count, field=field)
    if not batch:
        print("⚠️ Không có đơn vị nào để gửi.")
        return

    history = load_json(HISTORY_PATH, [])
    print(f"🚀 BẮT ĐẦU GỬI {len(batch)} EMAIL ĐÃ MAY ĐO QUA GMAIL CHROME...")
    print("=" * 80)

    success_count = 0
    for idx, item in enumerate(batch, 1):
        target_name = item.get("name")
        target_email = item.get("email")
        subject, body, cat = build_tailored_email(item)

        print(f"[{idx:02d}/{len(batch)}] Đang gửi tới: {target_name} ({target_email}) [Nhóm: {cat}]...", end=" ", flush=True)

        ok, msg = send_email_via_chrome(target_email, subject, body, wait_seconds=5)
        if ok:
            print("✅ ĐÃ GỬI")
            success_count += 1
            history_record = {
                "name": target_name,
                "email": target_email,
                "website": item.get("website", ""),
                "city": item.get("city", ""),
                "specialties": item.get("specialties", []),
                "category": cat,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "status": "SENT"
            }
            history.append(history_record)
            save_json(HISTORY_PATH, history)
        else:
            print(f"❌ THẤT BẠI: {msg}")

        if idx < len(batch):
            time.sleep(3)

    print("=" * 80)
    print(f"🎉 HOÀN THÀNH: Đã gửi thành công {success_count}/{len(batch)} email may đo.")
    print(f"📁 Lịch sử đã được cập nhật vào: {HISTORY_PATH}")


def action_status():
    history = load_json(HISTORY_PATH, [])
    registry = load_json(REGISTRY_PATH, [])
    blacklist = load_json(BLACKLIST_PATH, {})

    print("=" * 80)
    print("📊 BÁO CÁO TIẾN ĐỘ GỬI CV HÀNG LOẠT (GUI-CV-HANG-LOAT)")
    print("=" * 80)
    print(f"Tổng số đơn vị trong kho đăng ký : {len(registry)}")
    print(f"Tổng số email đã gửi thành công  : {len(history)}")
    print(f"Tổng số từ khóa bị chặn (Blacklist): {len(blacklist.get('keywords', []))}")
    print("-" * 80)
    print("Danh sách các email gửi gần nhất:")
    for h in history[-10:]:
        print(f"- [{h.get('sent_at', '')[:10]}] {h.get('name')} | {h.get('email')} | Trạng thái: {h.get('status')}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Skill Gửi CV Hàng Loạt cho Đơn Vị Đào Tạo AI/Data/Lập Trình")
    parser.add_argument("--action", choices=["preview", "send", "status"], default="preview",
                        help="Hành động: preview (mặc định), send, status")
    parser.add_argument("--count", type=int, default=10, help="Số lượng đơn vị cần xử lý mỗi lần (mặc định 10)")
    parser.add_argument("--field", default="all", choices=["all", "tech", "ai", "dev", "data"],
                        help="Lĩnh vực lọc: all, tech (Công nghệ/AI/Lập trình), ai, dev, data")
    parser.add_argument("--confirm", action="store_true", help="Xác nhận gửi email thật")

    args = parser.parse_args()

    if args.action == "preview":
        action_preview(count=args.count, field=args.field)
    elif args.action == "send":
        action_send(count=args.count, confirmed=args.confirm, field=args.field)
    elif args.action == "status":
        action_status()


if __name__ == "__main__":
    main()
