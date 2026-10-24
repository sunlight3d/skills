#!/usr/bin/env python3
"""
Downsize MP4 (Media Studio Engine)
Giảm dung lượng file video (MP4, MOV, MKV, AVI, TS...) mà không làm giảm độ phân giải.
Sử dụng bộ mã hóa H.265/HEVC (CRF 28) + AAC 128k, hỗ trợ nén ảnh thông minh (JPEG step-down)
và tùy chọn loại bỏ khoảng lặng âm thanh (silence removal).
"""

import os
import sys
import re
import math
import shutil
import tempfile
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SUPPORTED_VIDEOS = {'.mp4', '.mov', '.avi', '.mkv', '.mpeg', '.mpg', '.wmv', '.flv', '.ts', '.m4v'}
SUPPORTED_IMAGES = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

def find_binary(name: str) -> Optional[str]:
    """Tìm đường dẫn binary ffmpeg hoặc ffprobe trên macOS/Linux/Windows"""
    paths_to_check = [
        f"/opt/homebrew/bin/{name}",
        f"/usr/local/bin/{name}",
        f"/usr/bin/{name}",
        f"/bin/{name}",
        name
    ]
    for p in paths_to_check:
        found = shutil.which(p)
        if found:
            return found
    return None

def format_size(size_bytes: int) -> str:
    """Định dạng byte thành KB, MB, GB dễ đọc"""
    if size_bytes == 0:
        return "0 B"
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def format_duration(seconds: float) -> str:
    """Định dạng số giây thành giờ:phút:giây"""
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def get_media_info(file_path: Path, ffprobe_bin: str) -> Dict[str, any]:
    """Lấy thông tin độ phân giải, thời lượng, codec của video bằng ffprobe"""
    info = {
        "duration": 0.0,
        "width": None,
        "height": None,
        "resolution": "Unknown",
        "codec": "Unknown",
        "fps": "Unknown"
    }
    if not ffprobe_bin or not file_path.exists():
        return info

    cmd = [
        ffprobe_bin,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name,r_frame_rate",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1",
        str(file_path)
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        for line in res.stdout.strip().splitlines():
            line = line.strip()
            if not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k == "width":
                info["width"] = int(v)
            elif k == "height":
                info["height"] = int(v)
            elif k == "codec_name":
                info["codec"] = v
            elif k == "duration":
                try:
                    info["duration"] = float(v)
                except ValueError:
                    pass
            elif k == "r_frame_rate":
                info["fps"] = v
        if info["width"] and info["height"]:
            info["resolution"] = f"{info['width']}x{info['height']}"
    except Exception:
        pass

    # Nếu duration vẫn bằng 0, thử lấy duration từ format
    if info["duration"] == 0.0:
        cmd2 = [
            ffprobe_bin, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        try:
            res2 = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            info["duration"] = float(res2.stdout.strip())
        except Exception:
            pass

    return info

def detect_silences(file_path: Path, ffmpeg_bin: str, min_duration_ms: int, silence_db: int) -> List[Tuple[str, str]]:
    """Phát hiện các khoảng lặng âm thanh trong file video"""
    d_sec = min_duration_ms / 1000.0
    cmd = [
        ffmpeg_bin, "-i", str(file_path),
        "-af", f"silencedetect=noise={silence_db}dB:d={d_sec}",
        "-f", "null", "-", "-nostats"
    ]
    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        starts = re.findall(r"silence_start:\s+([\d\.]+)", process.stderr)
        ends = re.findall(r"silence_end:\s+([\d\.]+)", process.stderr)
        return list(zip(starts, ends))
    except Exception as e:
        print(f"⚠️ Cảnh báo lỗi quét khoảng lặng: {e}", file=sys.stderr)
        return []

def compress_video(
    input_path: Path,
    output_dir: Path,
    ffmpeg_bin: str,
    ffprobe_bin: str,
    crf: int = 28,
    preset: str = "medium",
    remove_silence: bool = False,
    silence_thresh_ms: int = 500,
    silence_db: int = -30,
    overwrite: bool = False,
    nvenc: bool = False
) -> Dict[str, any]:
    """Nén video bằng H.265 CRF 28 - Giữ nguyên 100% độ phân giải"""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{input_path.stem}.mp4"

    orig_size = input_path.stat().st_size
    info_before = get_media_info(input_path, ffprobe_bin)
    
    result = {
        "type": "video",
        "file": input_path.name,
        "input_path": str(input_path.resolve()),
        "output_path": str(output_path.resolve()),
        "orig_size": orig_size,
        "new_size": 0,
        "saved_bytes": 0,
        "saved_pct": 0.0,
        "orig_resolution": info_before["resolution"],
        "new_resolution": "Unknown",
        "duration": info_before["duration"],
        "status": "pending",
        "message": ""
    }

    if output_path.exists() and not overwrite:
        new_size = output_path.stat().st_size
        info_after = get_media_info(output_path, ffprobe_bin)
        result["new_size"] = new_size
        result["saved_bytes"] = orig_size - new_size
        result["saved_pct"] = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0
        result["new_resolution"] = info_after["resolution"]
        result["status"] = "skipped"
        result["message"] = f"Bỏ qua: File đầu ra đã tồn tại ({output_path.name})"
        return result

    codec_desc = "hevc_nvenc (NVIDIA GPU)" if nvenc else "libx265 (HEVC)"
    preset_desc = "p4" if nvenc else preset
    print(f"\n==================================================")
    print(f"🎬 ĐANG ÉP VIDEO: {input_path.name}")
    print(f"📦 DUNG LƯỢNG GỐC: {format_size(orig_size)} | 📺 ĐỘ PHÂN GIẢI: {info_before['resolution']} | ⏱ ĐỘ DÀI: {format_duration(info_before['duration'])}")
    print(f"⚙️ CẤU HÌNH: Codec={codec_desc}, CRF={crf}, Preset={preset_desc}, Audio=AAC 128k")

    v_filter_path, a_filter_path = None, None
    has_filters = False

    try:
        if remove_silence:
            print(f"🔍 Đang dò tìm khoảng lặng (ngưỡng: >{silence_thresh_ms}ms, tạp âm: {silence_db}dB)...")
            silences = detect_silences(input_path, ffmpeg_bin, silence_thresh_ms, silence_db)
            if silences:
                print(f"✂️ Phát hiện {len(silences)} khoảng lặng. Đang chuẩn bị bộ lọc cắt bỏ...")
                drops = "-".join([f"between(t,{s},{e})" for s, e in silences])
                v_fd, v_filter_path = tempfile.mkstemp(suffix=".txt", text=True)
                a_fd, a_filter_path = tempfile.mkstemp(suffix=".txt", text=True)
                with os.fdopen(v_fd, 'w', encoding='utf-8') as f:
                    f.write(f"select='1-{drops}',setpts=N/FRAME_RATE/TB")
                with os.fdopen(a_fd, 'w', encoding='utf-8') as f:
                    f.write(f"aselect='1-{drops}',asetpts=N/SR/TB")
                has_filters = True
            else:
                print("ℹ️ Không tìm thấy khoảng lặng đáng kể nào.")

        if nvenc:
            cmd = [
                ffmpeg_bin, "-y", "-hwaccel", "auto",
                "-i", str(input_path),
                "-c:v", "hevc_nvenc",
                "-cq", str(crf),
                "-preset", "p4",
                "-pix_fmt", "yuv420p",
                "-tag:v", "hvc1"
            ]
        else:
            cmd = [
                ffmpeg_bin, "-y", "-hwaccel", "auto",
                "-i", str(input_path),
                "-c:v", "libx265",
                "-crf", str(crf),
                "-preset", preset,
                "-pix_fmt", "yuv420p",
                "-tag:v", "hvc1"
            ]
        if has_filters:
            cmd.extend(["-filter_script:v", v_filter_path, "-filter_script:a", a_filter_path])
        cmd.extend(["-c:a", "aac", "-b:a", "128k", str(output_path)])

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', errors='replace',
            universal_newlines=True
        )

        time_regex = re.compile(r"time=(\d{2}):(\d{2}):(\d{2}\.\d+)")
        total_sec = info_before["duration"]

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            if "frame=" in line or "fps=" in line:
                match = time_regex.search(line)
                if match and total_sec > 0:
                    h, m, s = match.groups()
                    current_sec = int(h) * 3600 + int(m) * 60 + float(s)
                    pct = min(100.0, (current_sec / total_sec) * 100.0)
                    print(f"\r⚡ Tiến trình: {pct:.1f}% ({format_duration(current_sec)} / {format_duration(total_sec)})", end="", flush=True)

        process.wait()
        print() # Dòng mới

        if process.returncode == 0:
            new_size = output_path.stat().st_size
            info_after = get_media_info(output_path, ffprobe_bin)
            saved_bytes = orig_size - new_size
            saved_pct = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0

            result["new_size"] = new_size
            result["saved_bytes"] = saved_bytes
            result["saved_pct"] = saved_pct
            result["new_resolution"] = info_after["resolution"]
            result["status"] = "success"
            result["message"] = "Nén thành công"

            print(f"✅ THÀNH CÔNG: {output_path.name}")
            print(f"   Dung lượng mới: {format_size(new_size)} (Giảm {format_size(saved_bytes)} / -{saved_pct:.1f}%)")
            print(f"   Độ phân giải:   {info_before['resolution']} ➔ {info_after['resolution']} (Giữ nguyên chuẩn xác)")
        else:
            result["status"] = "error"
            result["message"] = f"FFmpeg trả về mã lỗi {process.returncode}"
            print(f"❌ THẤT BẠI: {input_path.name} (Lỗi mã {process.returncode})")

    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        print(f"💥 Lỗi hệ thống: {e}")
    finally:
        if v_filter_path and os.path.exists(v_filter_path):
            try: os.remove(v_filter_path)
            except: pass
        if a_filter_path and os.path.exists(a_filter_path):
            try: os.remove(a_filter_path)
            except: pass

    return result

def compress_image(
    input_path: Path,
    output_dir: Path,
    target_mb: float = 1.0,
    overwrite: bool = False
) -> Dict[str, any]:
    """Nén ảnh bằng thuật toán Step-down thích ứng để đạt mục tiêu target_mb"""
    try:
        import io
        from PIL import Image
    except ImportError:
        return {
            "type": "image",
            "file": input_path.name,
            "status": "error",
            "message": "Thiếu thư viện Pillow (pip install pillow)"
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{input_path.stem}.jpg"
    orig_size = input_path.stat().st_size
    target_bytes = int(target_mb * 1024 * 1024)

    result = {
        "type": "image",
        "file": input_path.name,
        "input_path": str(input_path.resolve()),
        "output_path": str(output_path.resolve()),
        "orig_size": orig_size,
        "new_size": 0,
        "saved_bytes": 0,
        "saved_pct": 0.0,
        "orig_resolution": "Unknown",
        "new_resolution": "Unknown",
        "status": "pending",
        "message": ""
    }

    if output_path.exists() and not overwrite:
        new_size = output_path.stat().st_size
        result["new_size"] = new_size
        result["saved_bytes"] = orig_size - new_size
        result["saved_pct"] = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0
        result["status"] = "skipped"
        result["message"] = f"Bỏ qua: File ảnh đã tồn tại ({output_path.name})"
        return result

    print(f"\n==================================================")
    print(f"🖼️ ĐANG ÉP ẢNH: {input_path.name}")
    print(f"📦 DUNG LƯỢNG GỐC: {format_size(orig_size)} | 📉 MỤC TIÊU: ≤ {target_mb} MB")

    try:
        with Image.open(input_path) as img:
            result["orig_resolution"] = f"{img.width}x{img.height}"
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            if orig_size <= target_bytes:
                img.save(output_path, format="JPEG", quality=95, optimize=True)
                new_size = output_path.stat().st_size
                result["new_size"] = new_size
                result["new_resolution"] = f"{img.width}x{img.height}"
                result["status"] = "success"
                result["message"] = "Đã nhỏ hơn mục tiêu, lưu JPEG chuẩn 95%"
                print(f"✅ XONG: {output_path.name} (Đạt chuẩn)")
                return result

            quality = 90
            scale = 1.0
            best_buffer = None

            while True:
                buffer = io.BytesIO()
                if scale < 1.0:
                    new_w = max(1, int(img.width * scale))
                    new_h = max(1, int(img.height * scale))
                    temp_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                else:
                    temp_img = img

                temp_img.save(buffer, format="JPEG", quality=quality, optimize=True)
                sz = buffer.tell()
                best_buffer = buffer

                if sz <= target_bytes or (quality <= 20 and scale <= 0.3):
                    break

                if quality > 30:
                    quality -= 10
                else:
                    scale -= 0.15

            with open(output_path, "wb") as f:
                f.write(best_buffer.getvalue())

            new_size = output_path.stat().st_size
            saved_bytes = orig_size - new_size
            saved_pct = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0

            with Image.open(output_path) as out_img:
                result["new_resolution"] = f"{out_img.width}x{out_img.height}"

            result["new_size"] = new_size
            result["saved_bytes"] = saved_bytes
            result["saved_pct"] = saved_pct
            result["status"] = "success"
            print(f"✅ XONG ẢNH: {output_path.name} | MỚI: {format_size(new_size)} (Giảm {saved_pct:.1f}%)")

    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        print(f"💥 Lỗi nén ảnh {input_path.name}: {e}")

    return result

def main():
    parser = argparse.ArgumentParser(
        description="Downsize MP4 - Nén video H.265/HEVC giữ nguyên độ phân giải & nén ảnh thông minh"
    )
    parser.add_argument("inputs", nargs="*", help="File(s) hoặc Thư mục chứa video/ảnh cần nén")
    parser.add_argument("-i", "--input", dest="opt_input", help="Đường dẫn file hoặc thư mục đầu vào")
    parser.add_argument("-o", "--output-dir", help="Thư mục xuất file (mặc định: subfolder 'output' tại nơi chứa file gốc)")
    parser.add_argument("--crf", type=int, default=28, help="Hệ số chất lượng CRF video x265 (mặc định: 28, khoảng tối ưu 24-30)")
    parser.add_argument("--preset", default="medium", choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"], help="Tốc độ mã hóa preset x265 (mặc định: medium)")
    parser.add_argument("--remove-silence", action="store_true", help="Bật tính năng phát hiện và tự động cắt bỏ khoảng lặng âm thanh")
    parser.add_argument("--silence-thresh-ms", type=int, default=500, help="Độ dài tối thiểu của khoảng lặng tính bằng ms (mặc định: 500)")
    parser.add_argument("--silence-db", type=int, default=-30, help="Ngưỡng âm lượng khoảng lặng dB (mặc định: -30)")
    parser.add_argument("--target-img-mb", type=float, default=1.0, help="Dung lượng tối đa mong muốn cho ảnh tính bằng MB (mặc định: 1.0)")
    parser.add_argument("--overwrite", action="store_true", help="Ghi đè file đầu ra nếu đã tồn tại")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ liệt kê và quét thông tin file mà không thực hiện nén")
    parser.add_argument("--open", action="store_true", help="Tự động mở thư mục chứa file nén sau khi hoàn thành")
    parser.add_argument("--nvenc", action="store_true", help="Sử dụng tăng tốc GPU NVIDIA NVENC (hevc_nvenc) siêu tốc")
    parser.add_argument("--gui", action="store_true", help="Khởi chạy giao diện Desktop PyQt6 ShrinkX Media Studio")

    args = parser.parse_args()

    # Chế độ khởi chạy giao diện GUI
    if args.gui:
        gui_script = Path("/Volumes/data/code/connect/downsize_mp4/downsize_mp4.py")
        if gui_script.exists():
            print(f"🚀 Đang khởi chạy giao diện Desktop UI: {gui_script}...")
            subprocess.run([sys.executable, str(gui_script)])
            return
        else:
            print(f"❌ Không tìm thấy script GUI tại {gui_script}", file=sys.stderr)
            sys.exit(1)

    # Thu thập danh sách đường dẫn đầu vào
    input_candidates = []
    if args.opt_input:
        input_candidates.append(args.opt_input)
    if args.inputs:
        input_candidates.extend(args.inputs)

    if not input_candidates:
        parser.print_help()
        print("\n[LỖI] Vui lòng truyền ít nhất một đường dẫn file hoặc thư mục cần nén.", file=sys.stderr)
        sys.exit(1)

    # Tìm ffmpeg và ffprobe
    ffmpeg_bin = find_binary("ffmpeg")
    ffprobe_bin = find_binary("ffprobe")
    if not ffmpeg_bin or not ffprobe_bin:
        print("❌ [LỖI] Không tìm thấy ffmpeg hoặc ffprobe trên hệ thống!", file=sys.stderr)
        print("Trên macOS, vui lòng cài đặt bằng: brew install ffmpeg", file=sys.stderr)
        print("Trên Ubuntu/Debian: sudo apt update && sudo apt install -y ffmpeg", file=sys.stderr)
        sys.exit(1)

    video_files: List[Path] = []
    image_files: List[Path] = []

    for item_str in input_candidates:
        item_path = Path(item_str).expanduser().resolve()
        if not item_path.exists():
            print(f"⚠️ Cảnh báo: Đường dẫn không tồn tại: {item_path}", file=sys.stderr)
            continue
        if item_path.is_file():
            ext = item_path.suffix.lower()
            if ext in SUPPORTED_VIDEOS:
                video_files.append(item_path)
            elif ext in SUPPORTED_IMAGES:
                image_files.append(item_path)
            else:
                print(f"⚠️ Bỏ qua file định dạng không hỗ trợ: {item_path.name}")
        elif item_path.is_dir():
            for f in sorted(item_path.iterdir()):
                if f.is_file() and f.parent.name != "output":
                    ext = f.suffix.lower()
                    if ext in SUPPORTED_VIDEOS:
                        video_files.append(f)
                    elif ext in SUPPORTED_IMAGES:
                        image_files.append(f)

    total_count = len(video_files) + len(image_files)
    if total_count == 0:
        print("⚠️ Không tìm thấy file Video hay Ảnh hợp lệ nào để xử lý.")
        sys.exit(0)

    print(f"🎯 TỔNG SỐ MEDIA CẦN XỬ LÝ: {total_count} (Video: {len(video_files)}, Ảnh: {len(image_files)})")

    if args.dry_run:
        print("\n--- CHẾ ĐỘ QUÉT THỬ THÔNG TIN (DRY-RUN) ---")
        for vf in video_files:
            inf = get_media_info(vf, ffprobe_bin)
            sz = vf.stat().st_size
            print(f"🎬 [Video] {vf.name}: {format_size(sz)} | Độ phân giải: {inf['resolution']} | Thời lượng: {format_duration(inf['duration'])}")
        for img in image_files:
            sz = img.stat().st_size
            print(f"🖼️ [Ảnh]   {img.name}: {format_size(sz)}")
        print("\nHoàn tất quét thử. Không có file nào bị thay đổi.")
        return

    results = []
    output_dirs_to_open = set()

    for vf in video_files:
        dest_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else (vf.parent / "output")
        res = compress_video(
            input_path=vf,
            output_dir=dest_dir,
            ffmpeg_bin=ffmpeg_bin,
            ffprobe_bin=ffprobe_bin,
            crf=args.crf,
            preset=args.preset,
            remove_silence=args.remove_silence,
            silence_thresh_ms=args.silence_thresh_ms,
            silence_db=args.silence_db,
            overwrite=args.overwrite,
            nvenc=args.nvenc
        )
        results.append(res)
        if res.get("status") in ("success", "skipped"):
            output_dirs_to_open.add(dest_dir)

    for img in image_files:
        dest_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else (img.parent / "output")
        res = compress_image(
            input_path=img,
            output_dir=dest_dir,
            target_mb=args.target_img_mb,
            overwrite=args.overwrite
        )
        results.append(res)
        if res.get("status") in ("success", "skipped"):
            output_dirs_to_open.add(dest_dir)

    # Báo cáo tổng kết
    print("\n" + "="*70)
    print("📊 BÁO CÁO TỔNG KẾT NÉN MEDIA (DOWNSIZE MP4)")
    print("="*70)

    total_orig = sum(r.get("orig_size", 0) for r in results if r.get("status") in ("success", "skipped"))
    total_new = sum(r.get("new_size", 0) for r in results if r.get("status") in ("success", "skipped"))
    total_saved = total_orig - total_new
    total_pct = (total_saved / total_orig * 100) if total_orig > 0 else 0

    for r in results:
        status_icon = "✅" if r["status"] == "success" else ("⏭️" if r["status"] == "skipped" else "❌")
        if r["type"] == "video":
            print(f"{status_icon} Video: {r['file']}")
            if r["status"] in ("success", "skipped"):
                print(f"   - Dung lượng:  {format_size(r['orig_size'])} ➔ {format_size(r['new_size'])} (Giảm {r['saved_pct']:.1f}%)")
                print(f"   - Độ phân giải: {r['orig_resolution']} ➔ {r['new_resolution']} (100% giữ nguyên)")
                print(f"   - File kết quả: {r['output_path']}")
            else:
                print(f"   - Lỗi: {r.get('message', 'Unknown error')}")
        else:
            print(f"{status_icon} Ảnh: {r['file']}")
            if r["status"] in ("success", "skipped"):
                print(f"   - Dung lượng:  {format_size(r['orig_size'])} ➔ {format_size(r['new_size'])} (Giảm {r['saved_pct']:.1f}%)")
                print(f"   - File kết quả: {r['output_path']}")
            else:
                print(f"   - Lỗi: {r.get('message', 'Unknown error')}")

    print("-" * 70)
    print(f"🎉 TỔNG KẾT:")
    print(f"   Dung lượng ban đầu: {format_size(total_orig)}")
    print(f"   Dung lượng sau nén: {format_size(total_new)}")
    print(f"   Tiết kiệm được:     {format_size(total_saved)} ({total_pct:.1f}% dung lượng)")
    print("=" * 70)

    if args.open and output_dirs_to_open:
        for od in output_dirs_to_open:
            if sys.platform == "darwin":
                subprocess.run(["open", str(od)])
            elif sys.platform == "win32":
                subprocess.run(["explorer", str(od)])
            else:
                subprocess.run(["xdg-open", str(od)])

if __name__ == "__main__":
    main()
