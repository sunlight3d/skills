#!/usr/bin/env python3
"""
NotebookLM Chrome Slide Generator via AppleScript + Base64 JS Evaluation.
Seamlessly drives NotebookLM in Google Chrome without needing CDP port or restarting Chrome.
"""

import os
import sys
import time
import glob
import json
import base64
import shutil
import subprocess
from io import BytesIO
from typing import List, Tuple, Optional
from pptx import Presentation

DEFAULT_PROMPT = (
    "hãy tạo slides có nội dung như file text tôi gửi, toàn bộ nội dung slides bằng Tiếng Việt, "
    "thêm nhiều hình ảnh để minh họa. Mầu chữ title: #004C7E, nếu chữ mầu đen thì dùng mầu đen tuyền (#000000), "
    "slide nền chút sóng bồng bềnh mầu #004C7E và #0080C0, slide nền sáng).Dùng tối đa 2 loại Font chữ không chân Việt hóa: "
    "Montserrat / SVN-Gotham.Đảm bảo chữ tối trên nền sáng"
)

TARGET_NOTEBOOK_KEY = "84ee5207-a93e-4c9f-90d4-ac1e183f48a3"


def get_chrome_notebook_tab(notebook_key: str = TARGET_NOTEBOOK_KEY) -> Tuple[int, int]:
    """Find the window and tab index of NotebookLM in Google Chrome."""
    scpt = f'''
tell application "Google Chrome"
    set wIndex to 1
    repeat with w in windows
        set tIndex to 1
        repeat with t in tabs of w
            set thisURL to URL of t
            if thisURL contains "{notebook_key}" or (thisURL contains "notebook.google.com/notebook" and "{notebook_key}" is "") then
                return (wIndex as string) & "," & (tIndex as string)
            end if
            set tIndex to tIndex + 1
        end repeat
        set wIndex to wIndex + 1
    end repeat
    return ""
end tell
'''
    p = subprocess.run(["osascript", "-"], input=scpt, text=True, capture_output=True)
    out = p.stdout.strip()
    if not out or "," not in out:
        raise RuntimeError(f"Could not find open NotebookLM tab with key '{notebook_key}' in Google Chrome.")
    w_str, t_str = out.split(",")[:2]
    return int(w_str), int(t_str)


def chrome_eval(js_code: str, notebook_key: str = TARGET_NOTEBOOK_KEY) -> str:
    """Execute arbitrary JavaScript in the Chrome NotebookLM tab using base64 encoding."""
    w_idx, t_idx = get_chrome_notebook_tab(notebook_key=notebook_key)
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    scpt = f'''
tell application "Google Chrome"
    set res to execute (tab {t_idx} of window {w_idx}) javascript "eval(atob('{b64}'))"
    return res as string
end tell
'''
    p = subprocess.run(["osascript", "-"], input=scpt, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"AppleScript error: {p.stderr.strip()}")
    return p.stdout.strip()


def close_any_viewer():
    """Dismiss any dialogs, artifact viewers, or overlays."""
    js = '''(() => {
        const closeBtn = document.querySelector('mat-dialog-container button[aria-label*="Close"]') ||
                         document.querySelector('[role="dialog"] button[aria-label*="Close"]');
        if (closeBtn) closeBtn.click();
        
        const selectors = [
            "button[aria-label='Close slide deck']",
            "button[aria-label*='Close']",
            "button[aria-label*='Collapse']",
            "button:has-text('collapse_content')"
        ];
        for (const sel of selectors) {
            document.querySelectorAll(sel).forEach(b => {
                if (b.offsetParent !== null) b.click();
            });
        }
        document.querySelectorAll('.cdk-overlay-backdrop').forEach(el => {
            el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        });
        return 'closed';
    })()'''
    chrome_eval(js)
    time.sleep(0.5)


def ensure_source_panel_expanded():
    """Ensure the left-side source panel is open."""
    js = '''(() => {
        const btn = document.querySelector('button[aria-label*="Expand source panel"]');
        if (btn && btn.offsetParent !== null) { btn.click(); return 'expanded'; }
        return 'already_open';
    })()'''
    chrome_eval(js)
    time.sleep(0.5)


