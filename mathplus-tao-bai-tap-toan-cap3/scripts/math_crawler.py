#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module thu thập, tìm kiếm và trích xuất bài tập Toán cấp 3 từ các website chuyên môn:
- https://toanmath.com
- https://www.toannbv.vn
- https://toanhocbactrungnam.vn
Hỗ trợ tìm kiếm theo từ khóa chủ đề, bóc tách bài viết, liên kết PDF, và cung cấp
ngân hàng kiến thức bài tập chuẩn chương trình GDPT 2018 phân hóa 4 mức độ:
1. Nhận biết (Dễ)
2. Thông hiểu (Trung bình)
3. Vận dụng (Khá)
4. Vận dụng cao (Nâng cao / Phân hóa)
"""

import os
import re
import json
import urllib.request
import urllib.parse
import ssl
from bs4 import BeautifulSoup

# Thiết lập SSL context không kiểm tra chứng chỉ nghiêm ngặt để tránh lỗi mạng
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

def fetch_url(url, timeout=12):
    """Gửi HTTP request và nhận về nội dung text (HTML/JSON)."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def search_toanmath(query, max_results=5):
    """
    Tìm kiếm tài liệu và chuyên đề bài tập trên toanmath.com.
    Trả về danh sách các bài viết kèm link tải PDF (nếu có).
    """
    results = []
    try:
        search_url = f"https://toanmath.com/?s={urllib.parse.quote(query)}"
        html = fetch_url(search_url)
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('article')
        
        for art in articles[:max_results]:
            title_tag = art.find(['h2', 'h3'])
            link_tag = art.find('a')
            desc_tag = art.find('div', class_='entry-summary') or art.find('p')
            
            if not title_tag or not link_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            url = link_tag.get('href', '')
            desc = desc_tag.get_text(strip=True) if desc_tag else ""
            
            # Khám phá link PDF bên trong bài viết
            pdf_link = None
            try:
                post_html = fetch_url(url, timeout=8)
                post_soup = BeautifulSoup(post_html, 'html.parser')
                entry = post_soup.find('div', class_='entry-content')
                if entry:
                    for a in entry.find_all('a'):
                        href = a.get('href', '')
                        if href and href.endswith('.pdf'):
                            pdf_link = href
                            break
            except Exception:
                pass
                
            results.append({
                'source': 'toanmath.com',
                'title': title,
                'url': url,
                'description': desc,
                'pdf_url': pdf_link
            })
    except Exception as e:
        print(f"[!] Lỗi tìm kiếm trên toanmath.com: {e}")
        
    return results

def search_toannbv(query, max_results=5):
    """
    Tìm kiếm tài liệu bài tập trên www.toannbv.vn (Toán Ninh Bình VIP - Thầy Nguyễn Bá Việt).
    """
    results = []
    try:
        search_url = f"https://www.toannbv.vn/search?q={urllib.parse.quote(query)}"
        html = fetch_url(search_url)
        soup = BeautifulSoup(html, 'html.parser')
        posts = soup.select('.post-title a, h2.entry-title a, .blog-post a')
        
        seen_urls = set()
        for p in posts:
            title = p.get_text(strip=True)
            url = p.get('href', '')
            if not title or not url or url in seen_urls:
                continue
            seen_urls.add(url)
            
            drive_links = []
            try:
                post_html = fetch_url(url, timeout=8)
                post_soup = BeautifulSoup(post_html, 'html.parser')
                post_body = post_soup.find('div', class_='post-body')
                if post_body:
                    for a in post_body.find_all('a'):
                        href = a.get('href', '')
                        if any(kw in href for kw in ['drive.google.com', '.pdf', '.docx', '.doc', 'mediafire']):
                            drive_links.append(href)
            except Exception:
                pass
                
            results.append({
                'source': 'toannbv.vn',
                'title': title,
                'url': url,
                'description': f"Tài liệu chuyên đề Toán: {title}",
                'drive_links': drive_links
            })
            if len(results) >= max_results:
                break
    except Exception as e:
        print(f"[!] Lỗi tìm kiếm trên toannbv.vn: {e}")
        
    return results

