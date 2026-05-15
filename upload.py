import os
import pickle
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = '1R7UFyYaRzHOFYSOalxkBMFEsS4Y-qjQs'

DOWNLOAD_URL = os.getenv("FILE_URL")

if not DOWNLOAD_URL:
    raise Exception("FILE_URL not found")

filename = DOWNLOAD_URL.split("/")[-1]

print("Downloading:", DOWNLOAD_URL)

response = requests.get(
    DOWNLOAD_URL,
    stream=True,
    verify=False,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=60
)

# ⭐ مهم: چک وضعیت
response.raise_for_status()

# ⭐ دانلود امن
temp_filename = filename + ".part"

with open(temp_filename, "wb") as file:
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if chunk:
            file.write(chunk)

# ⭐ بررسی سایز
if os.path.getsize(temp_filename) == 0:
    raise Exception("Downloaded file is empty!")

os.rename(temp_filename, filename)

print("Download complete")

# ---------- Google Drive ----------
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
