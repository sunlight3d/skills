import sys
import os

# Thêm thư mục hiện tại vào sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_filter
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Skill qnet-filter-pdf")
    parser.add_argument('--input-dir', '-i', required=True, help="Thư mục chứa các tệp PDF")
    parser.add_argument('--tracker-file', '-t', default=None, help="Đường dẫn file theo dõi IP_CSKCB_INTERNET - VPN.xlsx")
    parser.add_argument('--output', '-o', default=None, help="Đường dẫn file Excel báo cáo đầu ra")
    
    args = parser.parse_args()
    out = run_filter(args.input_dir, args.tracker_file, args.output)
    print(f"[HOÀN TẤT] Báo cáo đã tạo tại: {out}")
