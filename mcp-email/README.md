# Gmail IMAP MCP Server

MCP Server cho phép kết nối trực tiếp với tài khoản Gmail qua giao thức bảo mật IMAP SSL (`imap.gmail.com:993`) để đọc, tìm kiếm và trích xuất thông tin email.

---

## ⚠️ Lưu ý quan trọng về mật khẩu Gmail
Google **đã ngừng hỗ trợ đăng nhập bằng mật khẩu tài khoản thông thường** qua giao thức IMAP/POP từ năm 2022 (Less Secure Apps đã bị khai tử).

Để kết nối được, bạn cần sử dụng **Mật khẩu ứng dụng (App Password)** gồm 16 ký tự:
1. Truy cập tài khoản Google: [Google Account Security](https://myaccount.google.com/security)
2. Đảm bảo đã bật **Xác minh 2 bước (2-Step Verification)**.
3. Tìm đến mục **Mật khẩu ứng dụng** (hoặc truy cập trực tiếp: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)).
4. Tạo một mật khẩu ứng dụng mới (ví dụ đặt tên: `Antigravity Mail`), Google sẽ hiển thị một chuỗi 16 ký tự dạng: `xxxx xxxx xxxx xxxx`.
5. Dùng chuỗi 16 ký tự này làm mật khẩu khi kết nối.

---

## Cấu hình

Tạo file `config.json` tại thư mục này (`C:\code\skills\mcp-email\config.json`):
```json
{
  "email": "your_address@gmail.com",
  "password": "xxxx xxxx xxxx xxxx"
}
```
*(File này sẽ được tự động đọc khi khởi chạy server hoặc chạy script).*

---

## Các công cụ (Tools) trong MCP Server
1. `get_today_emails(limit=20)`: Lấy danh sách các email mới nhất nhận được trong ngày hôm nay kèm ID, người gửi, tiêu đề, thời gian và trích dẫn nội dung ngắn.
2. `read_email_detail(email_id)`: Xem toàn bộ nội dung chi tiết của một email theo ID.
3. `check_connection()`: Kiểm tra kết nối tới hòm thư.

---

## Chạy trực tiếp từ dòng lệnh
```bash
# Tải email hôm nay (dùng cấu hình từ config.json):
python fetch_today.py

# Hoặc truyền trực tiếp tài khoản và mật khẩu ứng dụng:
python fetch_today.py --user your_address@gmail.com --pass "xxxx xxxx xxxx xxxx" --limit 10
```
