#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MathPlus Seeding Engine
Tự động tìm kiếm & join tối đa 3 nhóm Facebook liên quan và đăng 2 bài ẩn danh.
"""

import os
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import time
import json
import random
import shutil
import argparse
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext

from spinner import generate_variants

DEFAULT_PROFILE_DIR = os.path.expanduser("~/.fb_auto_profile")
HISTORY_FILE = os.path.expanduser("~/.mathplus_seeding_history.json")

# Danh sách nhóm ưu tiên đã kiểm tra hỗ trợ đăng ẩn danh
VERIFIED_GROUPS = [
    {"name": "Hội Phụ Huynh Quận Đống Đa - Hà Nội ✅", "url": "https://www.facebook.com/groups/1513900589388779/"},
    {"name": "Toán - Lý - Hóa Cấp 3", "url": "https://www.facebook.com/groups/938110672992963/"},
    {"name": "Ôn thi Cấp 3 -Toán THCS", "url": "https://www.facebook.com/groups/703304181597056/"},
]

SEARCH_KEYWORDS = [
    "hội phụ huynh đống đa",
    "phụ huynh lớp 10 11 hà nội",
    "hội phụ huynh kim liên đống đa"
]


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sync_chrome_profile(target_dir: str = DEFAULT_PROFILE_DIR):
    """Đồng bộ session và cookies từ Chrome thật của máy vào profile tự động."""
    src_dir = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
    if not os.path.exists(src_dir):
        return
    
    os.makedirs(target_dir, exist_ok=True)
    local_state_src = os.path.join(src_dir, "Local State")
    local_state_dst = os.path.join(target_dir, "Local State")
    if os.path.exists(local_state_src):
        try:
            shutil.copy2(local_state_src, local_state_dst)
        except Exception:
            pass

    default_src = os.path.join(src_dir, "Default")
    default_dst = os.path.join(target_dir, "Default")
    os.makedirs(default_dst, exist_ok=True)

    for fname in ["Preferences", "Secure Preferences", "Login Data", "Web Data"]:
        s = os.path.join(default_src, fname)
        d = os.path.join(default_dst, fname)
        if os.path.exists(s):
            try:
                shutil.copy2(s, d)
            except Exception:
                pass

    net_src = os.path.join(default_src, "Network")
    net_dst = os.path.join(default_dst, "Network")
    os.makedirs(net_dst, exist_ok=True)
    if os.path.exists(net_src):
        for fname in os.listdir(net_src):
            if "Cookies" in fname:
                try:
                    shutil.copy2(os.path.join(net_src, fname), os.path.join(net_dst, fname))
                except Exception:
                    pass


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
    """Gõ phím mô phỏng người thật với độ trễ ngẫu nhiên."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line:
            for char in line:
                page.keyboard.type(char, delay=random.randint(20, 50))
                if random.random() < 0.04:
                    time.sleep(random.uniform(0.1, 0.25))
        if i < len(lines) - 1:
            page.keyboard.press("Shift+Enter")
            time.sleep(0.06)


