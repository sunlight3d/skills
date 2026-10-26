# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
#   "python-pptx",
#   "requests",
#   "Pillow",
# ]
# ///

import socket
# Force IPv4 to bypass broken IPv6 resolution on macOS
orig_getaddrinfo = socket.getaddrinfo
def forced_getaddrinfo(*args, **kwargs):
    args = list(args)
    if len(args) > 2:
        args[2] = socket.AF_INET
    else:
        while len(args) < 3:
            args.append(None)
        args[2] = socket.AF_INET
    return orig_getaddrinfo(*args, **kwargs)
socket.getaddrinfo = forced_getaddrinfo

import os
import re
import sys
import uuid
import argparse
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

# URL to the uploaded logo image (raw GitHub URL from skills repository)
DEFAULT_IMAGE_URL = 'https://raw.githubusercontent.com/sunlight3d/skills/master/pptx-add-mathplus-logo/logo_mathplus.png'
LOCAL_LOGO_NAME = 'logo_mathplus.png'

# Aspect ratio of logo_mathplus.png (2400 x 900)
LOGO_ORIG_WIDTH = 2400
LOGO_ORIG_HEIGHT = 900

# Dimensions in EMUs: width 2,300,000 EMU (~181 pt) covers NotebookLM watermark completely with generous margin
DEFAULT_IMG_WIDTH_EMU = 2300000
DEFAULT_IMG_HEIGHT_EMU = int(DEFAULT_IMG_WIDTH_EMU * (LOGO_ORIG_HEIGHT / LOGO_ORIG_WIDTH))  # ~862,500 EMU (~67.9 pt)
DEFAULT_MARGIN_X = 0
DEFAULT_MARGIN_Y = 38100  # ~3 pt

def get_script_dir():
    return Path(__file__).resolve().parent

def parse_input_target(input_str):
    """
    Parses input string to determine if it is:
    - A local .pptx file path
    - A local directory containing .pptx files
    - A Google Drive folder URL or ID
    - A Google Slides presentation URL or ID
    """
    s = input_str.strip()
    
    # 1. Local path check
    if os.path.exists(s):
        if os.path.isdir(s):
            return 'local_folder', s
        elif s.lower().endswith('.pptx'):
            return 'local_file', s

    # 2. Google Drive Folder URL
    folder_match = re.search(r'drive\.google\.com/drive/(?:u/\d+/)?folders/([a-zA-Z0-9_-]+)', s)
    if folder_match:
        return 'drive_folder', folder_match.group(1)
        
    # 3. Google Slides URL
    slide_match = re.search(r'docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)', s)
    if slide_match:
        return 'google_slide', slide_match.group(1)

    # 4. Fallback: Raw ID
    return 'raw_id', s

def process_google_slides(slides_service, presentation_id, image_url, remove_only=False,
                          img_width_emu=DEFAULT_IMG_WIDTH_EMU, margin_x=DEFAULT_MARGIN_X, margin_y=DEFAULT_MARGIN_Y):
    """
    Inserts or removes the MathPlus Academy logo rectangle at the bottom-right corner of Google Slides.
    """
    try:
        presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    except Exception as e:
        print(f"  ❌ Error fetching presentation {presentation_id}: {e}")
        return False
        
    title = presentation.get('title', presentation_id)
    slides = presentation.get('slides', [])
    page_size = presentation.get('pageSize', {})
    slide_width = page_size.get('width', {}).get('magnitude', 16256000)
    slide_height = page_size.get('height', {}).get('magnitude', 9144000)

    img_height_emu = int(img_width_emu * (LOGO_ORIG_HEIGHT / LOGO_ORIG_WIDTH))
    pos_x = slide_width - img_width_emu - margin_x
    pos_y = slide_height - img_height_emu - margin_y

    requests = []
    for slide in slides:
        slide_id = slide.get('objectId')
        elements = slide.get('pageElements', [])
        
        # 1. Delete previous logo and rectangle cover objects
        for el in elements:
            el_id = el.get('objectId', '')
            if el_id.startswith('cover_img_') or el_id.startswith('cover_rect_') or el_id.startswith('mathplus_logo_'):
                requests.append({'deleteObject': {'objectId': el_id}})
                
        img_id = f"mathplus_logo_{slide_id}_{uuid.uuid4().hex[:8]}"
        
        # 2. Add the MathPlus logo on top (opaque white rectangle covers watermark)
        if not remove_only:
            requests.append({
                'createImage': {
                    'objectId': img_id,
                    'url': image_url,
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': img_width_emu, 'unit': 'EMU'},
                            'height': {'magnitude': img_height_emu, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': pos_x,
                            'translateY': pos_y,
                            'unit': 'EMU'
                        }
                    }
                }
            })

    if requests:
        action_name = "Removing" if remove_only else "Adding"
        print(f"  ⚡ {action_name} MathPlus logo on '{title}' ({len(slides)} slides)...")
        body = {'requests': requests}
        slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        print(f"  ✅ Done! Processed '{title}' successfully.")
        return True
    else:
        print(f"  ℹ️ No action needed for '{title}'.")
        return True

