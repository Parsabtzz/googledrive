from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

SERVICE_ACCOUNT_FILE = 'service_account.json'

FOLDER_ID = '1R7UFyYaRzHOFYSOalxkBMFEsS4Y-qjQs'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

service = build('drive', 'v3', credentials=creds)

file_path = 'test.txt'

file_metadata = {
    'name': 'test.txt',
    'parents': [FOLDER_ID]
}

media = MediaFileUpload(file_path, resumable=True)

uploaded = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print("DONE:", uploaded.get('id'))