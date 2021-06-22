from __future__ import print_function
import os.path
from random import sample
from time import process_time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from google.oauth2 import service_account
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'
creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1Q_FB9htsJazmCO1nP5VFND7DtD8O3Kyto2ObBKa1K4Q'
def main():

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range='Sheet1!B:B').execute()
    values = result.get('values', [])
    find = 'Set'
    if not values:
        print('No data found.')
    else:
        for x, in values:
            if x == find:
                print(x)



class sheet:
    def __init__(self,sheet_ID,sheet_name,search_column,update_column,team_name_column):
        # If modifying these scopes, delete the file token.json.
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SERVICE_ACCOUNT_FILE = 'keys.json'
        self.creds = None
        self.creds = service_account.Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        # The ID and range of a sample spreadsheet.
        self.SAMPLE_SPREADSHEET_ID = sheet_ID
        self.sheet_name = sheet_name
        self.search_column = search_column
        self.update_column = update_column
        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet = self.service.spreadsheets()
        self.team_name_column = team_name_column


    def search(self,search_value):
        # Call the Sheets API
        result = self.sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                    range='{0}!{1}:{1}'.format(self.sheet_name,self.search_column)).execute()
        values = result.get('values', [])
        if not values:
            return None
        else:
            for x,y in enumerate(values):
                if search_value in y:
                    return x+1

    def add_checkmark(self,row):
        request = self.sheet.values().update(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                            range='{0}!{1}{2}'.format(self.sheet_name,self.update_column,row),valueInputOption='USER_ENTERED',body={'values': [['TRUE']]}).execute()
    def remove_checkmark(self,row):
        request = self.sheet.values().update(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                            range='{0}!{1}{2}'.format(self.sheet_name,self.update_column,row),valueInputOption='USER_ENTERED',body={'values': [['FALSE']]}).execute()
    def get_team_name(self,row):
        result = self.sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                    range='{0}!{1}{2}'.format(self.sheet_name,self.team_name_column,row)).execute()
        values = result.get('values',[])
        return values[0][0]    

if __name__ == '__main__':
    main()