def process_drive_pptx(drive_service, file_id, file_name, logo_img_path, remove_only=False,
                       img_width_emu=DEFAULT_IMG_WIDTH_EMU, margin_x=DEFAULT_MARGIN_X, margin_y=DEFAULT_MARGIN_Y):
    """
    Downloads an Office PPTX file from Google Drive, overlays the MathPlus logo on each slide,
    and updates the file on Google Drive in place.
    """
    import io
    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
    from pptx import Presentation
    from pptx.util import Emu

    print(f"  ⚡ Processing Office PPTX on Google Drive: '{file_name}' (ID: {file_id})...")
    req = drive_service.files().get_media(fileId=file_id)
    fh_in = io.BytesIO()
    downloader = MediaIoBaseDownload(fh_in, req)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh_in.seek(0)

    prs = Presentation(fh_in)
    slide_w = prs.slide_width
    slide_h = prs.slide_height

    w_emu = Emu(img_width_emu)
    h_emu = Emu(int(img_width_emu * (LOGO_ORIG_HEIGHT / LOGO_ORIG_WIDTH)))
    mx = Emu(margin_x)
    my = Emu(margin_y)

    pos_x = slide_w - w_emu - mx
    pos_y = slide_h - h_emu - my

    for slide in prs.slides:
        to_remove = []
        for s in slide.shapes:
            if s.name.startswith('mathplus_logo_') or s.name.startswith('cover_img_') or s.name.startswith('cover_rect_'):
                to_remove.append(s._element)
        for el in to_remove:
            el.getparent().remove(el)

        if not remove_only:
            pic = slide.shapes.add_picture(str(logo_img_path), pos_x, pos_y, width=w_emu, height=h_emu)
            pic.name = f"mathplus_logo_{uuid.uuid4().hex[:8]}"

    fh_out = io.BytesIO()
    prs.save(fh_out)
    fh_out.seek(0)

    media = MediaIoBaseUpload(fh_out, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation', resumable=True)
    drive_service.files().update(fileId=file_id, media_body=media).execute()
    print(f"  ✅ Done! Updated '{file_name}' ({len(prs.slides)} slides) on Google Drive.")
    return True

def process_target_presentation(drive_service, slides_service, file_id, image_url, local_logo_path,
                                 remove_only=False, img_width_emu=DEFAULT_IMG_WIDTH_EMU,
                                 margin_x=DEFAULT_MARGIN_X, margin_y=DEFAULT_MARGIN_Y):
    """
    Intelligently routes a presentation on Google Drive to either Google Slides API
    or Google Drive PPTX stream update depending on its MIME type.
    """
    try:
        meta = drive_service.files().get(fileId=file_id, fields='id, name, mimeType').execute()
        mime_type = meta.get('mimeType', '')
        name = meta.get('name', file_id)
    except Exception as e:
        print(f"  ⚠️ Could not fetch metadata via Drive API ({e}), attempting Google Slides API...")
        mime_type = 'application/vnd.google-apps.presentation'
        name = file_id

    if mime_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        return process_drive_pptx(drive_service, file_id, name, local_logo_path, remove_only,
                                  img_width_emu, margin_x, margin_y)
    else:
        # Standard Google Slides presentation
        return process_google_slides(slides_service, file_id, image_url, remove_only,
                                     img_width_emu, margin_x, margin_y)

def process_local_pptx(pptx_path, logo_img_path, output_path=None,
                       img_width_emu=DEFAULT_IMG_WIDTH_EMU, margin_x=DEFAULT_MARGIN_X, margin_y=DEFAULT_MARGIN_Y):
    """
    Inserts the MathPlus Academy logo rectangle into a local PowerPoint (.pptx) file.
    """
    from pptx import Presentation
    from pptx.util import Emu

    if not os.path.exists(pptx_path):
        print(f"  ❌ Error: File not found at {pptx_path}")
        return False

    prs = Presentation(pptx_path)
    slide_width = prs.slide_width
    slide_height = prs.slide_height

    w_emu = Emu(img_width_emu)
    h_emu = Emu(int(img_width_emu * (LOGO_ORIG_HEIGHT / LOGO_ORIG_WIDTH)))
    mx = Emu(margin_x)
    my = Emu(margin_y)
    
    pos_x = slide_width - w_emu - mx
    pos_y = slide_height - h_emu - my

    for idx, slide in enumerate(prs.slides):
        to_remove = []
        for s in slide.shapes:
            if s.name.startswith('mathplus_logo_') or s.name.startswith('cover_img_') or s.name.startswith('cover_rect_'):
                to_remove.append(s._element)
        for el in to_remove:
            el.getparent().remove(el)

        pic = slide.shapes.add_picture(
            str(logo_img_path),
            pos_x,
            pos_y,
            width=w_emu,
            height=h_emu
        )
        pic.name = f"mathplus_logo_{uuid.uuid4().hex[:8]}"

    save_path = output_path if output_path else pptx_path
    prs.save(save_path)
    print(f"  ✅ Processed local PPTX: {save_path} ({len(prs.slides)} slides)")
    return True

def get_presentations_in_folder(drive_service, folder_id):
    """Fetches all Google Slides and Office PPTX presentations inside a Google Drive folder."""
    query = (
        f"'{folder_id}' in parents and "
        f"(mimeType='application/vnd.google-apps.presentation' or "
        f" mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation') and "
        f"trashed=false"
    )
    results = []
    page_token = None
    while True:
        response = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token
        ).execute()
        results.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return results

