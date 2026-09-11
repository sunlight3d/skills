# Module Sinh Dữ Liệu Tự Động (Data Generator & Validator)

Bộ công cụ sinh dữ liệu tự động tiếng Việt dựa trên file mẫu `template.json` và quy tắc kiểm tra ràng buộc `validation rules`.

---

## 1. Cấu trúc thư mục

```
SinhDuLieuTuDong/
├── template.json                # File template JSON mẫu của bạn
├── data_generator.py            # Core engine: phân tích schema, sinh dữ liệu tiếng Việt & validator
├── run_skill.py                 # CLI script thực thi chính
├── rules_schema.example.json    # File ví dụ cấu hình validation rules tùy chọn
├── generated_data.json          # File dữ liệu JSON kết quả sinh ra
├── test_export.csv              # File dữ liệu CSV kết quả mẫu
└── README.md                    # Tài liệu hướng dẫn sử dụng
```

---

## 2. Cách sử dụng nhanh qua CLI

### Sinh dữ liệu cơ bản từ `template.json`:
```powershell
python run_skill.py -t template.json -n 20 -o generated_data.json
```

### Sinh dữ liệu và xuất trực tiếp ra file Excel CSV:
```powershell
python run_skill.py -t template.json -n 50 -o nhan_vien.csv --format csv
```

### Sinh dữ liệu kèm quy tắc Validation tùy biến:
```powershell
python run_skill.py -t template.json -n 100 -r rules_schema.example.json -o nhan_vien_chuan.json
```

### Xem trước phân tích Schema trên màn hình terminal:
```powershell
python run_skill.py -t template.json --preview
```

---

## 3. Các tham số dòng lệnh chính

| Tham số | Cờ ngắn | Mặc định | Ý nghĩa |
| :--- | :---: | :--- | :--- |
| `--template` | `-t` | `template.json` | Đường dẫn tệp JSON mẫu. |
| `--count` | `-n` | `10` | Số lượng bản ghi cần tạo. |
| `--rules` | `-r` | `None` | Đường dẫn file JSON cấu hình validation rules hoặc chuỗi JSON. |
| `--output` | `-o` | `generated_data.json` | Tên file kết quả lưu ra. |
| `--format` | `-f` | `json` | Định dạng xuất: `json` hoặc `csv`. |
| `--preview` | `-p` | `False` | Bật chế độ xem trước dữ liệu và cấu trúc. |
| `--seed` | `-s` | `None` | Số nguyên seed ngẫu nhiên cho mục đích kiểm thử cố định. |

---

## 4. Tùy biến quy tắc Validation (`rules.json`)

Bạn có thể tạo một file cấu hình rules với các thuộc tính:
- `choices`: Mảng danh sách các giá trị được phép chọn (VD: `["IT", "HR", "Kế toán"]`).
- `min` / `max`: Giá trị tối thiểu và tối đa (cho số, lương, tuổi).
- `step`: Bước nhảy làm tròn (VD: `500000`).
- `unique`: `true` để đảm bảo không bản ghi nào trùng lặp trường này.
- `auto_increment`: `true` để số tự động tăng theo từng dòng.
- `date_format`: Định dạng chuỗi ngày tháng (VD: `"%Y-%m-%dT%H:%M:%S"`).
- `start_date` / `end_date`: Giới hạn mốc thời gian phát sinh (VD: `"2026-01-01"` đến `"2026-12-31"`).
