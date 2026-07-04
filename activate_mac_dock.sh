#!/bin/bash
# Script để kích hoạt Dash2Dock Lite và tắt Ubuntu Dock mặc định
echo "Đang tắt thanh Ubuntu Dock mặc định..."
gnome-extensions disable ubuntu-dock@ubuntu.com

echo "Đang kích hoạt thanh Dash2Dock Animated (mới)..."
gnome-extensions enable dash2dock-lite@icedman.github.com

echo "Đã hoàn thành! Hãy mở ứng dụng 'Extensions' (hoặc 'Extension Manager') để cấu hình hiệu ứng Zoom theo ý thích của bạn."
