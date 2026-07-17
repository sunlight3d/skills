---
name: aptech-cham-bai
description: "Sử dụng skill này khi người dùng yêu cầu tạo phiếu chấm, sinh phiếu chấm, hoặc cung cấp một thư mục chứa các file đề thi (.doc, .docx) để tạo thành các file Excel rubric chấm điểm."
---

# Aptech Chấm Bài (Tự động sinh phiếu chấm Excel từ đề thi)

## Overview
Skill này giúp tự động bóc tách các yêu cầu chấm điểm từ các file đề thi Word (.doc, .docx) và tạo ra các file phiếu chấm Excel tương ứng vào thư mục `debai`. File Excel sẽ được tạo dựa trên một template chuẩn, giữ nguyên công thức tính điểm và cấu trúc đẹp mắt.

## Hướng dẫn các bước cho Agent

Khi skill này được gọi, bạn hãy thực hiện theo trình tự sau:

### Bước 1: Trích xuất nội dung từ file đề thi
1. Liệt kê các file `.doc` và `.docx` trong thư mục mà người dùng cung cấp.
2. Với mỗi file, hãy đọc nội dung của nó.
   - Đối với `.docx`, bạn có thể dùng `pandoc` hoặc giải nén file `.docx` để đọc `word/document.xml`.
   - Đối với `.doc` (nếu có), bạn có thể chạy một đoạn script powershell nhỏ dùng COM object của Word để trích xuất text, hoặc in ra các chuỗi printable nếu COM không hoạt động.

### Bước 2: Dùng tư duy (LLM) để phân tích yêu cầu
- Dựa trên văn bản đã trích xuất, hãy phân tích để tìm ra các "Yêu cầu" và "Điểm số" tương ứng của đề bài.
- Tổng hợp lại dưới dạng danh sách các tuple `(Requirement, Score)`. Giữ nguyên văn các câu chữ chi tiết từ đề bài. Đảm bảo tổng điểm trùng khớp với đề bài (thường là 20 điểm).

### Bước 3: Chuẩn bị file JSON dữ liệu
Tạo một file `data.json` tạm thời trong thư mục của người dùng (ví dụ `C:\Users\nguye\Downloads\data.json`) chứa mảng các cấu trúc như sau:
```json
[
  {
    "filename": "NodeJS_PE1.xlsx",
    "word_filename": "NodeJS_PE1.doc",
    "reqs": [
      ["Create book", 4.0],
      ["Update book", 4.0]
    ]
  }
]
```

### Bước 4: Chạy script tạo Excel
Gọi đoạn script Python được tích hợp sẵn trong skill này để tự động sinh file.
Lệnh chạy:
```powershell
python "C:\Users\nguye\.gemini\config\skills\aptech-cham-bai\scripts\generate_rubrics.py" "C:\path\to\data.json" "C:\path\to\target\dir\debai" "C:\Users\nguye\.gemini\config\skills\aptech-cham-bai\assets\template.xlsx"
```
*Lưu ý: Bạn phải dùng đường dẫn tuyệt đối cho tất cả các đối số. Script này yêu cầu `openpyxl`, hãy đảm bảo chạy bằng python có cài sẵn thư viện này (ví dụ python trong thư mục `.venv` của dự án chambai).*

### Bước 5: Thông báo hoàn tất
Khi script chạy xong, bạn có thể xóa file `data.json` nếu muốn, sau đó thông báo cho người dùng biết các file Excel phiếu chấm đã được sinh thành công trong thư mục `debai`.
