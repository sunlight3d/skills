---
name: make-notebook-lm-slides
description: "Tự động tạo slide trình chiếu PowerPoint (.pptx) chuyên nghiệp bằng Google NotebookLM từ danh sách các file Markdown (.md) và câu prompt tùy chỉnh. Tự động nạp từng nguồn đơn lẻ, mở Slide Deck, nhập prompt, chọn Tiếng Việt, tải các phần PPTX về và ghép thành bài thuyết trình hoàn chỉnh."
---

# Make NotebookLM Slides

## Tổng quan (Overview)
Skill này tự động hóa 100% quy trình tạo slide thuyết trình chuyên nghiệp từ tài liệu văn bản / giáo trình Markdown (`.md`) thông qua tính năng **Slide Deck** của **Google NotebookLM**:
1. Nhận đầu vào là **danh sách các file Markdown (.md)** và **câu prompt định hướng thiết kế slide**.
2. Kết nối trực tiếp vào trình duyệt (Opera, Chrome, Cốc Cốc, v.v.) qua giao thức **Playwright CDP** (Chrome DevTools Protocol - port 9222).
3. Tuần tự xử lý từng file Markdown:
   - Dọn sạch nguồn cũ (đảm bảo chỉ có duy nhất 1 nguồn tài liệu tại một thời điểm).
   - Thêm nội dung Markdown vào NotebookLM qua tính năng *Văn bản đã sao chép (Copied text)*.
   - Mở cửa sổ tùy chỉnh *Slide Deck*, chọn ngôn ngữ **Tiếng Việt**, điền câu prompt yêu cầu.
   - Kích hoạt tạo slide ngay (*Generate now*), theo dõi tiến trình sinh hình ảnh/nội dung.
   - Tự động bắt sự kiện tải xuống và lưu file `.pptx` về thư mục chỉ định.
4. Tự động ghép nối các phần slide rời rạc thành một file PowerPoint thuyết trình duy nhất (`merged_presentation.pptx` hoặc `buổi X.pptx`) giữ nguyên 100% bố cục và hình ảnh minh họa chất lượng cao.

---

## Khi nào kích hoạt Skill này (Triggers)
Kích hoạt skill này khi người dùng yêu cầu:
- "Tạo slide từ các file md bằng NotebookLM"
- "Lên NotebookLM tạo slide từ danh sách bài học / syllabus"
- "Tạo slide deck từ file text / markdown kèm prompt mầu sắc / font chữ"
- "Chạy batch tạo slide NotebookLM và ghép file pptx"
- Hoặc gọi trực tiếp: `/make-notebook-lm-slides`

---

## Đầu vào (Inputs) & Đầu ra (Outputs)

### Đầu vào (Inputs):
1. **Danh sách file Markdown (`files`)**: Danh sách các đường dẫn file `.md` cục bộ hoặc pattern glob (ví dụ: `mds/1.*.md`, `mds/7.1-*.md mds/7.2-*.md`).
2. **Câu prompt (`prompt`)**: Chuỗi văn bản chỉ định phong cách thiết kế, màu sắc, font chữ, bố cục cho slide.
   *Nếu người dùng không cung cấp prompt, sử dụng prompt mặc định chuẩn corporate:*
   ```text
   hãy tạo slides có nội dung như file text tôi gửi, toàn bộ nội dung slides bằng Tiếng Việt, thêm nhiều hình ảnh để minh họa. Mầu chữ title: #004C7E, nếu chữ mầu đen thì dùng mầu đen tuyền (#000000), slide nền chút sóng bồng bềnh mầu #004C7E và #0080C0, slide nền sáng. Dùng tối đa 2 loại Font chữ không chân Việt hóa: Montserrat / SVN-Gotham. Đảm bảo chữ tối trên nền sáng
   ```

### Đầu ra (Outputs):
- File PowerPoint tổng hợp hoàn chỉnh: `output.pptx` (chứa đầy đủ các slide của tất cả các bài được ghép lại).
- Các file PowerPoint từng phần: lưu trữ trong thư mục con `parts_dir` (mặc định: `slides_parts/` hoặc `slides/buoi_X/`).

---

## Hướng dẫn sử dụng cho Agent (Execution Guide)

### 1. Chuẩn bị môi trường & Trình duyệt
Skill sử dụng môi trường Python đã cài đặt `playwright` và `python-pptx`:
- **Python interpreter khuyến nghị:**
  `/Users/hoangnd/.gemini/config/skills/fb-group-anonymous-poster/.venv/bin/python3`
- **Trình duyệt:** Mở sẵn trình duyệt đã đăng nhập tài khoản Google có quyền truy cập NotebookLM (Opera, Chrome, v.v.). Trình duyệt cần được khởi động với cờ `--remote-debugging-port=9222` (script sẽ tự động khởi động lại nếu phát hiện chưa mở cổng CDP).

### 2. Cú pháp dòng lệnh (CLI Command)

Chạy script chính của skill:

