---
name: funix-cham-bai-sinh-vien
description: Tự động kết nối Portal FUNiX trên trình duyệt (Vivaldi, Chrome, Edge), bóc tách link bài làm học viên, giải nén và đánh giá chi tiết (mã nguồn hoặc lời giải Toán/Giải tích), sau đó tự động điền điểm từng tiêu chí, nhận xét chi tiết và nhận xét chung vào form phiếu chấm (fx.asm.marksheet).
---

# Tên Skill: Chấm bài sinh viên FUNiX (Portal FUNiX Automator)

## 1. Mục Đích & Phạm Vi
Skill này tự động hóa toàn bộ quy trình chấm bài Assignment/Lab của sinh viên FUNiX:
1. Kết nối trực tiếp vào giao diện Portal FUNiX đang mở trên trình duyệt (Vivaldi, Chrome, Edge).
2. Lấy link bài nộp từ trường **Link file** trên form phiếu chấm (`fx.asm.marksheet`), tự động tải file bài làm về máy.
3. Giải nén an toàn và dọn dẹp file nén ngay lập tức.
4. Kiểm tra, đối chiếu bài làm với các tiêu chí trong bảng điểm:
   - **Bài thi Lập trình (IT)**: Rà soát logic, cú pháp, kiến trúc code, bảo mật, bắt lỗi cú pháp hoặc code lai tạp.
   - **Bài thi Toán / Giải tích (MAC101x,...)**: Kiểm tra từng bước biến đổi đại số, vi phân/tích phân, điều kiện xác định ($x \ne 0$), giới hạn, đạo hàm kiểm tra lại, và kết quả cuối cùng.
5. Tự động tương tác với form Odoo: cuộn từng dòng tiêu chí, chọn điểm (Scale 0-5), nhập nhận xét chi tiết từng tiêu chí (tối thiểu 10 ký tự), và nhập **Nhận xét chung** nghiêm khắc, khách quan, mang tính xây dựng cao.

---

## 2. Trình Tự Thực Hiện (Workflow Chi Tiết)

```
[Portal FUNiX Tab] ──> [Switch Desktop WinSta0\default] ──> [Extract Link File]
        │                                                               │
        ▼                                                               ▼
[Fill Form Odoo] <── [Code/Math Rigorous Review] <── [Download & Unzip Sub]
(Scores + Comments)
```

### Bước 1: Kết nối Trình duyệt & Desktop Isolation
Trong môi trường Antigravity trên Windows, tiến trình Agent có thể chạy trong một Desktop ảo tách biệt (`exebox-...`). Để thao tác được với cửa sổ trình duyệt (Vivaldi, Chrome...) của người dùng:
1. Gọi API Windows chuyển `ThreadDesktop` sang `default`:
   ```python
   import win32service
   desk = win32service.OpenDesktop('default', 0, False, 0x01FF)
   desk.SetThreadDesktop()
   ```
2. Kích hoạt và đưa cửa sổ trình duyệt chứa tab Portal FUNiX lên Foreground:
   ```python
   import uiautomation as auto
   win = auto.WindowControl(searchDepth=1, ClassName='Chrome_WidgetWin_1', SubName='Portal FUNiX')
   # Sử dụng AttachThreadInput để SetForegroundWindow tuyệt đối tin cậy
   ```

### Bước 2: Bóc tách Link bài làm & Tải về
1. Tìm thẻ `HyperlinkControl` chứa URL tải bài nộp (thường là link Google Cloud Storage / Google Drive):
   - Domain: `storage.googleapis.com/portal-feedback.appspot.com/...`
2. Sử dụng `urllib.request.urlretrieve` tải file về thư mục làm việc cục bộ.
3. Giải nén bằng `zipfile` hoặc công cụ dòng lệnh (`unzip`, `7z`).
4. **BẮT BUỘC:** Xóa ngay file nén gốc (`.zip`, `.rar`) sau khi giải nén xong để dọn dẹp tài nguyên.

### Bước 3: Đọc và Đánh giá Mã nguồn / Lời giải
1. **Nếu là bài thi Toán / Giải tích (PDF / Word):**
   - Dùng `pymupdf` (PyMuPDF) render các trang thành ảnh PNG độ nét cao (DPI 150) hoặc trích xuất văn bản/công thức.
   - Dùng công cụ `read_file` để kiểm tra trực quan từng bước chứng minh, hình vẽ và công thức toán.
   - Soát lỗi: Điều kiện xác định, dấu âm/dương khi khai căn hay đổi cận, tính chuẩn xác của giới hạn khi $t \to \infty$ hoặc $t \to x_0^\pm$.
