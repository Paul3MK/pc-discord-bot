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


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
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

        # Call the Drive v3 API
        results = service.files().list(
            spaces="drive", corpora="allDrives", includeItemsFromAllDrives="true", supportsAllDrives="true", pageSize=10, fields="nextPageToken, files(id, name, webViewLink)", q="name contains 'Lost'").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

        parts = service.files().list(corpora="allDrives", includeItemsFromAllDrives="true", supportsAllDrives="true", pageSize=10, fields="nextPageToken, files(id, name, webViewLink)", q=f"parents in '1dBg8fTB6M7ogsVYAFS2m8ktyBogcKPlv'").execute()
        part_items = parts.get('files', [])

        if not part_items:
            print('No files found.')
            return
        print('Files:')
        for part_item in part_items:
            print(u'{0} ({1})'.format(part_item['name'], part_item['webViewLink']))

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()