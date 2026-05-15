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
temp_filename = filename + ".part"

print("Downloading:", DOWNLOAD_URL)

# =======================
# 🔥 DOWNLOAD SAFE VERSION
# =======================
try:
    response = requests.get(
        DOWNLOAD_URL,
        stream=True,
        verify=False,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=60
    )

    response.raise_for_status()

    total = int(response.headers.get("Content-Length", 0))
    downloaded = 0

    with open(temp_filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
                print(f"{downloaded}/{total}")

    # اگر فایل خالی بود
    if os.path.getsize(temp_filename) == 0:
        raise Exception("Downloaded file is empty!")

    # اگر سایز mismatch بود
    if total != 0 and os.path.getsize(temp_filename) != total:
        raise Exception("Download incomplete (file corrupted)")

    # rename فقط وقتی کامل شد
    os.rename(temp_filename, filename)

    print("Download complete")

except Exception as e:
    print("Download failed:", e)
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
    raise

# =======================
# 🔥 GOOGLE DRIVE UPLOAD
# =======================
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