2. **Nếu là bài thi Lập trình (Java, C++, Python, Web...):**
   - Đọc từng file mã nguồn, phân tích cú pháp và kiến trúc.
   - Bắt lỗi nghiêm ngặt với các lỗi cú pháp, code lai tạp (nhầm lẫn giữa các ngôn ngữ), không tuân thủ coding convention, thiếu xử lý ngoại lệ.

### Bước 4: Tự Động Điền Điểm & Nhận Xét Từng Tiêu Chí
Trên giao diện Odoo `fx.asm.marksheet`, bảng điểm là một `TableControl` / `DataGridControl`:
- Cột 0: Tên tiêu chí.
- Cột 1: Mô tả / Câu hỏi.
- Cột 2: Điểm tham chiếu (Trọng số: 1.00, 2.00...).
- Cột 4: Phổ điểm (Scale 0-5).
- Cột 5: **Điểm số** (`ComboBoxControl`).
- Cột 6: Điểm quy đổi (Tự động tính: $\text{Điểm số} \times \frac{\text{Tham chiếu}}{5}$).
- Cột 7: **Nhận xét** (`EditControl`, yêu cầu tối thiểu 10 ký tự).

**Quy tắc điều khiển UIAutomation trên Odoo:**
1. Cuộn dòng vào khung nhìn: `row.GetScrollItemPattern().ScrollIntoView()`.
2. Click vào góc trên của ô Điểm số (`cy = rect.top + 25`) để kích hoạt chế độ chỉnh sửa dòng của Odoo.
3. Chọn điểm trong `ComboBoxControl`: gửi ký tự điểm (ví dụ: `5`) + `{Enter}`.
4. Chuyển sang ô Nhận xét: gửi phím `{Tab}`, dán nhận xét chi tiết từ Clipboard bằng `{Ctrl}a{Ctrl}v`.
5. Tiếp tục chuyển sang dòng tiếp theo bằng phím `{Tab}`.

### Bước 5: Điền Nhận Xét Chung (Overall Evaluation)
1. Cuộn trang xuống cuối bằng phím `{PageDown}` trên vùng webview.
2. Tìm trường `EditControl` có `AutomationId="overall_evaluation"`.
3. Nhập nhận xét tổng quan bài làm:
   - Tóm tắt kết quả đạt được.
   - Nêu rõ các ưu điểm nổi bật (trình bày bài bản, có bước tự kiểm tra lại bằng đạo hàm/quy đồng).
   - **Nhắc nhở rèn luyện (Bắt buộc):** Giữ thái độ nghiêm túc, khách quan, không khen ngợi thái quá. Nêu trực diện các chi tiết cần hoàn thiện (như bổ sung điều kiện triệt tiêu mẫu, test kỹ code trước khi nộp) để sinh viên không chủ quan.

### Bước 6: Đối Chiếu Tổng Điểm & Báo Cáo
- Kiểm tra lại các ô `QuyDoi` của từng dòng, đảm bảo tổng điểm quy đổi khớp với tổng điểm tham chiếu (ví dụ 10.00 / 10.00).
- Hiển thị bảng tổng hợp điểm và nhận xét chi tiết trong chat để người dùng kiểm tra trước khi bấm **Lưu** hoặc **Nộp phiếu chấm**.

---

## 3. Quy Tắc Bắt Buộc (Strict Constraints)
- **Dọn dẹp:** LUÔN xóa file nén (.zip, .rar) sau khi đã giải nén xong.
- **Tối thiểu 10 ký tự:** Nhận xét ở mỗi tiêu chí trên Odoo bắt buộc phải trên 10 ký tự, không được để trống.
- **Thái độ chấm:** Luôn nghiêm khắc, chuẩn mực sư phạm, mang tính xây dựng cao.
- **An toàn giao diện:** Không tự ý bấm nút "Nộp phiếu chấm" cuối cùng nếu chưa có sự đồng ý của Mentor/Người dùng; để người dùng rà soát lại trên trình duyệt rồi tự xác nhận nộp.
