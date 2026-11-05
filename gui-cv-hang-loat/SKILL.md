---
name: gui-cv-hang-loat
description: "Tự động tìm kiếm các đơn vị đào tạo AI, lập trình, phân tích dữ liệu, tạo báo cáo động trên Google, Facebook, LinkedIn... Lọc bỏ các đơn vị đối tác thân thiết (Cecomtech, NetPro, Qnet, VietIS, Aptech), xuất danh sách 10 đơn vị mới nhất và hiển thị bảng xem trước (preview) để người dùng duyệt (Human-in-the-loop). Sau khi được phê duyệt, tự động gửi email hợp tác giảng dạy qua tài khoản Gmail trên Chrome và lưu vết lịch sử chống trùng lặp."
---

# Gửi CV Hàng Loạt: Tìm Kiếm Đơn Vị Đào Tạo & Gửi Email Hợp Tác

## 1. Giới thiệu tổng quan
Skill **`gui-cv-hang-loat`** là trợ lý tự động hóa chuyên biệt phục vụ công tác phát triển đối tác đào tạo cho **Thầy Nguyễn Đức Hoàng**:
- **Mục tiêu**: Hàng ngày tìm kiếm các học viện, trung tâm công nghệ, viện đào tạo hoặc doanh nghiệp EdTech có nhu cầu đào tạo/tuyển dụng giảng viên về **Trí tuệ nhân tạo (AI)**, **Lập trình phần mềm (Java, Python, Full-stack, Mobile)**, **Phân tích dữ liệu (Data Analytics)** và **Tạo báo cáo động (Power BI, Dashboard)**.
- **Quy mô xử lý**: Mỗi đợt thực hiện **tìm 10 đơn vị mới** và **soạn thảo/gửi 10 email hợp tác**.
- **Cơ chế gửi thư an toàn**: Tương tác trực tiếp qua AppleScript với tài khoản Gmail (`sunlight4d@gmail.com`) đang đăng nhập sẵn trên Google Chrome, bảo đảm tỷ lệ vào Inbox cao nhất và không lo lỗi xác thực SMTP.

---

## 2. Các nguyên tắc bắt buộc (Safety & Policies)

### ⚠️ A. Chốt chặn phê duyệt (Human-in-the-loop)
- **TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ Ý GỬI EMAIL** khi chưa có sự xác nhận rõ ràng từ người dùng.
- Khi Agent hoặc người dùng kích hoạt skill:
  1. Luôn chạy ở chế độ **`preview`** trước.
  2. Hiển thị bảng tổng hợp 10 đơn vị gồm: Tên đơn vị, Email, Website, Thế mạnh, Tiêu đề thư và Trích đoạn thư mẫu.
  3. Dừng lại, hỏi ý kiến người dùng và chỉ gửi khi nhận được phản hồi đồng ý (ví dụ: *"Gửi"*, *"Đồng ý"*, *"OK"*, *"Gửi đi"*).

### 🚫 B. Danh sách loại trừ nghiêm ngặt (Blacklist)
Hệ thống tự động bỏ qua và **tuyệt đối không gửi email** đến các đơn vị sau:
- **Cecomtech** (`cecomtech.com.vn`, `cecomtech.vn`)
- **NetPro** (`netpro.com.vn`, `netpro.vn`)
- **Qnet** (`qnet.vn`)
- **VietIS** (`vietis.com.vn`)
- **Aptech / Aprotrain** (`aptech.vn`, `aprotrain.com`)
- **SmartPro** (`smartpro.vn`)
*(Lý do: Đây là các đơn vị đối tác chiến lược mà Thầy Hoàng đã và đang giảng dạy).*

### 🛡️ C. Chống gửi trùng lặp (Zero Duplicates)
- Mọi email đã gửi được ghi nhận tức thì vào `history.json` kèm ngày giờ (ISO timestamp).
- Trước khi đề xuất 10 đơn vị mới, hệ thống tự động đối chiếu Email, Domain và Tên đơn vị với `history.json`. Một đơn vị đã liên hệ sẽ không bao giờ bị gửi lại.

---

