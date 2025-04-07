from utils.drive_utils import list_pdfs, download_pdf_and_extract_text
from utils.index_utils import build_index_from_texts
from config import FOLDER_ID

files = list_pdfs(FOLDER_ID)
texts = []

for f in files:
    print(f"🔄 Processing {f['name']}...")
    text = download_pdf_and_extract_text(f["id"])
    if text:
        texts.append(text)

print("📚 Building index...")
build_index_from_texts(texts)
print("✅ Index saved!")