```bash
/Users/hoangnd/.gemini/config/skills/fb-group-anonymous-poster/.venv/bin/python3 \
  "/Volumes/data/code/skills/make-notebook-lm-slides/scripts/notebooklm_slide_generator.py" \
  mds/7.1-*.md mds/7.2-*.md mds/7.3-*.md mds/7.4-*.md \
  --prompt "hãy tạo slides có nội dung như file text tôi gửi, toàn bộ nội dung slides bằng Tiếng Việt..." \
  --output "slides/buổi 7.pptx" \
  --parts-dir "slides/buoi_7" \
  --notebook-key "c470196d-afcb-4919-b639-82aff885e953"
```

#### Các tham số bổ sung:
- `--notebook-key <UUID>`: ID của Notebook trên URL (`https://notebook.google.com/notebook/<UUID>`).
- `--port <PORT>`: Cổng CDP (mặc định: `9222`).
- `--lang <LANGUAGE>`: Ngôn ngữ cho Slide Deck (mặc định: `'Tiếng Việt'`).
- `--force`: Ép buộc tạo lại ngay cả khi file pptx từng phần đã tồn tại trong thư mục `parts-dir`.
- `--no-merge`: Chỉ tạo các file PPTX thành phần, không ghép lại.

---

### 3. Tích hợp trực tiếp trong mã Python (Programmatic Usage)

```python
from scripts.notebooklm_slide_generator import process_markdown_list

files = [
    "mds/1.1-gioi-thieu.md",
    "mds/1.2-cai-dat.md",
    "mds/1.3-bien-va-kieu-du-lieu.md",
    "mds/1.4-vong-lap.md"
]
prompt = "hãy tạo slides có nội dung như file text tôi gửi..."
output_file = "slides/buổi 1.pptx"

final_pptx = process_markdown_list(
    files=files,
    output_path=output_file,
    prompt=prompt,
    parts_dir="slides/buoi_1",
    notebook_key="c470196d-afcb-4919-b639-82aff885e953",
    lang="Tiếng Việt"
)
print("Đã tạo xong:", final_pptx)
```

---

## Các chế độ hoạt động (Supported Drivers)

Skill hỗ trợ 2 chế độ tự động hóa linh hoạt:

### Chế độ 1: Playwright CDP (Khuyên dùng cho Opera / Cốc Cốc / Chromium độc lập)
- Script: `scripts/notebooklm_slide_generator.py`
- Kết nối trực tiếp vào trình duyệt qua cổng DevTools CDP (`--remote-debugging-port=9222`).
- Sử dụng Playwright API mạnh mẽ, tự động vượt qua mọi rào cản actionability, CDK overlay, và download interception.

### Chế độ 2: Google Chrome AppleScript + Base64 JS (Không cần khởi động lại Chrome)
- Script: `scripts/notebooklm_chrome_generator.py`
- Tự động tìm tab NotebookLM đang mở trong Google Chrome của người dùng, thực thi lệnh an toàn qua mã hóa Base64 mà không cần mở cờ `--remote-debugging-port`.
- Tự động bắt sự kiện chuột phức tạp (`PointerEvent`, `MouseEvent`), nhận diện file tải về tạm thời của Chrome (`.com.google.Chrome.*`) và chuyển thành `.pptx`.

---

## Cơ chế kỹ thuật chuyên sâu (Technical Architecture)

1. **Playwright CDP Direct Connection & AppleScript Base64 Bridge**:
   - Chế độ CDP: Sử dụng `connect_over_cdp("http://localhost:9222")` giải quyết triệt để vấn đề Opera chặn Apple Events.
   - Chế độ Chrome: Mã hóa Base64 toàn bộ chuỗi JavaScript thực thi qua AppleScript, loại bỏ 100% các lỗi escaping ký tự nháy kép hoặc dấu gạch chéo.

2. **Chính xác hóa phần tử Form & Kích hoạt Angular Reactive Forms**:
   - Ô tiêu đề trong dialog *Copied text* là một thẻ `<input class="title-input">` (không phải textarea).
   - Ô nội dung là `<textarea class="copied-text-input-textarea">`.
   - Sử dụng `document.execCommand('insertText')` hoặc `locator.fill()` để Angular cập nhật state của FormGroup và kích hoạt nút *Insert*.

3. **Tự động đóng Viewer & CDK Backdrop Overlays**:
   - Hàm `close_any_viewer()` tự động đóng các modal mở sẵn, click đóng dialog, bấm phím Escape ảo và giải phóng các lớp phủ `.cdk-overlay-backdrop` chắn chuột.
   - Đảm bảo thẻ nút `basic-create-artifact-button[data-create-button-type='8']` (Slide Deck) luôn xuất hiện trên giao diện Studio.

4. **Quản lý Giới hạn Tốc độ (Rate Limit Detection)**:
   - Script phát hiện khi tài khoản đạt hạn mức tạo nhanh hàng ngày (modal hiển thị nút *"Generate later"* thay vì *"Generate now"*).
   - Ném ngoại lệ `RuntimeError` rõ ràng để thông báo cho người dùng đổi tài khoản hoặc notebook khác.

5. **Ghép nối Slide giữ nguyên định dạng (Lossless Slide Merging)**:
   - File PPTX do NotebookLM xuất ra gồm các slide trình bày dưới dạng ảnh full-bleed (Shape Type 13 - `PICTURE`).
   - Hàm `merge_presentations` trích xuất `image.blob` nguyên gốc từ các slide thành phần và ghép vào presentation chính, giữ nguyên độ phân giải và tỉ lệ 16:9 gốc.

