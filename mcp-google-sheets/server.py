import os
import json
import gspread
from google.oauth2.service_account import Credentials
from mcp.server.fastmcp import FastMCP

# Define the scopes for Google Sheets and Drive
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Create FastMCP server
mcp = FastMCP("Google Sheets MCP")

def get_gspread_client():
    # Look for credentials.json in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, 'credentials.json')
    
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Could not find {creds_path}. Please place your Service Account credentials file here.")
        
    credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client

@mcp.tool()
def read_sheet_data(spreadsheet_id: str, range_name: str) -> str:
    """
    Reads data from a Google Sheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in the URL).
        range_name: The A1 notation of the range to read (e.g., 'Sheet1!A1:D10' or just 'Sheet1').
    """
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(range_name.split('!')[0]) if '!' in range_name else sheet.sheet1
        
        # Determine if there's a specific range requested
        if '!' in range_name:
            cell_range = range_name.split('!')[1]
            data = worksheet.get(cell_range)
        else:
            data = worksheet.get_all_values()
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error reading sheet: {str(e)}"

@mcp.tool()
def write_sheet_data(spreadsheet_id: str, range_name: str, values: list[list[str]]) -> str:
    """
    Writes data to a Google Sheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_name: The A1 notation of the range to write to (e.g., 'Sheet1!A1').
        values: A 2D list of strings representing the rows and columns to write.
    """
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(range_name.split('!')[0]) if '!' in range_name else sheet.sheet1
        
        cell_range = range_name.split('!')[1] if '!' in range_name else 'A1'
        
        # Support for gspread >= 6.0.0
        worksheet.update(values=values, range_name=cell_range)
        return f"Successfully updated range {range_name} in spreadsheet {spreadsheet_id}."
    except Exception as e:
        return f"Error writing to sheet: {str(e)}"

@mcp.tool()
def create_spreadsheet_in_folder(title: str, folder_id: str) -> str:
    """
    Creates a new Google Sheet inside a specified Google Drive folder.
    
    Args:
        title: The title of the new spreadsheet.
        folder_id: The ID of the Google Drive folder.
    """
    try:
        from google.auth.transport.requests import AuthorizedSession
        script_dir = os.path.dirname(os.path.abspath(__file__))
        creds_path = os.path.join(script_dir, 'credentials.json')
        
        if not os.path.exists(creds_path):
            return f"Error: Could not find credentials.json at {creds_path}."
            
        credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        authed_session = AuthorizedSession(credentials)
        
        drive_create_url = "https://www.googleapis.com/drive/v3/files"
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "name": title,
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [folder_id]
        }
        
        create_resp = authed_session.post(drive_create_url, json=body, headers=headers, timeout=10)
        if create_resp.status_code != 200:
            return f"Error creating spreadsheet: {create_resp.status_code} - {create_resp.text}"
            
        sh_data = create_resp.json()
        sh_id = sh_data['id']
        sh_url = f"https://docs.google.com/spreadsheets/d/{sh_id}/edit"
        
        return json.dumps({
            "spreadsheet_id": sh_id,
            "spreadsheet_url": sh_url,
            "message": f"Successfully created spreadsheet '{title}' in folder '{folder_id}'."
        }, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Run the server using stdin/stdout transport
    mcp.run()