def ensure_studio_panel_expanded():
    """Ensure the right-side studio panel is open."""
    js = '''(() => {
        const btn = document.querySelector('button[aria-label*="Expand studio panel"]');
        if (btn && btn.offsetParent !== null) { btn.click(); return 'expanded'; }
        return 'already_open';
    })()'''
    chrome_eval(js)
    time.sleep(0.5)


def get_source_count() -> int:
    """Return number of sources currently attached."""
    ensure_source_panel_expanded()
    res = chrome_eval('document.querySelectorAll(".single-source-container, .source-item").length')
    try:
        return int(res)
    except Exception:
        return 0


def remove_first_source() -> bool:
    """Delete the top source in the notebook."""
    close_any_viewer()
    ensure_source_panel_expanded()
    
    js_more = '''(() => {
        const btn = document.querySelector('.single-source-container button.source-item-more-button, .source-item button[aria-label="More"]');
        if (!btn) return 'not_found';
        btn.click();
        return 'clicked';
    })()'''
    if chrome_eval(js_more) != 'clicked':
        return False
    time.sleep(1)
    
    js_rem = '''(() => {
        const items = Array.from(document.querySelectorAll('[role="menuitem"], .mat-mdc-menu-item'));
        const rem = items.find(el => el.innerText.includes('Remove') || el.innerText.includes('Xóa'));
        if (!rem) return 'not_found';
        rem.click();
        return 'clicked';
    })()'''
    if chrome_eval(js_rem) != 'clicked':
        return False
    time.sleep(1)
    
    js_del = '''(() => {
        const btns = Array.from(document.querySelectorAll('mat-dialog-container button, [role="dialog"] button'));
        const del = btns.find(el => el.innerText.includes('Delete') || el.innerText.includes('Xóa'));
        if (!del) return 'not_found';
        del.click();
        return 'clicked';
    })()'''
    chrome_eval(js_del)
    time.sleep(2)
    return True


def clear_all_sources(max_attempts: int = 10) -> bool:
    """Clear all sources so each generation runs strictly on one isolated source."""
    close_any_viewer()
    for _ in range(max_attempts):
        cnt = get_source_count()
        if cnt == 0:
            print("  Sources cleared (count = 0).")
            return True
        print(f"  Removing source ({cnt} remaining)...")
        if not remove_first_source():
            break
        time.sleep(1)
    return get_source_count() == 0


def add_source_from_file(md_path: str) -> bool:
    """Upload a single Markdown file content as a source via 'Copied text'."""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    filename = os.path.basename(md_path)
    title = filename.replace(".md", "")
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line.replace("#", "").strip()
            break

    print(f"  Adding source: '{title}' ({len(content)} chars)...")
    close_any_viewer()
    ensure_source_panel_expanded()

    # 1. Click Add source
    js_add = '''(() => {
        const btn = document.querySelector("button[aria-label*='Add source'], button[aria-label*='Thêm nguồn']");
        if (!btn) return 'not_found';
        btn.click();
        return 'clicked';
    })()'''
    chrome_eval(js_add)
    print("    [1/4] Clicked 'Add source'")
    time.sleep(1.5)

    # 2. Click Copied text
    js_copied = '''(() => {
        const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
        const btn = btns.find(b => b.innerText.includes('Copied text') || b.innerText.includes('Văn bản đã sao chép'));
        if (!btn) return 'not_found';
        btn.click();
        return 'clicked';
    })()'''
    chrome_eval(js_copied)
    print("    [2/4] Clicked 'Copied text'")
    time.sleep(1.5)

    # 3. Fill Title & Content via execCommand
    payload = json.dumps({"title": title, "content": content})
    b64_payload = base64.b64encode(payload.encode("utf-8")).decode("ascii")
    js_fill = f'''(() => {{
        const data = JSON.parse(atob('{b64_payload}'));
        const titleInp = document.querySelector('input.title-input');
        const contentTa = document.querySelector('textarea.copied-text-input-textarea');
        if (!titleInp || !contentTa) return JSON.stringify('inputs_not_found');
        
        titleInp.focus();
        titleInp.select();
        document.execCommand('insertText', false, data.title);
        
        contentTa.focus();
        contentTa.select();
        document.execCommand('insertText', false, data.content);
        
        const insertBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Insert' || b.innerText.trim() === 'Chèn');
        return JSON.stringify({{
            insertDisabled: insertBtn ? insertBtn.disabled : true
        }});
    }})()'''
    res = json.loads(chrome_eval(js_fill))
    print(f"    [3/4] Filled Title & Content (insertDisabled={res.get('insertDisabled')})")
    time.sleep(1)

    # 4. Click Insert
    js_insert = '''(() => {
        const insertBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Insert' || b.innerText.trim() === 'Chèn');
        if (!insertBtn) return 'not_found';
        insertBtn.click();
        return 'clicked';
    })()'''
    chrome_eval(js_insert)
    print("    [4/4] Clicked 'Insert'")

    # 5. Wait for count >= 1
    print("    Waiting for source to process...")
    for _ in range(20):
        time.sleep(1)
        if get_source_count() >= 1:
            print("  Source registered successfully.")
            return True
    return False