def find_default_credentials():
    """Searches common paths for service account credentials JSON."""
    script_dir = get_script_dir()
    candidates = [
        script_dir / 'credentials.json',
        script_dir.parent / 'pptx-add-qnet-logo' / 'credentials.json',
        Path('/Users/hoangnd/.gemini/config/skills/pptx-add-qnet-logo/credentials.json'),
        Path('/Users/hoangnd/.gemini/config/skills/pptx-add-mathplus-logo/credentials.json'),
        Path('/Users/hoangnd/Documents/connect-gemini-api-471309-f8bf3d1a89f5.json'),
        Path('/Users/hoangnd/Documents/connect-gemini-api-471309-2da0973af1ba.json'),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Add MathPlus Academy logo rectangle to the bottom-right corner of Google Slides / PPTX to cover NotebookLM watermark."
    )
    parser.add_argument("target", help="The Google Slides presentation ID/URL, Google Drive Folder ID/URL, or local PPTX file/folder")
    parser.add_argument("--folder", action="store_true", help="Treat target as a Google Drive Folder ID and process all presentations inside it")
    parser.add_argument("--credentials", default=None, help="Path to Google Service Account Credentials JSON")
    parser.add_argument("--image-url", default=DEFAULT_IMAGE_URL, help="URL of the logo image to insert (Google Slides)")
    parser.add_argument("--remove-only", action="store_true", help="Remove existing logos without adding new ones")
    parser.add_argument("--output", default=None, help="Output path for local PPTX file")
    parser.add_argument("--width", type=int, default=DEFAULT_IMG_WIDTH_EMU, help=f"Width of logo in EMU (default: {DEFAULT_IMG_WIDTH_EMU})")
    parser.add_argument("--margin-x", type=int, default=DEFAULT_MARGIN_X, help=f"Right margin in EMU (default: {DEFAULT_MARGIN_X})")
    parser.add_argument("--margin-y", type=int, default=DEFAULT_MARGIN_Y, help=f"Bottom margin in EMU (default: {DEFAULT_MARGIN_Y})")
    
    args = parser.parse_args()
    
    target_type, target_val = parse_input_target(args.target)
    if args.folder:
        target_type = 'drive_folder'

    # Local file or directory execution
    local_logo_path = get_script_dir() / LOCAL_LOGO_NAME
    if not local_logo_path.exists():
        local_logo_path = Path('/Volumes/data/code/skills/pptx-add-mathplus-logo') / LOCAL_LOGO_NAME

    if target_type == 'local_file':
        print(f"Processing local PowerPoint presentation: {target_val}")
        process_local_pptx(target_val, local_logo_path, args.output, args.width, args.margin_x, args.margin_y)
        return

    elif target_type == 'local_folder':
        pptx_files = sorted(list(Path(target_val).glob('*.pptx')))
        print(f"Found {len(pptx_files)} .pptx files in folder: {target_val}")
        for p in pptx_files:
            process_local_pptx(str(p), local_logo_path, None, args.width, args.margin_x, args.margin_y)
        return

    # Google Slides / Drive execution
    creds_path = args.credentials or find_default_credentials()
    if not creds_path or not os.path.exists(creds_path):
        print("❌ Error: Google Service Account credentials JSON not found!")
        print("   Please provide --credentials /path/to/credentials.json")
        sys.exit(1)

    scopes = [
        'https://www.googleapis.com/auth/presentations',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
    slides_service = build('slides', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    if target_type == 'drive_folder':
        print(f"Searching for presentations in folder {target_val}...")
        try:
            presentations = get_presentations_in_folder(drive_service, target_val)
        except Exception as e:
            print(f"❌ Error listing folder: {e}")
            print(f"   Please make sure folder {target_val} is shared with Editor permission to:")
            print(f"   {creds.service_account_email}")
            sys.exit(1)

        print(f"Found {len(presentations)} presentations.")
        for i, p in enumerate(presentations):
            print(f"[{i+1}/{len(presentations)}] Processing '{p['name']}' (ID: {p['id']})")
            process_target_presentation(drive_service, slides_service, p['id'], args.image_url,
                                        local_logo_path, args.remove_only,
                                        args.width, args.margin_x, args.margin_y)
    else:
        print(f"Processing presentation (ID: {target_val})")
        process_target_presentation(drive_service, slides_service, target_val, args.image_url,
                                    local_logo_path, args.remove_only,
                                    args.width, args.margin_x, args.margin_y)

if __name__ == '__main__':
    main()
