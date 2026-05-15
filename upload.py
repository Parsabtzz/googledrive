import os
import pickle
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

FOLDER_ID = '1R7UFyYaRzHOFYSOalxkBMFEsS4Y-qjQs'

DOWNLOAD_URL = os.getenv("FILE_URL")

if not DOWNLOAD_URL:
    raise Exception("FILE_URL not found")

filename = DOWNLOAD_URL.split("/")[-1]

print("Downloading:", DOWNLOAD_URL)

response = requests.get(DOWNLOAD_URL, stream=True)

with open(filename, "wb") as file:
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if chunk:
            file.write(chunk)

print("Download complete")

creds = None

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

service = build('drive', 'v3', credentials=creds)

file_metadata = {
    'name': filename,
    'parents': [FOLDER_ID]
}

media = MediaFileUpload(filename, resumable=True)

uploaded = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print("Uploaded:", uploaded.get('id'))