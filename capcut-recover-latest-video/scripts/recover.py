#!/usr/bin/env python3
"""
CapCut Latest Video Recovery Tool
Recovers raw screen and camera recordings from CapCut when it hangs or crashes,
backs them up to a safe location, and terminates the hung process.
"""

import os
import sys
import glob
import shutil
import argparse
import subprocess
from datetime import datetime

VIDEO_RECORD_DIR = os.path.expanduser("~/Movies/CapCut/User Data/VideoRecord")
DEFAULT_BACKUP_DIR = os.path.expanduser("~/Movies/CapCut_Recording_Backup")

def find_ffprobe():
    for p in ["/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe", "ffprobe"]:
        if shutil.which(p):
            return p
    return None

def get_video_info(ffprobe_bin, file_path):
    if not ffprobe_bin or not os.path.exists(file_path):
        return None
    try:
        cmd = [
            ffprobe_bin,
            "-v", "error",
            "-show_entries", "format=duration:stream=width,height,codec_name,codec_type",
            "-of", "csv=p=0",
            file_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = res.stdout.strip().splitlines()
        info = {"duration": "Unknown", "resolution": "Unknown", "streams": []}
        for l in lines:
            parts = l.split(",")
            if len(parts) == 1:
                try:
                    dur_sec = float(parts[0])
                    m, s = divmod(int(dur_sec), 60)
                    info["duration"] = f"{m:02d}:{s:02d}"
                except ValueError:
                    pass
            elif len(parts) >= 3 and parts[0] == "video":
                info["resolution"] = f"{parts[1]}x{parts[2]}"
                info["streams"].append(f"video ({parts[1]}x{parts[2]})")
            elif len(parts) >= 1:
                info["streams"].append(parts[0])
        return info
    except Exception:
        return None

def get_latest_sessions(video_dir):
    if not os.path.exists(video_dir):
        return []
    
    # Match CapCut recordings
    patterns = [
        os.path.join(video_dir, "Capcut_Record*.mp4"),
        os.path.join(video_dir, "screen_*.mp4"),
        os.path.join(video_dir, "camera_*.mp4")
    ]
    files = []
    for pat in patterns:
        files.extend(glob.glob(pat))
    
    if not files:
        return []

    # Sort files by modification time descending
    files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

    # Group by session (files modified within 60 seconds of each other)
    sessions = []
    current_session = []
    last_mtime = None

    for f in files:
        mtime = os.path.getmtime(f)
        if last_mtime is None or abs(last_mtime - mtime) <= 60:
            current_session.append(f)
            last_mtime = mtime
        else:
            sessions.append(current_session)
            current_session = [f]
            last_mtime = mtime
    if current_session:
        sessions.append(current_session)

    return sessions

def kill_capcut():
    try:
        res = subprocess.run(["pkill", "-9", "-i", "capcut"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return res.returncode == 0
    except Exception as e:
        print(f"Lỗi khi dừng CapCut: {e}", file=sys.stderr)
        return False

def is_capcut_running():
    try:
        res = subprocess.run(["pgrep", "-i", "capcut"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return res.returncode == 0
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description="Khôi phục video CapCut mới nhất khi bị treo và đóng tiến trình.")
    parser.add_argument("--dest", default=DEFAULT_BACKUP_DIR, help="Thư mục lưu bản sao lưu (mặc định: ~/Movies/CapCut_Recording_Backup)")
    parser.add_argument("--no-kill", action="store_true", help="Không tự động tắt tiến trình CapCut")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ kiểm tra và liệt kê file mà không copy hay tắt CapCut")
    args = parser.parse_args()

    print("==================================================")
    print("🔍 CAPCUT LATEST VIDEO RECOVERY TOOL")
    print("==================================================")

    running_before = is_capcut_running()
    if running_before:
        print("⚠️ Phát hiện tiến trình CapCut đang chạy.")
    else:
        print("ℹ️ CapCut hiện không chạy (hoặc đã tắt).")

    sessions = get_latest_sessions(VIDEO_RECORD_DIR)
    if not sessions:
        print(f"❌ Không tìm thấy file quay nào trong thư mục: {VIDEO_RECORD_DIR}")
        sys.exit(1)

    latest_files = sessions[0]
    ffprobe_bin = find_ffprobe()

    print(f"\n📁 Tìm thấy {len(latest_files)} file quay trong phiên ghi hình mới nhất:")
    for f in latest_files:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")
        info = get_video_info(ffprobe_bin, f)
        dur_str = f", Thời lượng: {info['duration']}" if info and info['duration'] != "Unknown" else ""
        res_str = f", Độ phân giải: {info['resolution']}" if info and info['resolution'] != "Unknown" else ""
        print(f"  • {os.path.basename(f)} ({size_mb:.1f} MB{dur_str}{res_str}) - Ghi lúc: {mtime}")

    if args.dry_run:
        print("\n[DRY RUN] Hoàn tất kiểm tra (không copy, không kill tiến trình).")
        sys.exit(0)

    # Prepare destination directory
    os.makedirs(args.dest, exist_ok=True)
    saved_files = []

    print(f"\n🚀 Đang sao lưu vào: {args.dest} ...")
    for f in latest_files:
        dest_file = os.path.join(args.dest, os.path.basename(f))
        shutil.copy2(f, dest_file)
        saved_files.append(dest_file)
        print(f"  ✅ Đã lưu: {dest_file}")

    # Terminate CapCut if requested
    if not args.no_kill and running_before:
        print("\n🛑 Đang tắt hẳn tiến trình CapCut bị treo...")
        killed = kill_capcut()
        if killed or not is_capcut_running():
            print("  ✅ Đã giải phóng hoàn toàn CapCut và các tiến trình phụ.")
        else:
            print("  ⚠️ Không thể tắt hoặc tiến trình đã tự thoát trước đó.")
    elif args.no_kill:
        print("\nℹ️ Bỏ qua bước tắt CapCut (tuỳ chọn --no-kill).")

    print("\n==================================================")
    print("🎉 HOÀN TẤT CỨU DỮ LIỆU THÀNH CÔNG!")
    print("==================================================")
    for sf in saved_files:
        print(f"👉 File an toàn: file://{sf}")

if __name__ == "__main__":
    main()
