import sys
import os
import argparse

# Ensure utf-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from email_client import GmailClient, load_credentials

def main():
    parser = argparse.ArgumentParser(description="Tải email mới nhất trong ngày từ Gmail")
    parser.add_argument("--user", help="Địa chỉ Gmail")
    parser.add_argument("--pass", dest="pwd", help="Mật khẩu ứng dụng Gmail (App Password)")
    parser.add_argument("--limit", type=int, default=10, help="Số lượng email tối đa")
    args = parser.parse_args()

    try:
        user, pwd = load_credentials(args.user, args.pwd)
    except Exception as e:
        print(f"LỖI: {e}")
        sys.exit(1)

    print(f"[*] Đang kết nối tới Gmail ({user})...")
    try:
        with GmailClient(user, pwd) as client:
            emails = client.get_today_emails(limit=args.limit)
            if not emails:
                print("\n[!] Không có email nào được gửi đến trong ngày hôm nay.")
                return

            print(f"\n[+] Tìm thấy {len(emails)} email trong ngày hôm nay:\n" + "="*70)
            for i, em in enumerate(emails, 1):
                print(f"#{i} | ID: {em['id']}")
                print(f"  Từ:      {em['from']}")
                print(f"  Tiêu đề: {em['subject']}")
                print(f"  Thời gian: {em['date']}")
                print(f"  Trích dẫn: {em['snippet'][:150]}...")
                print("-" * 70)
    except Exception as e:
        print(f"\n[X] LỖI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
