---
name: aptech-cham-bai
description: "Sử dụng skill này khi người dùng yêu cầu tạo phiếu chấm, bóc tách đề bài (.doc, .docx), tự động chấm bài làm học viên và cập nhật toàn bộ điểm số cùng lời phê chi tiết vào file ChamBai.xlsx."
---

# Aptech Chấm Bài Tự Động (End-to-End: Bóc tách Đề -> Chấm Điểm -> Ghi ChamBai.xlsx & Lời Phê)

## Overview
Skill này giúp tự động hóa toàn bộ quy trình chấm thi thực hành của sinh viên Aptech:
1. **Bóc tách đề thi** (`.doc`, `.docx`, `.pdf`) để tạo các file rubric Excel chuẩn vào thư mục đề bài.
2. **Dọn dẹp bài làm học viên** trong thư mục bài làm (giải nén zip/rar/7z, làm phẳng cấu trúc thư mục lồng nhau đơn lẻ).
3. **Tiến hành chấm bài tự động**: Khớp bài thi với đề bài, phân tích mã nguồn (Java, C, C#, Web, Scratch `.sb3`, v.v.) theo từng tiêu chí trong rubric.
4. **Cập nhật trực tiếp vào file `ChamBai.xlsx`**:
   - Tạo sheet chi tiết cho từng học viên (clone format rubric, điền điểm, công thức tính tổng điểm `=SUM(...)` và lời phê chi tiết màu đỏ cho từng câu có trừ điểm).
   - Cập nhật bảng tổng hợp `Result` (Tên học viên, điểm số liên kết công thức `='<sheet>'!D19`, môn thi, và lời phê / nhận xét tổng quát).
   - Thiết lập chuẩn hiển thị: **Text wrapping (`wrap_text = True`)**, **Auto Row Height (`height = None`)**, độ rộng cột lời phê (`width = 45`).

---

## Quy trình Thực hiện cho Agent

Khi skill này được gọi (ví dụ: `"/aptech-cham-bai thư mục debai và bailam trong Downloads"` hoặc chấm theo môn cụ thể):

### Bước 1: Trích xuất nội dung đề thi & Sinh Rubric Excel
1. Quét thư mục đề bài tìm các file đề thi (`.doc`, `.docx`, `.pdf`).
2. Đọc nội dung văn bản (dùng `textutil`, `pypdf`, `pdfplumber` hoặc thư viện phù hợp).
3. Phân tích các tiêu chí yêu cầu và điểm số tương ứng (thường tổng điểm = 20.0).
4. Tạo rubric Excel chuẩn (`<MON>_De01.xlsx`, `<MON>_De02.xlsx`...) lưu vào thư mục đề thi.

### Bước 2: Dọn dẹp & Chuẩn bị thư mục bài làm (`bailam`)
- Quét và giải nén các file nén (`.zip`, `.rar`, `.7z`) nếu có.
- Tự động làm phẳng cấu trúc thư mục: nếu một thư mục học viên chỉ chứa duy nhất 1 thư mục con bên trong, di chuyển toàn bộ nội dung ra ngoài và xóa thư mục con trống, dọn dẹp file rác (`.DS_Store`, `__MACOSX`).

### Bước 3: Đảm bảo File Mẫu `ChamBai.xlsx`
- Kiểm tra file `~/Downloads/ChamBai.xlsx`. Nếu chưa có, tự động sao chép từ file mẫu gốc trong thư mục mã nguồn `/Volumes/data/code/connect/chambai/ChamBai.xlsx`.

### Bước 4: Chạy Chấm bài & Cập nhật `ChamBai.xlsx`
Có 2 phương thức chấm bài linh hoạt:

1. **Chấm tự động qua Headless CLI (Ollama API)**:
   ```bash
   /Volumes/data/code/connect/chambai/.venv/bin/python /Volumes/data/code/connect/chambai/cli_chambai.py \
       --debai "/path/to/debai" \
       --bailam "/path/to/bailam" \
       --template "/path/to/ChamBai.xlsx"
   ```

2. **Chấm trực tiếp bằng Agent / Gemini Reasoning**:
   - Sử dụng khi người dùng yêu cầu chấm trực tiếp bằng mô hình AI đang hội thoại, hoặc bài làm có định dạng đặc thù (như Scratch `.sb3`, bài tập đồ họa, ảnh chụp màn hình).
   - Agent trực tiếp phân tích mã nguồn (hoặc file `project.json` trong file `.sb3`), đánh giá chi tiết theo từng tiêu chí của đề bài, chấm điểm và tổng hợp lời phê.
   - Ghi kết quả vào `ChamBai.xlsx` bằng `openpyxl`.

#### Quy chuẩn Định dạng & Lời phê (Bắt buộc):
- **Ngắn gọn, tự nhiên, tiếng Việt có dấu chuẩn**, phản ánh đúng thực tế bài làm:
  - Nếu học viên **chưa làm** hoặc bỏ sót tiêu chí: ghi rõ `"Chưa làm"`.
  - Nếu làm sai hoặc thiếu sót: chỉ rõ lỗi sai cụ thể (ví dụ: *"Dùng repeat 10 thay vì repeat until"*, *"Khung vuông kích thước chưa đúng"*).
  - Tiêu chí bị trừ điểm được ghi màu đỏ (`Font(color="FF0000")`) tại Cột F.
- **Auto Height & Text Wrapping**:
  - Bật `wrap_text = True` trên tất cả ô nhận xét (Cột F) ở cả sheet cá nhân và sheet `Result`.
  - Đặt `row_dimensions[row].height = None` để Excel tự động co giãn dòng theo độ dài văn bản.
  - Cột F đặt độ rộng `width = 45`.
- **Liên kết công thức Excel**:
  - Tại sheet học viên: Tổng điểm ở ô `D19` tính bằng `=SUM(D4:D18)`.
  - Tại sheet `Result`: Cột Điểm chấm (Cột C) trỏ công thức `='<safe_sheet>'!D19`.
  - Tên sheet tối đa 31 ký tự, không chứa ký tự đặc biệt (`\/*?:[]`).

### Bước 5: Báo cáo Hoàn tất
- In ra bảng tóm tắt kết quả (Tên học viên | Môn | Điểm tổng kết | Lời phê tổng quát).
- Cung cấp đường dẫn file `ChamBai.xlsx` đã hoàn thiện để người dùng mở kiểm tra.
