#!/bin/bash
# Script điều phối chạy Tool Facebook Anonymous Poster
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ ! -d ".venv" ]; then
  echo "[*] Đang tạo môi trường ảo và cài đặt Playwright..."
  /Users/hoangnd/.local/bin/uv venv .venv
  /Users/hoangnd/.local/bin/uv pip install playwright
  .venv/bin/playwright install chromium
fi

.venv/bin/python3 "$@"
