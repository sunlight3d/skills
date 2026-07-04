#!/bin/bash
# Script cài đặt Docker Engine chính thức trên Ubuntu 26.04 (Resolute)
set -e

echo "=== 1. Gỡ bỏ các phiên bản Docker cũ (nếu có) ==="
apt-get remove -y docker docker-engine docker.io containerd runc || true

echo "=== 2. Cài đặt các gói phụ thuộc để tải qua HTTPS ==="
apt-get update
apt-get install -y ca-certificates curl gnupg

echo "=== 3. Tạo thư mục keyrings và tải GPG key chính thức của Docker ==="
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "=== 4. Cấu hình kho lưu trữ (Repository) Docker ==="
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu resolute stable" > /etc/apt/sources.list.d/docker.list

echo "=== 5. Cập nhật lại danh sách gói từ kho mới ==="
apt-get update

echo "=== 6. Tiến hành cài đặt Docker Engine, CLI, Containerd và Docker Compose ==="
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "=== 7. Khởi động và cấu hình Docker tự chạy cùng hệ thống ==="
systemctl enable --now docker

echo "=== 8. Thêm người dùng 'nguyenduchoang' vào nhóm 'docker' ==="
# Việc này giúp bạn có thể chạy các lệnh docker mà không cần gõ sudo
usermod -aG docker nguyenduchoang

echo "=== 9. Kiểm tra phiên bản Docker vừa cài đặt ==="
docker --version

echo "=== CÀI ĐẶT HOÀN TẤT THÀNH CÔNG! ==="
