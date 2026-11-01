---
name: mathplus-tra-loi-comment-tim-lop
description: "Tự động tìm kiếm & join khoảng 3 nhóm Facebook liên quan đến dạy Toán từ lớp 6 đến lớp 12 (không cần confirm), ngẫu nhiên quét các nhóm để tìm bài phụ huynh đăng tìm lớp/gia sư cho con, sinh lời bình luận giới thiệu Thầy Dũng Toán (Xã Đàn, Hồ Đắc Di - 0977961189) thiên biến vạn hóa, chống trùng lặp/spam (3 đến 5 bài/lần), và BẮT BUỘC đưa ra danh sách chờ Human xác nhận trước khi đăng bình luận thật."
---

# MathPlus Trả Lời Comment Tìm Lớp (Lớp 6 – Lớp 12)

Skill này chuyên trách việc seeding bằng cách bình luận trực tiếp vào các bài viết phụ huynh đang có nhu cầu tìm lớp học thêm Toán hoặc tìm gia sư cho con (từ lớp 6 đến lớp 12) trên Facebook:

1. **Tìm kiếm & Tham gia nhóm (Tự động, không cần confirm)**:
   - Mỗi lần gọi skill sẽ tự động tìm kiếm các hội nhóm liên quan đến Toán THCS, THPT, ôn thi vào 10, ôn thi tốt nghiệp THPT, gia sư Toán Hà Nội... và gửi yêu cầu tham gia tối đa **3 nhóm/lần**.
   - Tự động điền câu trả lời xét duyệt và tick chọn đồng ý quy tắc nhóm.

2. **Quét tìm bài viết phụ huynh tìm lớp**:
   - Truy cập ngẫu nhiên vào các nhóm mục tiêu, tìm kiếm các bài viết có phụ huynh đăng tìm lớp Toán, tìm gia sư, con mất gốc/học chậm cần tìm thầy kèm sát.
   - Mỗi lần quét sẽ thu thập từ **3 đến 5 bài viết** phù hợp nhất.

3. **Chống trùng lặp & Chống Spam**:
   - Kiểm tra lịch sử bình luận tại `~/.mathplus_comment_history.json`.
   - Nếu bài viết nào đã được bình luận trước đó (hoặc trong bài đã có sự xuất hiện của số điện thoại `0977961189`), hệ thống sẽ **bỏ qua ngay lập tức**, tuyệt đối không trả lời lại.

4. **Nội dung bình luận thiên biến vạn hóa**:
   - Xoay quanh việc giới thiệu Thầy Dũng Toán (dạy ở khu vực Xã Đàn, Hồ Đắc Di).
   - Số điện thoại **`0977961189`** (Zalo) được giữ nguyên vẹn, đặt tự nhiên, dễ đọc, dễ copy và bấm gọi trên điện thoại.
   - **Tuyệt đối KHÔNG có dấu markdown (`**`, `*`, `#`)** để hoàn toàn tự nhiên như người thật giới thiệu.

5. **BẮT BUỘC Human Confirm trước khi đăng bình luận**:
   - Trước khi gửi bình luận lên Facebook, hệ thống bắt buộc phải xuất danh sách dự thảo gồm: Nhóm, URL bài viết, tóm tắt bài đăng gốc, và nội dung bình luận đề xuất.
   - Chỉ khi người dùng bấm xác nhận đồng ý (hoặc qua cờ `--confirm`), hệ thống mới tiến hành đăng bình luận lên từng bài.

---

## Cấu Trúc Thư Mục Skill

```
mathplus-tra-loi-comment-tim-lop/
├── SKILL.md                  # Hướng dẫn chi tiết cho Agent
├── run.bat                   # File thực thi nhanh trên Windows CMD
├── run.ps1                   # File thực thi nhanh trên PowerShell
└── scripts/
    ├── spinner.py            # Sinh biến thể lời bình luận tự nhiên (sđt 0977961189 chuẩn copy)
    ├── joiner.py             # Tìm và tự động join 3 nhóm Toán lớp 6-12
    └── commenter.py          # Engine quét bài, xuất dự thảo và đăng bình luận sau confirm
```

---

## Quy Trình Vận Hành Chuẩn Cho AI Agent

Khi người dùng yêu cầu: *"Hãy tìm và trả lời comment tìm lớp toán..."*:

### Bước 1: Quét bài & Tạo dự thảo bình luận (Kèm join 3 nhóm)
Chạy script ở chế độ `--scan`:
```powershell
& "c:\code\mathplus\.agents\skills\mathplus-tra-loi-comment-tim-lop\run.ps1" -Scan -CommentCount 3
```
- Script sẽ tự động join 3 nhóm mới (không cần hỏi người dùng).
- Script sẽ quét tìm 3 đến 5 bài viết phụ huynh đang tìm lớp Toán và lưu dự thảo vào `~/.mathplus_comment_drafts.json`.

### Bước 2: Hiển thị danh sách cho Human duyệt
AI Agent lấy danh sách bài viết và nội dung đề xuất từ file dự thảo, trình bày bảng rõ ràng cho người dùng xem trước:
- Tên nhóm & Link bài viết
- Trích đoạn bài đăng của phụ huynh
- Nội dung bình luận đề xuất (chứa sđt `0977961189`)

### Bước 3: Đợi Human Confirm
AI Agent hỏi người dùng: *"Tôi đã quét được các bài viết trên và chuẩn bị nội dung bình luận. Bạn có đồng ý để tôi đăng các bình luận này không?"*

### Bước 4: Thực thi đăng bình luận (Sau khi Human đồng ý)
Chạy lệnh với cờ `-Confirm`:
```powershell
& "c:\code\mathplus\.agents\skills\mathplus-tra-loi-comment-tim-lop\run.ps1" -Confirm
```
- Hệ thống sẽ duyệt qua từng bài trong dự thảo, gõ phím với tốc độ người thật và bấm Enter đăng bình luận.
- Tự động nghỉ an toàn 30 – 50 giây giữa mỗi bài để chống checkpoint Facebook.
- Lưu lại lịch sử vào `~/.mathplus_comment_history.json`.
