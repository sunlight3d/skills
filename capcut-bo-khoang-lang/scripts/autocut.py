#!/usr/bin/env python3
"""
CapCut Bỏ Khoảng Lặng (AutoCut Media Studio)
Tự động phát hiện và cắt bỏ hoàn toàn các khoảng lặng trong video hoặc dự án CapCut.
Hỗ trợ:
  1. Tạo / nhân bản Timeline CapCut (draft_info.json) chứa các đoạn cắt liền mạch.
  2. Xuất trực tiếp file MP4 chuẩn YouTube 1080p 60fps bằng tăng tốc phần cứng VideoToolbox.
"""

import os
import sys
import subprocess
import re
import time
import json
import uuid
import copy
import shutil
import argparse
from pathlib import Path

DEFAULT_CAPCUT_DRAFT_DIR = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}", flush=True)

def check_dependencies():
    for cmd in ["ffmpeg", "ffprobe"]:
        if not shutil.which(cmd):
            sys.exit(f"❌ Lỗi: Không tìm thấy '{cmd}' trên hệ thống. Vui lòng cài đặt ffmpeg: brew install ffmpeg")

def get_media_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(res.stdout.strip())
    except:
        return 0.0

def detect_speech_intervals(file_path: str, min_start: float = 0.0, noise_db: int = -30, min_silence_sec: float = 0.5, pad_sec: float = 0.15):
    """
    Quét tìm các đoạn nói (bỏ khoảng lặng) sử dụng bộ lọc silencedetect của ffmpeg.
    pad_sec: đệm thêm thời gian trước và sau khoảng lặng để tránh bị cụt âm cuối từ.
    """
    total_dur = get_media_duration(file_path)
    if total_dur <= 0:
        return [], 0.0, 0.0

    cmd = [
        "ffmpeg", "-i", file_path,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence_sec}",
        "-vn", "-f", "null", "-"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

    starts = [float(x) for x in re.findall(r"silence_start:\s+([\d\.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s+([\d\.]+)", proc.stderr)]

    silence_spans = list(zip(starts, ends))
    speech = []
    curr = min_start

    for s_start, s_end in silence_spans:
        if s_end < min_start:
            continue
        sp_start = max(min_start, curr - pad_sec if curr > min_start else min_start)
        sp_end = min(total_dur, s_start + pad_sec)
        if sp_end - sp_start > 0.15:
            speech.append((sp_start, sp_end))
        curr = max(min_start, s_end - pad_sec)

    if curr < total_dur:
        sp_start = max(min_start, curr - pad_sec if curr > min_start else min_start)
        speech.append((sp_start, total_dur))

    # Hợp nhất các đoạn giao thoa
    merged = []
    for st, en in speech:
        if not merged or st > merged[-1][1]:
            merged.append([st, en])
        else:
            merged[-1][1] = max(merged[-1][1], en)

    total_speech_sec = sum(en - st for st, en in merged)
    return merged, total_dur, total_speech_sec

# ==============================================================================
# PHẦN 1: TỰ ĐỘNG TẠO DỰ ÁN CAPCUT (DRAFT TIMELINE)
# ==============================================================================

