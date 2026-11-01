#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MathPlus Trả Lời Comment Tìm Lớp - Group Joiner
Tự động tìm kiếm và tham gia khoảng 3 nhóm liên quan đến dạy Toán từ lớp 6 đến lớp 12.
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
from typing import List
from playwright.sync_api import Page

HISTORY_FILE = os.path.expanduser("~/.mathplus_joined_groups_history.json")

# Từ khóa tìm kiếm nhóm dạy toán lớp 6 - 12
SEARCH_KEYWORDS = [
    "hội phụ huynh toán cấp 2 cấp 3 hà nội",
    "phụ huynh tìm gia sư toán hà nội",
    "ôn thi vào 10 môn toán hà nội",
    "toán thcs thpt hà nội",
    "đồng hành cùng con môn toán lớp 6 7 8 9",
    "phụ huynh lớp 10 11 12 hà nội",
    "học toán cấp 2 cấp 3 hà nội",
    "phụ huynh đống đa học thêm toán",
]


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_joined_history() -> List[str]:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_joined_history(urls: List[str]):
    history = load_joined_history()
    for u in urls:
        if u not in history:
            history.append(u)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def join_group(page: Page, group_url: str) -> bool:
    """Truy cập nhóm và bấm tham gia nếu chưa tham gia."""
    log(f"Kiểm tra nhóm: {group_url}")
    try:
        page.goto(group_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(random.uniform(2.5, 4.0))
    except Exception as e:
        log(f"❌ Không thể truy cập {group_url}: {e}")
        return False

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

    log("-> Bấm 'Tham gia nhóm'...")
    join_btn.click()
    time.sleep(2.5)

    # Xử lý popup câu hỏi / quy tắc nhóm nếu có
    modal = page.locator("div[role='dialog']")
    if modal.count() > 0 and modal.first.is_visible():
        log("-> Xuất hiện popup câu hỏi/quy định nhóm. Đang tự động điền...")
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

    log(f"✅ Đã gửi yêu cầu tham gia: {group_url}")
    return True


def search_and_join_groups(page: Page, max_join: int = 3) -> List[str]:
    """Tìm kiếm và tham gia khoảng 3 nhóm liên quan Toán lớp 6-12."""
    log(f"=== Bắt đầu tìm kiếm & tham gia tối đa {max_join} nhóm dạy Toán lớp 6-12 ===")
    history = load_joined_history()
    joined = []

    # Xáo trộn từ khóa để mỗi lần gọi tìm ở các góc khác nhau
    keywords = list(SEARCH_KEYWORDS)
    random.shuffle(keywords)

    for kw in keywords:
        if len(joined) >= max_join:
            break

        search_url = f"https://www.facebook.com/search/groups/?q={kw.replace(' ', '%20')}"
        log(f"Tìm kiếm nhóm từ khóa: '{kw}'")
        try:
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)
        except Exception:
            continue

        links = page.locator("a[href*='/groups/']").all()
        candidates = []
        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip()
            if href and text and "/groups/" in href and not any(skip in href for skip in ["/feed", "/discover", "/joins", "/search"]):
                base_url = href.split("?")[0]
                if base_url not in history and base_url not in candidates and len(text) > 3:
                    candidates.append(base_url)

        log(f"-> Tìm thấy {len(candidates)} nhóm tiềm năng mới.")
        for g_url in candidates:
            if len(joined) >= max_join:
                break
            success = join_group(page, g_url)
            if success:
                joined.append(g_url)
                time.sleep(random.uniform(4.0, 8.0))

    if joined:
        save_joined_history(joined)
    log(f"Hoàn tất tham gia nhóm: Đã gửi yêu cầu tới {len(joined)}/{max_join} nhóm.")
    return joined
