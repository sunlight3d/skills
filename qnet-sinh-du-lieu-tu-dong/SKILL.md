---
name: qnet-sinh-du-lieu-tu-dong
description: "Đọc file template JSON mẫu, phân tích cấu trúc và ngữ nghĩa các trường (schema inference), sau đó tự động sinh dữ liệu mẫu theo số lượng yêu cầu (count) và các quy tắc ràng buộc (validation rules). Tối ưu chuẩn ngữ nghĩa tiếng Việt (Họ tên tiếng Việt tự nhiên, phòng ban doanh nghiệp, tiền lương, ngày tháng ISO, số điện thoại, email, địa chỉ). Xuất đồng thời định dạng JSON và CSV với 100% bản ghi đạt chuẩn validation."
---

# QNet Sinh Dữ Liệu Tự Động (Data Generator & Validator)

## 1. Tổng quan & Khả năng

Kỹ năng **`qnet-sinh-du-lieu-tu-dong`** giải quyết bài toán tạo dữ liệu giả lập (mock/test data) có cấu trúc từ bất kỳ tệp JSON mẫu nào. Hệ thống tự động phân tích ngữ nghĩa các trường dữ liệu, áp dụng các ràng buộc nghiệp vụ (validation rules) và sinh ra số lượng bản ghi mong muốn.

### Điểm nổi bật:
- **Tự động nhận diện Schema & Ngữ nghĩa (Semantic Inference)**:
  - Phân tích kiểu dữ liệu: `integer`, `float`, `string`, `datetime`, `date`, `boolean`, `list`, `dict`.
  - Nhận diện các trường thực tế: Họ tên tiếng Việt (`vietnamese_name`), phòng ban doanh nghiệp (`department`), chức vụ (`position`), lương/tiền tệ (`salary`), ngày giờ (`datetime`), email, số điện thoại, địa chỉ, mã số/ID.
- **Hỗ trợ Validation Rules đa dạng**:
  - `min` / `max`: Giới hạn khoảng giá trị số hoặc mốc thời gian.
  - `choices` / `enum`: Danh sách các giá trị hợp lệ được phép.
  - `unique`: Đảm bảo giá trị duy nhất (không trùng lặp) trên toàn bộ tập dữ liệu (VD: `id`, `code`, `email`).
  - `auto_increment`: Tự động tăng tuần tự theo bước nhảy (cho `id`).
  - `step`: Bước nhảy làm tròn số tiền (VD: bội số của 500.000 VNĐ).
  - `pattern` / `regex`: Định dạng chuỗi theo biểu thức chính quy.
  - `nullable` / `null_ratio`: Quy định trường có được phép rỗng không và xác suất rỗng.
- **Độc lập 100% (Zero-dependency)**:
  - Chạy thuần túy trên Python Standard Library, không phụ thuộc vào `faker` hay thư viện ngoài.
- **Định dạng xuất linh hoạt**:
  - Hỗ trợ xuất ra `.json` (UTF-8 thụt lề chuẩn) và `.csv` (mã hóa `utf-8-sig` hiển thị hoàn hảo trên Microsoft Excel tiếng Việt).

---

## 2. Quy trình Thực thi Chuẩn cho AI Agent

Khi người dùng yêu cầu sinh dữ liệu từ một file template JSON:

```
[Người dùng cung cấp template JSON & yêu cầu số lượng / validation]
                               ↓
[Bước 1: Phân tích cấu trúc template JSON]
                               ↓
[Bước 2: Xác định hoặc tạo bộ quy tắc Validation (nếu có yêu cầu riêng)]
                               ↓
[Bước 3: Thực thi lệnh sinh dữ liệu CLI]
                               ↓
[Bước 4: Kiểm tra kết quả & Báo cáo số lượng, mẫu dữ liệu, vị trí lưu file]
```

### Bước 1: Kiểm tra tệp template JSON
Xem nội dung tệp template mẫu của người dùng để xác định các trường có sẵn:
```powershell
python "C:\Users\nguye\.gemini\config\skills\qnet-sinh-du-lieu-tu-dong\run_skill.py" -t "<đường_dẫn_template.json>" --preview
```

### Bước 2: Chạy sinh dữ liệu
Chạy lệnh với số lượng bản ghi (`-n`) và đường dẫn file xuất (`-o`):

**Sinh file JSON:**
```powershell
python "C:\Users\nguye\.gemini\config\skills\qnet-sinh-du-lieu-tu-dong\run_skill.py" `
    -t "<đường_dẫn_template.json>" `
    -n 50 `
    -o "<đường_dẫn_file_xuat.json>"
```

**Sinh file CSV (hỗ trợ mở trực tiếp trên Excel):**
```powershell
python "C:\Users\nguye\.gemini\config\skills\qnet-sinh-du-lieu-tu-dong\run_skill.py" `
    -t "<đường_dẫn_template.json>" `
    -n 50 `
    -o "<đường_dẫn_file_xuat.csv>" `
    --format csv
```

**Sinh kèm file Validation Rules tùy chỉnh:**
```powershell
python "C:\Users\nguye\.gemini\config\skills\qnet-sinh-du-lieu-tu-dong\run_skill.py" `
    -t "<đường_dẫn_template.json>" `
    -n 100 `
    -r "<đường_dẫn_rules.json>" `
    -o "<đường_dẫn_file_xuat.json>"
```

---

## 3. Danh mục Tham số Lệnh CLI

| Tham số | Cờ ngắn | Mặc định | Mô tả |
| :--- | :---: | :--- | :--- |
| `--template` | `-t` | `template.json` | Đường dẫn tệp JSON mẫu (chứa 1 object hoặc mảng các object mẫu). |
| `--count` | `-n` | `10` | Số lượng bản ghi cần sinh. |
| `--rules` | `-r` | `None` | Đường dẫn file JSON cấu hình validation rules hoặc chuỗi JSON. |
| `--output` | `-o` | `generated_data.json` | Đường dẫn tệp lưu dữ liệu kết quả. |
| `--format` | `-f` | `json` | Định dạng file xuất (`json` hoặc `csv`). |
| `--preview` | `-p` | `False` | In xem trước cấu trúc schema và 3 bản ghi đầu tiên trên màn hình. |
| `--seed` | `-s` | `None` | Số nguyên seed ngẫu nhiên nhằm tái lập chính xác tập dữ liệu kiểm thử. |

---

## 4. Cấu trúc Cấu hình Validation Rules (Tùy chọn nâng cao)

Người dùng có thể tạo một file JSON chứa các quy tắc bổ sung hoặc ghi đè cho từng trường:

```json
{
  "id": {
    "unique": true,
    "auto_increment": true,
    "start": 1,
    "step": 1
  },
  "name": {
    "semantic": "vietnamese_name"
  },
  "department": {
    "choices": ["IT", "HR", "Kế toán", "Kinh doanh", "Marketing"]
  },
  "salary": {
    "min": 10000000,
    "max": 50000000,
    "step": 500000
  },
  "created_at": {
    "date_format": "%Y-%m-%dT%H:%M:%S",
    "start_date": "2026-01-01",
    "end_date": "2026-12-31"
  }
}
```
