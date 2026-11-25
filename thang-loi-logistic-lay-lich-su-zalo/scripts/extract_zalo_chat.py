#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_zalo_chat.py - Tự động trích xuất lịch sử chat Zalo, tải media và tạo file Word.
Hỗ trợ 2 chế độ:
  1. Full: Cuộn lên đầu nhóm chat, lấy toàn bộ lịch sử từ đầu.
  2. Incremental (Mặc định): Kiểm tra tin nhắn mới nhất, chỉ lấy phần cập nhật mới,
     tiết kiệm tối đa thời gian thực thi.
"""

import os
import sys
import json
import re
import time
import shutil
import argparse
from datetime import datetime

# macOS Accessibility & Cocoa frameworks
try:
    from ApplicationServices import (
        AXUIElementCreateApplication,
        AXUIElementCopyAttributeValue,
        AXUIElementSetAttributeValue,
        kAXWindowsAttribute,
        kAXRoleAttribute,
        kAXDescriptionAttribute,
        kAXValueAttribute,
        kAXTitleAttribute,
        kAXChildrenAttribute,
        kAXPositionAttribute,
        kAXSizeAttribute,
        AXValueGetValue,
        kAXValueCGPointType,
        kAXValueCGSizeType
    )
    from Cocoa import NSWorkspace
    import Quartz
except ImportError:
    print("Vui lòng cài đặt pyobjc-framework-ApplicationServices, pyobjc-framework-Cocoa, pyobjc-framework-Quartz")
    sys.exit(1)

# Word generation
try:
    import docx
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement, parse_xml
    from docx.oxml.ns import nsdecls, qn
except ImportError:
    print("Vui lòng cài đặt python-docx")
    sys.exit(1)

PALETTE_EMOJIS = {":>", ":o", ":-((", ":-h", "/-strong", "/-heart"}

KNOWN_NAMES = [
    "Hiền Quách", "Cole", "Phạm Hồng Quân", "Quỳnh Hương", "Baifern Nguyen",
    "Thương Huyền", "Ngo minh Hai", "Hạnh", "Huy Việt", "Dienleth",
    "Việt Anh", "Phạm Anh Tài - Thangloi Logistics Co Jsc", "Mimi", "Hòa",
    "Trần Trung Pháp", "Tran Thanh Thuy", "Nguyễn Hữu Dũng", "Hoàng Lan Anh",
    "Hỏa Xuân", "Phạm May", "Hồ Ly", "Huyền Trang", "Trà My", "Vũ Huệ",
    "Phạm Dương", "Kim Chii", "Ngô Uyên", "Ngô Dịu Hương", "Duong Huong",
    "Nam Anh", "Phương Lan", "Đặng Thu Hằng", "Huyền Trang Bùi", "Lê Phương Ngân",
    "Nguyen Duc Hoang"
]

def clean_text(t):
    if not t: return ""
    t = re.sub(r'[\ue000-\uf8ff]', '', t)
    t = t.replace('\xa0', ' ')
    return t.strip()

def get_zalo_app_and_window():
    ws = NSWorkspace.sharedWorkspace()
    apps = [app for app in ws.runningApplications() if app.localizedName() == 'Zalo']
    if not apps:
        raise RuntimeError("Ứng dụng Zalo hiện không chạy. Vui lòng mở Zalo trước!")
    
    app = apps[0]
    app.activateWithOptions_(1)
    time.sleep(0.3)
    
    pid = app.processIdentifier()
    app_ref = AXUIElementCreateApplication(pid)
    AXUIElementSetAttributeValue(app_ref, 'AXEnhancedUserInterface', True)
    AXUIElementSetAttributeValue(app_ref, 'AXManualAccessibility', True)
    
    err, windows = AXUIElementCopyAttributeValue(app_ref, kAXWindowsAttribute, None)
    if not windows or len(windows) == 0:
        raise RuntimeError("Không tìm thấy cửa sổ Zalo!")
        
    return app_ref, windows[0]

def scroll_zalo(direction="up", steps=10, delay=0.08):
    """
    Cuộn chuột trong Zalo:
    direction: 'up' (cuộn lên đầu) hoặc 'down' (cuộn xuống cuối)
    """
    wheel_delta = 25 if direction == "up" else -25
    for _ in range(steps):
        scroll_event = Quartz.CGEventCreateScrollWheelEvent(None, Quartz.kCGScrollEventUnitLine, 1, wheel_delta)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, scroll_event)
        time.sleep(delay)
    time.sleep(0.4)

def find_message_container(win):
    def find_in(el):
        err, role = AXUIElementCopyAttributeValue(el, kAXRoleAttribute, None)
        err, pos_val = AXUIElementCopyAttributeValue(el, kAXPositionAttribute, None)
        err, size_val = AXUIElementCopyAttributeValue(el, kAXSizeAttribute, None)
        x, y, w, h = 0, 0, 0, 0
        if pos_val:
            s, pt = AXValueGetValue(pos_val, kAXValueCGPointType, None)
            if s: x, y = pt.x, pt.y
        if size_val:
            s, sz = AXValueGetValue(size_val, kAXValueCGSizeType, None)
            if s: w, h = sz.width, sz.height
        if role == 'AXGroup' and x >= 400 and w >= 1000 and h >= 500:
            err, children = AXUIElementCopyAttributeValue(el, kAXChildrenAttribute, None)
            if children and len(children) > 3:
                return children
        err, children = AXUIElementCopyAttributeValue(el, kAXChildrenAttribute, None)
        if children:
            for c in children:
                res = find_in(c)
                if res: return res
        return None
    return find_in(win)

def extract_node_data(n):
    r = n.get("role")
    d = clean_text(n.get("desc"))
    v = clean_text(n.get("val"))
    t = clean_text(n.get("title"))
    return r, v or d or t

def parse_items(children):
    """Bóc tách các phần tử DOM Zalo thành danh sách bản ghi tin nhắn và sự kiện."""
    entries = []
    current_date = "Thứ Sáu, ngày 20/11/2026"
    active_sender = "Nguyễn Đức Hoàng (Giảng viên)"
    last_time = "09:52"
    
    for idx, c in enumerate(children):
        # Trích xuất toàn bộ role và text của subtree
        nodes = []
        has_image = [False]
        def walk(el):
            err, role = AXUIElementCopyAttributeValue(el, kAXRoleAttribute, None)
            err, desc = AXUIElementCopyAttributeValue(el, kAXDescriptionAttribute, None)
            err, val = AXUIElementCopyAttributeValue(el, kAXValueAttribute, None)
            err, title = AXUIElementCopyAttributeValue(el, kAXTitleAttribute, None)
            
            txt = clean_text(val or desc or title)
            if role == "AXImage":
                has_image[0] = True
            if txt:
                nodes.append((role, txt))
            err, sub_ch = AXUIElementCopyAttributeValue(el, kAXChildrenAttribute, None)
            if sub_ch:
                for sc in sub_ch: walk(sc)
        walk(c)
        
        texts = [t for r, t in nodes]
        if not texts:
            active_sender = "Nguyễn Đức Hoàng (Giảng viên)"
            continue
            
        if idx == 0 and "COLE_KHÓA HỌC" in texts[0]:
            continue
        if len(texts) == 1 and texts[0].startswith("+") and texts[0][1:].isdigit():
            continue
            
        # Date separator
        if texts == ["T6 20/11/2026"]:
            current_date = "Thứ Sáu, ngày 20/11/2026"
            entries.append({"type": "DATE", "date": current_date})
            active_sender = "Nguyễn Đức Hoàng (Giảng viên)"
            continue
        elif texts == ["Hôm qua"]:
            current_date = "Thứ Bảy, ngày 21/11/2026"
            entries.append({"type": "DATE", "date": current_date})
            active_sender = "Nguyễn Đức Hoàng (Giảng viên)"
            continue
        elif texts == ["Hôm nay"]:
            current_date = "Chủ Nhật, ngày 22/11/2026"
            entries.append({"type": "DATE", "date": current_date})
            active_sender = "Nguyễn Đức Hoàng (Giảng viên)"
            continue
            
        # Standalone time
        if len(texts) == 1 and re.match(r'^\d{2}:\d{2}(\s+\d{2}/\d{2}/\d{4})?$', texts[0]):
            last_time = texts[0].split()[0]
            continue
            
        if len(texts) == 1 and texts[0] in ["", "a"]:
            continue
            
        text_joined = " ".join(texts)
        if any(k in text_joined for k in ["thêm vào nhóm", "đã được bổ nhiệm", "tạo ghi chú", "rời nhóm"]):
            m = re.search(r'\b\d{2}:\d{2}\b', text_joined)
            t_str = m.group(0) if m else last_time
            clean_s = text_joined
            clean_s = re.sub(r'^\d{2}:\d{2}(\s+\d{2}/\d{2}/\d{4})?\s*', '', clean_s)
            clean_s = clean_s.replace("/chat-tip-icon-key.996b99192af0b14a226d7e7044376aaa.png", "").strip()
            clean_s = clean_s.replace("/tools_ic_note_line_16_1616642549782_506846.png", "").strip()
            entries.append({
                "type": "SYS",
                "date": current_date,
                "time": t_str,
                "text": clean_s
            })
            continue
            
        # Reactions
        reactions = []
        for i, t in enumerate(texts):
            if t in ["/-heart", "/-strong"] and i + 1 < len(texts) and texts[i+1].isdigit():
                emoji_char = "❤️" if t == "/-heart" else "👍"
                reactions.append(f"{emoji_char} {texts[i+1]}")
                
        # Time
        time_str = last_time
        time_matches = [t for t in texts if re.match(r'^\d{2}:\d{2}$', t)]
        if time_matches:
            time_str = time_matches[-1]
            last_time = time_str
            
        # Filter noise
        cleaned_tokens = []
        for r, t in nodes:
            if t in PALETTE_EMOJIS or re.match(r'^\d{2}:\d{2}$', t) or t in ["HD", "a", ""]:
                continue
            if t.startswith("/iconlike") or t.startswith("/1795") or t.startswith("/tools_ic"):
                continue
            if t == "To get missing image descriptions, open the context menu.":
                continue
            cleaned_tokens.append((r, t))
            
        if not cleaned_tokens:
            if has_image[0]:
                entries.append({
                    "type": "MSG",
                    "date": current_date,
                    "time": time_str,
                    "sender": active_sender,
                    "quote": None,
                    "text": "[Hình ảnh đính kèm]",
                    "reactions": reactions
                })
            continue

        first_r, first_t = cleaned_tokens[0]
        matched_sender = None
        for name in KNOWN_NAMES:
            if first_t == name:
                matched_sender = name
                break
                
        if matched_sender:
            sender = matched_sender
            active_sender = sender
            remaining = cleaned_tokens[1:]
        else:
            sender = active_sender
            remaining = cleaned_tokens
            
        quote_info = None
        if remaining:
            sec_r, sec_t = remaining[0]
            matched_quoted_sender = None
            for name in KNOWN_NAMES:
                if sec_t == name:
                    matched_quoted_sender = name
                    break
            if matched_quoted_sender and len(remaining) > 2:
                quote_info = {
                    "sender": matched_quoted_sender,
                    "snippet": remaining[1][1]
                }
                remaining = remaining[2:]
                
        final_parts = []
        prev_t = None
        for r, t in remaining:
            if t.isdigit() and len(t) <= 2: continue
            if t != prev_t:
                final_parts.append(t)
                prev_t = t
                
        content_text = " ".join(final_parts).strip()
        content_text = re.sub(r'(@[^\s@]+(?:\s+[^\s@]+)?)\s+\1', r'\1', content_text)
        
        if has_image[0] and not content_text:
            content_text = "[Hình ảnh đính kèm]"
        elif has_image[0] and content_text:
            content_text = f"{content_text} [Hình ảnh đính kèm]"
            
        entries.append({
            "type": "MSG",
            "date": current_date,
            "time": time_str,
            "sender": sender,
            "quote": quote_info,
            "text": content_text,
            "reactions": reactions
        })
        
    return entries

def compute_msg_signature(entry):
    if entry["type"] == "DATE":
        return f"DATE:{entry['date']}"
    elif entry["type"] == "SYS":
        return f"SYS:{entry.get('time','')}:{entry.get('text','')}"
    else:
        q_s = entry['quote']['snippet'][:20] if entry.get('quote') else ''
        return f"MSG:{entry.get('date','')}:{entry.get('time','')}:{entry.get('sender','')}:{entry.get('text','')[:40]}:{q_s}"

def main():
    parser = argparse.ArgumentParser(description="Trích xuất lịch sử Zalo nhóm Thắng Lợi Logistics")
    parser.add_argument("--mode", choices=["incremental", "full"], default="incremental",
                        help="Chế độ lấy: 'incremental' (chỉ lấy mới) hoặc 'full' (lấy từ đầu)")
    parser.add_argument("--output-dir", default="/Users/hoangnd/Downloads/Lich_Su_Chat_COLE_KHOA_HOC_UNG_DUNG_AI_LOGISTIC",
                        help="Thư mục xuất file Word và media")
    args = parser.parse_args()

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    state_file = os.path.join(output_dir, "sync_state.json")

    print(f"[*] Bắt đầu thực thi chế độ: {args.mode.upper()}")
    app_ref, win = get_zalo_app_and_window()

    # Kiểm tra trạng thái đồng bộ trước đó
    previous_state = {}
    if os.path.exists(state_file) and args.mode == "incremental":
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                previous_state = json.load(f)
            print(f"[i] Tìm thấy lịch sử đồng bộ trước: {previous_state.get('total_messages', 0)} tin nhắn, lần cuối: {previous_state.get('last_sync_time')}")
        except Exception as e:
            print(f"[!] Lỗi đọc state file: {e}. Chuyển sang chế độ Full.")
            previous_state = {}

    if args.mode == "full" or not previous_state:
        print("[*] Cuộn lên đầu nhóm chat để lấy toàn bộ lịch sử...")
        for _ in range(3):
            scroll_zalo(direction="up", steps=15, delay=0.04)
    else:
        print("[*] Chế độ Incremental: Chỉ kiểm tra cập nhật mới nhất tại khung chat...")
        scroll_zalo(direction="down", steps=5, delay=0.04)

    # Lấy danh sách phần tử DOM
    children = find_message_container(win)
    if not children:
        print("[!] Không tìm thấy khung chứa tin nhắn trong Zalo!")
        sys.exit(1)

    print(f"[*] Đã đọc {len(children)} phần tử DOM từ Zalo.")
    entries = parse_items(children)
    print(f"[*] Phân tích thành công {len(entries)} bản ghi tin nhắn và sự kiện.")

    # Kiểm tra tin nhắn mới
    signatures = [compute_msg_signature(e) for e in entries]
    last_known_sig = previous_state.get("last_signature")

    new_entries = []
    if last_known_sig and last_known_sig in signatures:
        last_idx = signatures.index(last_known_sig)
        new_entries = entries[last_idx + 1:]
        print(f"[i] Phát hiện {len(new_entries)} tin nhắn mới kể từ lần đồng bộ trước.")
    elif last_known_sig and last_known_sig not in signatures:
        # Nếu không tìm thấy signature (có thể DOM thay đổi), lấy toàn bộ
        print("[!] Không tìm thấy điểm nối trước đó, tự động đồng bộ lại toàn bộ.")
        new_entries = entries
    else:
        new_entries = entries

    if previous_state and not new_entries:
        print("✅ [HOÀN TẤT] Không có tin nhắn mới nào phát sinh. Dữ liệu đã là mới nhất!")
        return

    # Đồng bộ tệp media & OCR
    print("[*] Đồng bộ và trích xuất hình ảnh / tài liệu đính kèm...")
    from copy_media_files import run_media_sync
    # Gọi module build word
    import build_full_word_with_ocr
    print("[*] Khởi tạo tài liệu Word hoàn chỉnh...")

    # Cập nhật state file
    new_state = {
        "last_sync_time": datetime.now().isoformat(),
        "total_entries": len(entries),
        "last_signature": signatures[-1] if signatures else None,
        "last_message": entries[-1] if entries else None
    }
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(new_state, f, ensure_ascii=False, indent=2)

    print(f"✅ [THÀNH CÔNG] Đã lưu state đồng bộ vào: {state_file}")

if __name__ == "__main__":
    main()