def generate_slide_deck(prompt: str = DEFAULT_PROMPT, lang: str = "Tiếng Việt") -> bool:
    """Open customize dialog, select language, fill prompt, and click Generate now."""
    print("  Triggering Slide Deck generation in Studio...")
    close_any_viewer()
    ensure_studio_panel_expanded()

    # 1. Open Customize dialog
    js_open = '''(() => {
        const container = document.querySelector("basic-create-artifact-button[data-create-button-type='8']");
        if (!container) return 'Container not found';
        container.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
        container.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
        const editIcon = container.querySelector('.option-icon, .edit-icon') || container;
        editIcon.style.display = 'inline-flex';
        editIcon.style.visibility = 'visible';
        const opts = { bubbles: true, cancelable: true, view: window };
        editIcon.dispatchEvent(new PointerEvent('pointerdown', opts));
        editIcon.dispatchEvent(new MouseEvent('mousedown', opts));
        editIcon.dispatchEvent(new PointerEvent('pointerup', opts));
        editIcon.dispatchEvent(new MouseEvent('mouseup', opts));
        editIcon.click();
        return 'clicked';
    })()'''
    chrome_eval(js_open)
    time.sleep(2)

    # 2. Fill prompt & check language
    b64_prompt = base64.b64encode(prompt.encode("utf-8")).decode("ascii")
    js_fill = f'''(() => {{
        const dlg = document.querySelector('mat-dialog-container');
        if (!dlg) return JSON.stringify({{ error: 'dialog_not_found' }});
        
        // Language check
        const sel = dlg.querySelector('mat-select');
        let selText = sel ? sel.innerText : '';
        if (sel && !selText.includes('{lang}')) {{
            sel.click();
        }}
        
        // Fill prompt
        const ta = dlg.querySelector('textarea');
        if (ta) {{
            ta.focus();
            ta.select();
            document.execCommand('insertText', false, atob('{b64_prompt}'));
        }}
        
        const btns = Array.from(dlg.querySelectorAll('button'));
        const genNow = btns.find(b => b.innerText.includes('Generate now') || b.innerText.includes('Tạo ngay'));
        const genLater = btns.find(b => b.innerText.includes('Generate later') || b.innerText.includes('Tạo sau'));
        
        return JSON.stringify({{
            lang: selText,
            hasGenNow: !!genNow,
            genNowDisabled: genNow ? genNow.disabled : true,
            hasGenLater: !!genLater
        }});
    }})()'''
    res = json.loads(chrome_eval(js_fill))
    print(f"  Prompt status: {res}")

    if not res.get("hasGenNow"):
        if res.get("hasGenLater"):
            raise RuntimeError("Fast generation quota reached in Chrome account (only 'Generate later' available).")
        raise RuntimeError("Neither 'Generate now' nor 'Generate later' found.")

    # 3. Click Generate now
    js_click_gen = '''(() => {
        const dlg = document.querySelector('mat-dialog-container');
        if (!dlg) return 'dialog_not_found';
        const btns = Array.from(dlg.querySelectorAll('button'));
        const genNow = btns.find(b => b.innerText.includes('Generate now') || b.innerText.includes('Tạo ngay'));
        if (!genNow) return 'not_found';
        genNow.click();
        return 'clicked';
    })()'''
    chrome_eval(js_click_gen)
    print("  Clicked 'Generate now' button")
    time.sleep(3)
    return True


