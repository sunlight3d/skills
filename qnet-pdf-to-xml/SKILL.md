---
name: qnet-pdf-to-xml
description: "Trích xuất dữ liệu từ 1 file PDF hoặc 1 thư mục chứa nhiều file PDF để tạo thành bộ 3 file XML, JSON và XLSX cùng tên, trong đó mỗi bản ghi (thẻ <item>) tương ứng với 1 file PDF. Tự động nhận diện cấu trúc trường dữ liệu, đề xuất tên thẻ XML, và chủ động hỏi người dùng để xác nhận hoặc đổi tên các trường trước khi tạo file. Kích hoạt khi người dùng muốn chuyển đổi PDF sang XML/JSON/Excel, xuất dữ liệu PDF thành XML, hoặc xử lý hóa đơn/hồ sơ PDF dạng lô."
---

# QNet PDF to XML / JSON / XLSX (Chuyển đổi PDF Đa định dạng Thông minh)

## 1. Tổng quan & Khả năng

Kỹ năng **`qnet-pdf-to-xml`** tự động hóa quy trình đọc, trích xuất dữ liệu có cấu trúc từ tệp PDF đơn lẻ hoặc toàn bộ thư mục chứa nhiều tệp PDF và đồng thời đóng gói thành bộ ba tệp chuẩn hóa: **XML, JSON và Excel (.xlsx)** cùng tên.

### Đặc điểm nổi bật:
- **Đầu vào linh hoạt**: Chấp nhận đường dẫn đến **1 file PDF** đơn lẻ hoặc **1 thư mục chứa nhiều file PDF** (tự động quét đệ quy các file `.pdf`).
- **Đầu ra bộ ba đồng bộ (XML, JSON, XLSX)**:
  - **File XML**: Mỗi file PDF được biểu diễn bằng một thẻ `<item id="..." file="...">` bên trong thẻ gốc `<records>`. Thụt lề đẹp chuẩn UTF-8.
  - **File JSON**: Cấu trúc mảng đối tượng JSON chuẩn hóa, hỗ trợ lồng nhau (`danh_sach_hang_hoa`).
  - **File XLSX**: Gồm 2 Sheet chuyên nghiệp:
    - *Sheet 1*: `TongHop_HoaDon` (Bản ghi tổng quan 1 file PDF / dòng, format header xanh đậm, text wrapping, căn chỉnh chuẩn mực).
    - *Sheet 2*: `ChiTiet_HangHoa` (Bóc tách chi tiết từng dòng mặt hàng, đơn giá, số lượng, thành tiền liên kết với mã hóa đơn).
- **Hỗ trợ kép Digital & Scanned PDF**:
  - Dùng engine `PyMuPDF` để trích xuất văn bản số cực nhanh và chính xác.
  - Tự động fallback sang `RapidOCR` quét ảnh scan quang học nếu file PDF là ảnh chụp hoặc scan không có text số.
- **Tự động nhận diện trường & Hóa đơn**:
  - Tự động nhận diện từ mục **Người mua hàng** đến hết **Danh sách hàng đã mua**.
  - Nhận diện các cặp khóa - giá trị, thông tin hành chính/doanh nghiệp, mã số thuế, số điện thoại, email, địa chỉ, ngày tháng, bảng hàng hóa...
- **Tương tác hỏi người dùng bắt buộc**: AI tự động chuyển hóa tên trường sang định dạng hợp lệ (snake_case), sau đó **chủ động hiển thị bảng xem trước và hỏi người dùng có muốn đổi tên trường nào không** trước khi xuất file.

---

## 2. Quy trình Thực thi Chuẩn cho AI Agent (Bắt buộc)

Khi người dùng yêu cầu trích xuất PDF sang XML/JSON/Excel, AI Agent cần tuân theo quy trình 4 bước sau:

```
[Người dùng cung cấp PDF/Thư mục] 
             ↓
[Bước 1: Quét Preview & Trích xuất các trường]
             ↓
[Bước 2: AI Đề xuất Tên thẻ & HỎI NGƯỜI DÙNG XÁC NHẬN / ĐỔI TÊN]
             ↓
[Bước 3: Người dùng phản hồi (Đồng ý hoặc cung cấp tên mới)]
             ↓
[Bước 4: Chạy script xuất đồng thời XML, JSON, XLSX & Báo cáo kết quả]
```

