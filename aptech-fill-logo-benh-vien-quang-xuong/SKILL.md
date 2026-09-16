---
name: aptech-fill-logo-benh-vien-quang-xuong
description: >-
  Chèn logo Bệnh viện Đa khoa Quảng Xương (tỷ lệ 16:9 - file logo_4552x2560.jpg) vào góc dưới bên phải các trang Google Slides (hoặc thư mục Google Drive chứa các slide) nhằm che hoàn toàn logo watermark của NotebookLM. Hỗ trợ cả link trực tiếp Google Slides, link thư mục Google Drive và file PowerPoint (.pptx) cục bộ.
---

# Skill: Chèn Logo Bệnh Viện Đa Khoa Quảng Xương (Che NotebookLM)

## 1. Giới thiệu (Overview)
Skill này giúp tự động hóa việc chèn logo chuẩn tỉ lệ 16:9 của **Bệnh viện Đa khoa Quảng Xương** (`logo_4552x2560.jpg`) vào **góc dưới bên phải** của tất cả các trang thuyết trình Google Slides hoặc file PowerPoint `.pptx`.

Mục tiêu chính:
- **Che hoàn toàn dòng chữ / logo watermark của NotebookLM** ở góc dưới bên phải slide.
- Giữ nguyên tỉ lệ 16:9 sắc nét của logo bệnh viện mà không làm méo hình hay sai lệch hệ mã màu gốc.
- Hỗ trợ xử lý hàng loạt: nhận đầu vào là link 1 bài trình bày Google Slides hoặc link thư mục Google Drive chứa nhiều slide.

---

## 2. Đầu vào & Đầu ra (Input / Output)

### Đầu vào (Input):
1. **Link Google Slide đơn lẻ**: Ví dụ `https://docs.google.com/presentation/d/<PRESENTATION_ID>/edit` hoặc `<PRESENTATION_ID>`.
2. **Link thư mục Google Drive**: Ví dụ `https://drive.google.com/drive/folders/<FOLDER_ID>` (tự động phát hiện) hoặc dùng kèm cờ `--folder`.
3. **File hoặc Thư mục PowerPoint cục bộ**: Đường dẫn file `.pptx` hoặc thư mục chứa các file `.pptx`.

### Đầu ra (Output):
- Toàn bộ các trang slide được phủ một hình chữ nhật trắng che watermark cũ, đồng thời chèn logo Bệnh viện Đa khoa Quảng Xương 16:9 sắc nét, chuyên nghiệp ngay ngắn ở góc dưới bên phải.

---

## 3. Cấu hình & Tọa độ (EMU Coordinates)
- **Tỉ lệ khung hình logo**: 16:9 (kích thước ảnh gốc: `4552 x 2560`).
- **Chiều rộng logo trên slide**: `2,000,000 EMU` (~157 pt).
- **Chiều cao logo tương ứng**: `1,124,780 EMU` (~88.5 pt).
- **Lề an toàn (Margin)**: Cách mép phải `50,000 EMU`, cách mép đáy `40,000 EMU`.
- Với kích thước này, logo bao phủ rộng rãi và che triệt để vùng watermark NotebookLM (vốn chỉ cao ~`325,000 EMU`).

---

## 4. Hướng dẫn sử dụng nhanh (Quick Start)

Script tiện ích `fill_logo_quang_xuong.py` nằm tại thư mục skill:
`/Users/hoangnd/.gemini/config/skills/aptech-fill-logo-benh-vien-quang-xuong/fill_logo_quang_xuong.py`

### 4.1. Xử lý 1 link Google Slide
```bash
uv run ~/.gemini/config/skills/aptech-fill-logo-benh-vien-quang-xuong/fill_logo_quang_xuong.py "https://docs.google.com/presentation/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
```

### 4.2. Xử lý toàn bộ thư mục Google Drive chứa nhiều Google Slides
```bash
uv run ~/.gemini/config/skills/aptech-fill-logo-benh-vien-quang-xuong/fill_logo_quang_xuong.py "https://drive.google.com/drive/folders/1aBcDeFgHiJkLmNoPqRsTuVwXyZ"
```
*(Script tự động nhận diện URL có dạng `/folders/` và quét toàn bộ các file Google Slides có trong thư mục để xử lý).*

### 4.3. Xử lý file PowerPoint (.pptx) trên máy
```bash
# Xử lý 1 file PPTX
uv run ~/.gemini/config/skills/aptech-fill-logo-benh-vien-quang-xuong/fill_logo_quang_xuong.py /path/to/slide.pptx

# Xử lý cả thư mục chứa nhiều file PPTX
uv run ~/.gemini/config/skills/aptech-fill-logo-benh-vien-quang-xuong/fill_logo_quang_xuong.py /path/to/pptx_folder/
```

### 4.4. Các tùy chọn nâng cao
- `--credentials /path/to/credentials.json`: Tùy chọn file xác thực Service Account nếu muốn dùng file khác.
- `--image-url <URL>`: Cung cấp link ảnh online khác nếu cần.
- `--remove-only`: Tự động gỡ các logo đã chèn trước đó mà không thêm mới.

---

## 5. Lưu ý quan trọng về phân quyền Google Drive
Khi sử dụng với Google Slides online, bạn cần **Chia sẻ (Share)** quyền **Người chỉnh sửa (Editor)** của Google Slide hoặc Thư mục Google Drive đó cho email của Service Account:

📧 Email Service Account:
```
vietis@connect-gemini-api-471309.iam.gserviceaccount.com
```
*(hoặc `hoangnd@connect-gemini-api-471309.iam.gserviceaccount.com` tùy theo file credentials được sử dụng)*.

---

## 6. Tính năng thông minh
- **Smart Cleanup**: Tự động tìm và xóa các logo/hình che cũ mà script đã từng tạo trên slide, không bao giờ bị chèn đè trùng lặp nhiều lần khi chạy lại.
- **Batch Processing**: Cập nhật toàn bộ các slide trong presentation chỉ bằng một lần gọi `batchUpdate`, hoàn thành chỉ trong 1 - 2 giây.
- **Cross-Platform & Offline Ready**: Sẵn sàng xử lý cả Google Slides online lẫn file PowerPoint `.pptx` ngoại tuyến.