def wait_for_deck_completion(timeout: int = 720, poll_interval: int = 10) -> bool:
    """Poll until Slide Deck generation is finished."""
    print("  Waiting for Slide Deck generation to start...")
    for i in range(20):
        time.sleep(1)
        is_gen = chrome_eval('''(() => {
            const t = document.body.innerText;
            const shimmer = !!document.querySelector('.artifact-item-button.shimmer-yellow');
            return t.includes('Generating Slide Deck') || shimmer;
        })()''') == 'true'
        if is_gen:
            print(f"  Generation started (detected at {i+1}s).")
            break

    print("  Waiting for Slide Deck generation to complete...")
    start = time.time()
    while time.time() - start < timeout:
        res_str = chrome_eval('''(() => {
            const text = document.body.innerText;
            const isGenerating = text.includes("Generating Slide Deck");
            const cards = Array.from(document.querySelectorAll(".artifact-item-button"));
            const deckCard = cards.find(c => {
                const desc = c.querySelector("button") ? (c.querySelector("button").getAttribute("aria-description") || "") : "";
                return desc.includes("Slide") || c.innerText.includes("Slide Deck") || c.classList.contains("shimmer-yellow");
            });
            const isShimmer = deckCard ? deckCard.classList.contains("shimmer-yellow") : isGenerating;
            return JSON.stringify({ isGenerating, isShimmer, cardText: deckCard ? deckCard.innerText.substring(0, 80) : "" });
        })()''')
        status = json.loads(res_str)
        elapsed = int(time.time() - start)
        is_gen = status.get("isGenerating")
        is_shimmer = status.get("isShimmer")
        print(f"  [{elapsed}s] generating: {is_gen}, shimmer: {is_shimmer}")

        if not is_gen and not is_shimmer:
            print("  Generation complete! Card:", status.get("cardText"))
            return True

        time.sleep(poll_interval)

    print("  Generation timed out.")
    return False


