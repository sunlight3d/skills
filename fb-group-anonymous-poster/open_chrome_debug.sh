#!/bin/bash
# Mở Google Chrome trên macOS với cổng gỡ lỗi từ xa 9222
# Giúp Playwright kết nối trực tiếp vào phiên đăng nhập Facebook có sẵn.

echo "Đang khởi động Google Chrome với cổng Remote Debugging 9222..."
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 > /dev/null 2>&1 &
echo "✅ Đã mở Chrome. Bạn có thể đăng nhập Facebook trên cửa sổ này và chạy poster với cờ --mode cdp."
