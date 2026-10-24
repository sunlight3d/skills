---
name: cecomtech-review-trinh
description: Tự động rà soát, đối chiếu mức độ tuân thủ của quy trình (file Markdown/Docx) với thư mục văn bản tham khảo (vanbanthamkhao). Tự động chuyển đổi file PDF sang Word (.docx) kèm OCR nhận dạng văn bản tiếng Việt khi gặp file PDF. Xuất báo cáo Word (reviews.docx) chuẩn mực A4 ngang, header bảng màu #197935, chữ màu đen, trích dẫn nguyên văn 100%, bôi đỏ các điểm chưa đạt và đề xuất kiến nghị. Sử dụng skill này khi người dùng yêu cầu rà soát quy trình, xử lý chuyển đổi PDF sang DOCX kèm OCR, hoặc tạo báo cáo reviews.docx.
---

# Quy trình Rà soát Tuân thủ Quy trình & Xuất Báo cáo Word

Skill này hướng dẫn quy trình tiêu chuẩn để rà soát, đối chiếu tính tuân thủ của tài liệu quy trình (ví dụ: `quytrinhtest.md`) với các văn bản quy định, khung kiến trúc tham chiếu (trong thư mục `vanbanthamkhao`), hỗ trợ **tự động chuyển đổi file PDF sang DOCX bằng OCR**, sau đó tự động khởi tạo file báo cáo Word chuẩn mực **`reviews.docx`** (hoặc tên file do người dùng chỉ định).

---

## 1. Đầu vào Yêu cầu

- **File quy trình cần rà soát:** File định dạng Markdown (`.md`), Word (`.docx`), hoặc văn bản mô tả các bước/cấp độ quy trình.
- **Thư mục văn bản tham khảo (`vanbanthamkhao`):** Chứa tất cả các văn bản quy phạm, quyết định, hướng dẫn khung kiến trúc (bao gồm mọi định dạng: `.docx`, `.pdf`, `.txt`, `.md`).
- **File Word đầu ra (tuỳ chọn):** `reviews.docx`, `reviews2.docx`, `reviews3.docx`,...

---

## 2. Quy trình Thực hiện Chuẩn (5 Bước)

### Bước 1: Tiền Xử Lý & Chuyển Đổi File PDF Sang DOCX (OCR)
1. Quét thư mục `vanbanthamkhao`. Nếu phát hiện có file `.pdf` (ví dụ: `1323.pdf`):
   - Chạy module chuyển đổi `scripts/pdf_converter.py`.
   - **Với PDF có text (Digital/Vector PDF):** Trích xuất cấu trúc văn bản trực tiếp sang `.docx`.
   - **Với PDF dạng ảnh quét (Scanned Image PDF):** Sử dụng công cụ OCR tiếng Việt (`rapidocr-onnxruntime` kết hợp `pymupdf`) để nhận diện toàn bộ câu chữ trên từng trang ảnh và tạo file `.docx` tương ứng.
2. File `.docx` sinh ra từ PDF sẽ được dùng làm dữ liệu văn bản chuẩn để tìm kiếm toàn văn và trích dẫn chính xác.

### Bước 2: Phân tích Tài liệu Quy trình
1. Đọc toàn bộ nội dung file quy trình cần rà soát.
2. Bóc tách danh mục các quy trình từ mức tổng quan đến chi tiết (Mức 1, Mức 2, Mức 3).
3. Đánh số thứ tự (STT) và ghi nhận tên gọi, phạm vi, luồng thực hiện của từng mục.

### Bước 3: Đọc & Trích xuất Toàn bộ Văn bản Tham khảo
1. Quét và đọc toàn bộ các file `.docx`, `.txt`, `.md` trong thư mục `vanbanthamkhao` (bao gồm các file vừa được OCR từ PDF).
2. Đọc đa nguồn (không chỉ dựa vào một file duy nhất): đối chiếu đồng thời với tất cả các quyết định/khung kiến trúc liên quan.
3. Đọc chính xác tên cơ quan ban hành và số quyết định (ví dụ: QĐ 1323/QĐ-BTC, QĐ 2839/QĐ-BTC, QĐ 292/QĐ-BKHCN).
4. Trích xuất chính xác các đoạn văn bản gốc quy định về từng chủ đề (siêu dữ liệu, vòng đời dữ liệu, kho dữ liệu, chất lượng dữ liệu, phân quyền truy cập, an toàn thông tin, dữ liệu mở, tích hợp liên thông, dữ liệu chủ...).

