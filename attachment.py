from __future__ import print_function
from mmap import PAGESIZE

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


def get_mixes(song_name):
    """Accesses the Drive v3 API.
    Prints the names and ids of mixes for a given song.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        no_items = "No files found."

        # Call the Drive v3 API
        results = service.files().list(
            spaces="drive", corpora="allDrives", includeItemsFromAllDrives="true", supportsAllDrives="true", pageSize=10, fields="nextPageToken, files(id, name, webViewLink)", q=f"parents in '11zeV_swcydQGyTHWiYsgOkAERIY-m2t3' and name contains '{song_name}'").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return no_items

        parts = service.files().list(corpora="allDrives", includeItemsFromAllDrives="true", supportsAllDrives="true", pageSize=10, fields="nextPageToken, files(id, name, webViewLink)", q=f"parents in '{items[0]['id']}' and mimeType contains 'audio/'").execute()
        part_items = parts.get('files', [])

        if not part_items:
            print('No files found.')
            return no_items
        
        mixes = []
        for part_item in part_items:
            mixes.append(u'{0} ({1})'.format(part_item['name'], part_item['webViewLink']))

        return mixes

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        return error


# if __name__ == '__main__':
#     get_mixes()