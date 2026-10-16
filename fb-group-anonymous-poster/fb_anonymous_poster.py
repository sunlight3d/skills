#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Group Anonymous Poster
Tự động đăng bài ẩn danh lên Facebook Groups với cơ chế chống checkpoint và chống spam.
"""

import os
import sys
import time
import json
import random
import argparse
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext

DEFAULT_PROFILE_DIR = os.path.expanduser("~/.fb_auto_profile")
HISTORY_FILE = os.path.expanduser("~/.fb_post_history.json")

# Selectors cho Facebook giao diện Tiếng Việt và Tiếng Anh
SELECTORS = {
    # Nút mở soạn thảo hoặc nút đăng ẩn danh trực tiếp ở đầu Group
    "anonymous_trigger_buttons": [
        "div[role='button']:has-text('Đăng bài ẩn danh')",
        "div[role='button']:has-text('Đăng ẩn danh')",
        "div[role='button']:has-text('Anonymous post')",
        "div[role='button']:has-text('Anonymous Post')",
        "span:has-text('Đăng bài ẩn danh')",
        "span:has-text('Anonymous post')",
        "div[role='button']:has-text('Viết gì đó...')",
        "div[role='button']:has-text('Bạn viết gì đi...')",
        "div[role='button']:has-text('Write something...')",
        "div[role='button']:has-text('Create a public post...')",
    ],
    # Nút xác nhận trong dialog giải thích đăng ẩn danh của Facebook
    "anonymous_dialog_confirm": [
        "div[role='button']:has-text('Tôi muốn đăng ẩn danh')",
        "div[role='button']:has-text('I want to post anonymously')",
        "div[role='button']:has-text('Bật')",
        "div[role='button']:has-text('Turn on')",
        "div[role='button']:has-text('Bắt đầu')",
        "div[role='button']:has-text('Get Started')",
    ],
    # Nút chuyển đổi sang ẩn danh bên trong popup soạn thảo (nếu có)
    "anonymous_toggle_inside": [
        "input[aria-label='Đăng bài ẩn danh']",
        "input[aria-label='Post anonymously']",
        "div[role='switch']:has-text('Đăng ẩn danh')",
        "div[role='switch']:has-text('Post anonymously')",
        "div[role='button']:has-text('Đăng bài ẩn danh')",
    ],
    # Khung nhập nội dung bài viết
    "textbox": [
        "div[role='textbox'][contenteditable='true']",
        "div[aria-label*='Bạn đang nghĩ gì']",
        "div[aria-label*=\"What's on your mind\"]",
        "div[aria-label*='Tạo bài viết']",
        "div[aria-label*='Create a post']",
    ],
    # Nút bấm Đăng
    "submit_button": [
        "div[aria-label='Đăng'][role='button']",
        "div[aria-label='Post'][role='button']",
        "div[role='button']:has-text('Đăng')",
        "div[role='button']:has-text('Post')",
    ],
}


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def save_history(entry: dict):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def human_type(page: Page, text: str):
    """Giả lập gõ văn bản như người thật với tốc độ và độ trễ ngẫu nhiên."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line:
            for char in line:
                page.keyboard.type(char, delay=random.randint(25, 65))
                if random.random() < 0.05: # thi thoảng dừng lại 0.1-0.2s như người thật đang suy nghĩ
                    time.sleep(random.uniform(0.1, 0.25))
        if i < len(lines) - 1:
            page.keyboard.press("Shift+Enter")
            time.sleep(0.08)


def activate_anonymous_mode(page: Page) -> bool:
    """Tìm và kích hoạt chế độ Đăng bài ẩn danh trong Group Facebook."""
    log("Đang tìm nút kích hoạt 'Đăng bài ẩn danh'...")
    
    # Bước 1: Thử tìm nút 'Đăng bài ẩn danh' trực tiếp trên thanh công cụ nhóm
    clicked_direct = False
    for sel in SELECTORS["anonymous_trigger_buttons"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=1500):
                log(f"-> Đã tìm thấy nút: {sel}")
                btn.click()
                clicked_direct = True
                time.sleep(1.5)
                break
        except Exception:
            continue
            
    if not clicked_direct:
        log("⚠️ Không tìm thấy nút trực tiếp, thử cuộn nhẹ trang để kích hoạt thanh soạn thảo...")
        page.mouse.wheel(0, 300)
        time.sleep(1)
        for sel in SELECTORS["anonymous_trigger_buttons"]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    btn.click()
                    time.sleep(1.5)
                    break
            except Exception:
                continue

    # Bước 2: Kiểm tra xem có xuất hiện dialog xác nhận "Tôi muốn đăng ẩn danh" không
    for sel in SELECTORS["anonymous_dialog_confirm"]:
        try:
            dialog_btn = page.locator(sel).first
            if dialog_btn.is_visible(timeout=2000):
                log(f"-> Xuất hiện popup xác nhận ẩn danh. Bấm xác nhận: '{sel}'")
                dialog_btn.click()
                time.sleep(1.5)
                break
        except Exception:
            continue

    # Bước 3: Kiểm tra nếu đang mở composer thường, thử bật switch ẩn danh bên trong
    for sel in SELECTORS["anonymous_toggle_inside"]:
        try:
            toggle = page.locator(sel).first
            if toggle.is_visible(timeout=1500):
                log(f"-> Tìm thấy nút gạt ẩn danh bên trong khung soạn thảo: {sel}")
                toggle.click()
                time.sleep(1)
                break
        except Exception:
            continue

    return True


