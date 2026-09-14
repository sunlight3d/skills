---
name: aptech-cham-bai
description: "Sử dụng skill này khi người dùng yêu cầu tạo phiếu chấm, bóc tách đề bài (.doc, .docx), tự động chấm bài làm học viên và cập nhật toàn bộ điểm số cùng lời phê chi tiết vào file ChamBai.xlsx."
---

# Aptech Chấm Bài Tự Động (End-to-End: Bóc tách Đề -> Chấm Điểm -> Ghi ChamBai.xlsx & Lời Phê)

## Overview
Skill này giúp tự động hóa toàn bộ quy trình chấm thi thực hành của sinh viên Aptech:
1. **Bóc tách đề thi Word** (`.doc`, `.docx`) để tạo các file rubric Excel chuẩn vào thư mục `debai`.
2. **Dọn dẹp bài làm học viên** trong thư mục `bailam` (giải nén, làm phẳng cấu trúc thư mục lồng nhau đơn lẻ).
3. **Tiến hành chấm bài tự động**: Khớp bài thi với đề bài, phân tích mã nguồn theo từng tiêu chí trong rubric.
4. **Cập nhật trực tiếp vào file `ChamBai.xlsx`**:
   - Tạo sheet chi tiết cho từng học viên (clone format rubric, điền điểm, công thức tính tổng điểm `=SUM(...)` và lời phê chi tiết cho từng câu).
   - Cập nhật bảng tổng hợp `Result` (Tên học viên, điểm số liên kết công thức, môn thi, và lời phê / nhận xét tổng quát).

---

## Quy trình Thực hiện cho Agent

Khi skill này được gọi (ví dụ: `"/aptech-cham-bai thư mục debai và bailam trong Downloads"`), bạn hãy thực hiện theo trình tự sau:

### Bước 1: Trích xuất nội dung đề thi & Sinh Rubric Excel
1. Quét thư mục `debai` tìm các file đề thi `.doc` và `.docx`.
2. Đọc nội dung văn bản (trên macOS dùng `textutil -convert txt <file> -stdout` hoặc thư viện đọc văn bản).
3. Phân tích các tiêu chí yêu cầu và điểm số tương ứng (thường tổng điểm = 20.0).
4. Tạo file `data.json` và chạy script sinh rubric Excel:
   ```bash
   python "/Users/hoangnd/.gemini/config/skills/aptech-cham-bai/scripts/generate_rubrics.py" "/path/to/data.json" "/path/to/debai" "/Users/hoangnd/.gemini/config/skills/aptech-cham-bai/assets/template.xlsx"
   ```

### Bước 2: Dọn dẹp & Chuẩn bị thư mục bài làm (`bailam`)
- Quét và giải nén các file nén (`.zip`, `.rar`, `.7z`) nếu có.
- Tự động làm phẳng cấu trúc thư mục (nếu một thư mục học viên chỉ chứa duy nhất 1 thư mục con bên trong, di chuyển toàn bộ nội dung ra ngoài và xóa thư mục con đó, loại bỏ `.DS_Store`).

### Bước 3: Đảm bảo File Mẫu `ChamBai.xlsx`
- Kiểm tra file `~/Downloads/ChamBai.xlsx`. Nếu chưa có, tự động sao chép từ file mẫu gốc trong thư mục mã nguồn `/Volumes/data/code/connect/chambai/ChamBai.xlsx`.

### Bước 4: Chạy Chấm bài & Cập nhật `ChamBai.xlsx`
Bạn có thể gọi trực tiếp script CLI Headless AutoGrader đã được tích hợp sẵn:

```bash
/Volumes/data/code/connect/chambai/.venv/bin/python /Volumes/data/code/connect/chambai/cli_chambai.py \
    --debai "/path/to/debai" \
    --bailam "/path/to/bailam" \
    --template "/path/to/ChamBai.xlsx"
```

#### Quy chuẩn Lời phê / Nhận xét (Bắt buộc):
- **Ngắn gọn, tự nhiên, tiếng Việt có dấu chuẩn**, không dùng câu chữ máy móc lặp lại.
- Nếu học viên **chưa làm** hoặc bỏ sót tiêu chí nào: ghi rõ `"Chưa làm"`.
- Nếu làm sai hoặc chưa hoàn thiện: chỉ rõ lỗi sai cụ thể (ví dụ: *"Chưa validate form nhập liệu"*, *"Sai tỷ lệ tính thuế bonus"*, *"Thiếu nút quay lại danh sách"*).
- Nếu hoàn thành tốt: để trống hoặc nhận xét khen ngợi ngắn gọn.
- **Lời phê tổng kết**: Được tự động tổng hợp và ghi vào **Cột 6 (Lời phê / Nhận xét)** trong sheet `Result` của file `ChamBai.xlsx`.

### Bước 5: Báo cáo Hoàn tất
- In ra bảng tóm tắt kết quả (Tên học viên | Môn | Điểm tổng kết | Lời phê tổng quát).
- Cung cấp đường dẫn file `ChamBai.xlsx` đã hoàn thiện để người dùng mở kiểm tra.
