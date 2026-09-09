import sys
import os
import json
from typing import Optional, List, Dict, Any

# Ensure utf-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from mcp.server.fastmcp import FastMCP
from email_client import GmailClient, load_credentials

# Initialize FastMCP Server
mcp = FastMCP("Gmail IMAP Server")

@mcp.tool()
def check_connection(email_user: Optional[str] = None, email_pass: Optional[str] = None) -> str:
    """
    Kiểm tra kết nối và xác thực tới Gmail IMAP.
    
    Args:
        email_user: Địa chỉ Gmail (ví dụ: user@gmail.com). Nếu bỏ trống, sẽ đọc từ config.json hoặc biến môi trường.
        email_pass: Mật khẩu ứng dụng Gmail (App Password 16 ký tự). Nếu bỏ trống, sẽ đọc từ config.json hoặc biến môi trường.
    """
    try:
        user, pwd = load_credentials(email_user, email_pass)
        with GmailClient(user, pwd) as client:
            return json.dumps({
                "status": "success",
                "message": f"Kết nối thành công tới tài khoản {user}!"
            }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def get_today_emails(
    limit: int = 20,
    email_user: Optional[str] = None,
    email_pass: Optional[str] = None
) -> str:
    """
    Tải danh sách các email mới nhất nhận được trong ngày hôm nay.
    
    Args:
        limit: Số lượng email tối đa cần lấy (mặc định 20).
        email_user: Địa chỉ Gmail (tùy chọn).
        email_pass: Mật khẩu ứng dụng Gmail (App Password 16 ký tự, tùy chọn).
    """
    try:
        user, pwd = load_credentials(email_user, email_pass)
        with GmailClient(user, pwd) as client:
            emails = client.get_today_emails(folder="INBOX", limit=limit)
            return json.dumps({
                "status": "success",
                "total_found": len(emails),
                "emails": emails
            }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def read_email_detail(
    email_id: str,
    email_user: Optional[str] = None,
    email_pass: Optional[str] = None
) -> str:
    """
    Đọc chi tiết toàn bộ nội dung của một email theo ID.
    
    Args:
        email_id: ID của email (lấy từ danh sách get_today_emails).
        email_user: Địa chỉ Gmail (tùy chọn).
        email_pass: Mật khẩu ứng dụng Gmail (App Password, tùy chọn).
    """
    try:
        user, pwd = load_credentials(email_user, email_pass)
        with GmailClient(user, pwd) as client:
            detail = client.read_email(email_id=email_id, folder="INBOX")
            return json.dumps({
                "status": "success",
                "email": detail
            }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mcp.run()
