---
name: fill-logo-nguyen-duc-hoang
description: "Chèn logo chữ 'Nguyễn Đức Hoàng' (chuẩn 16:9) vào góc dưới bên phải các trang Google Slides hoặc file PowerPoint (.pptx) cục bộ để che hoàn toàn watermark của NotebookLM. Hỗ trợ cả link Google Slides đơn lẻ, link thư mục Google Drive chứa nhiều slide và file .pptx ngoại tuyến."
---

# Skill: Chèn Logo Nguyễn Đức Hoàng (Che NotebookLM)

## 1. Giới thiệu (Overview)
Skill này giúp tự động hóa việc chèn logo thương hiệu cá nhân chữ **NGUYỄN ĐỨC HOÀNG** chuẩn tỉ lệ 16:9 (`logo_chu_nguyen_duc_hoang_dark.jpg`) vào **góc dưới bên phải** của tất cả các trang thuyết trình Google Slides hoặc file PowerPoint `.pptx`.

Mục tiêu chính:
- **Che hoàn toàn watermark NotebookLM** ở góc dưới bên phải slide một cách tinh tế và thẩm mỹ.
- Giữ nguyên tỉ lệ 16:9 sắc nét, căn lề chuẩn xác tự động theo độ phân giải của từng bài thuyết trình.
- Hỗ trợ xử lý hàng loạt: nhận đầu vào là link 1 bài trình bày Google Slides, link thư mục Google Drive chứa nhiều slide, hoặc file/thư mục PowerPoint trên máy.

---

## 2. Đầu vào & Đầu ra (Input / Output)

### Đầu vào (Input):
1. **Link Google Slide đơn lẻ**: Ví dụ `https://docs.google.com/presentation/d/<PRESENTATION_ID>/edit` hoặc `<PRESENTATION_ID>`.
2. **Link thư mục Google Drive**: Ví dụ `https://drive.google.com/drive/folders/<FOLDER_ID>` (tự động quét toàn bộ bài thuyết trình bên trong).
3. **File hoặc Thư mục PowerPoint cục bộ**: Đường dẫn file `.pptx` hoặc thư mục chứa các file `.pptx`.

### Đầu ra (Output):
- Toàn bộ các trang slide được chèn phủ logo Nguyễn Đức Hoàng 16:9 sắc nét, ngay ngắn ở góc dưới bên phải, che sạch logo NotebookLM cũ.

---

## 3. Cấu hình & Tọa độ (EMU Coordinates)
- **Tỉ lệ khung hình logo**: Dạng dải ngang gọn gàng (đã crop bỏ viền đen thừa trên dưới).
- **Chiều rộng logo trên slide**: `2,000,000 EMU` (~157 pt).
- **Chiều cao logo tương ứng**: `~453,488 EMU` (~35.7 pt).
- **Lề an toàn (Margin)**: Cách mép phải `50,000 EMU`, cách mép đáy `40,000 EMU`.
- **Độ mờ (Opacity)**: `70%` (bán trong suốt tinh tế, không cấn dòng chữ nội dung slide bên cạnh).

---

## 4. Hướng dẫn sử dụng nhanh (Quick Start)

Script tiện ích `fill_logo_nguyen_duc_hoang.py` nằm tại thư mục skill:
`/Volumes/data/code/skills/fill-logo-nguyen-duc-hoang/fill_logo_nguyen_duc_hoang.py`

### 4.1. Xử lý 1 link Google Slide
```bash
uv run /Volumes/data/code/skills/fill-logo-nguyen-duc-hoang/fill_logo_nguyen_duc_hoang.py "https://docs.google.com/presentation/d/<PRESENTATION_ID>/edit"
```

### 4.2. Xử lý toàn bộ thư mục Google Drive chứa nhiều Google Slides
```bash
uv run /Volumes/data/code/skills/fill-logo-nguyen-duc-hoang/fill_logo_nguyen_duc_hoang.py "https://drive.google.com/drive/folders/<FOLDER_ID>"
```

### 4.3. Xử lý file PowerPoint (.pptx) trên máy
```bash
# Xử lý 1 file PPTX
uv run /Volumes/data/code/skills/fill-logo-nguyen-duc-hoang/fill_logo_nguyen_duc_hoang.py /path/to/slide.pptx

# Xử lý cả thư mục chứa nhiều file PPTX
uv run /Volumes/data/code/skills/fill-logo-nguyen-duc-hoang/fill_logo_nguyen_duc_hoang.py /path/to/pptx_folder/
```

### 4.4. Các tùy chọn nâng cao
- `--credentials /path/to/credentials.json`: Tùy chọn file xác thực Service Account khác.
- `--image-url <URL>`: Cung cấp link ảnh online khác nếu muốn.
- `--remove-only`: Tự động gỡ các logo đã chèn trước đó mà không thêm mới.

---

## 5. Lưu ý quan trọng về phân quyền Google Drive
Khi sử dụng với Google Slides online, bạn cần **Chia sẻ (Share)** quyền **Người chỉnh sửa (Editor)** của Google Slide hoặc Thư mục Google Drive đó cho email của Service Account:

📧 Email Service Account:
```text
hoangnd@connect-gemini-api-471309.iam.gserviceaccount.com
```
*(hoặc `vietis@connect-gemini-api-471309.iam.gserviceaccount.com`)*.

---

## 6. Tính năng thông minh
- **Smart Cleanup**: Tự động tìm và xóa các logo/hình che cũ mà script đã từng tạo trên slide, không bao giờ bị chèn đè trùng lặp nhiều lần khi chạy lại.
- **Batch Processing**: Cập nhật toàn bộ các slide trong presentation chỉ bằng một lần gọi `batchUpdate` của Google API, hoàn thành cực nhanh.
- **Cross-Platform & Offline Ready**: Hỗ trợ cả Google Slides online lẫn file PowerPoint `.pptx` ngoại tuyến.
