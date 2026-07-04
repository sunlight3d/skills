#!/bin/bash
# Script cài đặt trình duyệt Cốc Cốc chính thức trên Ubuntu
set -e

echo "=== 1. Tải và thêm khóa bảo mật GPG của Cốc Cốc... ==="
curl -fsSL https://browser-linux.coccoc.com/deb/public.gpg | gpg --yes --dearmor -o /etc/apt/trusted.gpg.d/coccoc-browser.gpg

echo "=== 2. Thêm kho lưu trữ (Repository) của Cốc Cốc vào hệ thống... ==="
echo "deb [arch=any] https://browser-linux.coccoc.com/deb/ stable main" > /etc/apt/sources.list.d/coccoc-browser.list

echo "=== 3. Cập nhật lại danh sách gói phần mềm... ==="
apt-get update

echo "=== 4. Tiến hành cài đặt Cốc Cốc Browser... ==="
apt-get install -y coccoc-browser-stable

echo "=== CÀI ĐẶT CỐC CỐC HOÀN TẤT THÀNH CÔNG! ==="
