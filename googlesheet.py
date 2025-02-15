





from google.oauth2 import service_account
import gspread
import json
import pandas as pd
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1

import common.v2.core as core
import common.v2.analytics as analytics




def getGoogleSheetClient(googleJSONFilePath):
    jsonContents = analytics.readFile(filePath=googleJSONFilePath, mode='r', encoding='utf-8', loggingPrefix=None, logLevel=None)
    service_account_info = json.loads(jsonContents)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive', "https://www.googleapis.com/auth/spreadsheets"]
    creds_with_scope = credentials.with_scopes(scope)
    client = gspread.authorize(creds_with_scope)
    return client







class Cell:
    def __init__(self, row, col, value):
        self.row = row
        self.col = col
        self.value = value
    def __repr__(self):
        return f"({self.row}, {self.col}, {self.value})"
    def __str__(self):
        return f"({self.row}, {self.col}, {self.value})"



def readGoogleSheet(googleSheetClient, url, worksheetNumber=0, worksheetName=None):
    spreadsheet = googleSheetClient.open_by_url(url)
    if worksheetName != None:
        worksheet1 = spreadsheet.worksheet(worksheetName)
    else:
        worksheet1 = spreadsheet.get_worksheet(worksheetNumber)
    records_data = worksheet1.get_all_records()
    do_df1 = pd.DataFrame.from_dict(records_data)
    return do_df1  




# Function to find column letter by name
def getColumnLetter(worksheet, column_name):
    try:
        headers = worksheet.row_values(1)  
        col_index = headers.index(column_name) + 1  # Convert to 1-based index
        return rowcol_to_a1(1, col_index).replace("1", "")  # Get letter and remove row number
    except ValueError:
        return None  # Column not found

















