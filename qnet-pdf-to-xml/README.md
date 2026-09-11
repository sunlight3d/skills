# QNet PDF to XML

Thư mục công cụ chuyển đổi dữ liệu từ 1 file PDF hoặc thư mục chứa nhiều file PDF sang file XML tổng hợp.

## Các tệp trong thư mục:
- `pdf_to_xml.py`: Module xử lý trích xuất văn bản (PyMuPDF + RapidOCR fallback), nhận diện cặp trường/thông tin và định dạng XML.
- `run_skill.py`: File khởi chạy nhanh script chuyển đổi.

## Cách sử dụng

### 1. Xem trước danh sách trường được AI tự động nhận diện:
```powershell
python run_skill.py -i "<đường_dẫn_file_pdf_hoặc_thư_mục>" --preview
```

### 2. Chuyển đổi sang file XML (giữ nguyên tên trường mặc định):
```powershell
python run_skill.py -i "<đường_dẫn_file_pdf_hoặc_thư_mục>" -o "output.xml"
```

### 3. Đổi tên thẻ XML theo yêu cầu tùy biến:
```powershell
python run_skill.py -i "<đường_dẫn_pdf>" -o "output.xml" -m '{"ten_doanh_nghiep_vn": "company_name", "ma_so_thue": "tax_id"}'
```

### 4. Chế độ hỏi tương tác đổi tên trực tiếp trên Terminal:
```powershell
python run_skill.py -i "<đường_dẫn_pdf>" -o "output.xml" --interactive
```
