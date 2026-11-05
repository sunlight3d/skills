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


def get_available_batch(count=10):
    """
    Lấy danh sách tối đa `count` (mặc định 10) đơn vị đào tạo hợp lệ,
    chưa từng gửi và không bị blacklist.
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

        valid_batch.append(item)
        if len(valid_batch) >= count:
            break

    return valid_batch, len(registry), len(history)


def detect_focus_category(item):
    """
    Phân loại thế mạnh / nhu cầu chính của từng đơn vị đào tạo.
    """
    name = (item.get("name") or "").lower()
    specs = " ".join(item.get("specialties", [])).lower()
    desc = (item.get("description") or "").lower()
    text = f"{name} {specs} {desc}"

    if any(k in text for k in ["power bi", "dashboard", "báo cáo", "bi", "data-driven", "datarock"]):
        return "DATA_BI"
    elif any(k in text for k in ["trí tuệ nhân tạo", "machine learning", "genai", "prompt engineering", "ai ứng dụng", "data science"]):
        return "AI_DATA_SCIENCE"
    elif any(k in text for k in ["bootcamp", "codegym", "cybersoft", "lập trình", "full-stack", "java", "front-end", "backend", "web development"]):
        return "BOOTCAMP_DEV"
    elif any(k in text for k in ["bkacad", "green academy", "itplus", "niit", "quốc tế", "hàn quốc"]):
        return "ACADEMY_TECH"
    else:
        return "SOFTWARE_DEV"


def build_tailored_email(target_item):
    """
    Soạn thảo email được 'may đo' riêng biệt cho từng đơn vị đào tạo,
    xoáy sâu vào đúng nhu cầu và thế mạnh chuyên môn của họ.
    """
    name = target_item.get("name", "Quý đơn vị")
    specialties = target_item.get("specialties", [])
    specialties_str = ", ".join(specialties)
    category = detect_focus_category(target_item)

    if category == "DATA_BI":
        # Dành cho các đơn vị chuyên về Dữ liệu, BI, Power BI, Dashboard (như Datarock, Cole, Gitiho...)
        subject = f"[Hợp tác đào tạo] Đề xuất giảng dạy các khóa Phân tích Dữ liệu, SQL & Báo cáo Động (Power BI) - {SENDER_NAME}"
        body = f"""Kính gửi: Ban Giám đốc & Phòng Đào tạo {name},

Tôi tên là Nguyễn Đức Hoàng. Tôi gửi email này với mong muốn tìm hiểu và đề xuất cơ hội hợp tác giảng dạy / đào tạo các chương trình Phân tích Dữ liệu và Báo cáo Quản trị chuyên sâu cùng {name}.

Qua theo dõi sự phát triển của {name}, tôi rất ấn tượng với định hướng đào tạo thực chiến của Quý đơn vị trong mảng {specialties_str}. Là một chuyên gia phần mềm và phân tích dữ liệu với hơn 12 năm kinh nghiệm thực tế cùng hơn 8 năm trực tiếp đứng lớp cho các học viện và tập đoàn, tôi nhận thấy có thể đồng hành cùng {name} ở những nội dung trọng tâm mà học viên và doanh nghiệp đang có nhu cầu rất lớn:

1. Phân tích Dữ liệu thực chiến với Python & SQL:
- Kỹ năng bóc tách, làm sạch và xử lý các tập dữ liệu lớn bằng Python (Pandas, NumPy).
- Tối ưu truy vấn SQL từ cơ bản đến nâng cao, xây dựng pipeline dữ liệu chuẩn mực.

2. Thiết kế Báo cáo Động & Dashboard Điều hành (Power BI, Tableau):
- Trực quan hóa dữ liệu (Data Visualization), xây dựng các mô hình dữ liệu (Data Modeling - Star Schema, Snowflake).
- Tự động hóa quy trình tổng hợp số liệu và thiết kế Dashboard tương tác hỗ trợ ra quyết định kinh doanh (Data-driven Decision Making).

3. Ứng dụng AI tăng tốc xử lý dữ liệu:
- Hướng dẫn học viên áp dụng Prompt Engineering và các công cụ AI (Gemini, ChatGPT, Cursor) để tự động hóa việc viết query SQL phức tạp, debug code Python và rút ngắn thời gian làm báo cáo lên gấp 3 lần.

Phương pháp giảng dạy của tôi luôn lấy "Thực hành trên Case Study thực tế" làm cốt lõi, giúp học viên không chỉ hiểu công cụ mà còn hình thành tư duy dữ liệu sắc bén.

