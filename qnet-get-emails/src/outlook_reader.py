import os
import sys
import glob
import re
import struct
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import cramjam
except ImportError:
    cramjam = None

MAGIC_SSTABLE = 0xdb4775248b80fb57

OLK_ATTACHMENTS_BASE = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    "Microsoft", "Olk", "Attachments"
)

OLK_LEVELDB_PATH = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\Olk\EBWebView\Default\IndexedDB\https_outlook.office.com_0.indexeddb.leveldb"
)

# Additional local attachment caches
EXTRA_ATTACHMENT_DIRS = [
    OLK_ATTACHMENTS_BASE,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "downloads_pdf"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "MailApp", "downloads_pdf"),
    os.path.expandvars(r"%USERPROFILE%\Downloads")
]

def _read_varint(data: bytes, offset: int):
    res = 0
    shift = 0
    while True:
        b = data[offset]
        offset += 1
        res |= (b & 0x7f) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return res, offset

def _parse_sstable_blocks(filepath: str) -> List[bytes]:
    """Parse and decompress all data blocks from a LevelDB .ldb file."""
    if not os.path.exists(filepath) or cramjam is None:
        return []

    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except Exception:
        return []

    if len(data) < 48:
        return []

    magic = struct.unpack_from("<Q", data, len(data) - 8)[0]
    if magic != MAGIC_SSTABLE:
        return []

    try:
        offset = len(data) - 48
        _, offset = _read_varint(data, offset)
        _, offset = _read_varint(data, offset)
        index_offset, offset = _read_varint(data, offset)
        index_size, offset = _read_varint(data, offset)

        idx_raw = data[index_offset : index_offset + index_size]
        idx_comp = data[index_offset + index_size]
        if idx_comp == 1:
            idx_raw = bytes(cramjam.snappy.decompress_raw(idx_raw))

        handles = []
        p = 0
        num_restarts = struct.unpack_from("<I", idx_raw, len(idx_raw) - 4)[0]
        restarts_end = len(idx_raw) - 4 - 4 * num_restarts

        while p < restarts_end:
            shared, p = _read_varint(idx_raw, p)
            unshared, p = _read_varint(idx_raw, p)
            val_len, p = _read_varint(idx_raw, p)
            p += unshared
            val_bytes = idx_raw[p : p + val_len]
            p += val_len
            b_off, vp = _read_varint(val_bytes, 0)
            b_size, vp = _read_varint(val_bytes, vp)
            handles.append((b_off, b_size))

        decompressed_blocks = []
        for b_off, b_size in handles:
            b_data = data[b_off : b_off + b_size]
            b_comp = data[b_off + b_size]
            if b_comp == 1:
                try:
                    dec = bytes(cramjam.snappy.decompress_raw(b_data))
                    decompressed_blocks.append(dec)
                except Exception:
                    decompressed_blocks.append(b_data)
            else:
                decompressed_blocks.append(b_data)

        return decompressed_blocks
    except Exception:
        return []

def _clean_str(raw_text: str) -> str:
    """Clean control characters and binary junk."""
    if not raw_text:
        return ""
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', raw_text)
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    return cleaned.strip()

