---
name: capcut-bo-khoang-lang
description: "Tự động phát hiện và cắt bỏ hoàn toàn các khoảng lặng (im lặng, ngắt nghỉ, viết bảng) trong video bài giảng, podcast, vlog; tự động tạo timeline dự án CapCut (draft) với các nhát cắt xếp liền mạch, hoặc xuất trực tiếp thành 1 video MP4 chuẩn YouTube 1080p 60fps bằng tăng tốc phần cứng Apple Silicon VideoToolbox."
---

# CapCut Bỏ Khoảng Lặng (AutoCut Media Studio)

## 📌 Tổng quan (Overview)

Khi quay video bài giảng (dạy học, viết bảng), quay podcast, vlog hoặc quay màn hình máy tính, thường xuyên xuất hiện các **khoảng lặng chết** (người nói suy nghĩ, dừng lại viết bảng, lật giáo án, chỉnh mic...). Những khoảng lặng này có thể chiếm từ **50% đến 85%** tổng thời lượng video raw.

Skill này cung cấp giải pháp tự động hóa toàn diện với 2 chế độ linh hoạt:
1. **Chế độ Timeline CapCut (Dự án Draft):**
   - Tự động quét dự án CapCut hiện tại trong `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`.
   - Nhân bản an toàn thành dự án mới: `<Tên_Dự_Án> (AutoCut)` (không làm ảnh hưởng dự án gốc).
   - Tự động chia nhỏ video thành hàng nghìn phân đoạn (`segments`) chuẩn xác từng mili-giây, xếp liền mạch trên Timeline CapCut.
   - Người dùng chỉ cần mở CapCut, bấm nút **Home** là thấy dự án mới sẵn sàng để kéo thả chỉnh sửa tiếp hoặc bấm Export.
2. **Chế độ Xuất Video MP4 Độc Lập (Chuẩn YouTube):**
   - Quét từng file video hoặc toàn bộ thư mục chứa các video bài giảng (`.MOV`, `.MP4`, `.MKV`...).
   - Bóc tách toàn bộ khoảng lặng (mặc định: ngưỡng $-30\text{ dB}$, khoảng lặng $>0.5\text{ s}$, kèm đệm $150\text{ ms}$ để không bị cụt âm cuối).
   - Mã hóa siêu tốc bằng phần cứng **Apple Silicon VideoToolbox** (`h264_videotoolbox` @ 1080p 60fps, 6Mbps).
   - Tự động ghép nối (concat) tất cả các video thành **1 file duy nhất** chuẩn SEO YouTube (nhẹ, nét, mượt mà).

---

## 🎯 Khi nào kích hoạt Skill này (Triggers)

Kích hoạt skill này bất cứ khi nào người dùng yêu cầu:
- "Cắt khoảng lặng trong CapCut" / "Cắt những đoạn không nói gì trong CapCut"
- "Bỏ khoảng lặng video / bài giảng / podcast"
- "AutoCut video / CapCut"
- "Cắt hết khoảng im lặng rồi ghép thành 1 video up YouTube"
- Hoặc gọi lệnh: `/capcut-bo-khoang-lang`

---

## 🛠 Hướng dẫn cho Agent (Step-by-Step Instructions)

### Bước 1: Xác định nhu cầu của người dùng
Kiểm tra xem người dùng muốn:
- **Tạo timeline trong CapCut** để tiếp tục dựng/chỉnh sửa trong app CapCut.
- **Xuất thẳng ra file video MP4 hoàn chỉnh** để up YouTube / lưu trữ.
- Hoặc **thực hiện cả hai**.

### Bước 2: Chạy script thực thi `autocut.py`

Đường dẫn script chính:
```bash
python3 "/Volumes/data/code/skills/capcut-bo-khoang-lang/scripts/autocut.py" [tham_số]
```

#### Các trường hợp lệnh thường dùng:

1. **Tự động áp dụng cho Dự án CapCut mới nhất (tạo dự án AutoCut mới):**
   ```bash
   python3 "/Volumes/data/code/skills/capcut-bo-khoang-lang/scripts/autocut.py" --capcut
   ```

2. **Áp dụng cho một dự án CapCut cụ thể theo tên:**
   ```bash
   python3 "/Volumes/data/code/skills/capcut-bo-khoang-lang/scripts/autocut.py" --capcut "Toán 11-Chương 4"
   ```

3. **Ghi đè trực tiếp lên dự án CapCut đang chọn (in-place):**
   ```bash
   python3 "/Volumes/data/code/skills/capcut-bo-khoang-lang/scripts/autocut.py" --capcut --in-place "Toán 11-Chương 4"
   ```

4. **Quét toàn bộ thư mục video, cắt khoảng lặng và ghép thành 1 video duy nhất:**
   ```bash
   python3 "/Volumes/data/code/skills/capcut-bo-khoang-lang/scripts/autocut.py" "/Volumes/data/code/YoutubeDayToan/Toán 11-Chương 4"
   ```

5. **Xử lý 1 file video đơn lẻ và xuất ra file MP4:**
   ```bash
   python3 "/Volumes/data/code/skills/capcut-bo-khoang-lang/scripts/autocut.py" "/path/to/video.MOV" -o "/path/to/output.mp4"
   ```

6. **Chỉ quét kiểm tra thống kê (Dry-run) xem cắt được bao nhiêu phút:**
   ```bash
   python3 "/Volumes/data/code/skills/capcut-bo-khoang-lang/scripts/autocut.py" "/path/to/folder" --dry-run
   ```

7. **Tùy chỉnh thông số âm thanh:**
   - `--noise-db -28`: Độ nhạy tiếng ồn (mặc định -30dB).
   - `--min-silence 0.4`: Khoảng ngắt nghỉ tối thiểu để cắt (mặc định 0.5s).
   - `--pad 0.2`: Thời gian đệm bảo vệ lời nói (mặc định 0.15s).

---

### Bước 3: Phản hồi cho người dùng
- Thông báo rõ thời lượng trước và sau khi cắt (ví dụ: rút gọn từ 6h xuống 1h07m, loại bỏ 84% thời gian chết).
- Cung cấp link markdown bấm được (`file:///...`) đến file MP4 thành phẩm hoặc hướng dẫn mở lại CapCut để xem dự án mới.