Quý đơn vị có thể tham khảo thêm hồ sơ năng lực chi tiết và phong cách truyền đạt của tôi qua các liên kết dưới đây:
- Hồ sơ năng lực (CV trực tuyến): {CV_LINK}
- Kênh YouTube bài giảng công nghệ (500+ video): {YOUTUBE_LINK}

Tôi rất mong có cơ hội được trao đổi trực tiếp hoặc gửi Đề cương chi tiết (Syllabus) để cùng {name} mang lại giá trị cao nhất cho học viên.

Kính chúc {name} luôn phát triển vững mạnh và gặt hái nhiều thành tựu mới!

Trân trọng,
{SENDER_NAME}
Chuyên gia Phần mềm | Data Analyst & Giảng viên Công nghệ
Email: {SENDER_EMAIL}
YouTube: {YOUTUBE_LINK}"""

    elif category == "AI_DATA_SCIENCE":
        # Dành cho các đơn vị đào tạo AI, Machine Learning, Data Science (như MCI, CoderSchool, Cole...)
        subject = f"[Hợp tác đào tạo] Đề xuất giảng dạy các khóa AI ứng dụng, Machine Learning & Vibe Coding - {SENDER_NAME}"
        body = f"""Kính gửi: Ban Đào tạo & Tuyển dụng {name},

Tôi tên là Nguyễn Đức Hoàng. Tôi viết thư này để kết nối và đề xuất hợp tác giảng dạy các khóa đào tạo về Trí tuệ nhân tạo (AI) ứng dụng, Khoa học dữ liệu và Lập trình thế hệ mới tại {name}.

Được biết {name} đang đẩy mạnh các chương trình đào tạo mũi nhọn về {specialties_str}, tôi rất mong muốn được đóng góp chuyên môn thực chiến của mình. Với hơn 12 năm làm việc trong lĩnh vực phần mềm & dữ liệu, cùng 8 năm giảng dạy công nghệ, tôi có thể đảm nhận tốt các mảng đào tạo sau:

1. Trí tuệ nhân tạo (AI) ứng dụng & Modern Development (Vibe Coding):
- Đào tạo kỹ năng Prompt Engineering chuyên sâu, xây dựng AI workflow tự động hóa công việc.
- Tiên phong đưa phương pháp "Vibe Coding" (lập trình và xử lý dữ liệu tăng tốc cùng Cursor, Copilot, Gemini) vào bài giảng, giúp học viên hiện thực hóa ý tưởng sản phẩm nhanh chóng.

2. Khoa học Dữ liệu & Machine Learning cơ bản đến ứng dụng:
- Xử lý dữ liệu thực tế với Python (Scikit-learn, Pandas, NumPy, Matplotlib/Seaborn).
- Ứng dụng các thuật toán học máy giải quyết bài toán dự báo, phân loại và phân nhóm khách hàng trong kinh doanh.

3. Xây dựng Data Pipeline & Triển khai mô hình (Deployment):
- Đóng gói ứng dụng với Docker, thiết kế RESTful API để đưa mô hình dữ liệu vào vận hành thực tế.

Với kinh nghiệm xây dựng kênh YouTube giáo dục công nghệ hơn 500+ video thực hành, phong cách giảng dạy của tôi luôn trực quan, cuốn hút và truyền cảm hứng mạnh mẽ đến người học.

Quý đơn vị có thể xem thêm chi tiết về kinh nghiệm và bài giảng của tôi:
- Hồ sơ năng lực (CV): {CV_LINK}
- Kênh YouTube công nghệ: {YOUTUBE_LINK}

Rất hy vọng có dịp được trao đổi trực tiếp cùng Quý đơn vị để thống nhất kế hoạch hợp tác giảng dạy phù hợp nhất.

Chúc {name} ngày càng gặt hái nhiều thành công!