def download_and_save_deck(dest_path: str, timeout: int = 120) -> str:
    """Download PPTX from Chrome and save to destination path."""
    downloads_dir = os.path.expanduser("~/Downloads")
    before_files = set(glob.glob(os.path.join(downloads_dir, "*.pptx")))

    close_any_viewer()
    time.sleep(1)

    # 1. Open top deck card
    js_open_deck = '''(() => {
        const topDeck = document.querySelector('artifact-library-item, .artifact-item-button');
        if (!topDeck) return false;
        const btn = topDeck.querySelector('button.artifact-stretched-button, button') || topDeck;
        const opts = { bubbles: true, cancelable: true, view: window };
        btn.dispatchEvent(new PointerEvent('pointerdown', opts));
        btn.dispatchEvent(new MouseEvent('mousedown', opts));
        btn.dispatchEvent(new PointerEvent('pointerup', opts));
        btn.dispatchEvent(new MouseEvent('mouseup', opts));
        btn.click();
        return true;
    })()'''
    chrome_eval(js_open_deck)
    print("  Opened top Slide Deck artifact")
    time.sleep(2.5)

    # 2. Click More options
    js_more = '''(() => {
        const moreBtn = document.querySelector('.artifact-header button[aria-label="More options"], .artifact-header button.mat-mdc-menu-trigger');
        if (!moreBtn) return false;
        moreBtn.focus();
        const opts = { bubbles: true, cancelable: true, view: window };
        moreBtn.dispatchEvent(new PointerEvent('pointerdown', opts));
        moreBtn.dispatchEvent(new MouseEvent('mousedown', opts));
        moreBtn.dispatchEvent(new PointerEvent('pointerup', opts));
        moreBtn.dispatchEvent(new MouseEvent('mouseup', opts));
        moreBtn.click();
        return true;
    })()'''
    chrome_eval(js_more)
    print("  Clicked 'More options'")
    time.sleep(1)

    # 3. Click PowerPoint (.pptx)
    js_pptx = '''(() => {
        const items = Array.from(document.querySelectorAll('[role="menuitem"], .mat-mdc-menu-item'));
        const pptx = items.find(el => el.innerText.includes('PowerPoint') || el.innerText.includes('.pptx'));
        if (!pptx) return false;
        pptx.focus();
        const opts = { bubbles: true, cancelable: true, view: window };
        pptx.dispatchEvent(new PointerEvent('pointerdown', opts));
        pptx.dispatchEvent(new MouseEvent('mousedown', opts));
        pptx.dispatchEvent(new PointerEvent('pointerup', opts));
        pptx.dispatchEvent(new MouseEvent('mouseup', opts));
        pptx.click();
        return true;
    })()'''
    chrome_eval(js_pptx)
    print("  Clicked 'PowerPoint' menu item")

    # 4. Monitor ~/Downloads
    start = time.time()
    downloaded_file = None
    while time.time() - start < timeout:
        current_pptx = set(glob.glob(os.path.join(downloads_dir, "*.pptx")))
        new_pptx = [f for f in (current_pptx - before_files) if not os.path.basename(f).startswith("~$")]
        if new_pptx:
            downloaded_file = max(new_pptx, key=os.path.getmtime)
            break

        # Check temporary Chrome download file .com.google.Chrome.*
        temps = [f for f in glob.glob(os.path.join(downloads_dir, ".com.*")) if os.path.getmtime(f) >= start - 5]
        if temps:
            latest_temp = max(temps, key=os.path.getmtime)
            s1 = os.path.getsize(latest_temp)
            if s1 > 1000000:
                time.sleep(2)
                s2 = os.path.getsize(latest_temp)
                if s1 == s2:
                    with open(latest_temp, "rb") as tf:
                        if tf.read(4) == b"PK\x03\x04":
                            downloaded_file = latest_temp
                            break

        time.sleep(1)

    if not downloaded_file:
        raise RuntimeError("Timed out waiting for PPTX download in ~/Downloads")

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if downloaded_file.startswith(downloads_dir + "/.com."):
        shutil.copy2(downloaded_file, dest_path)
        try:
            os.remove(downloaded_file)
        except Exception:
            pass
    else:
        shutil.move(downloaded_file, dest_path)
    print(f"  Saved: {dest_path} ({os.path.getsize(dest_path):,} bytes)")
    close_any_viewer()
    return dest_path


def merge_presentations(input_pptx_paths: List[str], output_path: str) -> str:
    """Merge multiple PPTX slide decks into one final master presentation."""
    print(f"\nMerging {len(input_pptx_paths)} presentations into: {output_path}...")
    valid_paths = [p for p in input_pptx_paths if os.path.exists(p) and os.path.getsize(p) > 100000]
    if not valid_paths:
        raise ValueError(f"No valid PPTX files to merge among: {input_pptx_paths}")

    prs_master = Presentation()
    first_prs = Presentation(valid_paths[0])
    prs_master.slide_width = first_prs.slide_width
    prs_master.slide_height = first_prs.slide_height
    blank_layout = prs_master.slide_layouts[6]

    total_slide_count = 0
    for pptx_path in valid_paths:
        prs = Presentation(pptx_path)
        print(f"  Adding {pptx_path}: {len(prs.slides)} slides")
        for slide in prs.slides:
            new_slide = prs_master.slides.add_slide(blank_layout)
            for shape in slide.shapes:
                if shape.shape_type == 13:  # PICTURE
                    img_stream = BytesIO(shape.image.blob)
                    new_slide.shapes.add_picture(
                        img_stream,
                        shape.left, shape.top, shape.width, shape.height
                    )
            total_slide_count += 1

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    prs_master.save(output_path)
    print(f"Merged successfully: {output_path} — {total_slide_count} slides ({os.path.getsize(output_path):,} bytes)")
    return output_path


