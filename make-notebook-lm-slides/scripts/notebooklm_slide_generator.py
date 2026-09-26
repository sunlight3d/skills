#!/usr/bin/env python3
"""
NotebookLM Slide Deck Generator
Automates generating slide decks from Markdown files using Google NotebookLM (via Playwright CDP).
Part of skill: make-notebook-lm-slides
"""

import os
import sys
import glob
import time
import json
import shutil
import io
import argparse
import subprocess
from typing import List, Optional
from pptx import Presentation
from playwright.sync_api import sync_playwright, Page, Browser

try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

DEFAULT_PROMPT = (
    "hãy tạo slides có nội dung như file text tôi gửi, toàn bộ nội dung slides bằng Tiếng Việt, "
    "thêm nhiều hình ảnh để minh họa. Mầu chữ title: #004C7E, nếu chữ mầu đen thì dùng mầu đen tuyền (#000000), "
    "slide nền chút sóng bồng bềnh mầu #004C7E và #0080C0, slide nền sáng. Dùng tối đa 2 loại Font chữ không chân Việt hóa: "
    "Montserrat / SVN-Gotham. Đảm bảo chữ tối trên nền sáng"
)

DEFAULT_OPERA_EXEC = "/Applications/Opera.app/Contents/MacOS/Opera"
DEFAULT_USER_DATA = os.path.expanduser("~/Library/Application Support/com.operasoftware.Opera")
DEFAULT_CDP_PORT = 9222

_playwright = None
_browser: Optional[Browser] = None
_page: Optional[Page] = None


def ensure_browser_running(
    cdp_port: int = DEFAULT_CDP_PORT,
    browser_exec: str = DEFAULT_OPERA_EXEC,
    user_data_dir: str = DEFAULT_USER_DATA,
    notebook_url: str = ""
):
    """Ensure browser is running with remote debugging port active."""
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=2)
        print(f"Browser CDP is active on port {cdp_port}")
        return
    except Exception:
        pass

    print(f"Starting browser on CDP port {cdp_port}...")
    subprocess.run(["pkill", "-f", os.path.basename(browser_exec)], capture_output=True)
    time.sleep(3)

    cmd = [
        browser_exec,
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={user_data_dir}",
    ]
    if notebook_url:
        cmd.append(notebook_url)

    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for i in range(20):
        time.sleep(1)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=2)
            print(f"Browser CDP is ready after {i+1}s")
            time.sleep(3)
            return
        except Exception:
            pass
    raise RuntimeError(f"Could not connect to browser CDP port {cdp_port} in time")


def get_notebook_page(cdp_port: int = DEFAULT_CDP_PORT, notebook_key: str = "") -> Page:
    """Connect to browser via CDP and locate or open the NotebookLM tab."""
    global _playwright, _browser, _page
    if _page is not None:
        try:
            _page.evaluate("1+1")
            return _page
        except Exception:
            _page = None

    ensure_browser_running(cdp_port=cdp_port)

    if _playwright is None:
        _playwright = sync_playwright().start()

    if _browser is None:
        _browser = _playwright.chromium.connect_over_cdp(f"http://localhost:{cdp_port}")

    # Search existing pages for notebook_key or notebook.google.com
    for ctx in _browser.contexts:
        for pg in ctx.pages:
            url_match = (notebook_key in pg.url) if notebook_key else ("notebook.google.com/notebook" in pg.url)
            if url_match:
                _page = pg
                print(f"Connected to NotebookLM tab: {_page.title()} ({_page.url})")
                _page.bring_to_front()
                return _page

    # Open notebook if key is provided
    if notebook_key:
        notebook_url = f"https://notebook.google.com/notebook/{notebook_key}"
        ctx = _browser.contexts[0]
        _page = ctx.new_page()
        _page.goto(notebook_url, wait_until="domcontentloaded", timeout=45000)
        print(f"Opened new NotebookLM tab: {notebook_url}")
        time.sleep(3)
        return _page

    raise RuntimeError("No NotebookLM tab found. Please provide --notebook-key or open NotebookLM in your browser.")


