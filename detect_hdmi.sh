#!/bin/bash
# Script đánh thức Card NVIDIA và quét lại cổng kết nối HDMI
set -e

echo "=== 1. Đang đánh thức Card đồ họa NVIDIA từ chế độ ngủ... ==="
nvidia-smi > /dev/null

echo "=== 2. Buộc các cổng kết nối đồ họa quét lại trạng thái (KMS Probe)... ==="
for f in /sys/class/drm/*/status; do
    echo -n "$f: "
    cat "$f"
done

echo "=== 3. Kích hoạt sự kiện udev thay đổi phần cứng để Ubuntu nhận diện màn hình... ==="
echo "Hung2011" | sudo -S udevadm trigger --action=change --subsystem-match=drm

echo "=== ĐÃ HOÀN TẤT QUÉT MÀN HÌNH NGOÀI! ==="
