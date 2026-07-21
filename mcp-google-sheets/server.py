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

if __name__ == "__main__":
    # Run the server using stdin/stdout transport
    mcp.run()
