---
name: qnet-get-emails
description: "Đọc email từ Outlook cục bộ theo tài khoản và khoảng thời gian, trích xuất tệp PDF hồ sơ đăng ký tài khoản, đối chiếu biểu mẫu chuẩn template01.docx (kiểm tra format, dấu đỏ mộc, mã QR), và tổng hợp tất cả vào 1 file Excel duy nhất 'TongHop_HoSo_DangKy.xlsx'. Có thể kích hoạt trên mọi project."
---

# QNet Get Emails (Trích xuất Email Outlook & Kiểm định Biểu mẫu PDF)

## Tổng quan
Kỹ năng toàn cục **`qnet-get-emails`** áp dụng cho **tất cả các project trong Antigravity**:
1. **Đọc email từ ứng dụng Outlook** trên máy tính cục bộ (New Outlook / Olk IndexedDB và thư mục cache `%LOCALAPPDATA%\Microsoft\Olk`). Hỗ trợ lọc chính xác theo tài khoản email người dùng yêu cầu (vì Outlook có thể đăng nhập nhiều tài khoản cùng lúc).
2. **Lọc danh sách email theo khoảng thời gian** (`fromDate` và `toDate` do người dùng cung cấp).
3. **Trích xuất nội dung**: Tiêu đề, người gửi, ngày nhận, nội dung mail, và các tệp PDF đính kèm (hỗ trợ cả PDF văn bản số và PDF scan ảnh thông qua engine `RapidOCR`).
4. **Đối chiếu với biểu mẫu chuẩn `template01.docx`**:
   - Kiểm tra định dạng cấu trúc văn bản: Tiêu đề Phiếu đăng ký, Mục 1 (Dự án), Mục 2 (Doanh nghiệp, Mã số DN / MST / Mã QHNS), Mục 3 (Người quản lý sử dụng tài khoản).
   - Kiểm tra **Dấu mộc đỏ** qua thuật toán phân tích thị giác máy tính OpenCV (HSV color thresholding & contour area).
   - Kiểm tra **Mã QR code** bằng bộ giải mã `cv2.QRCodeDetector` quét toàn trang và góc trên bên phải.
   - Phân loại đánh giá chính xác:
     - **Hợp lệ**: Đúng format mẫu + có dấu đỏ + có mã QR.
     - **Đúng format nhưng thiếu dấu đỏ**
     - **Đúng format nhưng thiếu QR**
     - **Đúng format nhưng thiếu cả dấu đỏ và QR**
     - **Sai format**: Liệt kê rõ các mục bị thiếu hoặc sai lệch.
5. **Tổng hợp vào 1 file Excel duy nhất**:
   - Toàn bộ các email và hồ sơ PDF trích xuất được tổng hợp vào **1 file Excel duy nhất** mang tên: **`TongHop_HoSo_DangKy.xlsx`**.
   - File Excel gồm 3 Sheet:
     - Sheet 1: `Báo Cáo Theo Ngày` (Thống kê số lượng email nhận theo từng ngày: tổng số mail, có/không có PDF, số lượng hợp lệ, thiếu QR, thiếu dấu đỏ, sai format, và tỷ lệ hợp lệ).
     - Sheet 2: `Tổng Hợp Hồ Sơ` (Chứa đầy đủ 24 cột: STT, Thời gian nhận, Tiêu đề, Người gửi, Tên file PDF, Đánh giá biểu mẫu, Dấu đỏ, Mã QR, Tên DN, Mã QHNS/MST, Loại dự án, Đối tượng, Ngày cấp, Trụ sở, Đại diện, Chức vụ, VSIC, Người quản lý, CMND, SĐT, Email, Chi tiết đánh giá).
     - Sheet 3: `Chi Tiết Email` (Metadata email và nội dung chi tiết/preview từ Outlook).
   - Tất cả các cell đều bật **Text Wrapping** và **Auto-height**.
   - Thư mục xuất file mặc định là thư mục `output_excel` tại project đang mở (hoặc thư mục người dùng chỉ định).

---

## Hướng dẫn Vận hành cho AI Agent

Khi người dùng ở bất kỳ project nào yêu cầu chạy skill này, thực hiện theo các bước sau:

### Bước 1: Thu thập thông tin từ người dùng
- **Địa chỉ email tài khoản Outlook**: (Ví dụ: `nguyenduchoang1979@outlook.com`).
- **Từ ngày (`fromDate`)**: Định dạng `YYYY-MM-DD` (Ví dụ: `2026-09-01`).
- **Đến ngày (`toDate`)**: Định dạng `YYYY-MM-DD` (Ví dụ: `2026-09-09`).

### Bước 2: Chạy script toàn cục
Thực thi lệnh Python sau:
```powershell
python "C:\Users\nguye\.gemini\config\skills\qnet-get-emails\run_skill.py" --account "<email_nguoi_dung>" --from-date "<YYYY-MM-DD>" --to-date "<YYYY-MM-DD>"
```
*(Nếu muốn xuất vào một thư mục cụ thể, thêm cờ `--output "<đường_dẫn_thư_mục>"`)*

### Bước 3: Báo cáo kết quả
1. Kiểm tra file Excel tổng hợp `output_excel\TongHop_HoSo_DangKy.xlsx`.
2. Trình bày bảng tóm tắt kết quả kiểm tra biểu mẫu (Đúng format, có dấu đỏ, có QR hay không, lý do chi tiết).
