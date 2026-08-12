# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
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
import sys
import uuid
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build

# URL to the uploaded logo image (publicly accessible)
DEFAULT_IMAGE_URL = 'https://raw.githubusercontent.com/sunlight3d/skills/master/pptx-add-vietis-logo/logo_vietis.png'

def process_google_slides(slides_service, presentation_id, image_url):
    try:
        presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    except Exception as e:
        print(f"  Error fetching presentation {presentation_id}: {e}")
        return
        
    slides = presentation.get('slides', [])
    page_size = presentation.get('pageSize', {})
    slide_width = page_size.get('width', {}).get('magnitude', 16256000)
    slide_height = page_size.get('height', {}).get('magnitude', 9144000)

    # Dimensions for VietIS logo (1149 x 453). Scaled to 1980000 width.
    IMG_WIDTH_EMU = 1980000
    IMG_HEIGHT_EMU = int(IMG_WIDTH_EMU * (453 / 1149))

    MARGIN_X = 0
    MARGIN_Y = 38100
    pos_x = slide_width - IMG_WIDTH_EMU - MARGIN_X
    pos_y = slide_height - IMG_HEIGHT_EMU - MARGIN_Y

    requests = []
    skipped = 0
    for slide in slides:
        slide_id = slide.get('objectId')
        
        # Delete old logos and rectangles created by this script
        elements = slide.get('pageElements', [])
        for el in elements:
            el_id = el.get('objectId', '')
            if el_id.startswith('cover_img_') or el_id.startswith('cover_rect_'):
                requests.append({'deleteObject': {'objectId': el_id}})
                
        img_id = f"cover_img_{slide_id}_{uuid.uuid4().hex[:8]}"
        
        # 2. Add the new logo on top
        requests.append({
            'createImage': {
                'objectId': img_id,
                'url': image_url,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': IMG_WIDTH_EMU, 'unit': 'EMU'},
                        'height': {'magnitude': IMG_HEIGHT_EMU, 'unit': 'EMU'}
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
        print(f"  Adding VietIS logo to {len(requests) // 3} slides (skipped {skipped})...")
        body = {'requests': requests}
        slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        print("  Done!")
    else:
        print(f"  No action needed. Skipped {skipped} slides.")

def get_presentations_in_folder(drive_service, folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.presentation' and trashed=false"
    results = []
    page_token = None
    while True:
        response = drive_service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)', pageToken=page_token).execute()
        results.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return results

def main():
    parser = argparse.ArgumentParser(description="Add VietIS logo to the bottom right of Google Slides to cover previous logos.")
    parser.add_argument("id", help="The Google Slides presentation ID or Google Drive Folder ID")
    parser.add_argument("--folder", action="store_true", help="Treat the ID as a Google Drive Folder ID and process all presentations inside it")
    parser.add_argument("--credentials", default="/Users/hoangnd/Documents/connect-gemini-api-471309-2da0973af1ba.json",
                        help="Path to Google Service Account Credentials JSON")
    parser.add_argument("--image-url", default=DEFAULT_IMAGE_URL,
                        help="URL of the logo image to insert")
    
    args = parser.parse_args()
    
    # We need both presentations and drive scopes if processing a folder
    scopes = ['https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive.readonly']
    creds = service_account.Credentials.from_service_account_file(args.credentials, scopes=scopes)
    
    slides_service = build('slides', 'v1', credentials=creds)
    
    if args.folder:
        drive_service = build('drive', 'v3', credentials=creds)
        print(f"Searching for presentations in folder {args.id}...")
        presentations = get_presentations_in_folder(drive_service, args.id)
        print(f"Found {len(presentations)} presentations.")
        
        for i, p in enumerate(presentations):
            print(f"[{i+1}/{len(presentations)}] Processing '{p['name']}' (ID: {p['id']})")
            process_google_slides(slides_service, p['id'], args.image_url)
    else:
        print(f"Processing single presentation (ID: {args.id})")
        process_google_slides(slides_service, args.id, args.image_url)

if __name__ == '__main__':
    main()