def close_any_viewer(page: Page):
    """Close any open artifact viewer, slide deck preview, or source panel."""
    selectors = [
        "button[aria-label='Close slide deck']",
        "button[aria-label*='Close']",
        "button[aria-label*='Collapse']",
        "button:has-text('collapse_content')",
        "button:has-text('close')"
    ]
    for sel in selectors:
        try:
            btns = page.locator(sel).all()
            for b in btns:
                if b.is_visible():
                    b.click(timeout=1000)
                    time.sleep(0.5)
        except Exception:
            pass

    try:
        page.keyboard.press("Escape")
        time.sleep(0.3)
    except Exception:
        pass


def ensure_source_panel_expanded(page: Page):
    """Ensure the left-side source panel is expanded so source items are visible in the DOM."""
    try:
        exp_btn = page.locator('button[aria-label*="Expand source panel"], button:has-text("side_nav_expand")').first
        if exp_btn.count() > 0 and exp_btn.is_visible():
            exp_btn.click(timeout=1500)
            time.sleep(1)
    except Exception:
        pass


def ensure_studio_panel_expanded(page: Page):
    """Ensure the right-side studio panel is expanded so artifact buttons are visible in the DOM."""
    try:
        exp_btn = page.locator('button[aria-label*="Expand studio panel"], button:has-text("side_nav_collapse")').first
        if exp_btn.count() > 0 and exp_btn.is_visible():
            exp_btn.click(timeout=1500)
            time.sleep(1)
    except Exception:
        pass


def get_source_count(page: Page) -> int:
    """Return count of sources currently attached in the notebook."""
    ensure_source_panel_expanded(page)
    try:
        return page.evaluate('document.querySelectorAll(".single-source-container, .source-item").length')
    except Exception:
        return 0


def remove_first_source(page: Page) -> bool:
    """Delete the top source in the notebook."""
    try:
        more_btn = page.locator(
            ".single-source-container button.source-item-more-button, .source-item button[aria-label='More']"
        ).first
        if more_btn.count() == 0:
            return False
        more_btn.click(timeout=3000)
        time.sleep(0.8)

        rem_item = page.locator("[role='menuitem'], .mat-mdc-menu-item").filter(has_text="Remove source").or_(
            page.locator("[role='menuitem'], .mat-mdc-menu-item").filter(has_text="Xóa nguồn")
        ).first
        rem_item.click(timeout=3000)
        time.sleep(0.8)

        del_btn = page.locator("mat-dialog-container button, [role='dialog'] button").filter(has_text="Delete").or_(
            page.locator("mat-dialog-container button, [role='dialog'] button").filter(has_text="Xóa")
        ).first
        del_btn.click(timeout=3000)
        time.sleep(1.5)
        return True
    except Exception as e:
        print(f"remove_first_source notice: {e}")
        return False


def clear_all_sources(page: Page, max_attempts: int = 10) -> bool:
    """Clear all sources so each generation runs strictly on one isolated source."""
    for _ in range(max_attempts):
        cnt = get_source_count(page)
        if cnt == 0:
            print("  Sources cleared (count = 0).")
            return True
        print(f"  Removing source ({cnt} remaining)...")
        if not remove_first_source(page):
            break
        time.sleep(1)
    return get_source_count(page) == 0


def add_source_from_file(page: Page, md_path: str) -> bool:
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

    # 1. Click Add source
    add_btn = page.locator(
        "button[aria-label*='Add source'], button[aria-label*='Thêm nguồn'], button:has-text('Add sources'), button:has-text('Add source'), button:has-text('Thêm nguồn')"
    ).first
    add_btn.click(timeout=10000)
    print("    [1/4] Clicked 'Add source'")
    time.sleep(1.5)

    # 2. Click Copied text
    copied_btn = page.locator(
        "button[aria-label*='Copied text'], [role='button'][aria-label*='Copied text'], button:has-text('Copied text'), [role='button']:has-text('Copied text'), button:has-text('Văn bản đã sao chép')"
    ).first
    copied_btn.click(timeout=10000)
    print("    [2/4] Clicked 'Copied text'")
    time.sleep(1.5)

    # 3. Fill Title (input.title-input) and Content (textarea.copied-text-input-textarea)
    title_inp = page.locator("input.title-input, input[placeholder*='title'], input[placeholder*='Tiêu đề']").first
    title_inp.fill(title)

    content_ta = page.locator("textarea.copied-text-input-textarea, textarea[placeholder*='Paste'], textarea[placeholder*='Dán']").first
    content_ta.fill(content)
    print("    [3/4] Filled Title & Content")
    time.sleep(1)

    # 4. Click Insert
    insert_btn = page.locator("button").filter(has_text="Insert").or_(
        page.locator("button").filter(has_text="Chèn")
    ).first
    insert_btn.click(timeout=10000)
    print("    [4/4] Clicked 'Insert'")

    # 5. Wait for source to register
    print("    Waiting for source to process...")
    for _ in range(20):
        time.sleep(1)
        if get_source_count(page) >= 1:
            print("  Source registered successfully.")
            return True
    return False