### Bước 4: Đánh giá Tuân thủ & Đối chiếu Chi tiết
1. **Mục Đạt:** Khi nội dung quy trình phù hợp và có căn cứ quy định rõ ràng trong các văn bản tham khảo.
2. **Mục Chưa đạt / Thiếu sót:** Khi quy trình thiếu nhóm nghiệp vụ bắt buộc, thiếu quy trình kiểm soát thay đổi, thiếu phân công vai trò trách nhiệm (Data Owner, Data Steward, Data Custodian), hoặc thiếu mô tả luồng quy trình tác nghiệp chi tiết.
3. **Quy tắc trích dẫn bắt buộc:**
   - **Trích dẫn nguyên văn 100%** từng câu chữ, dấu câu, khoảng trắng trực tiếp từ văn bản tham khảo.
   - **Tuyệt đối không tự tạo thêm tiền tố** (như `Điều X, Mục Y:...`, `Chương Z:...` bên trong đoạn trích dẫn).

### Bước 5: Tạo File Báo cáo Word
Sử dụng script Python với `python-docx` để tạo báo cáo chuẩn định dạng theo cấu trúc sau:

#### Tiêu chuẩn Định dạng Bắt buộc:
- **Khổ giấy:** Chuẩn **A4 nằm ngang (Landscape)** `11.69 x 8.27 inches` (297 x 210 mm).
- **Màu chữ:** Toàn bộ tiêu đề, đề mục, nội dung trích dẫn Đạt sử dụng **chữ màu đen thuần (`#000000`)**.
- **Header của bảng:** Nền màu xanh lá đậm **`#197935`**, chữ trắng in đậm căn giữa.
- **Font chữ:** Unicode chuẩn (`Times New Roman`), 11pt cho nội dung, 16pt cho tiêu đề chính, 13pt cho các đề mục lớn.

#### Cấu trúc Nội dung Báo cáo:

1. **I. TỔNG QUAN KẾT QUẢ ĐÁNH GIÁ**
   - Viết lời mở đầu tự nhiên, thực tế, nêu chính xác các văn bản đã sử dụng để đối chiếu.
   - Thống kê: Tổng số mục kiểm tra, Số mục Đạt (màu `#197935`), Số mục Chưa đạt (màu đỏ `#C62828`).
   - *Lưu ý: Không dùng các gạch đầu dòng liệt kê máy móc kiểu AI.*

2. **II. BẢNG CHI TIẾT ĐỐI CHIẾU VÀ ĐÁNH GIÁ TUÂN THỦ**
   - Bảng gồm đúng **5 cột**:
     | STT | Nội dung quy trình | Trạng thái | Thông tin trích dẫn | Tên file trích dẫn |
   - **Quy tắc bảng:**
     - Header bảng có nền màu **`#197935`**.
     - Cột **`Thông tin trích dẫn`** là cột rộng nhất (chiếm ~48-50% chiều ngang).
     - Định dạng chữ trong cột trích dẫn: **Chữ thường (Regular, non-Italic, không in đậm)**.
     - **Phân tách dòng (Split-Row):** Nếu một mục quy trình có từ 2 file tham chiếu trở lên, tách cột `Thông tin trích dẫn` và `Tên file trích dẫn` thành các dòng độc lập tương ứng; các cột `STT`, `Nội dung`, `Trạng thái` được gộp ô (merge) theo chiều dọc.
     - **Mục Chưa đạt:** Trích dẫn hiển thị **chữ màu đỏ (`#C62828`)**, dòng được tô nền phớt hồng (`#FFF5F5`).
     - **Mục Đạt:** Trích dẫn hiển thị chữ màu đen thuần (`#000000`).

3. **III. KIẾN NGHỊ VÀ ĐỀ XUẤT ĐIỀU CHỈNH QUY TRÌNH**
   - Đưa ra các khuyến nghị cụ thể, khả thi để hoàn thiện quy trình đạt chuẩn tuân thủ.
   - *Lưu ý: Bỏ hoàn toàn phần trích dẫn rời rạc bên ngoài bảng để tài liệu cô đọng, liền mạch.*

---

## 3. Các Script Tiện Ích Kèm Theo

1. **`scripts/pdf_converter.py`**: Tự động nhận dạng OCR và chuyển đổi file PDF thành file Word `.docx`.
   ```bash
   python scripts/pdf_converter.py <file.pdf> [<output.docx>]
   ```
2. **`scripts/generate_report.py`**: Sinh báo cáo Word chuẩn format A4 ngang, header xanh `#197935`, chữ đen thuần.
   ```bash
   python scripts/generate_report.py
   ```