def get_latest_capcut_project(drafts_dir: str):
    root_meta_path = os.path.join(drafts_dir, "root_meta_info.json")
    if os.path.exists(root_meta_path):
        with open(root_meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        all_drafts = meta.get("all_draft_store", [])
        if all_drafts:
            for item in all_drafts:
                p_path = item.get("draft_fold_path")
                if p_path and os.path.exists(p_path) and not item.get("draft_is_invisible", False):
                    return p_path, item.get("draft_name", os.path.basename(p_path))

    # Fallback: Quét theo thời gian sửa đổi thư mục
    subdirs = [os.path.join(drafts_dir, d) for d in os.listdir(drafts_dir) if os.path.isdir(os.path.join(drafts_dir, d))]
    subdirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    for sd in subdirs:
        if os.path.exists(os.path.join(sd, "draft_info.json")):
            return sd, os.path.basename(sd)
    return None, None

def process_capcut_project(project_path: str = None, in_place: bool = False, noise_db: int = -30, min_silence: float = 0.5, pad: float = 0.15):
    drafts_dir = DEFAULT_CAPCUT_DRAFT_DIR
    if not os.path.exists(drafts_dir):
        sys.exit(f"❌ Không tìm thấy thư mục dự án CapCut tại: {drafts_dir}")

    if not project_path:
        project_path, proj_name = get_latest_capcut_project(drafts_dir)
        if not project_path:
            sys.exit("❌ Không tìm thấy dự án CapCut nào gần đây.")
        log(f"🔎 Tự động chọn dự án CapCut mới nhất: {proj_name}")
    else:
        if not os.path.isdir(project_path):
            candidate = os.path.join(drafts_dir, project_path)
            if os.path.isdir(candidate):
                project_path = candidate
            else:
                sys.exit(f"❌ Đường dẫn dự án không hợp lệ: {project_path}")
        proj_name = os.path.basename(project_path)

    draft_info_file = os.path.join(project_path, "draft_info.json")
    if not os.path.exists(draft_info_file):
        sys.exit(f"❌ Không tìm thấy draft_info.json trong {project_path}")

    # Xác định thư mục đích
    if in_place:
        target_dir = project_path
        target_name = proj_name
    else:
        target_name = f"{proj_name} (AutoCut)"
        target_dir = os.path.join(drafts_dir, target_name)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(project_path, target_dir)
        # Xóa file khóa nếu có
        lock_f = os.path.join(target_dir, ".locked")
        if os.path.exists(lock_f):
            os.remove(lock_f)

    log(f"🎬 Bắt đầu phân tích timeline dự án: {proj_name}...")
    with open(os.path.join(target_dir, "draft_info.json"), "r", encoding="utf-8") as f:
        draft = json.load(f)

    tracks = draft.get("tracks", [])
    if not tracks:
        sys.exit("❌ Không tìm thấy track video nào trong dự án.")

    video_track = None
    for t in tracks:
        if t.get("type") == "video":
            video_track = t
            break
    if not video_track:
        sys.exit("❌ Không tìm thấy track video trong dự án.")

    old_segments = video_track.get("segments", [])
    videos_mat = {v["id"]: v for v in draft.get("materials", {}).get("videos", [])}

    # Gom danh sách các video file xuất hiện trên timeline
    # Lưu template segment cho từng video
    video_templates = {}
    for seg in old_segments:
        m_id = seg.get("material_id")
        if m_id in videos_mat and m_id not in video_templates:
            video_templates[m_id] = {
                "file_path": videos_mat[m_id].get("path", ""),
                "template_seg": seg
            }

    # Thu thập các video độc nhất theo thứ tự xuất hiện
    unique_materials = []
    seen_ids = set()
    for seg in old_segments:
        m_id = seg.get("material_id")
        if m_id and m_id not in seen_ids:
            seen_ids.add(m_id)
            unique_materials.append(m_id)

    log(f"   Tìm thấy {len(unique_materials)} file video nguyên liệu trên Timeline.")

    new_segments = []
    curr_target_start = 0
    total_orig_sec = 0.0
    total_speech_sec = 0.0

    for m_id in unique_materials:
        info = video_templates.get(m_id)
        if not info or not os.path.exists(info["file_path"]):
            # Giữ nguyên segment cũ nếu không tìm thấy file vật lý
            for s in old_segments:
                if s.get("material_id") == m_id:
                    new_segments.append(s)
            continue

        fpath = info["file_path"]
        fname = os.path.basename(fpath)
        log(f"   🔍 Quét khoảng lặng: {fname}...")
        intervals, orig_dur, speech_dur = detect_speech_intervals(fpath, 0.0, noise_db, min_silence, pad)
        total_orig_sec += orig_dur
        total_speech_sec += speech_dur
        log(f"      -> {len(intervals)} đoạn nói | {speech_dur/60:.2f}m / {orig_dur/60:.2f}m (giảm {(1 - speech_dur/orig_dur)*100:.1f}%)")

        tpl_seg = info["template_seg"]
        for st, en in intervals:
            dur_us = int((en - st) * 1000000)
            src_st_us = int(st * 1000000)

            seg = copy.deepcopy(tpl_seg)
            seg["id"] = str(uuid.uuid4()).upper()
            seg["material_id"] = m_id
            seg["source_timerange"] = {"start": src_st_us, "duration": dur_us}
            seg["target_timerange"] = {"start": curr_target_start, "duration": dur_us}
            new_segments.append(seg)
            curr_target_start += dur_us

    video_track["segments"] = new_segments
    draft["duration"] = curr_target_start
    new_draft_id = str(uuid.uuid4()).upper()
    draft["id"] = new_draft_id
    draft["name"] = target_name

    # Lưu draft_info.json
    with open(os.path.join(target_dir, "draft_info.json"), "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)

    # Cập nhật draft_meta_info.json
    draft_meta_file = os.path.join(target_dir, "draft_meta_info.json")
    if os.path.exists(draft_meta_file):
        with open(draft_meta_file, "r", encoding="utf-8") as f:
            d_meta = json.load(f)
        d_meta["draft_id"] = new_draft_id
        d_meta["draft_name"] = target_name
        d_meta["draft_fold_path"] = target_dir
        d_meta["tm_duration"] = curr_target_start
        d_meta["tm_draft_modified"] = int(time.time() * 1000000)
        with open(draft_meta_file, "w", encoding="utf-8") as f:
            json.dump(d_meta, f, ensure_ascii=False)

    # Cập nhật root_meta_info.json để CapCut hiển thị ngay trong danh sách dự án
    root_meta_file = os.path.join(drafts_dir, "root_meta_info.json")
    if os.path.exists(root_meta_file):
        with open(root_meta_file, "r", encoding="utf-8") as f:
            root_meta = json.load(f)
        all_d = root_meta.get("all_draft_store", [])
        all_d = [d for d in all_d if d.get("draft_fold_path") != target_dir]
        entry = {
            "cloud_draft_cover": False,
            "cloud_draft_sync": False,
            "draft_cloud_last_action_download": False,
            "draft_cloud_purchase_info": "",
            "draft_cloud_template_id": "",
            "draft_cloud_tutorial_info": "",
            "draft_cloud_videocut_purchase_info": "",
            "draft_cover": os.path.join(target_dir, "draft_cover.jpg"),
            "draft_fold_path": target_dir,
            "draft_id": new_draft_id,
            "draft_is_ai_shorts": False,
            "draft_is_cloud_temp_draft": False,
            "draft_is_invisible": False,
            "draft_is_web_article_video": False,
            "draft_json_file": os.path.join(target_dir, "draft_info.json"),
            "draft_name": target_name,
            "draft_new_version": "",
            "draft_root_path": drafts_dir,
            "draft_timeline_materials_size": 0,
            "draft_type": "",
            "draft_web_article_video_enter_from": "",
            "streaming_edit_draft_ready": True,
            "tm_draft_cloud_completed": "",
            "tm_draft_cloud_entry_id": -1,
            "tm_draft_cloud_modified": 0,
            "tm_draft_cloud_parent_entry_id": -1,
            "tm_draft_cloud_space_id": -1,
            "tm_draft_cloud_user_id": -1,
            "tm_draft_create": int(time.time() * 1000000),
            "tm_draft_modified": int(time.time() * 1000000),
            "tm_draft_removed": 0,
            "tm_duration": curr_target_start
        }
        all_d.insert(0, entry)
        root_meta["all_draft_store"] = all_d
        with open(root_meta_file, "w", encoding="utf-8") as f:
            json.dump(root_meta, f, ensure_ascii=False)

    log("==================================================")
    log(f"🎉 TẠO DỰ ÁN CAPCUT THÀNH CÔNG: {target_name}")
    log(f"📁 Thư mục: {target_dir}")
    log(f"⏱ Thời lượng gốc: {total_orig_sec/60:.2f} phút -> Sau cắt: {curr_target_start/1e6/60:.2f} phút")
    log(f"✂️ Tổng số phân đoạn trên Timeline: {len(new_segments)}")
    log("💡 Bạn có thể mở CapCut lên, bấm Home để thấy ngay dự án mới này!")
    return target_dir

# ==============================================================================
# PHẦN 2: XUẤT TRỰC TIẾP FILE MP4 CHUẨN YOUTUBE
# ==============================================================================

def get_best_video_encoder():
    res = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True)
    if "h264_videotoolbox" in res.stdout:
        return "h264_videotoolbox"
    elif "h264_nvenc" in res.stdout:
        return "h264_nvenc"
    return "libx264"

def render_batch_chunk(input_path: str, intervals, out_path: str, encoder: str, bitrate: str = "6000k"):
    batch_start = intervals[0][0]
    batch_end = intervals[-1][1]

    terms = []
    for st, en in intervals:
        rel_st = max(0.0, st - batch_start)
        rel_en = en - batch_start
        terms.append(f"(gte(t,{rel_st:.3f})*lte(t,{rel_en:.3f}))")

    expr = "+".join(terms)
    v_filter = f"select='{expr}',setpts=N/FRAME_RATE/TB"
    a_filter = f"aselect='{expr}',asetpts=N/SR/TB"

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{batch_start:.3f}",
        "-to", f"{batch_end:.3f}",
        "-i", input_path,
        "-vf", v_filter,
        "-af", a_filter,
        "-c:v", encoder,
    ]
    if "videotoolbox" in encoder:
        cmd.extend(["-b:v", bitrate])
    elif "nvenc" in encoder:
        cmd.extend(["-cq", "23", "-b:v", bitrate])
    else:
        cmd.extend(["-preset", "fast", "-crf", "22"])

    cmd.extend(["-c:a", "aac", "-b:a", "128k", out_path])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def process_and_export_videos(files, output_file: str, noise_db: int = -30, min_silence: float = 0.5, pad: float = 0.15, bitrate: str = "6000k"):
    encoder = get_best_video_encoder()
    log(f"⚙️ Sử dụng bộ mã hóa phần cứng: {encoder}")

    work_dir = os.path.join(os.path.dirname(os.path.abspath(output_file)), ".autocut_cache")
    os.makedirs(work_dir, exist_ok=True)

    part_files = []
    t_start = time.time()

    for idx, fpath in enumerate(files, start=1):
        fname = os.path.basename(fpath)
        part_out = os.path.join(work_dir, f"part_{idx:02d}_{os.path.splitext(fname)[0]}.mp4")

        if os.path.exists(part_out) and os.path.getsize(part_out) > 500000:
            log(f"✅ Part {idx}/{len(files)} đã có sẵn, bỏ qua: {fname}")
            part_files.append(part_out)
            continue

        log(f"🎬 Đang xử lý Video {idx}/{len(files)}: {fname}...")
        intervals, orig_dur, speech_dur = detect_speech_intervals(fpath, 0.0, noise_db, min_silence, pad)
        log(f"   {len(intervals)} đoạn nói | {speech_dur/60:.2f}m / {orig_dur/60:.2f}m")

        batch_size = 40
        chunk_files = []
        for b_idx in range(0, len(intervals), batch_size):
            chunk = intervals[b_idx:b_idx + batch_size]
            chunk_file = os.path.join(work_dir, f"chunk_{idx:02d}_{b_idx:04d}.mp4")
            if not (os.path.exists(chunk_file) and os.path.getsize(chunk_file) > 10000):
                render_batch_chunk(fpath, chunk, chunk_file, encoder, bitrate)
            chunk_files.append(chunk_file)

        concat_list_file = os.path.join(work_dir, f"list_{idx:02d}.txt")
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for cf in chunk_files:
                f.write(f"file '{cf}'\n")

        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_file, "-c", "copy", part_out],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        for cf in chunk_files:
            try: os.remove(cf)
            except: pass
        try: os.remove(concat_list_file)
        except: pass

        part_files.append(part_out)
        log(f"   Hoàn thành Part {idx}: {os.path.getsize(part_out)/(1024*1024):.1f} MB")

    # Ghép nối nếu có nhiều file
    if len(part_files) == 1:
        shutil.copy2(part_files[0], output_file)
    else:
        log("🔗 Đang ghép toàn bộ các phần thành 1 file video hoàn chỉnh...")
        final_list = os.path.join(work_dir, "final_concat.txt")
        with open(final_list, "w", encoding="utf-8") as f:
            for pf in part_files:
                f.write(f"file '{pf}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", final_list, "-c", "copy", output_file],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        try: os.remove(final_list)
        except: pass

    elapsed = time.time() - t_start
    final_dur = get_media_duration(output_file) / 60.0
    final_size = os.path.getsize(output_file) / (1024 * 1024)

    log("==================================================")
    log(f"🎉 XUẤT VIDEO YOUTUBE THÀNH CÔNG!")
    log(f"📁 Đường dẫn file: {output_file}")
    log(f"⏱ Thời lượng: {final_dur:.2f} phút")
    log(f"📦 Dung lượng: {final_size:.1f} MB")
    log(f"⚡ Thời gian xử lý: {elapsed/60:.2f} phút")
    return output_file

