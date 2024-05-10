# requirements: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import sys

# Define the scopes
# TODO reduce scope
SCOPES = ['https://www.googleapis.com/auth/drive']

def service_account_login(creds_file):
    creds = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES)
    return creds

def get_service(creds_file):
    creds = service_account_login(creds_file)
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_file(service, file_name, file_path, folder_id):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]  # Folder ID of the Google Drive folder
    }
    media = MediaFileUpload(file_path, mimetype='application/zip')

    print(f"google-drive > starting upload")
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"google-drive > uploaded with id: {file.get('id')}")

def main():
    if not len(sys.argv) == 4:
        print("usage: upload.py service_account.json driver_foler_id file_name.tgz")
    service = get_service(sys.argv[1])
    upload_file(service, os.path.basename(sys.argv[3]), sys.argv[3], sys.argv[2])

if __name__ == '__main__':
    main()


