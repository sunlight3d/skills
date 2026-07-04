#!/bin/bash
# Script mở camera hình vuông, không viền, luôn nổi ở góc màn hình
WAYLAND_DISPLAY= mpv /dev/video0 --profile=low-latency --untimed --vf=crop=ih:ih --no-border --ontop --geometry=250x250-20-20