def main():
    check_dependencies()
    parser = argparse.ArgumentParser(description="CapCut Bỏ Khoảng Lặng & Tự Động Ghép Video YouTube")
    parser.add_argument("input", nargs="?", default=None, help="Đường dẫn file video, thư mục video, hoặc tên/đường dẫn dự án CapCut")
    parser.add_argument("--capcut", action="store_true", help="Chế độ tạo/cập nhật Timeline trong CapCut")
    parser.add_argument("--export", action="store_true", help="Chế độ xuất thẳng ra file video MP4")
    parser.add_argument("--in-place", action="store_true", help="Ghi đè trực tiếp dự án CapCut thay vì nhân bản")
    parser.add_argument("-o", "--output", help="Đường dẫn file MP4 đầu ra")
    parser.add_argument("--noise-db", type=int, default=-30, help="Ngưỡng tiếng ồn tính là khoảng lặng (dB), mặc định: -30")
    parser.add_argument("--min-silence", type=float, default=0.5, help="Độ dài tối thiểu của khoảng lặng (giây), mặc định: 0.5")
    parser.add_argument("--pad", type=float, default=0.15, help="Đệm thời gian trước và sau tiếng nói (giây), mặc định: 0.15")
    parser.add_argument("--bitrate", default="6000k", help="Bitrate video khi xuất MP4 (mặc định: 6000k)")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ quét thống kê thời lượng và khoảng lặng, không ghi đè hay render")

    args = parser.parse_args()

    # Mặc định nếu không chỉ định cờ:
    # Nếu input là thư mục hoặc file video -> Chế độ xuất video
    # Nếu input là None hoặc có --capcut -> Chế độ CapCut draft
    target_input = args.input

    if args.dry_run:
        target = target_input if target_input else os.getcwd()
        if os.path.isfile(target):
            files = [target]
        elif os.path.isdir(target):
            files = [os.path.join(target, f) for f in sorted(os.listdir(target)) if f.lower().endswith(('.mov', '.mp4', '.mkv', '.avi'))]
        else:
            sys.exit(f"❌ Không tìm thấy file/thư mục: {target}")

        log(f"📊 [DRY-RUN] Quét thống kê khoảng lặng cho {len(files)} file...")
        tot_orig, tot_speech = 0.0, 0.0
        for f in files:
            ivs, odur, sdur = detect_speech_intervals(f, 0.0, args.noise_db, args.min_silence, args.pad)
            tot_orig += odur
            tot_speech += sdur
            print(f"  - {os.path.basename(f)}: Gốc={odur/60:.2f}m | Còn lại={sdur/60:.2f}m | Khoảng lặng={(odur-sdur)/60:.2f}m ({((odur-sdur)/odur*100) if odur else 0:.1f}%)")
        print("--------------------------------------------------")
        print(f"TỔNG CỘNG: Gốc={tot_orig/60:.2f}m -> Sau cắt={tot_speech/60:.2f}m | Tiết kiệm={(tot_orig-tot_speech)/60:.2f}m ({((tot_orig-tot_speech)/tot_orig*100) if tot_orig else 0:.1f}%)")
        return

    if args.capcut or (not args.export and (not target_input or not os.path.exists(target_input) or "com.lveditor.draft" in target_input)):
        process_capcut_project(target_input, args.in_place, args.noise_db, args.min_silence, args.pad)
        return

    # Chế độ xuất MP4
    if target_input and os.path.isdir(target_input):
        video_files = [os.path.join(target_input, f) for f in sorted(os.listdir(target_input)) if f.lower().endswith(('.mov', '.mp4', '.mkv', '.avi', '.ts'))]
        if not video_files:
            sys.exit(f"❌ Không tìm thấy file video nào trong thư mục: {target_input}")
        default_out = os.path.join(target_input, f"{os.path.basename(os.path.abspath(target_input))}_Ban_Chuan_YouTube.mp4")
    elif target_input and os.path.isfile(target_input):
        video_files = [target_input]
        stem = Path(target_input).stem
        default_out = os.path.join(os.path.dirname(target_input), f"{stem}_autocut.mp4")
    else:
        sys.exit(f"❌ Vui lòng cung cấp đường dẫn file hoặc thư mục video hợp lệ.")

    out_file = args.output if args.output else default_out
    process_and_export_videos(video_files, out_file, args.noise_db, args.min_silence, args.pad, args.bitrate)

if __name__ == "__main__":
    main()
