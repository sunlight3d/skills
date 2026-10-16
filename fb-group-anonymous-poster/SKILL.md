---
name: fb-group-anonymous-poster
description: "Tự động tạo các biến thể bài viết tự nhiên (spinning nội dung không trùng lặp) và tự động đăng bài ẩn danh (Anonymous Post) lên các nhóm/groups Facebook bằng Playwright qua profile Chrome có sẵn. Sử dụng skill này bất cứ khi nào người dùng yêu cầu: đăng bài ẩn danh lên nhóm Facebook, tự động post bài group FB, spin nội dung đăng bài tìm lớp/tìm gia sư/rao vặt, đăng bài Facebook nhiều nhóm với nội dung hơi khác nhau, hoặc tự động hóa Facebook Groups."
---

# Facebook Group Anonymous Poster

Skill này hỗ trợ tự động hóa 2 công đoạn quan trọng khi đăng bài lên các hội nhóm Facebook:
1. **Sinh biến thể nội dung tự nhiên (Content Spinning)**: Tự động tạo ra các bài viết khác nhau về câu chữ, góc nhìn (tâm tình mẹ lo lắng, gạch đầu dòng ngắn gọn, ngỏ ý tìm người ghép nhóm, hỏi kinh nghiệm thầy cô...), đảo trật tự ý và dùng từ đồng nghĩa để tránh bị thuật toán Facebook đánh dấu spam.
2. **Tự động đăng bài ẩn danh (Anonymous Posting)**: Sử dụng Playwright tự động điều khiển trình duyệt Google Chrome (tận dụng phiên đăng nhập Facebook có sẵn), tìm nút "Đăng bài ẩn danh", xác nhận popup, nhập nội dung với tốc độ gõ phím ngẫu nhiên của người thật, và xuất bản bài viết.

---

## ⚠️ Nguyên Tắc An Toàn & Chống Checkpoint Facebook

1. **Không đăng trùng lặp 100% nội dung**: Mỗi nhóm PHẢI dùng 1 biến thể văn bản khác nhau.
2. **Thời gian chờ ngẫu nhiên (Delay)**: Giữa mỗi lần đăng sang nhóm kế tiếp, hệ thống tự động nghỉ từ **60 – 150 giây**. Tuyệt đối không đăng liên tục dồn dập.
3. **Mô phỏng thao tác người thật (Human Typing)**: Gõ từng ký tự với độ trễ ngẫu nhiên (30ms – 80ms), thỉnh thoảng dừng nghỉ như người đang suy nghĩ để tránh bị bot detection.
4. **Chốt chặn người dùng (Human-in-the-loop)**:
   - Mặc định script luôn chạy ở chế độ **Dry-run / Xem trước** (mở giao diện, bật ẩn danh, nhập chữ vào khung và chụp ảnh màn hình lưu tại `/tmp/fb_preview_*.png` hoặc để trên màn hình Chrome).
   - Chỉ khi người dùng xác nhận đồng ý đăng, mới thực thi với cờ `--confirm`.

---

## Cấu Trúc Thư Mục Skill

```
fb-group-anonymous-poster/
├── SKILL.md                  # Hướng dẫn chi tiết cho Agent
├── fb_content_spinner.py     # Module sinh biến thể bài viết tự nhiên
├── fb_anonymous_poster.py    # Module Playwright tự động đăng ẩn danh
├── open_chrome_debug.sh      # Mở Google Chrome với Remote Debugging Port 9222
├── run.sh                    # Wrapper script tự động quản lý môi trường ảo uv
├── groups.example.json       # Mẫu danh sách các nhóm mục tiêu
└── .venv/                    # Môi trường ảo Python & Playwright
```

---

## Hướng Dẫn Vận Hành Cho AI Agent

Khi người dùng yêu cầu đăng bài ẩn danh lên các nhóm (ví dụ: *"Đăng bài tìm lớp toán cho 2 bé lên các nhóm sau: link1, link2..."*):

### Bước 1: Sinh các biến thể nội dung
Chạy script sinh nội dung theo số lượng nhóm cần đăng:
```bash
/Volumes/data/code/skills/fb-group-anonymous-poster/run.sh fb_content_spinner.py \
  --count 5 \
  --subject "Toán" \
  --grade1 "lớp 8" \
  --grade2 "lớp 10" \
  --location "Xã Đàn, Giải Phóng" \
  --export-json /tmp/fb_variants.json
```
Hiển thị danh sách các bài viết biến thể này cho người dùng xem trước.

---

### Bước 2: Chọn phương thức kết nối Trình duyệt

Hệ thống hỗ trợ 2 chế độ:
* **Chế độ 1 (Profile riêng - Khuyên dùng):** Mở cửa sổ Chrome độc lập lưu phiên tại `~/.fb_auto_profile`. Lần đầu tiên bạn chỉ cần đăng nhập Facebook trên cửa sổ này 1 lần, các lần sau sẽ tự động nhớ đăng nhập mãi mãi.
* **Chế độ 2 (CDP - Dùng trực tiếp Chrome đang mở):**
  1. Mở Chrome với lệnh: `/Volumes/data/code/skills/fb-group-anonymous-poster/open_chrome_debug.sh`
  2. Playwright sẽ gắn trực tiếp vào Chrome này qua cổng `9222` bằng cờ `--mode cdp`.

---

### Bước 3: Chạy thử nghiệm / Xem trước (Dry-run)
Chạy thử trên nhóm đầu tiên mà KHÔNG bấm Đăng:
```bash
/Volumes/data/code/skills/fb-group-anonymous-poster/run.sh fb_anonymous_poster.py \
  --group-url "https://www.facebook.com/groups/<group_id>" \
  --content-file /tmp/fb_variants.json
```
Script sẽ tự động:
1. Mở nhóm trên Chrome.
2. Tìm và bật tính năng **Đăng bài ẩn danh**.
3. Điền nội dung biến thể vào khung soạn thảo.
4. Chụp ảnh màn hình lưu tại `/tmp/fb_preview_*.png` để bạn kiểm tra.

---

### Bước 4: Chạy Đăng thật (Khi Người Dùng Xác Nhận)
Thêm cờ `--confirm` để tự động bấm nút **Đăng**:
```bash
/Volumes/data/code/skills/fb-group-anonymous-poster/run.sh fb_anonymous_poster.py \
  --groups-file /Volumes/data/code/skills/fb-group-anonymous-poster/groups.json \
  --content-file /tmp/fb_variants.json \
  --delay-min 60 \
  --delay-max 120 \
  --confirm
```

Lịch sử đăng bài (thời gian, URL nhóm, trạng thái) sẽ được tự động lưu vào file `~/.fb_post_history.json`.
