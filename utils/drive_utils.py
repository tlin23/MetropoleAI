# drive_utils.py

import io
from googleapiclient.http import MediaIoBaseDownload
from PyPDF2 import PdfReader
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials from the JSON file
def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        'service_account.json',
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

# List PDF files in a given folder ID
def list_pdfs(folder_id: str):
    service = get_drive_service()
    query = f"'{folder_id}' in parents and mimeType='application/pdf'"
    response = service.files().list(q=query, fields="files(id, name)").execute()
    return response.get('files', [])

# Download pdf and extract text
def download_pdf_and_extract_text(file_id: str) -> str:
    try:
        service = get_drive_service()

        # Download PDF to memory
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()

        # Extract text using PyPDF2
        fh.seek(0)
        reader = PdfReader(fh)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to process PDF {file_id}: {e}")
        return ""