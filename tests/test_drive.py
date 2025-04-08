import unittest
import os
from unittest.mock import patch, MagicMock
from utils.drive_utils import list_pdfs, download_pdf_and_extract_text
from config import FOLDER_ID

class TestDrive(unittest.TestCase):
    """Test cases for Google Drive integration."""
    
    @unittest.skipIf(not FOLDER_ID, "FOLDER_ID environment variable not set")
    def test_list_pdfs(self):
        """Test that list_pdfs returns a list of PDF files."""
        files = list_pdfs(FOLDER_ID)
        self.assertIsInstance(files, list)
        if files:  # Only run these assertions if files were found
            self.assertIn('id', files[0])
            self.assertIn('name', files[0])
            self.assertTrue(files[0]['name'].endswith('.pdf') or 
                           'pdf' in files[0]['name'].lower())
    
    @unittest.skipIf(not FOLDER_ID, "FOLDER_ID environment variable not set")
    def test_download_pdf_and_extract_text(self):
        """Test that download_pdf_and_extract_text returns text from a PDF."""
        files = list_pdfs(FOLDER_ID)
        if not files:
            self.skipTest("No PDF files found in the specified folder")
        
        # Test with the first file
        file_id = files[0]['id']
        text = download_pdf_and_extract_text(file_id)
        
        self.assertIsInstance(text, str)
        self.assertTrue(len(text) > 0, "Extracted text should not be empty")
        
        # Print a preview of the extracted text for manual verification
        print(f"\nExtracted text preview from {files[0]['name']}:")
        print(f"{text[:500]}...\n")

if __name__ == "__main__":
    unittest.main()