def join_group(page: Page, group_url: str) -> bool:
    """Truy cập nhóm và bấm tham gia nếu chưa tham gia."""
    log(f"Đang kiểm tra nhóm để tham gia: {group_url}")
    try:
        page.goto(group_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(random.uniform(2.5, 4.0))
    except Exception as e:
        log(f"❌ Không thể truy cập {group_url}: {e}")
        return False

    # Kiểm tra nút tham gia
    join_selectors = [
        "div[role='button']:has-text('Tham gia nhóm')",
        "div[role='button']:has-text('Tham gia')",
        "div[role='button']:has-text('Join group')",
        "span:has-text('Tham gia nhóm')",
        "span:has-text('Join group')",
    ]
    
    join_btn = None
    for sel in join_selectors:
        btn = page.locator(sel).first
        if btn.is_visible(timeout=1500):
            join_btn = btn
            break

    if not join_btn:
        log("ℹ️ Đã tham gia nhóm này từ trước hoặc đang chờ phê duyệt.")
        return False

    log("-> Bấm nút 'Tham gia nhóm'...")
    join_btn.click()
    time.sleep(2.5)

    # Xử lý nếu có popup câu hỏi quy tắc nhóm
    modal = page.locator("div[role='dialog']")
    if modal.count() > 0 and modal.first.is_visible():
        log("-> Xuất hiện popup câu hỏi/quy định nhóm. Đang tự động hoàn tất...")
        checkboxes = page.locator("div[role='dialog'] input[type='checkbox'], div[role='dialog'] div[role='checkbox']").all()
        for cb in checkboxes:
            try:
                cb.click()
            except Exception:
                pass

        textareas = page.locator("div[role='dialog'] textarea, div[role='dialog'] input[type='text']").all()
        for ta in textareas:
            try:
                ta.fill("Phụ huynh tìm lớp học toán")
            except Exception:
                pass

        submit_btn = page.locator("div[role='dialog'] div[role='button']:has-text('Gửi'), div[role='dialog'] div[role='button']:has-text('Submit'), div[role='dialog'] div[role='button']:has-text('Hoàn tất')").first
        if submit_btn.is_visible(timeout=2000):
            submit_btn.click()
            time.sleep(2)

    log(f"✅ Đã gửi yêu cầu tham gia thành công: {group_url}")
    return True


def search_and_join_groups(page: Page, keywords: List[str], max_join: int = 3) -> List[str]:
    """Tìm kiếm các nhóm liên quan trên Facebook và bấm tham gia tối đa max_join nhóm."""
    log(f"=== Bắt đầu tìm kiếm và tham gia tối đa {max_join} nhóm liên quan ===")
    joined_urls = []

    for kw in keywords:
        if len(joined_urls) >= max_join:
            break

        search_url = f"https://www.facebook.com/search/groups/?q={kw.replace(' ', '%20')}"
        log(f"Tìm kiếm nhóm với từ khóa: '{kw}'")
        try:
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)
        except Exception:
            continue

        links = page.locator("a[href*='/groups/']").all()
        group_candidates = []
        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip()
            if href and text and "/groups/" in href and not any(skip in href for skip in ["/feed", "/discover", "/joins", "/search"]):
                base_url = href.split("?")[0]
                if not any(g == base_url for g in group_candidates) and len(text) > 3:
                    group_candidates.append(base_url)

        log(f"-> Tìm thấy {len(group_candidates)} nhóm ứng viên từ kết quả tìm kiếm.")
        for g_url in group_candidates:
            if len(joined_urls) >= max_join:
                break
            success = join_group(page, g_url)
            if success:
                joined_urls.append(g_url)
                save_history({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "action": "join_group",
                    "group_url": g_url,
                    "status": "requested"
                })
                time.sleep(random.uniform(5, 10))

    log(f"Hoàn tất tham gia nhóm: Đã gửi yêu cầu tới {len(joined_urls)}/{max_join} nhóm.")
    return joined_urls


def sanitize_social_text(text: str) -> str:
    """Loại bỏ hoàn toàn dấu ** và ký tự markdown để tránh lộ dấu vết AI."""
    import re
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = text.replace("**", "").replace("*", "")
    text = re.sub(r"__(.*?)__", r"\1", text)
    return text.strip()