def generate_slide_deck(page: Page, prompt_text: str = DEFAULT_PROMPT, lang: str = "Tiếng Việt", max_retries: int = 3) -> bool:
    """Click customize Slide Deck icon, select language, enter prompt, and start generation."""
    print("  Triggering Slide Deck generation in Studio...")
    close_any_viewer(page)
    ensure_studio_panel_expanded(page)

    for attempt in range(max_retries):
        # Ensure studio panel is expanded
        ensure_studio_panel_expanded(page)

        # Wait for Slide Deck button container to be present
        res_click = page.evaluate("""(() => {
            const container = document.querySelector("basic-create-artifact-button[data-create-button-type='8']");
            if (!container) return "Container not found";
            container.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
            container.dispatchEvent(new MouseEvent("mouseover", { bubbles: true }));
            const editIcon = container.querySelector(".option-icon, .edit-icon") || container;
            editIcon.style.display = "inline-flex";
            editIcon.style.visibility = "visible";
            const opts = { bubbles: true, cancelable: true, view: window };
            editIcon.dispatchEvent(new PointerEvent('pointerdown', opts));
            editIcon.dispatchEvent(new MouseEvent('mousedown', opts));
            editIcon.dispatchEvent(new PointerEvent('pointerup', opts));
            editIcon.dispatchEvent(new MouseEvent('mouseup', opts));
            editIcon.click();
            return "Clicked editIcon";
        })()""")

        if res_click != "Clicked editIcon":
            print(f"  Container status: {res_click}, retrying in 2s...")
            close_any_viewer(page)
            ensure_studio_panel_expanded(page)
            time.sleep(2)
            continue

        dialog = page.locator("mat-dialog-container")
        try:
            dialog.wait_for(state="visible", timeout=6000)
        except Exception:
            print("  Modal dialog did not appear, retrying...")
            close_any_viewer(page)
            time.sleep(1.5)
            continue

        # Language selection
        sel = dialog.locator("mat-select").first
        if sel.count() > 0:
            sel_text = sel.inner_text()
            if lang not in sel_text:
                sel.click()
                time.sleep(0.8)
                lang_opt = page.locator("mat-option, [role='option']").filter(has_text=lang).first
                if lang_opt.count() > 0:
                    lang_opt.click()
                    print(f"  Selected language: {lang}")
                time.sleep(0.5)

        # Fill prompt
        prompt_ta = dialog.locator("textarea").first
        prompt_ta.fill(prompt_text)
        time.sleep(1)

        # Check rate limit vs Generate now
        gen_btn = dialog.locator("button").filter(has_text="Generate now").or_(
            dialog.locator("button").filter(has_text="Tạo ngay")
        ).first

        if gen_btn.count() == 0:
            dialog_text = dialog.inner_text()
            if "Generate later" in dialog_text or "Tạo sau" in dialog_text:
                raise RuntimeError("Fast generation rate limit reached on this Google account (only 'Generate later' available).")
            print("  'Generate now' button not found, retrying...")
            continue

        gen_btn.click()
        print("  Clicked 'Generate now' button")
        time.sleep(3)
        return True

    return False


def wait_for_deck_completion(page: Page, timeout: int = 720, poll_interval: int = 10) -> bool:
    """Poll until Slide Deck generation is finished."""
    print("  Waiting for Slide Deck generation to start...")
    for i in range(20):
        time.sleep(1)
        is_gen = page.evaluate("""(() => {
            const t = document.body.innerText;
            const shimmer = !!document.querySelector('.artifact-item-button.shimmer-yellow');
            return t.includes('Generating Slide Deck') || shimmer;
        })()""")
        if is_gen:
            print(f"  Generation started (detected at {i+1}s).")
            break

    print("  Waiting for Slide Deck generation to complete...")
    start = time.time()
    while time.time() - start < timeout:
        status = page.evaluate("""(() => {
            const text = document.body.innerText;
            const isGenerating = text.includes("Generating Slide Deck");
            const cards = Array.from(document.querySelectorAll(".artifact-item-button"));
            const deckCard = cards.find(c => {
                const desc = c.querySelector("button") ? (c.querySelector("button").getAttribute("aria-description") || "") : "";
                return desc.includes("Slide") || c.innerText.includes("Slide Deck") || c.classList.contains("shimmer-yellow");
            });
            const isShimmer = deckCard ? deckCard.classList.contains("shimmer-yellow") : isGenerating;
            return { isGenerating, isShimmer, cardText: deckCard ? deckCard.innerText.substring(0, 80) : "" };
        })()""")

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


