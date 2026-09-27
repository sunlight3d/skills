---
name: capcut-recover-latest-video
description: "Cứu và sao lưu các video quay màn hình / camera mới nhất của CapCut khi CapCut bị treo (hung/deadlock/not responding), kiểm tra tính toàn vẹn của file video, cung cấp đường dẫn lưu trữ dự phòng và tắt hẳn tiến trình CapCut đang bị treo."
---

# CapCut Recover Latest Video

## Tổng quan (Overview)
Khi người dùng sử dụng tính năng **Ghi hình màn hình (Screen Recording) / Quay Camera** trên CapCut (macOS), CapCut thường xuyên gặp tình trạng bị treo (deadlock ở CoreAudio khi ngắt microphone Yeti/mic rời, hoặc đứng hình ở bước import file vào timeline).

Thực tế, dữ liệu video màn hình và camera đã được CapCut ghi thô theo thời gian thực (real-time) và đóng file hoàn chỉnh tại thư mục ngầm:
`~/Movies/CapCut/User Data/VideoRecord/`

Skill này giúp:
1. Tự động quét và phát hiện các file video quay màn hình (`Capcut_RecordScreen_*.mp4`) và camera (`Capcut_RecordCamera_*.mp4`) mới nhất.
2. Kiểm tra tính toàn vẹn của file (kích thước, thời lượng, khả năng phát) bằng `ffprobe`.
3. Tự động sao lưu an toàn sang thư mục dự phòng `~/Movies/CapCut_Recording_Backup/` (trên macOS) hoặc `%USERPROFILE%\Videos\CapCut_Recording_Backup\` (trên Windows).
4. Tự động mở cửa sổ Finder (macOS) hoặc Windows Explorer (Windows) hiển thị ngay thư mục chứa file đã cứu.
5. Trả về đường dẫn file dự phòng có thể bấm trực tiếp (`file://...`).
6. Tắt dứt điểm tiến trình CapCut đang bị treo để giải phóng tài nguyên CPU/RAM.

---

## Khi nào kích hoạt Skill này (Triggers)
Kích hoạt skill này khi người dùng phản ánh:
- "CapCut bị treo khi quay màn hình"
- "CapCut record bị đứng hình / không lưu được"
- "Cứu file quay CapCut"
- "CapCut treo khi đang xuất / dừng quay"
- Hoặc yêu cầu: `/capcut-recover-latest-video`

---

## Hướng dẫn các bước thực hiện cho Agent

### Bước 1: Chạy script cứu file
Chạy trực tiếp script Python có sẵn trong skill:

```bash
python3 "/Volumes/data/code/skills/capcut-recover-latest-video/scripts/recover.py"
```

*Tuỳ chọn bổ sung nếu cần:*
- Chỉ kiểm tra thông tin mà không copy hay kill app:
  `python3 .../recover.py --dry-run`
- Chỉ sao lưu mà không tắt CapCut:
  `python3 .../recover.py --no-kill`
- Không tự động mở Finder / Windows Explorer:
  `python3 .../recover.py --no-open`
- Chỉ định thư mục lưu bản backup khác:
  `python3 .../recover.py --dest "/đường/dẫn/khác"`

### Bước 2: Đọc kết quả từ script
Script sẽ:
- Sao lưu các file video vừa cứu và tự động mở thư mục trong Finder (macOS) hoặc Windows Explorer (Windows).
- In ra tên các file kèm dung lượng (MB) và thời lượng (phút:giây).
- In đường dẫn tuyệt đối của các file đã sao lưu.
- Trạng thái tắt tiến trình CapCut bị treo.

### Bước 3: Phản hồi cho người dùng
- Thông báo rõ ràng các file đã được cứu thành công.
- Cung cấp link markdown bấm được (`file:///...`) đến thư mục backup và từng file video.
- Hướng dẫn người dùng có thể mở lại CapCut và kéo thả trực tiếp các file này vào timeline dự án để tiếp tục chỉnh sửa.