def post_anonymous(
    page: Page,
    group_url: str,
    content: str,
    dry_run: bool = False,
    screenshot_dir: str = os.path.expanduser(r"~\AppData\Local\Temp")
) -> bool:
    """Đăng 1 bài ẩn danh lên nhóm Facebook chỉ định."""
    content = sanitize_social_text(content)
    log(f"\n=== Đang chuẩn bị đăng bài ẩn danh lên nhóm: {group_url} ===")
    try:
        page.goto(group_url, wait_until="domcontentloaded", timeout=35000)
        time.sleep(random.uniform(3.0, 4.5))
    except Exception as e:
        log(f"❌ Không thể truy cập {group_url}: {e}")
        return False

    # 1. Tìm nút 'Anonymous post' / 'Đăng bài ẩn danh'
    anon_triggers = [
        "span:has-text('Anonymous post')",
        "div[role='button']:has-text('Anonymous post')",
        "span:has-text('Đăng bài ẩn danh')",
        "div[role='button']:has-text('Đăng bài ẩn danh')",
        "span:has-text('Đăng ẩn danh')",
        "div[role='button']:has-text('Đăng ẩn danh')",
    ]

    clicked_trigger = False
    for sel in anon_triggers:
        btn = page.locator(sel).first
        if btn.is_visible(timeout=2000):
            log(f"-> Bấm nút kích hoạt ẩn danh: {sel}")
            btn.click()
            clicked_trigger = True
            time.sleep(2)
            break

    if not clicked_trigger:
        log("⚠️ Không thấy nút 'Anonymous post' trực tiếp, thử mở khung 'Write something...'...")
        composer_trigger = page.locator("span:has-text('Write something...'), span:has-text('Bạn viết gì đi...'), div[role='button']:has-text('Viết gì đó...')").first
        if composer_trigger.is_visible(timeout=2000):
            composer_trigger.click()
            time.sleep(2)
            # Kiểm tra nút gạt ẩn danh bên trong
            toggle = page.locator("input[aria-label*='anonymous'], div[role='switch']:has-text('Post anonymously'), div[role='switch']:has-text('Đăng bài ẩn danh')").first
            if toggle.is_visible(timeout=2000):
                toggle.click()
                time.sleep(1.5)
                clicked_trigger = True

    # 2. Xử lý popup xác nhận "Create Anonymous Post"
    confirm_triggers = [
        "div[role='button']:has-text('Create Anonymous Post')",
        "span:has-text('Create Anonymous Post')",
        "div[role='button']:has-text('Tôi muốn đăng ẩn danh')",
        "div[role='button']:has-text('Bật')",
    ]
    for sel in confirm_triggers:
        btn = page.locator(sel).first
        if btn.is_visible(timeout=2000):
            log(f"-> Xác nhận popup giải thích ẩn danh: {sel}")
            btn.click()
            time.sleep(2)
            break

    # 3. Tìm ô nhập nội dung
    textbox = page.locator("div[role='dialog'] div[role='textbox'][contenteditable='true']").first
    if not textbox.is_visible(timeout=4000):
        log("❌ Không tìm thấy khung soạn thảo bài viết ẩn danh!")
        err_path = os.path.join(screenshot_dir, f"fb_error_{int(time.time())}.png")
        page.screenshot(path=err_path)
        log(f"Ảnh chụp màn hình lỗi: {err_path}")
        return False

    log("-> Đang gõ nội dung bài viết với tốc độ người thật...")
    textbox.click()
    time.sleep(0.5)
    human_type(page, content)
    time.sleep(2)

    # Chụp ảnh xem trước
    preview_path = os.path.join(screenshot_dir, f"fb_preview_{int(time.time())}.png")
    page.screenshot(path=preview_path)
    log(f"📸 Đã lưu ảnh chụp xem trước tại: {preview_path}")

    if dry_run:
        log("[DRY-RUN] Đã nhập nội dung bài viết hoàn tất. KHÔNG bấm nút Đăng.")
        save_history({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "action": "post_anonymous",
            "group_url": group_url,
            "status": "dry_run",
            "preview_image": preview_path,
            "content": content[:150] + "..."
        })
        return True

    # 4. Bấm nút Đăng (Post / Submit)
    post_selectors = [
        "div[role='dialog'] div[aria-label='Post'][role='button']",
        "div[role='dialog'] div[role='button']:has-text('Post')",
        "div[role='dialog'] div[aria-label='Submit'][role='button']",
        "div[role='dialog'] div[role='button']:has-text('Submit')",
        "div[role='dialog'] div[aria-label='Đăng'][role='button']",
        "div[role='dialog'] div[role='button']:has-text('Đăng')",
    ]

    posted = False
    for sel in post_selectors:
        btn = page.locator(sel).first
        if btn.is_visible(timeout=2500):
            if btn.get_attribute("aria-disabled") == "true":
                log("⚠️ Nút Đăng đang bị vô hiệu hóa.")
                continue
            log(f"-> Đang bấm nút xuất bản bài viết: {sel}")
            btn.click()
            posted = True
            time.sleep(5)
            log("✅ ĐÃ ĐĂNG BÀI ẨN DANH THÀNH CÔNG!")
            break

    save_history({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "action": "post_anonymous",
        "group_url": group_url,
        "status": "posted" if posted else "failed_submit",
        "preview_image": preview_path,
        "content": content[:150] + "..."
    })
    return posted