### Bước 1: Quét sơ bộ cấu trúc dữ liệu
Chạy script ở chế độ `--preview` để kiểm tra danh sách trường và giá trị mẫu:
```powershell
python "c:\Users\nguye\Downloads\KhoaHocAIQNetT09-2026\PdfToXml\run_skill.py" -i "<đường_dẫn_pdf_hoặc_thư_mục>" --preview
```

### Bước 2: Hiển thị Đề xuất & Hỏi Người dùng (Tương tác bắt buộc)
AI dừng lại và gửi tin nhắn trực tiếp cho người dùng với bảng thống kê các trường đã phát hiện:
> *"Tôi đã quét nội dung file PDF và trích xuất được các trường dữ liệu sau. Tôi đề xuất tên các thẻ tương ứng:*
>
> | STT | Tên thẻ đề xuất | Ý nghĩa trường | Giá trị mẫu |
> |---|---|---|---|
> | 1 | `<ten_don_vi_mua>` | Tên đơn vị mua | PHÒNG KINH TẾ XÃ KÉP |
> | 2 | `<ma_so_thue_mua>` | Mã số thuế / MST | 2401028292-003 |
> | 3 | `<dia_chi_mua>` | Địa chỉ người mua | Xã Kép, Tỉnh Bắc Ninh |
> | 4 | `<danh_sach_hang_hoa>` | Bảng hàng hóa | Danh sách các mặt hàng đã mua |
> | ... | ... | ... | ... |
>
> **Bạn có muốn đổi tên thẻ nào hoặc loại bỏ bớt trường nào không?**
> Hãy cho tôi biết tên mới bạn muốn gán, hoặc xác nhận nếu bạn hài lòng để tôi xuất file nhé!"*

### Bước 3: Tiếp nhận phản hồi từ người dùng
- **Nếu người dùng đồng ý**: Tiến hành xuất file với schema mặc định.
- **Nếu người dùng muốn đổi tên hoặc bỏ bớt trường**: Tạo dictionary mapping tương ứng:
  `{"ten_don_vi_mua": "company_name", "ma_so_thue_mua": "tax_id", "truong_khong_can": None}`

### Bước 4: Thực thi xuất file & Báo cáo kết quả
Thực thi script kèm tham số `--output` (script tự động tạo cả `.xml`, `.json` và `.xlsx` cùng tên):
```powershell
python "c:\Users\nguye\Downloads\KhoaHocAIQNetT09-2026\PdfToXml\run_skill.py" `
    -i "<đường_dẫn_pdf_hoặc_thư_mục>" `
    -o "<đường_dẫn_file_xuat.xml>"
```

---

## 3. Danh mục Tham số Lệnh CLI

| Tham số | Cờ lệnh ngắn | Bắt buộc | Mặc định | Mô tả |
| :--- | :---: | :---: | :--- | :--- |
| `--input` | `-i` | **Có** | - | Đường dẫn tới 1 file PDF hoặc 1 thư mục chứa nhiều file PDF. |
| `--output` | `-o` | Không | Cùng thư mục input | Đường dẫn file kết quả (tự động sinh ra cả .xml, .json, .xlsx cùng tên). |
| `--preview` | `-p` | Không | False | Chỉ quét và hiển thị JSON các trường phát hiện được, không tạo file. |
| `--mapping` | `-m` | Không | `{}` | Chuỗi JSON hoặc đường dẫn file `.json` ánh xạ đổi tên trường. |
| `--interactive`| `-t` | Không | False | Bật chế độ hỏi đổi tên trường trực tiếp trên dòng lệnh terminal. |
| `--root-tag` | - | Không | `records` | Tùy biến tên thẻ gốc XML. |
| `--item-tag` | - | Không | `item` | Tùy biến tên thẻ từng bản ghi. |
| `--include-raw`| - | Không | False | Lưu toàn bộ nội dung text thô vào thẻ `<raw_content>`. |
