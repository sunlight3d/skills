---
name: qnet-bao-cao-bao-mat-hang-thang
description: "Tự động đọc, phân tích và trích xuất dữ liệu từ thư mục chứa các tệp Excel báo cáo an ninh bảo mật hàng tháng (báo cáo phụ lục tấn công mạng, virus, mã độc, botnet CnC, tài khoản đăng nhập sai, tồn đọng bản vá lỗi) và khởi tạo ứng dụng Web Dashboard trực quan chạy trên localhost với biểu đồ Plotly đa màu sắc, bộ lọc dropdown tỉnh thành và bộ chọn khoảng thời gian From-To phục vụ lãnh đạo."
---

# QNet Báo Cáo An Ninh Bảo Mật Hàng Tháng (Security Executive Dashboard)

## 1. Tổng quan & Khả năng

Kỹ năng **`qnet-bao-cao-bao-mat-hang-thang`** tự động hóa hoàn toàn quy trình xử lý dữ liệu giám sát An toàn thông tin (ATTT / SOC) định kỳ từ các tệp Excel đầu vào, phân tích hàng trăm nghìn bản ghi sự cố mạng và chuyển hóa thành **Web Dashboard trực quan điều hành** phục vụ lãnh đạo cơ quan (non-technical) và các chuyên viên kỹ thuật.

### Đặc điểm nổi bật:
- **Đầu vào**: Đường dẫn đến **1 thư mục chứa các file Excel** báo cáo an ninh mạng (ví dụ: `BC An ninh bảo mật PhuLuc...xlsx`, `DATA ATTT...xlsx`).
- **Đầu ra**: 
  - **Web Dashboard tương tác (Streamlit + Plotly)** chạy trực tiếp trên `localhost` (hoặc mở rộng mạng LAN / VPS).
  - Tệp dữ liệu sạch chuẩn hóa: `dashboard_data.json`.
  - Tệp báo cáo HTML độc lập: `BaoCao_ATTT.html` (mở xem ngay offline không cần server).
- **Tối ưu riêng cho Lãnh đạo (Non-technical Executive)**:
  - Khối **Tóm tắt điều hành (Executive Summary)** bằng ngôn ngữ nghiệp vụ rõ ràng, giải thích nguy cơ và đưa ra 3 khuyến nghị hành động khẩn cấp.
  - **4 Thẻ chỉ số KPI lớn** với màu sắc nổi bật (Gradient Red, Blue, Purple, Amber).
  - **5 Biểu đồ trực quan đa màu sắc (Plotly)**: Donut phân bổ nguy cơ, Cột đỏ cảnh báo Botnet CnC, Cột ngang Top IP nguồn tấn công, Cột tài khoản bị dò quét mật khẩu, Cột phân tích lỗ hổng bản vá.
- **Bộ lọc tương tác linh hoạt**:
  - **Hộp chọn Dropdown List Tỉnh/Thành phố**: Xem nhanh số liệu và danh sách máy trạm vi phạm theo từng địa phương.
  - **Bộ chọn khoảng thời gian (From - To)**: Mặc định từ ngày này năm trước đến hôm nay (1 năm).
  - **Tìm kiếm tức thì (Instant Search)** theo IP máy trạm (`10.x.x.x`), IP nguồn, tài khoản và nút xuất dữ liệu **CSV**.

---

## 2. Quy trình Thực thi Chuẩn cho AI Agent

Khi người dùng yêu cầu phân tích thư mục chứa các file Excel báo cáo an ninh mạng, AI Agent thực hiện theo quy trình 3 bước sau:

```
[Thư mục chứa các file Excel ATTT]
               ↓
[Bước 1: Trích xuất & Tổng hợp dữ liệu sang JSON]
               ↓
[Bước 2: Khởi tạo Web Dashboard Streamlit trên Localhost]
               ↓
[Bước 3: Cung cấp liên kết Web và hướng dẫn xem báo cáo cho người dùng]
```

### Bước 1: Trích xuất dữ liệu từ thư mục Excel
Chạy lệnh trích xuất dữ liệu:
```powershell
python "C:\code\skills\qnet-bao-cao-bao-mat-hang-thang\scripts\extract_data.py" `
    --input-dir "<đường_dẫn_thư_mục_chứa_excel>"
```

### Bước 2: Khởi động Web Dashboard trên Localhost
Khởi chạy Streamlit Dashboard:
```powershell
streamlit run "C:\code\skills\qnet-bao-cao-bao-mat-hang-thang\scriptspp.py" `
    -- --data-dir "<đường_dẫn_thư_mục_chứa_excel>"
```
*(Hoặc chạy trực tiếp với tham số `--run-app` trong lệnh extract_data.py)*.

### Bước 3: Cung cấp liên kết cho người dùng
- Đường dẫn máy cục bộ: `http://localhost:8501`
- Đường dẫn mạng LAN (nếu cần chia sẻ): `http://<IP_LAN>:8501`

---

## 3. Cấu trúc Thư mục Skill

```
qnet-bao-cao-bao-mat-hang-thang/
├── SKILL.md                          # Tài liệu hướng dẫn sử dụng và workflow
├── requirements.txt                  # Các thư viện phụ thuộc
└── scripts/
    ├── extract_data.py               # Module phân tích & trích xuất dữ liệu Excel
    ├── app.py                        # Ứng dụng Web Dashboard (Streamlit + Plotly)
    ├── generate_standalone_html.py   # Trình tạo file HTML báo cáo độc lập
    └── run_dashboard.bat             # Kịch bản khởi động nhanh 1-click trên Windows
```

---

## 4. Danh mục Tham số Lệnh CLI (`extract_data.py`)

| Tham số | Cờ ngắn | Bắt buộc | Mặc định | Mô tả |
| :--- | :---: | :---: | :--- | :--- |
| `--input-dir` | `-i` | **Có** | - | Đường dẫn thư mục chứa các tệp Excel báo cáo bảo mật. |
| `--output-dir`| `-o` | Không | Cùng `input-dir` | Thư mục lưu tệp `dashboard_data.json` và `BaoCao_ATTT.html`. |
| `--run-app`   | `-r` | Không | False | Tự động khởi chạy Web Dashboard trên localhost ngay sau khi trích xuất. |
| `--port`      | `-p` | Không | 8501 | Cổng mạng cho Web Server. |

---

## 5. Hướng dẫn Triển khai Lên Máy Chủ / VPS

Nếu người dùng yêu cầu triển khai lên máy chủ VPS để xem qua Internet:
1. Copy thư mục mã nguồn và file dữ liệu lên VPS:
   ```bash
   scp -r scripts/ root@<IP_VPS>:/opt/dashboard_attt/
   ```
2. Cài đặt môi trường Python 3.11+ trên VPS và cài đặt `requirements.txt`.
3. Mở cổng tường lửa:
   ```bash
   firewall-cmd --add-port=8501/tcp --permanent && firewall-cmd --reload
   ```
4. Thiết lập Systemd Service `dashboard_attt.service` để tự động duy trì 24/7.
