---
name: pptx-insert-slides
description: >-
  Chèn các slide mới vào file PowerPoint (.pptx) tại vị trí trang chỉ định. Các slide được chèn hoàn toàn là các đối tượng gốc (native shapes & text) có thể chỉnh sửa trực tiếp (editable) trong Microsoft PowerPoint, màu sắc đồng bộ chuẩn nhận diện bài giảng/công nghệ (#004C7E, #0077B6), font chữ tối thiểu 22pt, và câu chữ cô đọng súc tích không bị tràn khung.
---

# PPTX Insert Slides (Native & Editable)

## 📌 Tổng quan (Overview)

Skill này tự động tạo và chèn các trang trình chiếu mới vào tệp PowerPoint (`.pptx`) hiện có tại bất kỳ vị trí trang nào mong muốn (`--after-slide`).

### ⭐ Các tiêu chuẩn bắt buộc được đảm bảo:
1. **100% Chỉnh sửa được (Fully Editable)**: Slide được dựng hoàn toàn bằng đối tượng gốc của PowerPoint (`Shape`, `Rounded Rectangle`, `TextBox`, `TextFrame`). **Tuyệt đối không dùng ảnh chụp** để người dùng có thể nhấp chuột sửa chữ, đổi màu, kéo thả trực tiếp trên Microsoft PowerPoint.
2. **Quy chuẩn Font chữ $\ge$ 22pt**: Toàn bộ nội dung diễn giải, nhãn thẻ, ghi chú đều có kích thước tối thiểu `22pt`. Tiêu đề thẻ `24pt - 26pt`, tiêu đề slide `34pt - 36pt`. Sử dụng font chuẩn `Segoe UI` (hỗ trợ hoàn hảo tiếng Việt có dấu, sắc nét trên Windows) hoặc `Arial` / `Montserrat`.
3. **Màu sắc đồng bộ nhận diện**: Hệ màu công nghệ cao cấp:
   - Xanh tiêu đề chính: `#004C7E`
   - Xanh điểm nhấn / category: `#0077B6`
   - Màu cảnh báo / nguy hiểm: `#DC2626`
   - Màu trạng thái / cam: `#EA580C`
   - Màu thành công / xanh lá: `#15803D`
   - Nền thẻ bo góc sáng: `#F8FAFC`, `#F0F7FF`, `#FEF2F2`, `#FFF7ED`
4. **Bố cục cô đọng (Concise & Clean)**: Thiết kế dạng thẻ (Card-based UI) phân tách rõ ràng, gạch đầu dòng súc tích, in đậm từ khóa trọng tâm để bài giảng trực quan, không bị tràn viền (overflow).

---

## 🚀 Hướng dẫn Sử dụng (Quick Start)

### 1. Gọi lệnh qua CLI

```bash
# Chèn nội dung từ file JSON vào sau slide số 10
python pptx_insert_slides.py "duong/dan/bai_giang.pptx" --after-slide 10 --content "slides_data.json"

# Chỉ định file đầu ra riêng (không ghi đè file gốc)
python pptx_insert_slides.py "bai_giang.pptx" --after-slide 10 --content "slides_data.json" --output "bai_giang_moi.pptx"

# Truyền trực tiếp chuỗi JSON qua CLI
python pptx_insert_slides.py "bai_giang.pptx" --after-slide 5 --json-str '[{"category": "BẢO MẬT", "title": "TIÊU ĐỀ", "layout": "2_column", ...}]'
```

*Lưu ý: Khi ghi đè file gốc, script tự động tạo file sao lưu `.bak` an toàn.*

---

## 📐 Các Bố cục Hỗ trợ (Supported Layouts)

### 1. `2_column` (Song song / So sánh 2 bên + Thẻ tổng kết đáy)
Rất phù hợp để giải thích 2 khái niệm đối chiếu (ví dụ: `SYN` vs `ACK`, `TCP` vs `UDP`, `MAC` vs `IP`):
```json
{
  "category": "TẦNG GIAO VẬN — CƠ CHẾ TIN CẬY",
  "title": "Ý NGHĨA CỜ SYN & ACK",
  "layout": "2_column",
  "left_card": {
    "badge": "⚡ CỜ KHỞI TẠO",
    "title": "SYN = Synchronize",
    "border_color": "#0077B6",
    "bg_color": "#F8FAFC",
    "items": [
      {"label": "Ý nghĩa: ", "text": "Đồng bộ số thứ tự byte gói tin ban đầu."},
      {"label": "Nhiệm vụ: ", "text": "Thỏa thuận mốc đếm SEQ = X.", "highlight": "SEQ = X"}
    ]
  },
  "right_card": {
    "badge": "✓ CỜ BÁO NHẬN",
    "title": "ACK = Acknowledgment",
    "border_color": "#15803D",
    "bg_color": "#F8FAFC",
    "items": [
      {"label": "Ý nghĩa: ", "text": "Xác nhận đã nhận gói an toàn."},
      {"label": "Nhiệm vụ: ", "text": "Báo số tiếp theo: ACK = SEQ + 1.", "highlight": "ACK = SEQ + 1"}
    ]
  },
  "bottom_card": {
    "title": "TẠI SAO CẦN BẮT TAY ĐỦ 3 BƯỚC?",
    "border_color": "#93C5FD",
    "bg_color": "#F0F7FF",
    "items": [
      "✦ Cả 2 bên đều cần gửi SYN và gửi ACK (Song công Full-Duplex).",
      "✦ 3 bước là số gói tối thiểu về mặt toán học để xác nhận thông suốt cả 2 chiều."
    ]
  }
}
```

---

### 2. `grid_2x2` (Lưới 4 thẻ tứ trụ)
Rất phù hợp để phân loại 4 nhóm tính chất, 4 cờ điều khiển, hoặc 4 kịch bản an ninh mạng:
```json
{
  "category": "PHÂN TÍCH GÓI TIN & AN NINH MẠNG",
  "title": "BỘ CỜ TCP FLAGS & GÓC NHÌN BẢO MẬT",
  "layout": "grid_2x2",
  "cards": [
    {
      "badge": "⚠️ SYN & ACK",
      "title": "Tấn công SYN Flood (DoS)",
      "border_color": "#DC2626",
      "bg_color": "#FEF2F2",
      "items": [
        {"label": "• Nguy cơ: ", "text": "Gửi SYN giả nhưng không gửi ACK cuối làm tràn hàng đợi Backlog Queue.", "highlight": "không gửi ACK cuối"},
        {"label": "• Phòng thủ: ", "text": "Bật tính năng SYN Cookies.", "highlight": "SYN Cookies"}
      ]
    },
    {
      "badge": "🛑 FIN & RST",
      "title": "Đóng kết nối vs. Ngắt khẩn cấp",
      "border_color": "#EA580C",
      "bg_color": "#FFF7ED",
      "items": [
        {"label": "• FIN: ", "text": "Đóng kết nối hòa bình sau khi truyền xong."},
        {"label": "• RST: ", "text": "Ngắt khẩn cấp do Port đóng hoặc Firewall chèn cờ ngắt mã độc.", "highlight": "Firewall chèn cờ"}
      ]
    },
    {
      "badge": "🚀 PSH & URG",
      "title": "Bỏ qua bộ đệm (Buffer Bypass)",
      "border_color": "#0284C7",
      "bg_color": "#F0F9FF",
      "items": [
        {"label": "• PSH: ", "text": "Đẩy dữ liệu lên app ngay (SSH Terminal, Chat realtime)."},
        {"label": "• URG: ", "text": "Xử lý ưu tiên dữ liệu khẩn cấp như Ctrl + C.", "highlight": "Ctrl + C"}
      ]
    },
    {
      "badge": "🕵️ TRINH SÁT",
      "title": "Quét cổng tàng hình (nmap -sS)",
      "border_color": "#334155",
      "bg_color": "#F8FAFC",
      "items": [
        {"label": "• Cơ chế: ", "text": "Gửi SYN ➔ nhận SYN-ACK ➔ gửi RST ngắt luôn.", "highlight": "RST"},
        {"label": "• Tàng hình: ", "text": "Do chưa bao giờ gửi ACK, máy chủ không ghi nhận log đăng nhập!", "highlight": "không ghi nhận log"}
      ]
    }
  ]
}
```

---

### 3. `stacked_rows` (Hàng ngang xếp tầng - 3 đến 4 hàng)
Dùng cho quy trình từng bước, mốc thời gian, hoặc danh sách tính năng theo hàng ngang.

---

## 🛠️ Gọi từ mã nguồn Python (Python API)

```python
from pptx_insert_slides import insert_slides

insert_slides(
    pptx_path=r"C:\path\to\presentation.pptx",
    after_slide=10,
    slides_data=[slide1_dict, slide2_dict],
    output_path=r"C:\path\to\output.pptx",
    font_name="Segoe UI"
)
```

---

## ⚙️ Yêu cầu môi trường (Requirements)
* Python 3.8+
* Thư viện `python-pptx`:
  ```bash
  pip install python-pptx
  ```