def main():
    parser = argparse.ArgumentParser(description="MathPlus Seeding Engine (Anonymous Group Poster)")
    parser.add_argument("--join-count", type=int, default=3, help="Số nhóm tối đa cần tham gia mỗi lần (mặc định 3)")
    parser.add_argument("--post-count", type=int, default=2, help="Số bài tối đa cần đăng mỗi lần (mặc định 2)")
    parser.add_argument("--dry-run", action="store_true", help="Chế độ xem trước, không bấm nút Đăng")
    parser.add_argument("--confirm", action="store_true", default=True, help="Xác nhận đăng bài thật (mặc định bật)")
    parser.add_argument("--delay-min", type=int, default=45, help="Thời gian chờ tối thiểu giữa 2 bài đăng (giây)")
    parser.add_argument("--delay-max", type=int, default=75, help="Thời gian chờ tối đa giữa 2 bài đăng (giây)")

    args = parser.parse_args()

    log("=" * 60)
    log("🚀 KHỞI ĐỘNG MATHPLUS SEEDING AUTOMATION")
    log(f"Mục tiêu: Tham gia {args.join_count} nhóm | Đăng {args.post_count} bài ẩn danh")
    log(f"Chế độ: {'🛡️ XEM TRƯỚC (DRY-RUN)' if args.dry_run else '🚀 ĐĂNG THẬT (--confirm)'}")
    log("=" * 60)

    # 1. Đồng bộ session Chrome mới nhất
    sync_chrome_profile(DEFAULT_PROFILE_DIR)

    # 2. Sinh các biến thể nội dung
    variants = generate_variants(count=args.post_count)
    log(f"Đã sinh {len(variants)} biến thể bài viết không trùng lặp.")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=DEFAULT_PROFILE_DIR,
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ],
            viewport=None
        )
        page = context.pages[0] if context.pages else context.new_page()

        # 3. Bước 1: Tham gia tối đa args.join_count nhóm
        if args.join_count > 0:
            search_and_join_groups(page, SEARCH_KEYWORDS, max_join=args.join_count)

        # 4. Bước 2: Đăng bài ẩn danh lên args.post_count nhóm
        target_post_groups = VERIFIED_GROUPS[:args.post_count]
        log(f"\n=== Bắt đầu đăng {len(target_post_groups)} bài ẩn danh ===")

        for idx, grp in enumerate(target_post_groups):
            content = variants[idx % len(variants)]
            log(f"\n--- Bài {idx + 1}/{len(target_post_groups)}: {grp['name']} ---")
            post_anonymous(
                page=page,
                group_url=grp["url"],
                content=content,
                dry_run=args.dry_run
            )

            if idx < len(target_post_groups) - 1:
                wait_sec = random.randint(args.delay_min, args.delay_max)
                log(f"⏳ Tạm dừng an toàn {wait_sec} giây trước khi đăng nhóm tiếp theo (chống spam)...")
                time.sleep(wait_sec)

        log("\n🎉 HOÀN TẤT PHIÊN SEEDING!")
        time.sleep(3)
        context.close()


if __name__ == "__main__":
    main()
