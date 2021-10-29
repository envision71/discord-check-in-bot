from random import sample
from time import process_time
from attr import validate
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys2.json'
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1AaxaYOMoD7a3ZUe-Ylp1osRenmFx5Qroutkx5aXtgQc'
def main():
    team_name = "testing"
    discord_name = "123456789123456789"
    nick = "["+team_name+"] "+ discord_name
    if(len(nick)>32):
        nick = nick[:32]
    print(nick,len(nick))

def search_column_names(self,search):
    result = self.sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                range='{0}'.format(self.sheet_name)).execute()
    values = result.get('values',[])
    for index,value in enumerate(values):
        for index2,value2 in enumerate(value):
            if value2 == search:
                search = chr(index2+97).upper()
                return search

class sheet:

    def __init__(self,sheet_ID,sheet_name,search_column,update_column,team_name_column):
        # If modifying these scopes, delete the file token.json.
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SERVICE_ACCOUNT_FILE = 'keys2.json'
        self.creds = None
        self.creds = service_account.Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        # The ID and range of a sample spreadsheet.
        self.SAMPLE_SPREADSHEET_ID = sheet_ID
        self.sheet_name = sheet_name
        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet = self.service.spreadsheets()
        self.search_column = search_column_names(self,search_column)
        self.update_column = search_column_names(self,update_column)
        self.team_name_column = search_column_names(self,team_name_column)

    def search(self,search_value, search_column_title):
        #search for the column
        self.search_column = search_column_names(self,search_column_title)
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
        print('{0}!{1}{2}'.format(self.sheet_name,self.update_column,row))
    def remove_checkmark(self,row):
        request = self.sheet.values().update(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                            range='{0}!{1}{2}'.format(self.sheet_name,self.update_column,row),valueInputOption='USER_ENTERED',body={'values': [['FALSE']]}).execute()
    def get_team_name(self,row):
        result = self.sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                    range='{0}!{1}{2}'.format(self.sheet_name,self.team_name_column,row)).execute()
        values = result.get('values',[])
        print(values)
        return values[0][0]

    def search_column_names(self,search):
        print("from search " + self.SAMPLE_SPREADSHEET_ID)
        result = self.sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                    range='{0}'.format(self.sheet_name)).execute()
        values = result.get('values',[])
        for index,value in enumerate(values):
            for index2,value2 in enumerate(value):
                if value2 == search:
                    search = chr(index2+97).upper()
                    return search
        

if __name__ == '__main__':
    main()