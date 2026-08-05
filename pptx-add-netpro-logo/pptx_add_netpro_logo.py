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
DEFAULT_IMAGE_URL = 'https://d.uguu.se/qCTMcHpz.png'

def process_google_slides(presentation_id, credentials_path, image_url):
    scopes = ['https://www.googleapis.com/auth/presentations']
    creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)

    slides_service = build('slides', 'v1', credentials=creds)

    try:
        presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    except Exception as e:
        print(f"Error fetching presentation: {e}")
        sys.exit(1)
        
    slides = presentation.get('slides', [])
    page_size = presentation.get('pageSize', {})
    slide_width = page_size.get('width', {}).get('magnitude', 16256000)
    slide_height = page_size.get('height', {}).get('magnitude', 9144000)

    # Dimensions for Netpro logo (2592 x 1660) -> width 2000000 EMU
    IMG_WIDTH_EMU = 2000000
    IMG_HEIGHT_EMU = int(IMG_WIDTH_EMU * (1660 / 2592))

    MARGIN = 100000
    pos_x = slide_width - IMG_WIDTH_EMU - MARGIN
    pos_y = slide_height - IMG_HEIGHT_EMU - MARGIN

    requests = []
    for slide in slides:
        slide_id = slide.get('objectId')
        
        rect_id = f"cover_rect_{slide_id}_{uuid.uuid4().hex[:8]}"
        img_id = f"cover_img_{slide_id}_{uuid.uuid4().hex[:8]}"
        
        # 1. Create a white rectangle to hide the old logo
        requests.append({
            'createShape': {
                'objectId': rect_id,
                'shapeType': 'RECTANGLE',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': IMG_WIDTH_EMU, 'unit': 'EMU'},
                        'height': {'magnitude': IMG_HEIGHT_EMU, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1.0,
                        'scaleY': 1.0,
                        'translateX': pos_x,
                        'translateY': pos_y,
                        'unit': 'EMU'
                    }
                }
            }
        })
        
        # Format shape with white fill, no border
        requests.append({
            'updateShapeProperties': {
                'objectId': rect_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': 1.0,
                                    'green': 1.0,
                                    'blue': 1.0
                                }
                            }
                        }
                    },
                    'outline': {
                        'propertyState': 'NOT_RENDERED'
                    }
                },
                'fields': 'shapeBackgroundFill.solidFill.color,outline'
            }
        })
        
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
        print(f"Adding Netpro logo to {len(slides)} slides...")
        body = {'requests': requests}
        slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        print("Done!")
    else:
        print("No slides found in the presentation.")

def main():
    parser = argparse.ArgumentParser(description="Add Netpro logo to the bottom right of Google Slides to cover previous logos.")
    parser.add_argument("presentation_id", help="The Google Slides presentation ID")
    parser.add_argument("--credentials", default="/Users/hoangnd/Documents/funix-auto-sheet-f464a0b5957e.json",
                        help="Path to Google Service Account Credentials JSON")
    parser.add_argument("--image-url", default=DEFAULT_IMAGE_URL,
                        help="URL of the logo image to insert")
    
    args = parser.parse_args()
    process_google_slides(args.presentation_id, args.credentials, args.image_url)

if __name__ == '__main__':
    main()
