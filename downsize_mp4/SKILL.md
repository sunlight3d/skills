---
name: downsize_mp4
description: "Giảm dung lượng file video (MP4, MOV, MKV, AVI, TS...) mà không làm giảm độ phân giải bằng ffmpeg x265/HEVC (CRF 28), nén ảnh thông minh (JPEG step-down), và tùy chọn tự động cắt bỏ khoảng lặng (silence removal). Kích hoạt khi người dùng muốn giảm dung lượng video, nén file mp4 giữ nguyên độ phân giải, tối ưu kích thước video để gửi/upload/lưu trữ, hoặc gọi lệnh /downsize_mp4."
---

# Downsize MP4 (Media Studio Compression)

## Tổng quan (Overview)

Skill này cung cấp giải pháp giảm dung lượng file video (MP4, MOV, MKV, AVI, TS...) và ảnh (JPG, PNG, WebP) **hoàn toàn giữ nguyên độ phân giải gốc** (100% resolution & framerate preservation).

### Cơ chế kỹ thuật:
1. **Video Encoding (H.265 / HEVC)**:
   - Sử dụng codec `libx265` với hệ số nén `CRF 28` (chuẩn tối ưu cho video màn hình, bài giảng, vlog, podcast — chất lượng hình ảnh sắc nét tương đương H.264 gốc nhưng dung lượng giảm 50% - 80%).
   - Gắn tag `-tag:v hvc1` để tương thích hoàn toàn với macOS QuickTime Player, iOS Safari và Windows Media Player.
   - Âm thanh được chuẩn hóa qua `AAC 128kbps` (`-c:a aac -b:a 128k`).
   - Tự động bật tăng tốc phần cứng `-hwaccel auto`.
   - **Tuyệt đối không scale hay downsample độ phân giải**: kích thước khung hình (width x height) giữ nguyên 100%.

2. **Cắt bỏ khoảng lặng thông minh (Silence Removal)**:
   - Tự động dò tìm các khoảng im lặng dài hơn ngưỡng quy định (mặc định >500ms, ngưỡng âm lượng -30dB) bằng bộ lọc `silencedetect`.
   - Cắt bỏ tự động các đoạn ngắt nghỉ không cần thiết, giúp rút ngắn thời lượng và giảm thêm dung lượng file mà không làm mất nội dung chính.

3. **Nén ảnh thông minh (Smart Adaptive Image Step-down)**:
   - Áp dụng thuật toán nén đa bước hạ chất lượng thông minh (JPEG quality từ 90 xuống 20) để đưa ảnh về dưới dung lượng mục tiêu (mặc định 1.0 MB).

4. **Giao diện Desktop (PyQt6 ShrinkX Media Studio)**:
   - Hỗ trợ khởi chạy app giao diện kéo thả trực quan nếu người dùng có nhu cầu thao tác trên GUI.

---

## Khi nào kích hoạt Skill này (Triggers)

Kích hoạt skill này bất cứ khi nào người dùng có nhu cầu:
- "Giảm dung lượng video / file mp4 mà không làm giảm độ phân giải"
- "Nén video giữ nguyên độ nét / giữ nguyên resolution"
- "Video này nặng quá, nén lại giúp tôi để gửi Zalo / Discord / Email / Drive"
- "Downsize mp4 / nén mp4"
- "Cắt bớt khoảng lặng trong video / podcast / bài giảng"
- Hoặc người dùng gọi slash command: `/downsize_mp4`

---

## Hướng dẫn các bước thực hiện cho Agent

Khi nhận yêu cầu nén video hoặc ảnh từ người dùng:

### Bước 1: Xác định đường dẫn file/thư mục và tham số
Kiểm tra xem người dùng truyền:
- 1 file cụ thể (ví dụ: `/path/to/video.mp4`)
- Nhiều file cùng lúc
- Một thư mục chứa nhiều video/ảnh (ví dụ: `/Volumes/data/videos/`)
- Có yêu cầu cắt khoảng lặng hay không (`--remove-silence`)
- Có yêu cầu mức nén CRF đặc biệt nào không (mặc định 28; nếu muốn chất lượng cao hơn dùng 24-26; muốn file nhẹ hơn nữa dùng 30-32).

### Bước 2: Chạy script nén CLI
Chạy lệnh bằng `run_command`:

```bash
python3 "/Volumes/data/code/skills/downsize_mp4/scripts/downsize.py" "/đường/dẫn/file.mp4"
```

#### Các tùy chọn lệnh thường dùng:
- **Nén 1 file video (mặc định lưu vào thư mục `output/` bên cạnh file gốc):**
  ```bash
  python3 "/Volumes/data/code/skills/downsize_mp4/scripts/downsize.py" "/path/to/video.mp4"
  ```

- **Nén toàn bộ video trong thư mục:**
  ```bash
  python3 "/Volumes/data/code/skills/downsize_mp4/scripts/downsize.py" "/path/to/folder"
  ```

- **Chỉ định thư mục xuất file tùy ý:**
  ```bash
  python3 "/Volumes/data/code/skills/downsize_mp4/scripts/downsize.py" "/path/to/video.mp4" -o "/path/to/custom_output"
  ```

- **Bật tự động loại bỏ khoảng lặng âm thanh:**
  ```bash
  python3 "/Volumes/data/code/skills/downsize_mp4/scripts/downsize.py" "/path/to/video.mp4" --remove-silence
  ```

- **Điều chỉnh độ nét CRF (Ví dụ: CRF 24 cho chất lượng rất cao):**
  ```bash
  python3 "/Volumes/data/code/skills/downsize_mp4/scripts/downsize.py" "/path/to/video.mp4" --crf 24
  ```

- **Chỉ quét kiểm tra thông tin kích thước và độ phân giải (Dry-run):**
  ```bash
  python3 "/Volumes/data/code/skills/downsize_mp4/scripts/downsize.py" "/path/to/video.mp4" --dry-run
  ```

- **Mở giao diện GUI Desktop ShrinkX:**
  ```bash
  python3 "/Volumes/data/code/skills/downsize_mp4/scripts/downsize.py" --gui
  ```

### Bước 3: Đọc kết quả và phản hồi cho người dùng
Sau khi script hoàn tất:
1. Đọc báo cáo tổng kết gồm:
   - Dung lượng trước và sau khi nén (`MB` hoặc `GB`).
   - Tỷ lệ giảm (% đã tiết kiệm).
   - Xác nhận độ phân giải **hoàn toàn giữ nguyên** (ví dụ: `1920x1080 ➔ 1920x1080`).
2. Trả về cho người dùng:
   - Đường dẫn file kết quả dạng link markdown bấm được (`file:///...`).
   - Đường dẫn thư mục chứa file nén.