def download_and_save_deck(page: Page, dest_path: str, timeout: int = 120) -> str:
    """Download PPTX from NotebookLM and save to destination path."""
    downloads_dir = os.path.expanduser("~/Downloads")
    before_files = set(glob.glob(os.path.join(downloads_dir, "*.pptx")))

    close_any_viewer(page)
    time.sleep(1)

    # 1. Open top valid artifact card
    top_deck = page.locator("artifact-library-item, .artifact-item-button").filter(has_text="Slide Deck").or_(
        page.locator("artifact-library-item, .artifact-item-button").filter(has_text="tablet")
    ).first
    button_in_deck = top_deck.locator("button.artifact-stretched-button, button").first
    button_in_deck.click()
    print("  Opened top Slide Deck artifact")
    time.sleep(2.5)

    # 2. Click More options
    more_btn = page.locator(".artifact-header button[aria-label='More options'], .artifact-header button").filter(has_text="more_vert").first
    more_btn.click()
    print("  Clicked 'More options'")
    time.sleep(1)

    # 3. Intercept download via Playwright expect_download
    downloaded_file = None
    try:
        with page.expect_download(timeout=15000) as download_info:
            pptx_item = page.locator("[role='menuitem'], .mat-mdc-menu-item").filter(has_text="PowerPoint").or_(
                page.locator("[role='menuitem'], .mat-mdc-menu-item").filter(has_text=".pptx")
            ).first
            pptx_item.click()

        download = download_info.value
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        download.save_as(dest_path)
        print(f"  Downloaded via Playwright: {dest_path} ({os.path.getsize(dest_path):,} bytes)")
        close_any_viewer(page)
        return dest_path
    except Exception as e:
        print(f"  Playwright direct download notice ({e}), monitoring ~/Downloads...")

    # Fallback: Monitor ~/Downloads
    start = time.time()
    while time.time() - start < timeout:
        crdownloads = glob.glob(os.path.join(downloads_dir, "*.crdownload"))
        current_pptx = set(glob.glob(os.path.join(downloads_dir, "*.pptx")))
        new_pptx = [f for f in (current_pptx - before_files) if not os.path.basename(f).startswith("~$")]
        if new_pptx and not crdownloads:
            downloaded_file = max(new_pptx, key=os.path.getmtime)
            break

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
    shutil.move(downloaded_file, dest_path)
    print(f"  Saved: {dest_path} ({os.path.getsize(dest_path):,} bytes)")
    close_any_viewer(page)
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
                    img_stream = io.BytesIO(shape.image.blob)
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
    page: Page,
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

            close_any_viewer(page)
            time.sleep(1)

            # 1. Clear existing sources
            print("Step 1: Clearing existing sources...")
            clear_all_sources(page)
            time.sleep(1)

            # 2. Add single Markdown source
            print("Step 2: Adding source...")
            if not add_source_from_file(page, md_path):
                raise RuntimeError(f"Failed to add source from {md_path}")
            time.sleep(2)

            # 3. Trigger Slide Deck generation
            print("Step 3: Triggering Slide Deck generation...")
            close_any_viewer(page)
            time.sleep(1)
            if not generate_slide_deck(page, prompt_text=prompt, lang=lang):
                raise RuntimeError("Failed to trigger slide deck generation")

            # 4. Wait for generation
            print("Step 4: Waiting for Slide Deck generation...")
            if not wait_for_deck_completion(page, timeout=720, poll_interval=10):
                raise RuntimeError("Slide deck generation timed out or failed")
            time.sleep(3)

            # 5. Download PPTX
            print("Step 5: Downloading PPTX...")
            saved = download_and_save_deck(page, dest_pptx_path, timeout=120)
            print(f"Completed successfully: {saved}")
            return saved

        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            if "rate limit" in str(e).lower():
                raise
            if attempt < max_retries:
                print("Retrying in 10 seconds...")
                time.sleep(10)
                close_any_viewer(page)
                clear_all_sources(page)
            else:
                raise


