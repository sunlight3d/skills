import imaplib
import email
from email.header import decode_header, make_header
from datetime import datetime
import json
import os
from typing import List, Dict, Any, Optional

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def get_imap_date_str(dt: Optional[datetime] = None) -> str:
    """Format datetime as IMAP date string (e.g. 09-Sep-2026) ensuring English month names."""
    if dt is None:
        dt = datetime.now()
    month_abbr = MONTH_NAMES[dt.month - 1]
    return f"{dt.day:02d}-{month_abbr}-{dt.year}"

def clean_header_val(val: Optional[str]) -> str:
    """Decode RFC 2047 encoded email headers."""
    if not val:
        return ""
    try:
        decoded = decode_header(val)
        return str(make_header(decoded))
    except Exception:
        return str(val)

def extract_body(msg: email.message.Message, max_chars: int = 1500) -> str:
    """Extract plain text or fallback HTML body from an email message."""
    body = ""
    if msg.is_multipart():
        # First try to find text/plain
        for part in msg.walk():
            ctype = part.get_content_type()
            cdisp = str(part.get("Content-Disposition", ""))
            if ctype == "text/plain" and "attachment" not in cdisp:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        body = payload.decode(charset, errors="replace")
                    except Exception:
                        body = payload.decode("utf-8", errors="replace")
                    break
        # If no plain text found, try text/html
        if not body:
            for part in msg.walk():
                ctype = part.get_content_type()
                cdisp = str(part.get("Content-Disposition", ""))
                if ctype == "text/html" and "attachment" not in cdisp:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        try:
                            body = payload.decode(charset, errors="replace")
                        except Exception:
                            body = payload.decode("utf-8", errors="replace")
                        break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                body = payload.decode(charset, errors="replace")
            except Exception:
                body = payload.decode("utf-8", errors="replace")

    body = body.strip()
    if max_chars and len(body) > max_chars:
        return body[:max_chars] + f"\n... [Nội dung đã được cắt ngắn bớt - Tổng {len(body)} ký tự]"
    return body

def load_credentials(email_user: Optional[str] = None, email_pass: Optional[str] = None) -> tuple[str, str]:
    """Resolve email and password from args, env vars, or config.json."""
    user = email_user or os.environ.get("GMAIL_USER") or os.environ.get("EMAIL_USER")
    pwd = email_pass or os.environ.get("GMAIL_PASS") or os.environ.get("EMAIL_PASS")

    if not user or not pwd:
        # Check config.json in current script directory
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    user = user or cfg.get("email") or cfg.get("user")
                    pwd = pwd or cfg.get("password") or cfg.get("app_password")
            except Exception:
                pass

    if not user or not pwd:
        raise ValueError(
            "Chưa có thông tin Gmail và Mật khẩu (App Password). "
            "Vui lòng cung cấp qua tham số, biến môi trường (GMAIL_USER, GMAIL_PASS) hoặc file config.json"
        )

    # Clean password (remove spaces if user copied with spaces e.g. 'abcd efgh ijkl mnop')
    pwd = pwd.replace(" ", "").strip()
    return user.strip(), pwd

class GmailClient:
    def __init__(self, user: str, password: str, host: str = "imap.gmail.com", port: int = 993):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.imap: Optional[imaplib.IMAP4_SSL] = None

    def connect(self):
        """Connect and login to IMAP server."""
        try:
            self.imap = imaplib.IMAP4_SSL(self.host, self.port)
            self.imap.login(self.user, self.password)
        except imaplib.IMAP4.error as e:
            err_msg = str(e)
            if "AUTHENTICATIONFAILED" in err_msg or "Invalid credentials" in err_msg:
                raise PermissionError(
                    "Đăng nhập thất bại (Invalid credentials).\n"
                    "LƯU Ý QUAN TRỌNG: Google đã chặn mật khẩu thông thường trên IMAP. "
                    "Bạn cần dùng 'Mật khẩu ứng dụng' (App Password - 16 ký tự).\n"
                    "Cách lấy: Bật xác minh 2 bước -> Truy cập https://myaccount.google.com/apppasswords -> Tạo mật khẩu ứng dụng."
                ) from e
            raise RuntimeError(f"Lỗi kết nối IMAP: {err_msg}") from e

    def close(self):
        """Close IMAP connection cleanly."""
        if self.imap:
            try:
                self.imap.close()
            except Exception:
                pass
            try:
                self.imap.logout()
            except Exception:
                pass
            self.imap = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_today_emails(self, folder: str = "INBOX", limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch emails received today (SINCE current date)."""
        if not self.imap:
            self.connect()

        self.imap.select(folder)
        date_str = get_imap_date_str()
        search_criteria = f'(SINCE "{date_str}")'

        status, data = self.imap.search(None, search_criteria)
        if status != "OK" or not data or not data[0]:
            return []

        email_ids = data[0].split()
        # Sort descending (newest first)
        email_ids.reverse()

        results = []
        for eid in email_ids[:limit]:
            eid_str = eid.decode("utf-8")
            status, msg_data = self.imap.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = clean_header_val(msg.get("Subject", "(Không có tiêu đề)"))
            from_sender = clean_header_val(msg.get("From", "(Không rõ người gửi)"))
            to_recipient = clean_header_val(msg.get("To", ""))
            date_header = msg.get("Date", "")
            body_snippet = extract_body(msg, max_chars=400)

            results.append({
                "id": eid_str,
                "subject": subject,
                "from": from_sender,
                "to": to_recipient,
                "date": date_header,
                "snippet": body_snippet
            })

        return results

    def read_email(self, email_id: str, folder: str = "INBOX") -> Dict[str, Any]:
        """Read full details of a specific email by ID."""
        if not self.imap:
            self.connect()

        self.imap.select(folder)
        status, msg_data = self.imap.fetch(email_id.encode("utf-8"), "(RFC822)")
        if status != "OK" or not msg_data or not msg_data[0]:
            raise ValueError(f"Không tìm thấy email với ID: {email_id}")

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = clean_header_val(msg.get("Subject", "(Không có tiêu đề)"))
        from_sender = clean_header_val(msg.get("From", "(Không rõ người gửi)"))
        to_recipient = clean_header_val(msg.get("To", ""))
        date_header = msg.get("Date", "")
        full_body = extract_body(msg, max_chars=10000)

        return {
            "id": email_id,
            "subject": subject,
            "from": from_sender,
            "to": to_recipient,
            "date": date_header,
            "body": full_body
        }