def post_to_group(
    page: Page,
    group_url: str,
    content: str,
    dry_run: bool = True,
    screenshot_dir: str = "/tmp"
) -> bool:
    """Thực hiện đăng 1 bài viết lên 1 nhóm cụ thể."""
    log(f"=== Đang xử lý nhóm: {group_url} ===")
    
    try:
        page.goto(group_url, wait_until="domcontentloaded", timeout=45000)
        time.sleep(random.uniform(3.0, 4.5))
    except Exception as e:
        log(f"❌ Không thể truy cập nhóm: {e}")
        return False

    # Kiểm tra xem có bị yêu cầu đăng nhập không
    if "login" in page.url:
        log("❌ Trình duyệt chưa đăng nhập Facebook! Vui lòng đăng nhập trước.")
        return False

    # Kích hoạt chế độ ẩn danh
    activate_anonymous_mode(page)

    # Tìm ô nhập nội dung
    textbox = None
    for sel in SELECTORS["textbox"]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=3000):
                textbox = loc
                log(f"-> Tìm thấy khung soạn thảo bài viết: {sel}")
                break
        except Exception:
            continue

    if not textbox:
        log("❌ Không tìm thấy khung soạn thảo bài viết. Nhóm có thể đã tắt quyền đăng bài hoặc cần được duyệt thành viên.")
        screenshot_path = os.path.join(screenshot_dir, f"fb_error_{int(time.time())}.png")
        page.screenshot(path=screenshot_path)
        log(f"Ảnh chụp màn hình lỗi: {screenshot_path}")
        return False

    # Click vào khung soạn thảo và gõ nội dung
    log("Đang nhập nội dung bài viết...")
    textbox.click()
    time.sleep(0.8)
    human_type(page, content)
    time.sleep(1.5)

    # Chụp ảnh xem trước
    preview_path = os.path.join(screenshot_dir, f"fb_preview_{int(time.time())}.png")
    page.screenshot(path=preview_path)
    log(f"📸 Đã lưu ảnh xem trước tại: {preview_path}")

    if dry_run:
        log("[DRY-RUN / CHẾ ĐỘ THỬ NGHIỆM] Nội dung đã được nhập hoàn tất. KHÔNG bấm nút Đăng.")
        save_history({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "group_url": group_url,
            "status": "dry_run",
            "preview_image": preview_path,
            "content": content[:120] + "..."
        })
        return True

    # Nếu confirm: Bấm nút Đăng
    log("Chế độ CONFIRM: Đang tìm nút Đăng để xuất bản bài viết...")
    posted = False
    for sel in SELECTORS["submit_button"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                # Kiểm tra nút có bị disable không
                if btn.get_attribute("aria-disabled") == "true":
                    log("⚠️ Nút Đăng đang bị disable (có thể Facebook đang xử lý kiểm duyệt hoặc cần tick chọn thêm quy định nhóm)")
                    continue
                btn.click()
                posted = True
                log("✅ ĐÃ BẤM NÚT ĐĂNG THÀNH CÔNG!")
                time.sleep(4)
                break
        except Exception:
            continue

    if not posted:
        log("⚠️ Không thể bấm nút Đăng tự động. Bạn có thể tự bấm nút Đăng trên màn hình trình duyệt đang mở.")
        return False

    save_history({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "group_url": group_url,
        "status": "posted",
        "preview_image": preview_path,
        "content": content[:120] + "..."
    })
    return True


def main():
    parser = argparse.ArgumentParser(description="Facebook Group Anonymous Poster (Playwright)")
    parser.add_argument("--groups-file", type=str, default=None, help="File JSON chứa danh sách URLs các nhóm cần đăng")
    parser.add_argument("--group-url", type=str, default=None, help="URL 1 nhóm cụ thể để test")
    parser.add_argument("--content-file", type=str, default=None, help="File JSON chứa danh sách biến thể bài viết")
    parser.add_argument("--mode", type=str, choices=["cdp", "persistent"], default="persistent",
                        help="Chế độ kết nối: 'cdp' (gắn vào Chrome đang mở qua port 9222) hoặc 'persistent' (mở Chrome tự động với profile riêng)")
    parser.add_argument("--cdp-url", type=str, default="http://localhost:9222", help="Địa chỉ CDP khi dùng mode 'cdp'")
    parser.add_argument("--profile-dir", type=str, default=DEFAULT_PROFILE_DIR, help="Thư mục profile khi dùng mode 'persistent'")
    parser.add_argument("--confirm", action="store_true", help="Xác nhận bấm nút Đăng thật sự (Mặc định là dry-run)")
    parser.add_argument("--delay-min", type=int, default=60, help="Thời gian chờ tối thiểu giữa các nhóm (giây)")
    parser.add_argument("--delay-max", type=int, default=120, help="Thời gian chờ tối đa giữa các nhóm (giây)")
    
    args = parser.parse_args()
    
    # 1. Thu thập danh sách nhóm
    group_urls = []
    if args.group_url:
        group_urls.append(args.group_url)
    elif args.groups_file and os.path.exists(args.groups_file):
        with open(args.groups_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                group_urls = [item if isinstance(item, str) else item.get("url") for item in data]
    else:
        log("❌ Cần chỉ định ít nhất 1 nhóm qua --group-url hoặc --groups-file")
        sys.exit(1)

    # 2. Thu thập danh sách nội dung
    contents = []
    if args.content_file and os.path.exists(args.content_file):
        with open(args.content_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                contents = [item.get("content", "") if isinstance(item, dict) else str(item) for item in data]
    
    # Nếu không có nội dung, tự động sinh bằng module fb_content_spinner
    if not contents:
        log("Không có file nội dung, tự động sinh các biến thể mới...")
        from fb_content_spinner import generate_variants
        variants = generate_variants(count=len(group_urls) or 3)
        contents = [v["content"] for v in variants]

    log(f"Tổng số nhóm cần đăng: {len(group_urls)}")
    log(f"Chế độ thực thi: {'🚀 ĐĂNG THẬT (--confirm)' if args.confirm else '🛡️ XEM TRƯỚC / DRY-RUN'}")

    # 3. Khởi tạo Playwright
    with sync_playwright() as p:
        context: Optional[BrowserContext] = None
        
        if args.mode == "cdp":
            log(f"Đang kết nối tới Google Chrome qua cổng CDP: {args.cdp_url}...")
            try:
                browser = p.chromium.connect_over_cdp(args.cdp_url)
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.new_page()
            except Exception as e:
                log(f"❌ Không thể kết nối tới Chrome qua {args.cdp_url}: {e}")
                log("💡 Hãy khởi động Chrome với lệnh: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
                sys.exit(1)
        else:
            log(f"Đang khởi động trình duyệt Chrome với profile: {args.profile_dir}...")
            os.makedirs(args.profile_dir, exist_ok=True)
            context = p.chromium.launch_persistent_context(
                user_data_dir=args.profile_dir,
                headless=False,
                channel="chrome", # Dùng trực tiếp Google Chrome của máy
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized"
                ],
                viewport=None
            )
            page = context.pages[0] if context.pages else context.new_page()

        # 4. Duyệt qua từng nhóm và đăng bài
        for idx, g_url in enumerate(group_urls):
            # Chọn nội dung tương ứng (hoặc xoay vòng nếu ít biến thể hơn số nhóm)
            post_text = contents[idx % len(contents)]
            
            log(f"\n[{idx + 1}/{len(group_urls)}] Bắt đầu đăng vào nhóm: {g_url}")
            success = post_to_group(
                page=page,
                group_url=g_url,
                content=post_text,
                dry_run=not args.confirm
            )

            if idx < len(group_urls) - 1:
                wait_sec = random.randint(args.delay_min, args.delay_max)
                log(f"⏳ Tạm dừng an toàn {wait_sec} giây trước khi đăng nhóm tiếp theo (chống spam)...")
                time.sleep(wait_sec)

        log("\n🎉 HOÀN TẤT TẤT CẢ CÁC NHÓM!")
        time.sleep(3)


if __name__ == "__main__":
    main()