def process_single_file(
    md_path: str,
    dest_pptx_path: str,
    prompt: str = DEFAULT_PROMPT,
    lang: str = "Tiếng Việt",
    force: bool = False,
    max_retries: int = 2
) -> str:
    """Complete end-to-end automation for a single Markdown source file."""
    if not force and os.path.exists(dest_pptx_path) and os.path.getsize(dest_pptx_path) > 100000:
        print(f"File already exists: {dest_pptx_path} ({os.path.getsize(dest_pptx_path):,} bytes). Skipping.")
        return dest_pptx_path

    for attempt in range(max_retries + 1):
        try:
            print(f"\n=======================================================")
            print(f"PROCESSING FILE (Attempt {attempt+1}/{max_retries+1}): {os.path.basename(md_path)}")
            print(f"TARGET OUTPUT:   {dest_pptx_path}")
            print(f"=======================================================")

            close_any_viewer()
            time.sleep(1)

            # 1. Clear existing sources
            print("Step 1: Clearing existing sources...")
            clear_all_sources()
            time.sleep(1)

            # 2. Add single Markdown source
            print("Step 2: Adding source...")
            close_any_viewer()
            if not add_source_from_file(md_path):
                raise RuntimeError(f"Failed to add source from {md_path}")
            time.sleep(2)

            # 3. Trigger Slide Deck generation
            print("Step 3: Triggering Slide Deck generation...")
            close_any_viewer()
            time.sleep(1)
            if not generate_slide_deck(prompt=prompt, lang=lang):
                raise RuntimeError("Failed to trigger slide deck generation")

            # 4. Wait for generation
            print("Step 4: Waiting for Slide Deck generation...")
            if not wait_for_deck_completion(timeout=720, poll_interval=10):
                raise RuntimeError("Slide deck generation timed out or failed")
            time.sleep(3)

            # 5. Download PPTX
            print("Step 5: Downloading PPTX...")
            saved = download_and_save_deck(dest_pptx_path, timeout=120)
            print(f"Completed successfully: {saved}")
            return saved

        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            if "quota reached" in str(e).lower() or "rate limit" in str(e).lower():
                raise
            if attempt < max_retries:
                print("Retrying in 10 seconds...")
                time.sleep(10)
                try:
                    close_any_viewer()
                    clear_all_sources()
                except Exception:
                    pass
            else:
                raise


def process_markdown_list(
    files: List[str],
    output_path: str,
    prompt: str = DEFAULT_PROMPT,
    parts_dir: str = "slides_parts",
    lang: str = "Tiếng Việt",
    force: bool = False
) -> str:
    """Process a list of Markdown files, generating individual PPTX decks and merging them."""
    print(f"Total Markdown files to process: {len(files)}")
    os.makedirs(parts_dir, exist_ok=True)
    generated_parts = []

    for idx, md_file in enumerate(files, start=1):
        base_name = os.path.splitext(os.path.basename(md_file))[0]
        part_tag = base_name.split("-")[0]
        short_output = os.path.join(parts_dir, f"{part_tag}.pptx")
        full_output = os.path.join(parts_dir, f"{base_name}.pptx")

        if os.path.exists(short_output) and os.path.getsize(short_output) > 100000 and not force:
            part_output = short_output
        elif os.path.exists(full_output) and os.path.getsize(full_output) > 100000 and not force:
            part_output = full_output
        else:
            part_output = short_output

        saved_file = process_single_file(
            md_path=md_file,
            dest_pptx_path=part_output,
            prompt=prompt,
            lang=lang,
            force=force
        )
        generated_parts.append(saved_file)

    merge_presentations(generated_parts, output_path)
    return output_path
