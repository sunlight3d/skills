---
name: pptx-add-vn-logo
description: >-
  Chèn logo Viện Đổi mới Sáng tạo và Chuyển đổi số Liên ngành (logo_vn) vào góc trên bên phải (top-right) của các trang thuyết trình Google Slides hoặc PowerPoint (.pptx). Hỗ trợ link Google Slides đơn lẻ, link Google Drive folder và file .pptx cục bộ.
---

# PPTX Add VN Logo (Viện Đổi mới Sáng tạo & CĐS Liên ngành)

## Giới thiệu
Skill này tự động chèn logo **Viện Đổi mới Sáng tạo và Chuyển đổi số Liên ngành** (`logo_vn.png`) vào **góc trên bên phải (top-right)** của tất cả các trang thuyết trình Google Slides hoặc file PowerPoint `.pptx`.

## Tính năng nổi bật
- **Vị trí chuẩn đẹp**: Đặt ở góc trên bên phải, giữ nguyên tỉ lệ logo (1200x339, width `2,400,000 EMU`, height `678,000 EMU`), căn lề trên `200,000 EMU`, lề phải `250,000 EMU`.
- **Nền trong suốt tinh tế**: Đã xử lý tách nền trong suốt, hòa hợp hoàn hảo với hình nền và dải sóng màu của slide mà không bị khung trắng đè lên.
- **Hỗ trợ đa định dạng**: Nhận link Google Slides, link folder Google Drive, hoặc file/thư mục `.pptx` ngoại tuyến.
- **Smart Cleanup**: Tự động dọn dẹp các logo cũ do script chèn trước đó nếu chạy lại.

## Hướng dẫn sử dụng

```bash
# 1. Chèn vào 1 bài thuyết trình Google Slides
python pptx_add_vn_logo.py "https://docs.google.com/presentation/d/<PRESENTATION_ID>/edit"

# 2. Chèn vào toàn bộ bài thuyết trình trong thư mục Google Drive
python pptx_add_vn_logo.py "https://drive.google.com/drive/folders/<FOLDER_ID>"

# 3. Chèn vào file PowerPoint (.pptx) ngoại tuyến
python pptx_add_vn_logo.py "C:\path\to\presentation.pptx"
```
