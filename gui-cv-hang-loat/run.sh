#!/usr/bin/env bash
# run.sh - Trợ lý dòng lệnh chạy nhanh skill gui-cv-hang-loat
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="python3"

ACTION="${1:-preview}"

case "$ACTION" in
    preview)
        echo "🔍 Đang tìm và tổng hợp 10 đơn vị đào tạo mới..."
        $PYTHON_BIN "$SCRIPT_DIR/gui_cv_assistant.py" --action preview --count 10
        ;;
    send)
        echo "⚠️ BẠN ĐANG CHUẨN BỊ GỬI 10 EMAIL THẬT QUA GMAIL TRÊN CHROME!"
        read -p "👉 Bạn có chắc chắn muốn gửi không? (Nhập 'yes' hoặc 'y' để xác nhận): " CONFIRM
        if [[ "$CONFIRM" =~ ^[Yy](es)?$ ]]; then
            $PYTHON_BIN "$SCRIPT_DIR/gui_cv_assistant.py" --action send --count 10 --confirm
        else
            echo "❌ Đã hủy thao tác gửi. Chưa có email nào được gửi đi."
        fi
        ;;
    status)
        $PYTHON_BIN "$SCRIPT_DIR/gui_cv_assistant.py" --action status
        ;;
    *)
        $PYTHON_BIN "$SCRIPT_DIR/gui_cv_assistant.py" "$@"
        ;;
esac