def search_toanhocbactrungnam(query, max_results=5):
    """
    Tìm kiếm tài liệu trên toanhocbactrungnam.vn.
    """
    results = []
    try:
        search_url = f"https://toanhocbactrungnam.vn/seek/?q={urllib.parse.quote(query)}"
        html = fetch_url(search_url)
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.select('h3 a, .result-content a')
        
        seen_urls = set()
        for a in links:
            title = a.get_text(strip=True)
            url = a.get('href', '')
            if not title or not url or url in seen_urls or url == '#':
                continue
            if not url.startswith('http'):
                url = urllib.parse.urljoin('https://toanhocbactrungnam.vn', url)
            seen_urls.add(url)
            
            results.append({
                'source': 'toanhocbactrungnam.vn',
                'title': title,
                'url': url,
                'description': f"Đề thi và tài liệu luyện thi: {title}"
            })
            if len(results) >= max_results:
                break
    except Exception as e:
        print(f"[!] Lỗi tìm kiếm trên toanhocbactrungnam.vn: {e}")
        
    return results

def search_all_sources(topic, max_per_source=3):
    """
    Tìm kiếm tổng hợp trên tất cả các trang web theo chủ đề.
    """
    print(f"[*] Đang tìm kiếm tài liệu về chủ đề '{topic}' trên các trang web Toán...")
    aggregated = {
        'toanmath': search_toanmath(topic, max_per_source),
        'toannbv': search_toannbv(topic, max_per_source),
        'toanhocbactrungnam': search_toanhocbactrungnam(topic, max_per_source)
    }
    total_found = sum(len(v) for v in aggregated.values())
    print(f"[+] Tìm thấy tổng cộng {total_found} bài viết/chuyên đề liên quan.")
    return aggregated

# ==============================================================================
# NGÂN HÀNG BÀI TẬP TOÁN CẤP 3 PHÂN HÓA THEO 4 CẤP ĐỘ (GDPT 2018)
# Dùng để tổ chức đề bài mẫu và tự động sinh câu hỏi chuẩn mực từ dễ đến khó
# ==============================================================================

DIFFICULTY_LEVELS = [
    {
        'level_id': 1,
        'code': 'NB',
        'name': 'MỨC ĐỘ 1: NHẬN BIẾT (DỄ)',
        'target_ratio': 0.35,
        'description': 'Kiểm tra định nghĩa, công thức cơ bản, nhận diện đồ thị và bảng biến thiên trực tiếp.'
    },
    {
        'level_id': 2,
        'code': 'TH',
        'name': 'MỨC ĐỘ 2: THÔNG HIỂU (TRUNG BÌNH)',
        'target_ratio': 0.30,
        'description': 'Yêu cầu tính toán từ 1 đến 2 bước, giải phương trình/bất phương trình cơ bản, tìm tham số đơn giản.'
    },
    {
        'level_id': 3,
        'code': 'VD',
        'name': 'MỨC ĐỘ 3: VẬN DỤNG (KHÁ)',
        'target_ratio': 0.20,
        'description': 'Tổng hợp nhiều kiến thức, bài toán tìm cực trị, điều kiện có nghiệm phức tạp, biện luận tham số.'
    },
    {
        'level_id': 4,
        'code': 'VDC',
        'name': 'MỨC ĐỘ 4: VẬN DỤNG CAO (NÂNG CAO / PHÂN HÓA)',
        'target_ratio': 0.15,
        'description': 'Bài toán ứng dụng thực tế tối ưu, bất đẳng thức, hình học không gian kết hợp giải tích, phân loại 9 - 10 điểm.'
    }
]

def calculate_level_counts(total_count):
    """
    Tính số lượng câu hỏi cho mỗi mức độ dựa trên tổng số câu yêu cầu:
    - Nhận biết: ~35%
    - Thông hiểu: ~30%
    - Vận dụng: ~20%
    - Vận dụng cao: ~15%
    """
    if total_count <= 4:
        # Nếu tổng số câu <= 4 thì mỗi mức 1 câu
        counts = [1] * total_count + [0] * (4 - total_count)
        return counts
        
    c1 = max(1, round(total_count * 0.35))
    c2 = max(1, round(total_count * 0.30))
    c3 = max(1, round(total_count * 0.20))
    c4 = total_count - (c1 + c2 + c3)
    
    if c4 < 1:
        c4 = 1
        if c1 > 1:
            c1 -= 1
        elif c2 > 1:
            c2 -= 1
            
    return [c1, c2, c3, c4]
