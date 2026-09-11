import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = r'C:\code\skills\mcp-google-sheets\credentials.json'

def main():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Credentials not found at {SERVICE_ACCOUNT_FILE}")
        return

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('drive', 'v3', credentials=creds)

    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo_imas.png')
    file_metadata = {'name': 'logo_imas.png'}
    media = MediaFileUpload(logo_path, mimetype='image/png')
    
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    
    # Make it public
    permission = {'type': 'anyone', 'role': 'reader'}
    service.permissions().create(fileId=file_id, body=permission).execute()
    
    # Get web content link
    file_info = service.files().get(fileId=file_id, fields='webContentLink').execute()
    print("Public Web URL:", file_info.get('webContentLink'))

if __name__ == '__main__':
    main()
