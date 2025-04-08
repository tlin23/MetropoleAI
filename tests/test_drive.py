import unittest
import os
import io
import sys
from unittest.mock import patch, MagicMock
from googleapiclient.errors import HttpError
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
    
    def test_pdf_ingestion_failure(self):
        """Test handling of PDF ingestion failure."""
        # Mock the PyPDF2.PdfReader to raise an exception
        with patch('utils.drive_utils.PdfReader') as mock_pdf_reader:
            # Simulate a PDF that can't be processed
            mock_pdf_reader.side_effect = Exception("Failed to read PDF")
            
            # Mock the service.files().get_media() call
            with patch('utils.drive_utils.get_drive_service') as mock_get_service:
                mock_service = MagicMock()
                mock_files = MagicMock()
                mock_get_media = MagicMock()
                
                mock_get_service.return_value = mock_service
                mock_service.files.return_value = mock_files
                mock_files.get_media.return_value = mock_get_media
                
                # Mock the downloader
                with patch('utils.drive_utils.MediaIoBaseDownload') as mock_downloader_class:
                    mock_downloader = MagicMock()
                    mock_downloader_class.return_value = mock_downloader
                    mock_downloader.next_chunk.return_value = (None, True)
                    
                    # Call the function with a dummy file ID
                    result = download_pdf_and_extract_text("dummy_file_id")
                    
                    # Verify that the function returns an empty string on failure
                    self.assertEqual(result, "")
    
    def test_file_too_large(self):
        """Test handling of files that are too large."""
        # Mock the MediaIoBaseDownload.next_chunk method to raise an error for a large file
        with patch('utils.drive_utils.MediaIoBaseDownload') as mock_downloader_class:
            mock_downloader = MagicMock()
            mock_downloader_class.return_value = mock_downloader
            
            # Simulate a file that's too large (raises an HttpError)
            mock_downloader.next_chunk.side_effect = HttpError(
                resp=MagicMock(status=403),
                content=b'The file is too large to download'
            )
            
            # Mock the service.files().get_media() call
            with patch('utils.drive_utils.get_drive_service') as mock_get_service:
                mock_service = MagicMock()
                mock_files = MagicMock()
                mock_get_media = MagicMock()
                
                mock_get_service.return_value = mock_service
                mock_service.files.return_value = mock_files
                mock_files.get_media.return_value = mock_get_media
                
                # Call the function with a dummy file ID
                result = download_pdf_and_extract_text("large_file_id")
                
                # Verify that the function returns an empty string on failure
                self.assertEqual(result, "")

if __name__ == "__main__":
    unittest.main()