def clean_pdf_filename(name: str) -> str:
    """Strip any leading junk bytes or wrong parity shifts before the actual PDF filename."""
    if not name:
        return ""
    m = re.search(r'([A-Za-z0-9\u00C0-\u00FF\u1EA0-\u1EF9].*?\.pdf)$', name, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return name.strip()

def find_pdf_attachment_path(filename: str) -> Optional[str]:
    """Find the full path of a PDF attachment across Outlook cache and local folders."""
    if not filename:
        return None

    cleaned = clean_pdf_filename(filename)
    target = cleaned.strip().lower()

    for base_dir in EXTRA_ATTACHMENT_DIRS:
        if not os.path.isdir(base_dir):
            continue

        # 1. Exact match
        pattern = os.path.join(base_dir, "**", cleaned)
        matches = glob.glob(pattern, recursive=True)
        if matches:
            matches.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            return matches[0]

        # 2. Case-insensitive or suffix match (e.g. '17459_36- QĐ-UBND...' matching '36- QĐ-UBND...')
        for root, dirs, files in os.walk(base_dir):
            for f in files:
                f_lower = f.lower().strip()
                if f_lower == target or f_lower.endswith(target) or target in f_lower:
                    return os.path.join(root, f)

    return None

def extract_pdf_names_from_context(context: bytes) -> List[str]:
    """
    Extract all PDF attachment filenames from raw message context,
    supporting both UTF-16LE (Vietnamese accented) and UTF-8/ASCII filenames.
    """
    found_names = []

    # 1. Search UTF-16LE filenames (.\x00p\x00d\x00f\x00)
    target_u16 = ".\x00p\x00d\x00f\x00".encode("latin1")
    pos = 0
    while True:
        pos = context.find(target_u16, pos)
        if pos == -1:
            break
        start = max(0, pos - 300)
        chunk = context[start : pos + 8]
        name_idx = chunk.rfind(b"Name")
        if name_idx != -1:
            sub = chunk[name_idx:]
            for off in range(4, 25):
                cand = sub[off:]
                try:
                    dec = cand.decode("utf-16le")
                    if dec.lower().endswith(".pdf"):
                        clean = clean_pdf_filename(dec)
                        if len(clean) > 4 and clean.lower().endswith(".pdf"):
                            if clean not in found_names:
                                found_names.append(clean)
                            break
                except Exception:
                    pass
        pos += 8

    # 2. Search ASCII / UTF-8 Name tag
    for m in re.finditer(rb'Name\"[\s\S]?([^\"]+\.pdf)', context, re.IGNORECASE):
        p_name = m.group(1).decode("utf-8", errors="ignore").strip()
        p_name = re.sub(r'^[,\x00-\x1f]+', '', p_name)
        p_name = clean_pdf_filename(_clean_str(p_name))
        if p_name and p_name not in found_names:
            found_names.append(p_name)

    # 3. Fallback: Any ASCII sequence ending with .pdf in context
    for m in re.finditer(rb'([a-zA-Z0-9_\-\. ]{4,100}\.pdf)', context, re.IGNORECASE):
        cand = m.group(1).decode("utf-8", errors="ignore").strip()
        cand = clean_pdf_filename(cand)
        if cand and not any(cand in x for x in found_names):
            if not cand.startswith("http") and not cand.startswith("www"):
                found_names.append(cand)

    return found_names

def fetch_outlook_emails(
    account_email: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Read emails from Outlook on local PC.
    Filters by account_email, from_date (YYYY-MM-DD), to_date (YYYY-MM-DD).
    Returns a list of email dicts with metadata and attachment paths.
    """
    if not os.path.exists(OLK_LEVELDB_PATH):
        print(f"[!] Không tìm thấy dữ liệu Outlook tại: {OLK_LEVELDB_PATH}")
        return []

    files = glob.glob(os.path.join(OLK_LEVELDB_PATH, "*.ldb")) + glob.glob(os.path.join(OLK_LEVELDB_PATH, "*.log"))
    
    d_from_dt = None
    d_to_dt = None
    if from_date:
        try:
            d_from_dt = datetime.strptime(from_date.strip(), "%Y-%m-%d")
        except Exception:
            pass
    if to_date:
        try:
            d_to_dt = datetime.strptime(to_date.strip(), "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except Exception:
            pass

    account_target = account_email.strip().lower() if account_email else ""

    extracted_map = {}

    for fp in files:
        if fp.endswith(".ldb"):
            blks = _parse_sstable_blocks(fp)
        else:
            try:
                with open(fp, "rb") as f:
                    blks = [f.read()]
            except Exception:
                blks = []

        for b in blks:
            for m in re.finditer(rb'(?:ConversationTopic|Subject)(?:\x00)?(["c])', b):
                tag = m.group(1)
                subj = ""
                pos = m.start()
                end_tag = m.end()

                if tag == b'"':
                    q_end = b.find(b'"', end_tag)
                    if q_end != -1 and (q_end - end_tag) < 400:
                        raw_val = b[end_tag:q_end]
                        if len(raw_val) > 1 and raw_val[0] < 128:
                            subj = raw_val[1:1+raw_val[0]].decode('utf-8', errors='ignore').strip()
                        elif len(raw_val) >= 3:
                            subj = raw_val.decode('utf-8', errors='ignore').strip()
                elif tag == b'c':
                    try:
                        v_len, p_start = _read_varint(b, end_tag)
                        if 0 < v_len < 1200:
                            raw_u16 = b[p_start : p_start + v_len]
                            subj = raw_u16.decode("utf-16le", errors="ignore").strip()
                    except Exception:
                        pass

                subj = _clean_str(subj)
                if not subj or len(subj) < 2 or subj.startswith("{") or subj.startswith(":") or "ConversationTopic" in subj:
                    continue

                pos = m.start()
                context = b[max(0, pos-2000):min(len(b), pos+4500)]

                # Extract Date
                date_str = ""
                dt_parsed = None
                m_date = re.search(rb'(?:DateTimeReceived|LastDeliveryTime|DateTimeCreated)\"\x19([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[^\"]*)', context)
                if m_date:
                    raw_dt_str = m_date.group(1).decode("utf-8", errors="ignore")
                    try:
                        dt_parsed = datetime.fromisoformat(raw_dt_str)
                        date_str = dt_parsed.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        date_str = raw_dt_str[:19].replace("T", " ")

                # If date filter is provided, skip items without valid date
                if (d_from_dt or d_to_dt):
                    if not dt_parsed:
                        continue
                    naive_dt = dt_parsed.replace(tzinfo=None)
                    if d_from_dt and naive_dt < d_from_dt:
                        continue
                    if d_to_dt and naive_dt > d_to_dt:
                        continue

                # Extract Sender
                sender_name = ""
                sender_email = ""
                m_from = re.search(rb'From[^\x22]*\"Mailbox[^\x22]*\"Name\"(.)', context)
                if m_from:
                    nl = m_from.group(1)[0]
                    if 0 < nl < 100:
                        sender_name = context[m_from.end():m_from.end()+nl].decode("utf-8", errors="ignore")

                m_email = re.search(rb'EmailAddress\"(.)', context)
                if m_email:
                    el = m_email.group(1)[0]
                    if 0 < el < 100:
                        cand = context[m_email.end():m_email.end()+el].decode("utf-8", errors="ignore")
                        if "@" in cand:
                            sender_email = cand

                if not sender_name:
                    m_snd2 = re.search(rb'UniqueSendersA\x01\"(.)', context)
                    if m_snd2:
                        nl = m_snd2.group(1)[0]
                        if 0 < nl < 100:
                            sender_name = context[m_snd2.end():m_snd2.end()+nl].decode("utf-8", errors="ignore")

                sender_name = _clean_str(sender_name)
                sender_email = _clean_str(sender_email)

                if not sender_name and not sender_email:
                    sender_str = "Microsoft Outlook"
                elif sender_name and sender_email:
                    sender_str = f"{sender_name} <{sender_email}>"
                else:
                    sender_str = sender_name or sender_email

                # Check Recipient / Account context
                recip_matches = True
                if account_target:
                    acc_bytes = account_target.encode("utf-8")
                    if acc_bytes not in context.lower():
                        if "outlook" not in account_target:
                            recip_matches = False

                if not recip_matches:
                    continue

                # Extract Preview / Body
                preview = ""
                m_prev_u16 = re.search(rb'Previewc', context)
                if m_prev_u16:
                    try:
                        v_len, p_start = _read_varint(context, m_prev_u16.end())
                        if 0 < v_len < 4000:
                            raw_u16 = context[p_start : p_start + v_len]
                            preview = raw_u16.decode("utf-16le", errors="ignore")
                    except Exception:
                        pass
                
                if not preview:
                    m_prev_ascii = re.search(rb'Preview\"(.)', context)
                    if m_prev_ascii:
                        pl = m_prev_ascii.group(1)[0]
                        if 0 < pl < 250:
                            preview = context[m_prev_ascii.end():m_prev_ascii.end()+pl].decode("utf-8", errors="ignore").strip()

                preview = _clean_str(preview)

                # Extract All PDF Attachments (UTF-16LE + ASCII)
                extracted_pdf_names = extract_pdf_names_from_context(context)
                
                pdf_attachments = []
                for p_name in extracted_pdf_names:
                    local_path = find_pdf_attachment_path(p_name)
                    pdf_attachments.append({
                        "filename": p_name,
                        "local_path": local_path
                    })

                # Deduplication key
                clean_topic = re.sub(r'^(?:FW|RE):\s*', '', subj, flags=re.IGNORECASE).strip()
                date_prefix = (date_str or "")[:16]
                unique_key = (clean_topic.lower(), date_prefix)

                existing = extracted_map.get(unique_key)
                if not existing or (len(pdf_attachments) > len(existing.get("pdf_attachments", []))) or (len(preview) > len(existing.get("body", ""))):
                    hash_sig = hashlib.sha256(f"{clean_topic}_{date_str}_{sender_str}".encode("utf-8")).hexdigest()[:10]
                    email_id = f"olk_{hash_sig}"

                    extracted_map[unique_key] = {
                        "email_id": email_id,
                        "subject": subj,
                        "date_str": date_str,
                        "sender": sender_str,
                        "recipient": account_email,
                        "body": preview or subj,
                        "pdf_attachments": pdf_attachments,
                        "pdf_count": len(pdf_attachments)
                    }

    results = list(extracted_map.values())
    results.sort(key=lambda x: x["date_str"] or "", reverse=True)
    return results[:limit]
