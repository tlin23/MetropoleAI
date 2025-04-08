from utils.drive_utils import list_pdfs, download_pdf_and_extract_text
from config import FOLDER_ID

files = list_pdfs(FOLDER_ID)
for f in files:
    print(f"{f['name']} — {f['id']}")
    text = download_pdf_and_extract_text(f["id"])
    print(f"--- Extracted Text Preview ---\n{text[:500]}\n")