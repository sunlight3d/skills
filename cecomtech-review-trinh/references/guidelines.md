# Hướng Dẫn Kỹ Thuật & Tiêu Chuẩn Báo Cáo Rà Soát Tuân Thủ Quy Trình

## 1. Xử Lý Tệp Tin PDF (OCR & Convert DOCX)
- **Tự động chuyển đổi PDF sang Word:** Mọi tệp `.pdf` trong thư mục văn bản tham khảo cần được xử lý chuyển đổi thành tệp `.docx` tương ứng để phục vụ việc trích xuất và đọc văn bản chính xác.
- **Cơ chế OCR:**
  - Với PDF scan ảnh: Sử dụng công cụ `rapidocr-onnxruntime` phối hợp với `pymupdf` để thực hiện nhận diện ký tự quang học tiếng Việt trên từng trang.
  - Văn bản nhận dạng được cấu trúc theo từng phân trang (`--- TRANG X ---`) và lưu lại dưới định dạng `.docx` chuẩn.

## 2. Nguyên Tắc Rà Soát
- **Đa nguồn tham chiếu:** Khi có nhiều văn bản tham khảo (ví dụ: QĐ 1323/QĐ-BTC, QĐ 2839/QĐ-BTC, QĐ 292/QĐ-BKHCN), phải quét và đối chiếu toàn bộ các văn bản, không được bỏ sót nguồn nào.
- **Trích dẫn nguyên văn 100%:** Nội dung trích dẫn phải lấy trực tiếp từ file gốc, giữ nguyên từng ký tự, dấu câu, không diễn giải, không tóm tắt, không thêm tiền tố như `Điều X...` hoặc `Chương Y...`.
- **Phân loại trạng thái:**
  - `Đạt`: Có căn cứ và quy định tương ứng trong văn bản tham khảo.
  - `Chưa đạt`: Thiếu quy trình bắt buộc (Master Data, Kiến trúc, Phân vai trách nhiệm Data Owner/Steward, Luồng chi tiết).

## 3. Tiêu Chuẩn Bảng Word (5 Cột)
- **Bố cục:** Chuẩn **A4 nằm ngang (Landscape)** `11.69 x 8.27 inches` (297 x 210 mm), lề 0.8 inch.
- **Màu chữ:** Toàn bộ tiêu đề, đề mục, nội dung trích dẫn Đạt sử dụng **chữ màu đen thuần (`#000000`)**.
- **Header của bảng:** Nền màu xanh lá đậm **`#197935`**, chữ trắng in đậm căn giữa.
- **5 Cột chuẩn:**
  1. `STT` (Width: 0.45 in, Căn giữa, chữ đen `#000000`)
  2. `Nội dung quy trình` (Width: 2.1 in, Căn trái, chữ đen `#000000`)
  3. `Trạng thái` (Width: 0.75 in, Căn giữa, Đạt = `#197935`, Chưa đạt = `#C62828`)
  4. `Thông tin trích dẫn` (Width: 4.9 in - rộng nhất, Căn trái, Chữ thường regular, non-italic; Đạt = `#000000`, Chưa đạt = `#C62828`)
  5. `Tên file trích dẫn` (Width: 1.9 in, Căn trái, chữ đen `#000000`)
- **Phân tách dòng (Split-Row):** Khi có nhiều file cho cùng một mục, tách dòng cho cột 4 và 5, đồng thời gộp dòng (merge) cho cột 1, 2, 3.