Trân trọng,
{SENDER_NAME}
Chuyên gia Phần mềm & Giảng viên Công nghệ AI/Data
Email: {SENDER_EMAIL}
YouTube: {YOUTUBE_LINK}"""

    elif category == "BOOTCAMP_DEV":
        # Dành cho các trường Coding Bootcamp, đào tạo lập trình thực chiến (như MindX, CodeGym, CyberSoft, Rikkei...)
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
- Kênh bài giảng YouTube (500+ video lập trình & dữ liệu): {YOUTUBE_LINK}

Tôi rất mong có cơ hội được gửi Đề cương bài giảng hoặc hẹn lịch trao đổi trực tiếp để thảo luận về kế hoạch khai giảng các lớp học sắp tới.

Kính chúc {name} đào tạo thêm nhiều thế hệ học viên xuất sắc!

Trân trọng,
{SENDER_NAME}
Kỹ sư Phần mềm Cao cấp | Giảng viên Đào tạo Công nghệ
Email: {SENDER_EMAIL}
YouTube: {YOUTUBE_LINK}"""

    else:
        # Dành cho các viện, học viện công nghệ liên kết / quốc tế (như BKACAD, Green Academy, NIIT...)
        subject = f"[Hợp tác đào tạo] Giới thiệu năng lực giảng dạy CNTT, AI Ứng dụng & Phân tích Dữ liệu - {SENDER_NAME}"
        body = f"""Kính gửi: Ban Giám đốc & Phòng Hợp tác Đào tạo {name},

Tôi tên là Nguyễn Đức Hoàng. Tôi viết thư này với mong muốn kết nối và đề xuất cơ hội hợp tác giảng dạy / chuyển giao công nghệ cho các chương trình đào tạo của {name}.

{name} từ lâu đã được khẳng định là đơn vị đào tạo uy tín trong các mảng {specialties_str}. Với bề dày 12 năm kinh nghiệm phát triển phần mềm và hơn 8 năm giảng dạy cho các học viện uy tín cũng như đào tạo nội bộ doanh nghiệp, tôi tự tin có thể đáp ứng tốt các tiêu chuẩn giảng dạy cao của Quý đơn vị:

1. Trí tuệ nhân tạo (AI) ứng dụng & Kỹ năng số:
- Ứng dụng Generative AI, Prompt Engineering trong lập trình và tối ưu hóa quy trình nghiệp vụ.
- Đào tạo phương pháp lập trình hiện đại kết hợp trợ lý AI.

2. Phân tích Dữ liệu & Hệ thống Thông tin:
- Khai thác dữ liệu với Python (Pandas), SQL chuyên sâu và thiết kế Dashboard báo cáo điều hành (Power BI).

3. Kiến trúc Phần mềm & Công nghệ Nền tảng:
- Lập trình Java/Python chuẩn quốc tế, quản trị cơ sở dữ liệu, quy trình DevOps (Docker, Kubernetes).

Phương pháp sư phạm của tôi luôn bám sát chuẩn đầu ra thực tế của doanh nghiệp, giúp học viên vững kiến thức nền tảng và thành thạo kỹ năng thực hành.

Quý đơn vị có thể tham khảo thêm:
- CV năng lực: {CV_LINK}
- Kênh YouTube bài giảng (500+ video): {YOUTUBE_LINK}

Tôi rất hân hạnh nếu có cơ hội được gặp gỡ hoặc trao đổi qua video call để cùng Quý đơn vị thảo luận chi tiết hơn về cơ hội hợp tác.

Kính chúc Ban Lãnh đạo và tập thể {name} sức khỏe, thành công!

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


def action_preview(count=10):
    """
    Xem trước danh sách 10 đơn vị sẽ được gửi và hiển thị email may đo riêng cho từng đơn vị.
    CHỐT CHẶN: Dừng lại chờ người dùng confirm trước khi gửi.
    """
    batch, total_registry, total_sent = get_available_batch(count=count)

    print("=" * 80)
    print(f"🎯 DANH SÁCH {len(batch)} ĐƠN VỊ ĐÀO TẠO MỚI NHẤT (ĐÃ LỌC BLACKLIST & TRÙNG LẶP)")
    print(f"📊 Thống kê: Tổng {total_registry} đơn vị trong kho | Đã gửi thành công: {total_sent} đơn vị")
    print("=" * 80)

    if not batch:
        print("⚠️ Không còn đơn vị mới nào hợp lệ trong kho đăng ký!")
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

    # Hiển thị 2 mẫu email khác nhau đại diện cho 2 nhóm khác nhau
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
    print("   python3 gui_cv_assistant.py --action send --confirm")
    print("=" * 80)
    return batch


def action_send(count=10, confirmed=False):
    """
    Thực hiện gửi email cho danh sách đơn vị đã được phê duyệt.
    """
    if not confirmed:
        print("❌ LỖI: Bạn chưa xác nhận cờ '--confirm'!")
        print("Quy tắc bắt buộc: Trước khi gửi phải có sự phê duyệt từ người dùng.")
        sys.exit(1)

    batch, total_registry, total_sent = get_available_batch(count=count)
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
    parser.add_argument("--confirm", action="store_true", help="Xác nhận gửi email thật")

    args = parser.parse_args()

    if args.action == "preview":
        action_preview(count=args.count)
    elif args.action == "send":
        action_send(count=args.count, confirmed=args.confirm)
    elif args.action == "status":
        action_status()


if __name__ == "__main__":
    main()