## 3. Cấu trúc thư mục của Skill
```
/Volumes/data/code/skills/gui-cv-hang-loat/
├── SKILL.md                  # Hướng dẫn toàn diện cho Agent & User
├── gui_cv_assistant.py       # Core script xử lý logic, lọc blacklist, gửi mail Chrome
├── blacklist.json            # Danh sách từ khóa, domain, email cấm
├── database_registry.json    # Kho dữ liệu 40+ học viện/trung tâm CNTT uy tín tại VN
├── history.json              # Nhật ký các email và đơn vị đã gửi thành công
├── templates/
│   └── email_template.txt    # Mẫu email hợp tác giảng dạy chuyên nghiệp
└── run.sh                    # Phím tắt CLI chạy nhanh với bash
```

---

## 4. Hồ sơ giảng viên sử dụng trong Email
- **Giảng viên**: Nguyễn Đức Hoàng
- **Chuyên môn**: Chuyên gia Phần mềm | Data Analyst & Giảng viên Công nghệ (12+ năm kinh nghiệm phần mềm, 8+ năm giảng dạy).
- **Email gửi**: `sunlight4d@gmail.com`
- **Hồ sơ năng lực (CV trực tuyến)**: `https://docs.google.com/document/d/1OjFtASPKX7krqgNnG-dKLMoQ2r2UMsf9XOHzKoCg-vQ/edit?tab=t.0`
- **Kênh YouTube bài giảng**: `https://www.youtube.com/nguyenduchoang`

---

## 5. Hướng dẫn vận hành cho AI Agent

Khi người dùng yêu cầu: *"Tìm 10 đơn vị đào tạo để gửi CV"*, *"Gửi email hợp tác giảng dạy cho các trung tâm"*, hoặc gọi lệnh liên quan đến skill `gui-cv-hang-loat`:

### Bước 1: Xem trước danh sách 10 đơn vị (Preview)
Chạy lệnh preview:
```bash
python3 /Volumes/data/code/skills/gui-cv-hang-loat/gui_cv_assistant.py --action preview --count 10
```

### Bước 2: Báo cáo danh sách và chờ người dùng duyệt
Agent hiển thị bảng 10 đơn vị dưới dạng Markdown trong chat:
| STT | Đơn vị đào tạo | Email liên hệ | Lĩnh vực trọng tâm | Website |
|---|---|---|---|---|
| 01 | Datapot Analytics | contact@datapot.vn | Phân tích dữ liệu, Power BI | https://datapot.vn |
| ... | ... | ... | ... | ... |

Và đưa ra thông điệp xác nhận:
> *"Em đã lọc và chuẩn bị xong danh sách 10 đơn vị đào tạo tiềm năng mới nhất (đã loại trừ Cecomtech, NetPro, Qnet, VietIS, Aptech và các đơn vị đã gửi trước đây). Anh kiểm tra giúp em xem danh sách này đã ổn chưa để em tiến hành gửi nhé!"*

### Bước 3: Thực hiện gửi khi có xác nhận (Send with Confirmation)
Khi và chỉ khi người dùng trả lời đồng ý (*"Gửi đi"*, *"OK"*, *"Đồng ý"*...), Agent mới thực thi lệnh gửi:
```bash
python3 /Volumes/data/code/skills/gui-cv-hang-loat/gui_cv_assistant.py --action send --count 10 --confirm
```

### Bước 4: Kiểm tra trạng thái và báo cáo
Sau khi gửi xong, kiểm tra lại trạng thái:
```bash
python3 /Volumes/data/code/skills/gui-cv-hang-loat/gui_cv_assistant.py --action status
```
Báo cáo cho người dùng số lượng email đã gửi thành công và đường dẫn lịch sử.

---

## 6. Các lệnh CLI hữu ích khác
- **Thêm đơn vị mới thủ công**:
  ```bash
  python3 /Volumes/data/code/skills/gui-cv-hang-loat/gui_cv_assistant.py --action add-target \
    --name "Học viện AI Mới" \
    --email "hr@aimoi.vn" \
    --website "https://aimoi.vn"
  ```
- **Xem tiến độ và lịch sử gửi**:
  ```bash
  python3 /Volumes/data/code/skills/gui-cv-hang-loat/gui_cv_assistant.py --action status
  ```
- **Chạy nhanh bằng bash script**:
  ```bash
  ./run.sh preview   # Xem trước 10 đơn vị
  ./run.sh send      # Hỏi xác nhận trước khi gửi thật
  ./run.sh status    # Xem lịch sử
  ```