def process_markdown_list(
    files: List[str],
    output_path: str,
    prompt: str = DEFAULT_PROMPT,
    parts_dir: str = "slides_parts",
    notebook_key: str = "",
    cdp_port: int = DEFAULT_CDP_PORT,
    lang: str = "Tiếng Việt",
    force: bool = False,
    no_merge: bool = False
) -> str:
    """Process a list of Markdown files, generating individual PPTX decks and merging them."""
    page = get_notebook_page(cdp_port=cdp_port, notebook_key=notebook_key)
    print(f"Total Markdown files to process: {len(files)}")

    os.makedirs(parts_dir, exist_ok=True)
    generated_parts = []

    for idx, md_file in enumerate(files, start=1):
        base_name = os.path.splitext(os.path.basename(md_file))[0]
        part_output = os.path.join(parts_dir, f"{base_name}.pptx")
        saved_file = process_single_file(
            page=page,
            md_path=md_file,
            dest_pptx_path=part_output,
            prompt=prompt,
            lang=lang,
            force=force
        )
        generated_parts.append(saved_file)

    if no_merge or len(generated_parts) <= 1:
        if len(generated_parts) == 1 and output_path:
            shutil.copy(generated_parts[0], output_path)
            return output_path
        return generated_parts[-1] if generated_parts else ""

    return merge_presentations(generated_parts, output_path)


def cleanup():
    global _playwright, _browser, _page
    if _page:
        _page = None
    if _browser:
        try:
            _browser.close()
        except Exception:
            pass
        _browser = None
    if _playwright:
        try:
            _playwright.stop()
        except Exception:
            pass
        _playwright = None


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="make-notebook-lm-slides: Generate PowerPoint presentations from Markdown files via Google NotebookLM"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="List of markdown files or glob patterns (e.g., mds/1.*.md)"
    )
    parser.add_argument(
        "--file-list",
        dest="file_list_file",
        help="Path to a text file containing markdown file paths (one per line)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt text for customizing the Slide Deck in NotebookLM"
    )
    parser.add_argument(
        "-o", "--output",
        default="merged_presentation.pptx",
        help="Destination path for final merged PPTX file"
    )
    parser.add_argument(
        "--parts-dir",
        default="slides_parts",
        help="Directory to save individual part PPTX files"
    )
    parser.add_argument(
        "--notebook-key",
        default=os.environ.get("NOTEBOOK_KEY", ""),
        help="NotebookLM UUID/key from the URL"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_CDP_PORT,
        help="CDP debugging port (default: 9222)"
    )
    parser.add_argument(
        "--lang",
        default="Tiếng Việt",
        help="Language for slides (default: 'Tiếng Việt')"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-generation of slides even if PPTX file already exists"
    )
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Only generate individual parts, do not merge into a final presentation"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Collect files
    md_files = []
    if args.file_list_file and os.path.exists(args.file_list_file):
        with open(args.file_list_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    md_files.append(line)

    for item in args.files:
        expanded = glob.glob(item)
        if expanded:
            md_files.extend(expanded)
        elif os.path.exists(item):
            md_files.append(item)

    if not md_files:
        print("Error: No markdown files specified. Provide files or glob pattern (e.g., mds/*.md)")
        sys.exit(1)

    # Sort files naturally
    md_files = sorted(
        list(dict.fromkeys(md_files)),
        key=lambda x: [int(c) if c.isdigit() else c for c in os.path.basename(x).split("-")[0].split(".")]
    )

    print("=" * 60)
    print("MAKE-NOTEBOOK-LM-SLIDES")
    print(f"Total files: {len(md_files)}")
    print(f"Output:      {args.output}")
    print(f"Parts dir:   {args.parts_dir}")
    print(f"Language:    {args.lang}")
    print("=" * 60)

    try:
        final_output = process_markdown_list(
            files=md_files,
            output_path=args.output,
            prompt=args.prompt,
            parts_dir=args.parts_dir,
            notebook_key=args.notebook_key,
            cdp_port=args.port,
            lang=args.lang,
            force=args.force,
            no_merge=args.no_merge
        )
        print(f"\nALL DONE! Final output: {final_output}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
