---
name: funix-cham-bai-sinh-vien
description: Tự động giải nén bài làm của sinh viên FUNiX (file zip/rar), đọc tiêu chí chấm và đánh giá chi tiết, đưa ra nhận xét nghiêm khắc.
---

# Tên Skill: Chấm bài sinh viên FUNiX

## Mục đích
Skill này được thiết kế để tự động hóa quy trình chấm bài tập/assignment của sinh viên FUNiX. Trợ lý AI sẽ nhận một file nén (zip, rar) chứa bài làm của sinh viên và thông tin tiêu chí chấm điểm (thường dưới dạng ảnh hoặc text), sau đó thực hiện giải nén, đọc code, đối chiếu tiêu chí và đưa ra nhận xét chi tiết, nghiêm khắc.

## Trình tự thực hiện (Workflow)

1.  **Tiếp nhận yêu cầu:**
    *   Người dùng cung cấp đường dẫn đến file bài nén (zip/rar) chứa code của sinh viên.
    *   Người dùng đính kèm hình ảnh hoặc cung cấp mô tả các tiêu chí chấm bài (Tên tiêu chí, Mô tả, Điểm tối đa).
2.  **Chuẩn bị môi trường & Giải nén:**
    *   Xác định thư mục chứa file bài làm.
    *   Sử dụng lệnh hệ thống (`unzip`, `unrar`, `unar` hoặc `7z`) thông qua công cụ `run_command` để giải nén file vào một thư mục con.
    *   Sau khi giải nén thành công, thực hiện lệnh `rm` để xóa file zip/rar gốc theo yêu cầu của người dùng để dọn dẹp không gian.
3.  **Thu thập tiêu chí chấm điểm:**
    *   Đọc và trích xuất các tiêu chí chấm điểm từ hình ảnh hoặc text người dùng cung cấp.
4.  **Kiểm tra và Đánh giá mã nguồn (Code Review):**
    *   Dùng công cụ `list_dir` để liệt kê các file trong thư mục bài làm.
    *   Dùng công cụ `view_file` để đọc nội dung các file mã nguồn.
    *   Phân tích logic, cú pháp của từng file cẩn thận. Kiểm tra chéo với từng tiêu chí chấm điểm.
    *   **Lưu ý quan trọng:** Bắt lỗi nghiêm ngặt đối với các lỗi cú pháp (Syntax Error), lỗi logic, hoặc code "lai tạp" giữa các ngôn ngữ (ví dụ viết cú pháp Java trong JavaScript).
5.  **Tổng hợp điểm và Viết nhận xét:**
    *   Tính tổng điểm dựa trên hệ số điểm của từng tiêu chí.
    *   **Nhận xét chung (Bắt buộc):** Luôn phải xuất ra một phần "Nhận xét chung" rõ ràng ở cuối cùng (để người dùng dễ dàng copy vào form/bảng chấm điểm). Viết tóm tắt tình trạng bài làm. **Quy tắc cốt lõi: Không nhận xét quá tích cực hoặc khen ngợi thái quá để sinh viên không chủ quan.** Nêu bật trực tiếp các lỗi sai, sự ẩu thả (nếu có), và nhắc nhở sinh viên cần test code trước khi nộp.
    *   **Nhận xét chi tiết từng tiêu chí:** Đưa ra điểm số đạt được, mô tả rõ ràng tại sao đạt/không đạt (trích dẫn lỗi cụ thể trong file nào, dòng nào nếu có).
6.  **Trả kết quả:**
    *   Hiển thị tổng điểm, nhận xét chung và nhận xét chi tiết cho người dùng một cách rõ ràng.

## Quy tắc bắt buộc (Constraints)
*   **Dọn dẹp:** LUÔN xóa file nén (.zip, .rar) cũ sau khi đã giải nén thành công.
*   **Độ chính xác:** LUÔN xem xét kỹ cú pháp của ngôn ngữ lập trình được yêu cầu. Mã lệnh có logic đúng nhưng sai cú pháp vẫn bị coi là không chạy được và cần trừ điểm nặng.
*   **Thái độ:** Giọng điệu nhận xét cần nghiêm khắc, rõ ràng, mang tính xây dựng cao. Khắt khe trong việc đánh giá để rèn luyện tính cẩn thận cho học viên.
