"""
FUNiX Portal Automator for Student Assignment Grading
Automates interaction with Portal FUNiX marksheet (Odoo fx.asm.marksheet)
via Windows UIAutomation.
"""

import sys
import os
import time
import io
import urllib.request
import zipfile
import ctypes

# Ensure stdout handles UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def switch_to_default_desktop():
    """Switches thread desktop to 'default' to break out of Antigravity desktop isolation."""
    try:
        import win32service
        desk = win32service.OpenDesktop('default', 0, False, 0x01FF)
        desk.SetThreadDesktop()
        return True
    except Exception as e:
        print(f"[Warn] switch_to_default_desktop: {e}")
        return False

def activate_window(hwnd):
    """Brings the target window to foreground reliably using AttachThreadInput."""
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    fg_hwnd = user32.GetForegroundWindow()
    cur_thread = kernel32.GetCurrentThreadId()
    fg_thread = user32.GetWindowThreadProcessId(fg_hwnd, None)
    user32.AttachThreadInput(cur_thread, fg_thread, True)
    user32.ShowWindow(hwnd, 3) # SW_MAXIMIZE
    user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(cur_thread, fg_thread, False)
    time.sleep(0.5)

def find_portal_window(browser_name="Vivaldi"):
    """Finds the browser window containing Portal FUNiX."""
    switch_to_default_desktop()
    import uiautomation as auto
    # Search for Portal FUNiX window
    win = auto.WindowControl(searchDepth=1, ClassName='Chrome_WidgetWin_1', SubName='Portal FUNiX')
    if not win.Exists(maxSearchSeconds=3):
        win = auto.WindowControl(searchDepth=1, SubName='Portal FUNiX')
    if win.Exists(maxSearchSeconds=2):
        activate_window(win.NativeWindowHandle)
        return win
    return None

def get_portal_root(window):
    """Retrieves the inner RootWebArea document of Portal FUNiX."""
    import uiautomation as auto
    webview = window.DocumentControl(AutomationId='webview-container')
    if not webview.Exists(maxSearchSeconds=3):
        # Fallback to direct walk
        for c, d in auto.WalkControl(window, maxDepth=10):
            if c.ControlTypeName == 'DocumentControl' and 'Portal FUNiX' in c.Name and c.AutomationId == 'RootWebArea':
                return c
    
    for c, d in auto.WalkControl(webview, maxDepth=10):
        if c.ControlTypeName == 'DocumentControl' and c.AutomationId == 'RootWebArea':
            return c
    return None

def extract_submission_link(root):
    """Extracts the student submission download URL from the 'Link file' field."""
    import uiautomation as auto
    for c, _ in auto.WalkControl(root, maxDepth=25):
        if c.ControlTypeName == 'HyperlinkControl':
            val = c.GetValuePattern().Value if hasattr(c, 'GetValuePattern') and c.GetValuePattern() else ''
            if not val and c.Name and c.Name.startswith('http'):
                val = c.Name
            if 'storage.googleapis.com' in val or 'drive.google.com' in val or 'github.com' in val or val.endswith('.zip') or val.endswith('.rar'):
                return val
    return None

def download_and_extract_submission(url, target_dir):
    """Downloads submission archive, extracts files, and deletes archive."""
    os.makedirs(target_dir, exist_ok=True)
    temp_zip = os.path.join(target_dir, 'temp_sub.zip')
    print(f"[Download] Fetching: {url}")
    urllib.request.urlretrieve(url, temp_zip)
    print(f"[Download] Saved to {temp_zip}")
    
    # Extract
    if zipfile.is_zipfile(temp_zip):
        with zipfile.ZipFile(temp_zip, 'r') as z:
            z.extractall(target_dir)
        os.remove(temp_zip)
        print(f"[Extract] Unzipped and cleaned up archive.")
        return target_dir
    else:
        # If it is not a zip or already raw file
        print(f"[Extract] File is not a zip archive, kept as is.")
        return temp_zip

def get_marksheet_table(root):
    """Finds the criteria TableControl in Odoo."""
    import uiautomation as auto
    for c, _ in auto.WalkControl(root, maxDepth=25):
        if c.ControlTypeName in ['TableControl', 'DataGridControl']:
            return c
    return None

def fill_row_score_and_comment(row, score_str, comment_str, window):
    """Fills score and comment into an active Odoo row."""
    import uiautomation as auto
    activate_window(window.NativeWindowHandle)
    
    # 1. Scroll row into view
    if hasattr(row, 'GetScrollItemPattern') and row.GetScrollItemPattern():
        row.GetScrollItemPattern().ScrollIntoView()
        time.sleep(0.5)
        
    cells = row.GetChildren()
    if len(cells) < 8:
        return False
        
    c5 = cells[5] # Diem so
    rect5 = c5.BoundingRectangle
    cx = (rect5.left + rect5.right) // 2
    cy = rect5.top + 25
    
    auto.Click(cx, cy)
    time.sleep(0.8)
    
    combo = row.ComboBoxControl()
    if not combo.Exists(maxSearchSeconds=1):
        auto.Click(cx, cy)
        time.sleep(0.8)
        combo = row.ComboBoxControl()
        
    if combo.Exists(maxSearchSeconds=1):
        combo.Click(simulateMove=False)
        time.sleep(0.2)
        auto.SendKeys(score_str)
        time.sleep(0.4)
        auto.SendKeys('{Enter}')
        time.sleep(0.4)
        auto.SendKeys('{Tab}') # Move to Edit
        time.sleep(0.4)
    else:
        print(f"[Warn] Combo not found for row.")
        
    edit = row.EditControl()
    if not edit.Exists(maxSearchSeconds=1):
        c7 = cells[7]
        rect7 = c7.BoundingRectangle
        cx7 = (rect7.left + rect7.right) // 2
        cy7 = rect7.top + 25
        auto.Click(cx7, cy7)
        time.sleep(0.5)
        edit = row.EditControl()
        
    if edit.Exists(maxSearchSeconds=1):
        edit.Click(simulateMove=False)
        time.sleep(0.2)
        auto.SetClipboardText(comment_str)
        auto.SendKeys('{Ctrl}a{Ctrl}v')
        time.sleep(0.4)
        auto.SendKeys('{Tab}')
        time.sleep(0.4)
        return True
    return False

def fill_overall_evaluation(root, window, comment_text):
    """Fills the overall evaluation text into overall_evaluation."""
    import uiautomation as auto
    activate_window(window.NativeWindowHandle)
    overall_eval = root.EditControl(AutomationId="overall_evaluation")
    if not overall_eval.Exists(maxSearchSeconds=2):
        for c, _ in auto.WalkControl(root, maxDepth=25):
            if c.AutomationId == "overall_evaluation":
                overall_eval = c
                break
                
    if overall_eval.Exists(maxSearchSeconds=2):
        # Scroll webview down to reveal overall evaluation
        webview = window.DocumentControl(AutomationId='webview-container')
        if webview.Exists(maxSearchSeconds=1):
            rect = webview.BoundingRectangle
            auto.Click((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
            time.sleep(0.3)
            auto.SendKeys('{PageDown}')
            time.sleep(0.5)
            
        rect_eval = overall_eval.BoundingRectangle
        auto.Click((rect_eval.left + rect_eval.right) // 2, (rect_eval.top + rect_eval.bottom) // 2)
        time.sleep(0.4)
        auto.SetClipboardText(comment_text)
        auto.SendKeys('{Ctrl}a{Ctrl}v')
        time.sleep(0.5)
        print("[Success] Overall evaluation filled.")
        return True
    return False
