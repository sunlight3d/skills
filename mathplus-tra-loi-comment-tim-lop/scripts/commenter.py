#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MathPlus Trả Lời Comment Tìm Lớp - Engine chính
Tìm bài viết phụ huynh tìm lớp Toán (lớp 6-12), sinh lời bình luận, yêu cầu Human confirm trước khi đăng.
"""

import os
import sys
import tempfile
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import time
import json
import random
import re
import argparse
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page

from spinner import generate_comment_variants
from joiner import search_and_join_groups

DEFAULT_PROFILE_DIR = os.path.expanduser("~/.fb_auto_profile")
DRAFTS_FILE = os.path.expanduser("~/.mathplus_comment_drafts.json")
HISTORY_FILE = os.path.expanduser("~/.mathplus_comment_history.json")

# Danh sách các nhóm mục tiêu thường xuyên có bài tìm lớp Toán
TARGET_GROUPS = [
    {"name": "Tìm Gia Sư Miễn Phí Tại Hà Nội", "url": "https://www.facebook.com/groups/timgiasumienphihn/"},
    {"name": "Gia sư Toán - Lý - Hoá - Anh Hà Nội", "url": "https://www.facebook.com/groups/189612596047674/"},
    {"name": "Toán - Lý - Hóa Cấp 3", "url": "https://www.facebook.com/groups/938110672992963/"},
    {"name": "Ôn thi Cấp 3 -Toán THCS", "url": "https://www.facebook.com/groups/703304181597056/"},
    {"name": "Hội Phụ Huynh Quận Đống Đa - Hà Nội ✅", "url": "https://www.facebook.com/groups/1513900589388779/"},
    {"name": "Hội Phụ Huynh Đống Đa ✅", "url": "https://www.facebook.com/groups/938373458335677/"},
    {"name": "Hội phụ huynh Hà Nội (Nhóm chính thức)", "url": "https://www.facebook.com/groups/hoiphuhuynhhanoichinhthuc/"},
]

SEARCH_QUERIES = [
    "tìm lớp toán",
    "tìm gia sư toán",
    "học toán",
    "cần tìm lớp toán",
]


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_history() -> List[Dict]:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(entry: Dict):
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def is_already_commented(post_url: str, post_text: str, history: List[Dict]) -> bool:
    """Kiểm tra xem bài viết đã từng được bình luận chưa."""
    for h in history:
        if post_url and h.get("post_url") == post_url:
            return True
        # So khớp tiêu đề ngắn nếu URL bị thay đổi
        if post_text and len(post_text) > 30 and h.get("post_snippet") and post_text[:40] in h.get("post_snippet"):
            return True
    return False


def human_type(page: Page, text: str):
    """Gõ phím mô phỏng người thật với tốc độ và độ trễ ngẫu nhiên."""
    for char in text:
        page.keyboard.type(char, delay=random.randint(18, 45))
        if random.random() < 0.03:
            time.sleep(random.uniform(0.08, 0.2))


def scan_candidate_posts(page: Page, target_count: int = 4) -> List[Dict]:
    """Quét các nhóm để tìm 3 đến 5 bài viết phụ huynh đang tìm lớp Toán."""
    log(f"=== Bắt đầu quét bài viết phụ huynh tìm lớp Toán (Mục tiêu: {target_count} bài) ===")
    history = load_history()
    candidates = []

    # Xáo trộn danh sách nhóm và từ khóa tìm kiếm để ngẫu nhiên
    groups_pool = list(TARGET_GROUPS)
    random.shuffle(groups_pool)

    for grp in groups_pool:
        if len(candidates) >= target_count:
            break

        g_url = grp["url"]
        g_name = grp["name"]
        query = random.choice(SEARCH_QUERIES)
        search_url = f"{g_url.rstrip('/')}/search/?q={query.replace(' ', '%20')}"
        log(f"Đang tìm trong nhóm '{g_name}' với từ khóa '{query}'...")

        try:
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(random.uniform(3.0, 4.5))
        except Exception as e:
            log(f"⚠️ Lỗi truy cập: {e}")
            continue

        # Lấy danh sách các bài viết trong feed tìm kiếm
        posts = page.locator("div[role='feed'] > div, div[role='article']").all()
        log(f"-> Thấy {len(posts)} bài viết từ kết quả tìm kiếm.")

        for p_el in posts:
            if len(candidates) >= target_count:
                break

            try:
                text = p_el.inner_text().strip()
            except Exception:
                continue

            if len(text) < 30:
                continue

            # Bỏ qua bài của chính mình hoặc bài của giáo viên/trung tâm quảng cáo
            text_lower = text.lower()
            if "thầy dũng toán mathplus" in text_lower or "0977961189" in text or "nguyen duc hoang" in text_lower:
                continue

            # Bỏ qua bài do chính tài khoản mình đăng từ lịch sử seeding
            seeding_file = os.path.expanduser("~/.mathplus_seeding_history.json")
            if os.path.exists(seeding_file):
                try:
                    with open(seeding_file, "r", encoding="utf-8") as sf:
                        s_hist = json.load(sf)
                        if any(s.get("content") and len(s["content"]) > 20 and s["content"][:25].lower() in text_lower for s in s_hist):
                            continue
                except Exception:
                    pass

            is_teacher_or_ad = any(kw in text_lower for kw in [
                "digital creator", "public figure", "tác giả kỹ thuật số", "người của công chúng",
                "tuyển sinh", "khai giảng", "lớp mới khai giảng", "thầy nhận lớp", "cô nhận lớp",
                "lịch học tuần", "giáo viên tại", "teacher at", "liên hệ hotline", "fanpage"
            ])
            if is_teacher_or_ad:
                continue

            # Kiểm tra xem có đúng là bài phụ huynh đăng tìm lớp cho con hay không
            is_parent_request = any(kw in text_lower for kw in [
                "mình cần tìm", "em cần tìm", "cần tìm lớp", "tìm lớp toán cho", "tìm gia sư toán",
                "bé nhà mình", "con nhà mình", "tìm thầy dạy toán", "tìm cô dạy toán", "tìm lớp toán",
                "nhờ các bố mẹ", "nhờ mn giới thiệu", "nhờ mn tư vấn", "tìm chỗ học toán", "học thêm toán",
                "lớp 6", "lớp 7", "lớp 8", "lớp 9", "lớp 10", "lớp 11", "lớp 12", "mất gốc toán"
            ])

            if not is_parent_request:
                continue

            # Tìm link permalink bài viết
            link_el = p_el.locator("a[href*='/permalink/'], a[href*='/posts/']").first
            href = None
            if link_el.count() > 0 and link_el.is_visible():
                href = link_el.get_attribute("href")
            clean_url = href.split("?")[0] if href else None

            # Bỏ qua nếu đã từng comment bài này
            if clean_url and is_already_commented(clean_url, text, history):
                continue
            if not clean_url and is_already_commented("", text, history):
                continue

            # Trích xuất đoạn trích ngắn
            lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 10]
            snippet = " ".join(lines[:2])[:140]

            # Kiểm tra trùng lặp trong candidates
            if any(c.get("post_url") == clean_url for c in candidates if clean_url):
                continue

            candidates.append({
                "group_name": g_name,
                "group_url": g_url,
                "post_url": clean_url or g_url,
                "post_snippet": snippet,
                "proposed_comment": ""
            })
            log(f"-> Chọn được bài ({len(candidates)}/{target_count}): {snippet[:70]}...")

    # Gán lời bình luận biến thể cho từng bài
    variants = generate_comment_variants(len(candidates))
    for i, c in enumerate(candidates):
        c["proposed_comment"] = variants[i]

    # Lưu danh sách chờ Human duyệt vào file drafts
    with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

    log(f"✅ Đã quét xong! Đã lưu {len(candidates)} dự thảo bình luận vào: {DRAFTS_FILE}")
    return candidates


def post_comment(page: Page, post_url: str, comment_text: str) -> bool:
    """Truy cập bài viết và đăng 1 bình luận."""
    log(f"\n--- Đang mở bài viết: {post_url} ---")
    try:
        page.goto(post_url, wait_until="domcontentloaded", timeout=35000)
        time.sleep(random.uniform(3.0, 4.0))
    except Exception as e:
        log(f"❌ Không thể truy cập bài viết: {e}")
        return False

    # Kiểm tra xem bài này mình đã comment số đt chưa
    body_text = page.inner_text("body")
    if "0977961189" in body_text:
        log("ℹ️ Bài này đã có bình luận số 0977961189 trước đó, bỏ qua để tránh spam.")
        return True

    # Tìm khung comment
    comment_box = page.locator("div[role='textbox'][contenteditable='true'][aria-label*='Comment'], div[role='textbox'][contenteditable='true'][aria-label*='Bình luận'], div[role='textbox'][contenteditable='true'][aria-label*='Answer'], div[role='textbox'][contenteditable='true']").first
    if not comment_box.is_visible(timeout=5000):
        # Thử tìm nút Comment để mở khung
        c_btn = page.locator("div[role='button']:has-text('Comment'), div[role='button']:has-text('Bình luận')").first
        if c_btn.is_visible(timeout=2000):
            c_btn.click()
            time.sleep(1.5)
            comment_box = page.locator("div[role='textbox'][contenteditable='true']").first

    if not comment_box.is_visible(timeout=4000):
        log("❌ Không tìm thấy khung bình luận trên bài viết này.")
        return False

    log("-> Click vào khung bình luận...")
    comment_box.click()
    time.sleep(0.5)

    log("-> Đang gõ nội dung bình luận...")
    human_type(page, comment_text)
    time.sleep(1.5)

    log("-> Bấm Enter để đăng bình luận...")
    page.keyboard.press("Enter")
    time.sleep(4)

    # Chụp ảnh xác nhận
    try:
        ss_path = os.path.join(tempfile.gettempdir(), f"fb_comment_{int(time.time())}.png")
        page.screenshot(path=ss_path)
    except Exception:
        pass

    log("✅ ĐÃ ĐĂNG BÌNH LUẬN THÀNH CÔNG!")
    return True


def execute_confirmed_comments(page: Page, drafts: List[Dict], delay_min: int = 30, delay_max: int = 60) -> int:
    """Đăng các bình luận đã được Human xác nhận."""
    log(f"=== Bắt đầu thực thi đăng {len(drafts)} bình luận đã được xác nhận ===")
    success_count = 0

    for idx, d in enumerate(drafts):
        post_url = d["post_url"]
        comment_text = d["proposed_comment"]
        log(f"\n[Bài {idx + 1}/{len(drafts)}] Nhóm: {d.get('group_name')}")
        log(f"Nội dung: {comment_text}")

        ok = post_comment(page, post_url, comment_text)
        if ok:
            success_count += 1
            save_history({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "group_name": d.get("group_name"),
                "post_url": post_url,
                "post_snippet": d.get("post_snippet"),
                "comment_text": comment_text,
                "status": "posted"
            })

        if idx < len(drafts) - 1:
            wait_sec = random.randint(delay_min, delay_max)
            log(f"⏳ Tạm dừng an toàn {wait_sec} giây trước khi bình luận bài kế tiếp (chống spam)...")
            time.sleep(wait_sec)

    # Xóa file drafts sau khi đã đăng xong
    if os.path.exists(DRAFTS_FILE):
        try:
            os.remove(DRAFTS_FILE)
        except Exception:
            pass

    log(f"\n🎉 HOÀN TẤT! Đã đăng thành công {success_count}/{len(drafts)} bình luận.")
    return success_count


def main():
    parser = argparse.ArgumentParser(description="MathPlus Trả Lời Comment Tìm Lớp")
    parser.add_argument("--scan", action="store_true", help="Chỉ quét tìm bài viết & sinh dự thảo bình luận (Chờ Human duyệt)")
    parser.add_argument("--confirm", action="store_true", help="Xác nhận thực hiện đăng các bình luận trong file drafts")
    parser.add_argument("--join-count", type=int, default=3, help="Số nhóm tối đa cần tham gia (mặc định 3, không cần confirm)")
    parser.add_argument("--comment-count", type=int, default=3, help="Số bài viết cần trả lời (mặc định 3)")
    parser.add_argument("--post-url", type=str, default=None, help="URL bài viết cụ thể bắt buộc cần bình luận")
    parser.add_argument("--skip-join", action="store_true", help="Bỏ qua bước tham gia nhóm mới")
    parser.add_argument("--delay-min", type=int, default=30, help="Thời gian chờ tối thiểu giữa các comment (giây)")
    parser.add_argument("--delay-max", type=int, default=50, help="Thời gian chờ tối đa giữa các comment (giây)")

    args = parser.parse_args()

    comment_count = max(1, args.comment_count)

    log("=" * 60)
    log("🚀 KHỞI ĐỘNG MATHPLUS TRẢ LỜI COMMENT TÌM LỚP")
    log(f"Tham gia nhóm: {args.join_count} nhóm | Mục tiêu trả lời: {comment_count} bài")
    log("=" * 60)

    # Nếu người dùng truyền cờ --confirm, thực thi đăng từ file drafts
    if args.confirm:
        if not os.path.exists(DRAFTS_FILE):
            log(f"❌ Không tìm thấy file dự thảo {DRAFTS_FILE}. Vui lòng chạy quét bài trước (dùng lệnh không có --confirm).")
            sys.exit(1)

        with open(DRAFTS_FILE, "r", encoding="utf-8") as f:
            drafts = json.load(f)

        if not drafts:
            log("❌ File dự thảo trống.")
            sys.exit(1)

        log(f"Đã nạp {len(drafts)} bình luận từ file dự thảo đã được duyệt.")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=DEFAULT_PROFILE_DIR,
                headless=False,
                channel="chrome",
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                viewport=None
            )
            page = context.pages[0] if context.pages else context.new_page()
            execute_confirmed_comments(page, drafts, delay_min=args.delay_min, delay_max=args.delay_max)
            context.close()
        return

    # Mặc định (hoặc có cờ --scan): Tiến hành Join nhóm + Quét bài + Sinh draft
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=DEFAULT_PROFILE_DIR,
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            viewport=None
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Bước 1: Join khoảng 3 nhóm (không cần confirm)
        if not args.skip_join and args.join_count > 0:
            search_and_join_groups(page, max_join=args.join_count)

        # Bước 2: Quét tìm 3 đến 5 bài viết và sinh bình luận
        drafts = scan_candidate_posts(page, target_count=comment_count)

        context.close()

    # In kết quả cho Human duyệt
    print("\n" + "=" * 60)
    print("📋 DANH SÁCH DỰ THẢO BÌNH LUẬN CHỜ HUMAN CONFIRM:")
    print("=" * 60)
    for idx, d in enumerate(drafts, 1):
        print(f"\n[BÀI {idx}]")
        print(f"Nhóm: {d.get('group_name')}")
        print(f"URL: {d.get('post_url')}")
        print(f"Nội dung bài gốc: \"{d.get('post_snippet')}\"")
        print(f"👉 Bình luận đề xuất: \"{d.get('proposed_comment')}\"")
        print("-" * 50)

    # Nếu chạy qua terminal tương tác trực tiếp
    if sys.stdin.isatty():
        choice = input("\nBạn có xác nhận đăng các bình luận trên không? [Y/N]: ").strip().upper()
        if choice == "Y":
            print("\nĐã xác nhận! Đang tiến hành đăng bình luận...")
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=DEFAULT_PROFILE_DIR,
                    headless=False,
                    channel="chrome",
                    args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                    viewport=None
                )
                page = context.pages[0] if context.pages else context.new_page()
                execute_confirmed_comments(page, drafts, delay_min=args.delay_min, delay_max=args.delay_max)
                context.close()
        else:
            print("Đã hủy bỏ. Chưa có bình luận nào được đăng.")


if __name__ == "__main__":
    main()
