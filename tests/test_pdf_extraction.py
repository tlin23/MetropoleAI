import unittest
import os
import shutil
from unittest.mock import patch, MagicMock
from utils.drive_utils import list_pdfs, download_pdf_and_extract_text
from model.index import build_index_from_texts, load_index
from config import FOLDER_ID

class TestPdfExtraction(unittest.TestCase):
    """Test cases for PDF extraction and indexing."""
    
    TEST_INDEX_DIR = "test_index"
    
    def setUp(self):
        """Set up the test case."""
        # Create a test index directory
        os.makedirs(self.TEST_INDEX_DIR, exist_ok=True)
    
    def tearDown(self):
        """Clean up after the test case."""
        # Remove the test index directory
        if os.path.exists(self.TEST_INDEX_DIR):
            shutil.rmtree(self.TEST_INDEX_DIR)
    
    @unittest.skipIf(not FOLDER_ID, "FOLDER_ID environment variable not set")
    def test_pdf_extraction_and_indexing(self):
        """Test the full PDF extraction and indexing process."""
        # List PDF files
        files = list_pdfs(FOLDER_ID)
        if not files:
            self.skipTest("No PDF files found in the specified folder")
        
        # Extract text from PDFs
        texts = []
        for f in files:
            print(f"🔄 Processing {f['name']}...")
            text = download_pdf_and_extract_text(f["id"])
            if text:
                texts.append(text)
        
        # Verify that we have extracted text
        self.assertTrue(len(texts) > 0, "No text was extracted from PDFs")
        
        # Build index
        print("📚 Building index...")
        index = build_index_from_texts(texts, self.TEST_INDEX_DIR)
        
        # Verify that the index was created
        self.assertIsNotNone(index, "Index was not created")
        self.assertTrue(os.path.exists(os.path.join(self.TEST_INDEX_DIR, "faiss.index")), 
                       "FAISS index file was not created")
        self.assertTrue(os.path.exists(os.path.join(self.TEST_INDEX_DIR, "texts.pkl")), 
                       "Texts file was not created")
        
        # Test loading the index
        loaded_index = load_index(self.TEST_INDEX_DIR)
        self.assertIsNotNone(loaded_index, "Failed to load the index")
        
        # Test querying the index
        query_engine = loaded_index.as_query_engine()
        response = query_engine.query("test query")
        self.assertIsInstance(str(response), str, "Query response should be convertible to string")
        
        print("✅ Index created and tested successfully!")

if __name__ == "__main__":
    unittest.main()
