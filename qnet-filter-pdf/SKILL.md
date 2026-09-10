---
name: qnet-filter-pdf
description: "Đọc các file PDF đăng ký địa chỉ IP của các Cơ sở khám chữa bệnh (CSKCB), kiểm tra chuẩn định dạng IPv4, kiểm tra chuẩn IP Public (không cho phép IP Local/Private), đối chiếu trùng lặp với cơ sở dữ liệu theo dõi hệ thống (IP_CSKCB_INTERNET - VPN.xlsx), xuất báo cáo Excel với đầy đủ auto-height, text wrapping và bôi đỏ nổi bật các bản ghi validation failed."
---

# QNet Filter PDF (Thẩm định Hồ sơ Đăng ký IP CSKCB từ PDF)

## 1. Tổng quan
Kỹ năng **`qnet-filter-pdf`** tự động hóa quy trình tiếp nhận, trích xuất và thẩm định hồ sơ đăng ký địa chỉ IP Internet của các Cơ sở Khám chữa bệnh (CSKCB) kết nối hệ thống BHYT từ các tệp PDF công văn/biểu mẫu.

### Các tiêu chí kiểm tra (Validation Rules):
1. **Chuẩn định dạng IP (IPv4)**:
   - Địa chỉ IP phải đúng định dạng chuẩn 4 octet `a.b.c.d`.
   - Mỗi octet là số nguyên nằm trong khoảng từ `0` đến `255`.
   - Không chứa ký tự chữ cái, không thiếu octet, không để trống.
2. **Chuẩn IP Public**:
   - Nghiêm cấm địa chỉ IP Private/Local theo chuẩn RFC 1918 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
   - Không cho phép địa chỉ Loopback (`127.0.0.0/8`), Link-local/APIPA (`169.254.0.0/16`), Multicast (`224.0.0.0/4`), hoặc Reserved (`240.0.0.0/4`).
   - Phải là địa chỉ IP Public toàn cầu hợp lệ.
3. **Kiểm tra trùng lặp với CSDL theo dõi hệ thống (`IP_CSKCB_INTERNET - VPN.xlsx`)**:
   - **Mục Thêm mới**: Kiểm tra xem IP này đã từng được cấp cho chính đơn vị này chưa (trùng lặp hồ sơ cũ), hoặc đã được cấp cho một đơn vị CSKCB khác trước đó chưa (xung đột IP giữa các đơn vị).
   - **Mục Hủy**: Kiểm tra xem IP xin hủy có đúng thuộc về đơn vị đó trong CSDL lịch sử không (phát hiện trường hợp đơn vị xin hủy IP thuộc sở hữu của đơn vị khác).
   - Kiểm tra tính đầy đủ của thông tin hồ sơ (như thiếu Mã CSKCB, sai lệch thông tin Tỉnh/Mã).

---

## 2. Đặc tả File Báo cáo Excel Đầu ra

File Excel được xuất ra tuân thủ nghiêm ngặt các quy chuẩn hiển thị:
- **Text Wrapping (`wrap_text=True`)**: Được kích hoạt trên 100% các ô dữ liệu (Tên CSKCB, Địa chỉ, Nhà mạng, Chi tiết lý do vi phạm...).
- **Auto Height**: Không hardcode chiều cao dòng cố định (để `None`), giúp Microsoft Excel tự động co giãn chiều cao theo độ dài văn bản khi mở tệp.
- **Bôi đỏ bản ghi Validation FAILED**: 
  - Toàn bộ dòng có trạng thái `FAILED` được tô nền đỏ nhạt (`#FFC7CE`), chữ màu đỏ đậm (`#9C0006`) và viền đỏ nổi bật.
  - Cột "Chi tiết lý do & Cảnh báo" nêu rõ bản chất lỗi và đối chiếu cụ thể với từng dòng trong CSDL theo dõi.
- **Gồm 3 Sheet chuyên biệt**:
  1. `KetQua_Validation_ChiTiet`: Bảng dữ liệu chi tiết 15 cột cho từng bản ghi thẩm định.
  2. `TongHop_ThongKe`: Dashboard số liệu tổng quan, tỷ lệ đạt/hỏng, bảng phân tích theo từng tiêu chí và danh sách các trường hợp vi phạm cần xử lý ngay.
  3. `TraCuu_LichSu_CSDL`: Bảng tra cứu đối chiếu chéo chi tiết từng IP với các dòng xuất hiện trong file theo dõi gốc.

---

## 3. Tham số Đầu vào & Đầu ra

| Tham số | Cờ lệnh | Bắt buộc | Mô tả |
| :--- | :---: | :---: | :--- |
| **Thư mục chứa PDF** | `--input-dir` / `-i` | **Có** | Đường dẫn tuyệt đối hoặc tương đối tới thư mục chứa các tệp PDF cần kiểm tra. |
| **File theo dõi hệ thống** | `--tracker-file` / `-t` | Không | Đường dẫn file Excel theo dõi (`IP_CSKCB_INTERNET - VPN.xlsx`). Nếu bỏ trống, script tự động tìm kiếm trong thư mục PDF hoặc project. |
| **File Excel đầu ra** | `--output` / `-o` | Không | Đường dẫn file Excel kết quả. Mặc định: `KetQua_KiemTra_IP_CSKCB.xlsx` nằm trong thư mục chứa file PDF. |

---

## 4. Cách sử dụng / Lệnh thực thi

### Lệnh chạy nhanh:
```powershell
python "c:\Users\nguye\Downloads\KhoaHocAIQNetT09-2026\.agent\skills\qnet-filter-pdf\run_skill.py" --input-dir "<đường_dẫn_thư_mục_pdf>"
```

### Lệnh chạy với đường dẫn tùy chọn:
```powershell
python "c:\Users\nguye\Downloads\KhoaHocAIQNetT09-2026\.agent\skills\qnet-filter-pdf\run_skill.py" `
    --input-dir "C:\Users\nguye\Downloads\KhoaHocAIQNetT09-2026\PdtReader" `
    --tracker-file "C:\Users\nguye\Downloads\KhoaHocAIQNetT09-2026\PdtReader\IP_CSKCB_INTERNET - VPN.xlsx" `
    --output "C:\Users\nguye\Downloads\KhoaHocAIQNetT09-2026\PdtReader\KetQua_KiemTra_IP_CSKCB.xlsx"
```

### Lệnh từ bộ Skill Toàn cục (Global Skill):
```powershell
python "C:\Users\nguye\.gemini\config\skills\qnet-filter-pdf\run_skill.py" --input-dir "<đường_dẫn_thư_mục_pdf>"
```
