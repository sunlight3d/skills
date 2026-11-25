---
name: thang-loi-logistic-lay-lich-su-zalo
description: "Trích xuất lịch sử chat Zalo nhóm COLE_KHÓA HỌC ỨNG DỤNG AI TRONG NGHIỆP VỤ LOGISTIC (hoặc nhóm tùy chọn), tự động tải ảnh, file đính kèm, trích xuất OCR nội dung trên ảnh và xuất báo cáo Word chuyên nghiệp. Hỗ trợ chế độ Incremental Update (chỉ lấy tin nhắn mới giúp tiết kiệm thời gian) hoặc Full Update."
---

# Thắng Lợi Logistics: Bộ Công Cụ Trích Xuất Lịch Sử Chat Zalo & Tự Động Hóa Báo Cáo

## 1. Tổng quan & Mục đích

Skill `thang-loi-logistic-lay-lich-su-zalo` cung cấp giải pháp hoàn chỉnh để:
1. **Kết nối trực tiếp ứng dụng Zalo trên macOS** thông qua Apple Accessibility API & Cocoa Framework mà không cần can thiệp reverse engineering hay can thiệp cơ sở dữ liệu mã hóa.
2. **Thu thập toàn bộ lịch sử tin nhắn**:
   - Tên người gửi, vai trò (Giảng viên, Ban tổ chức COLE, Học viên Thắng Lợi Logistics).
   - Mốc thời gian chi tiết theo từng ngày (Thứ Sáu, Thứ Bảy, Chủ Nhật...).
   - Tin nhắn trả lời/trích dẫn (Quote replies), liên kết URL, cảm xúc (Reactions: ❤️, 👍...).
   - Sự kiện hệ thống (thêm học viên, bổ nhiệm phó nhóm, ghim ghi chú).
3. **Tải & Quản lý toàn bộ Media**:
   - Tự động phát hiện và trích xuất ảnh gốc có độ nét cao (`.jpg`) và tệp tài liệu đính kèm (`.txt`, `.pdf`, `.docx`...).
   - Lưu trữ toàn bộ vào thư mục đầu ra có tên trùng với tên file Word.
4. **Trích xuất thông tin OCR từ hình ảnh**:
   - Tự động nhận diện chữ tiếng Việt & tiếng Anh trên các ảnh chụp màn hình (danh sách học viên, màn hình lỗi hệ thống LMS, thông tin điều khiển từ xa RustDesk, màn hình chờ Microsoft Teams...).
   - Đưa nội dung trích xuất vào bảng chú thích chuyên nghiệp ngay dưới từng bức ảnh trong file Word.
5. **Cơ chế Cập Nhật Gia Tăng (Incremental Update - Tiết Kiệm Thời Gian)**:
   - Lưu trạng thái (`sync_state.json`) sau mỗi lần xuất.
   - Khi chạy lại, hệ thống **không cần cuộn lên đầu nhóm**, mà chỉ kiểm tra các tin nhắn mới phát sinh kể từ mốc đồng bộ gần nhất.
   - Nếu không có tin nhắn mới, hoàn thành ngay trong 1 giây mà không tốn tài nguyên.

---

## 2. Cấu trúc thư mục Skill

```
thang-loi-logistic-lay-lich-su-zalo/
├── SKILL.md                                 # Hướng dẫn chi tiết skill
├── scripts/
│   ├── extract_zalo_chat.py                 # Script điều phối chính (hỗ trợ --mode incremental/full)
│   ├── copy_media_files.py                  # Module đồng bộ tải ảnh và file đính kèm
│   └── build_full_word_with_ocr.py          # Module tạo file Word chuẩn mực với ảnh & bảng OCR
```

---

## 3. Hướng dẫn sử dụng

### 3.1. Chế độ Mặc định (Incremental Update - Lấy tin nhắn mới nhất)
Chế độ này được khuyến nghị sử dụng khi bạn đã từng xuất lịch sử trước đó và muốn cập nhật thêm tin nhắn mới:

```bash
uv run --with pyobjc-framework-ApplicationServices --with pyobjc-framework-Cocoa --with pyobjc-framework-Quartz --with python-docx python3 \
  /Volumes/data/code/skills/thang-loi-logistic-lay-lich-su-zalo/scripts/extract_zalo_chat.py --mode incremental
```

*Nếu không có tin nhắn mới, script sẽ thông báo dữ liệu đã là mới nhất và dừng lại ngay lập tức.*

### 3.2. Chế độ Toàn bộ (Full Update - Quét lại từ đầu)
Sử dụng khi xuất lần đầu tiên hoặc muốn làm mới toàn bộ tài liệu từ tin nhắn đầu tiên khi thành lập nhóm:

```bash
uv run --with pyobjc-framework-ApplicationServices --with pyobjc-framework-Cocoa --with pyobjc-framework-Quartz --with python-docx python3 \
  /Volumes/data/code/skills/thang-loi-logistic-lay-lich-su-zalo/scripts/extract_zalo_chat.py --mode full
```

### 3.3. Tùy biến thư mục xuất dữ liệu
Bạn có thể chỉ định thư mục đích mong muốn thông qua tham số `--output-dir`:

```bash
uv run --with pyobjc-framework-ApplicationServices --with pyobjc-framework-Cocoa --with pyobjc-framework-Quartz --with python-docx python3 \
  /Volumes/data/code/skills/thang-loi-logistic-lay-lich-su-zalo/scripts/extract_zalo_chat.py \
  --mode incremental \
  --output-dir "/Users/hoangnd/Downloads/Lich_Su_Chat_COLE_KHOA_HOC_UNG_DUNG_AI_LOGISTIC"
```

---

## 4. Quy chuẩn đầu ra của File Word & Media

1. **Thư mục đầu ra**:
   - Đường dẫn mặc định: `/Users/hoangnd/Downloads/Lich_Su_Chat_COLE_KHOA_HOC_UNG_DUNG_AI_LOGISTIC/`
   - Chứa file Word chính: `Lich_Su_Chat_COLE_KHOA_HOC_UNG_DUNG_AI_LOGISTIC.docx`.
   - Chứa toàn bộ các file ảnh đính kèm (`Anh_01_...jpg`, `Anh_02_...jpg`...).
   - Chứa toàn bộ các file tài liệu đính kèm (`File_DinhKem_01_...txt`).
   - Chứa file trạng thái đồng bộ: `sync_state.json`.

2. **Định dạng tài liệu Word**:
   - **Bìa & Bảng Metadata**: Tên khóa học, đơn vị đào tạo (COLE), doanh nghiệp thụ hưởng (Thắng Lợi Logistics), Giảng viên (Thầy Nguyễn Đức Hoàng), sĩ số 42 học viên.
   - **Hộp thông tin ghim**: Lịch học, tài khoản LMS, link Teams/Meet dự phòng, link Google Drive tài liệu buổi 1 và buổi 2.
   - **Phân tách theo ngày**: Header xanh navy `#1F4E79` nổi bật cho từng ngày học.
   - **Thẻ tin nhắn**: Màu sắc phân định theo vai trò (Đỏ đô cho Giảng viên, Xanh lá cho Ban tổ chức COLE, Xanh xám cho Học viên).
   - **Hình ảnh & OCR**: Hình ảnh nhúng trực tiếp kèm bảng `🔍 THÔNG TIN TRÍCH XUẤT TỪ HÌNH ẢNH` màu vàng hổ phách trang nhã.
   - **Tài liệu đính kèm**: Hộp `📎 TỆP ĐÍNH KÈM ĐÃ TẢI VỀ THƯ MỤC` hiển thị toàn văn nội dung tệp.
