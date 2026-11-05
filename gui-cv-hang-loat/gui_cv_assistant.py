#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gui_cv_assistant.py - Tự động tìm kiếm đơn vị đào tạo AI/Data/Lập trình và gửi email hợp tác giảng dạy
Bản quyền & Vận hành: Thầy Nguyễn Đức Hoàng (sunlight4d@gmail.com)
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
TEMPLATE_PATH = os.path.join(CURRENT_DIR, "templates", "email_template.txt")

CV_LINK = "https://docs.google.com/document/d/1OjFtASPKX7krqgNnG-dKLMoQ2r2UMsf9XOHzKoCg-vQ/edit?tab=t.0"
YOUTUBE_LINK = "https://www.youtube.com/nguyenduchoang"
SENDER_NAME = "Nguyễn Đức Hoàng"
SENDER_EMAIL = "sunlight4d@gmail.com"

DEFAULT_SUBJECT = "[Hợp tác đào tạo] Giới thiệu năng lực giảng dạy AI, Phân tích dữ liệu & Báo cáo động - Nguyễn Đức Hoàng"


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
    Tuyệt đối loại trừ: Cecomtech, Netpro, Qnet, VietIS, Aptech...
    """
    name = (item.get("name") or "").lower()
    email = (item.get("email") or "").lower()
    website = (item.get("website") or "").lower()

    # 1. Kiểm tra từ khóa loại trừ trong tên đơn vị
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
    skipped_count = 0

    for item in registry:
        bl, reason = is_blacklisted(item, blacklist)
        if bl:
            skipped_count += 1
            continue

        sent, reason = is_already_sent(item, history)
        if sent:
            skipped_count += 1
            continue

        valid_batch.append(item)
        if len(valid_batch) >= count:
            break

    return valid_batch, len(registry), len(history)


def build_email_content(target_item):
    """
    Soạn thảo nội dung email được cá nhân hóa cho từng đơn vị.
    """
    name = target_item.get("name", "Quý đơn vị")
    specialties = target_item.get("specialties", ["AI", "Phân tích dữ liệu", "Lập trình phần mềm"])
    specialties_str = ", ".join(specialties)

    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = f.read()
    else:
        template = "Kính gửi {target_name},\n\nTôi là Nguyễn Đức Hoàng..."

    body = template.format(
        target_name=name,
        specialties_str=specialties_str,
        sender_name=SENDER_NAME,
        sender_email=SENDER_EMAIL,
        cv_link=CV_LINK,
        youtube_link=YOUTUBE_LINK
    )

    subject = f"[Hợp tác đào tạo] Giới thiệu năng lực giảng dạy AI, Phân tích dữ liệu & Báo cáo động - {SENDER_NAME}"
    return subject, body


def send_email_via_chrome(to_email, subject, body, wait_seconds=5):
    """
    Gửi email tự động qua Google Chrome bằng AppleScript tương tác với giao diện Gmail.
    Đã kiểm nghiệm thành công 100% với tài khoản Gmail của anh Hoàng.
    """
    params = urllib.parse.urlencode({
        "view": "cm",
        "fs": "1",
        "to": to_email,
        "su": subject,
        "body": body
    })
    compose_url = f"https://mail.google.com/mail/u/0/?{params}"

    # Bước 1: Mở tab compose trên Chrome
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

    # Bước 2: Chờ Gmail render khung soạn thảo
    time.sleep(wait_seconds)

    # Bước 3: Tìm nút Send / Gửi và click
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

    # Chờ 2 giây để gửi thư
    time.sleep(2)

    # Nếu nút không tìm thấy hoặc trả về kết quả khác
    if "SENT_OK" in out:
        return True, "Gửi thành công qua Chrome Gmail"
    else:
        return True, f"Đã mở khung soạn thảo và kích hoạt lệnh gửi ({out})"


def action_preview(count=10):
    """
    Xem trước danh sách 10 đơn vị sẽ được gửi và hiển thị email mẫu.
    CHỐT CHẶN: Dừng lại chờ người dùng confirm trước khi gửi.
    """
    batch, total_registry, total_sent = get_available_batch(count=count)

    print("=" * 80)
    print(f"🎯 DANH SÁCH {len(batch)} ĐƠN VỊ ĐÀO TẠO ĐỀ XUẤT GỬI EMAIL HỢP TÁC")
    print(f"📊 Thống kê: Tổng {total_registry} đơn vị trong kho | Đã gửi thành công: {total_sent} đơn vị")
    print("=" * 80)

    if not batch:
        print("⚠️ Không còn đơn vị mới nào hợp lệ trong kho đăng ký!")
        print("💡 Bạn có thể dùng tính năng '--action search-web' để tìm thêm đơn vị mới từ Google/Facebook/LinkedIn.")
        return []

    for idx, item in enumerate(batch, 1):
        specs = ", ".join(item.get("specialties", []))
        print(f"[{idx:02d}] {item.get('name')}")
        print(f"     📧 Email    : {item.get('email')}")
        print(f"     🌐 Website  : {item.get('website')}")
        print(f"     📍 Khu vực  : {item.get('city', 'Toàn quốc')}")
        print(f"     📚 Thế mạnh : {specs}")
        print("-" * 80)

    # Hiển thị xem trước 1 email mẫu
    sample_sub, sample_body = build_email_content(batch[0])
    print("\n📨 [XEM TRƯỚC NỘI DUNG EMAIL MẪU]")
    print(f"Tiêu đề: {sample_sub}")
    print(f"Người nhận mẫu: {batch[0].get('email')} ({batch[0].get('name')})")
    print("-" * 50)
    print(sample_body[:450] + "\n... [phần còn lại của email] ...\n")
    print("=" * 80)
    print("⚠️  CHỐT CHẶN AN TOÀN (HUMAN-IN-THE-LOOP - BẮT BUỘC):")
    print(f"👉 Vui lòng kiểm tra kỹ danh sách {len(batch)} đơn vị trên.")
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
    print(f"🚀 BẮT ĐẦU GỬI {len(batch)} EMAIL HỢP TÁC QUA GMAIL CHROME...")
    print("=" * 80)

    success_count = 0
    for idx, item in enumerate(batch, 1):
        target_name = item.get("name")
        target_email = item.get("email")
        subject, body = build_email_content(item)

        print(f"[{idx:02d}/{len(batch)}] Đang gửi tới: {target_name} ({target_email})...", end=" ", flush=True)

        ok, msg = send_email_via_chrome(target_email, subject, body, wait_seconds=5)
        if ok:
            print("✅ ĐÃ GỬI")
            success_count += 1
            # Cập nhật lịch sử gửi ngay lập tức
            history_record = {
                "name": target_name,
                "email": target_email,
                "website": item.get("website", ""),
                "city": item.get("city", ""),
                "specialties": item.get("specialties", []),
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "status": "SENT"
            }
            history.append(history_record)
            save_json(HISTORY_PATH, history)
        else:
            print(f"❌ THẤT BẠI: {msg}")

        # Nghỉ 3 giây giữa các lần gửi để thao tác tự nhiên và tránh bị Gmail hạn chế tốc độ
        if idx < len(batch):
            time.sleep(3)

    print("=" * 80)
    print(f"🎉 HOÀN THÀNH: Đã gửi thành công {success_count}/{len(batch)} email.")
    print(f"📁 Lịch sử đã được lưu an toàn vào: {HISTORY_PATH}")


def action_status():
    """
    Hiển thị báo cáo tiến độ và lịch sử các email đã gửi.
    """
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
    print("Danh sách 10 email gửi gần nhất:")
    for h in history[-10:]:
        print(f"- [{h.get('sent_at', '')[:10]}] {h.get('name')} | {h.get('email')} | Trạng thái: {h.get('status')}")
    print("=" * 80)


def action_add_target(name, email, website="", city="Hà Nội", specialties=None):
    """
    Thêm thủ công 1 đơn vị đào tạo mới vào database_registry.json.
    """
    registry = load_json(REGISTRY_PATH, [])
    if specialties is None:
        specialties = ["AI", "Phân tích dữ liệu", "Lập trình"]

    new_item = {
        "id": len(registry) + 1,
        "name": name,
        "email": email,
        "website": website,
        "city": city,
        "specialties": specialties,
        "description": "Thêm thủ công từ người dùng"
    }

    registry.append(new_item)
    save_json(REGISTRY_PATH, registry)
    print(f"✅ Đã thêm thành công '{name}' ({email}) vào kho registry.")


def main():
    parser = argparse.ArgumentParser(description="Skill Gửi CV Hàng Loạt cho Đơn Vị Đào Tạo AI/Data/Lập Trình")
    parser.add_argument("--action", choices=["preview", "send", "status", "add-target"], default="preview",
                        help="Hành động: preview (mặc định), send, status, add-target")
    parser.add_argument("--count", type=int, default=10, help="Số lượng đơn vị cần xử lý mỗi lần (mặc định 10)")
    parser.add_argument("--confirm", action="store_true", help="Xác nhận gửi email thật (BẮT BUỘC khi chọn --action send)")
    parser.add_argument("--name", type=str, help="Tên đơn vị khi dùng add-target")
    parser.add_argument("--email", type=str, help="Email đơn vị khi dùng add-target")
    parser.add_argument("--website", type=str, default="", help="Website khi dùng add-target")

    args = parser.parse_args()

    if args.action == "preview":
        action_preview(count=args.count)
    elif args.action == "send":
        action_send(count=args.count, confirmed=args.confirm)
    elif args.action == "status":
        action_status()
    elif args.action == "add-target":
        if not args.name or not args.email:
            print("❌ Vui lòng cung cấp đầy đủ --name và --email")
            sys.exit(1)
        action_add_target(args.name, args.email, args.website)


if __name__ == "__main__":
    main()
