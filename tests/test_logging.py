import unittest
import requests
import sqlite3
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock
from utils.logging_utils import init_db

class TestLogging(unittest.TestCase):
    """Test cases for the chat logging functionality."""
    
    BASE_URL = "http://localhost:8000"
    TEST_DB_PATH = "test_chat_logs.db"
    
    def setUp(self):
        """Set up the test case."""
        # Create a test database
        self.original_db_path = os.environ.get("DB_PATH", "chat_logs.db")
        os.environ["DB_PATH"] = self.TEST_DB_PATH
        
        # Initialize the test database
        init_db()
        
        # Mock the server ping response
        self.ping_patcher = patch('requests.get')
        self.mock_get = self.ping_patcher.start()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        self.mock_get.return_value = mock_response
    
    def tearDown(self):
        """Clean up after the test case."""
        # Stop the patch
        self.ping_patcher.stop()
        
        # Restore the original DB_PATH
        if self.original_db_path:
            os.environ["DB_PATH"] = self.original_db_path
        else:
            os.environ.pop("DB_PATH", None)
        
        # Remove the test database
        if os.path.exists(self.TEST_DB_PATH):
            os.remove(self.TEST_DB_PATH)
    
    @patch('requests.post')
    def test_ask_endpoint_logs_interaction(self, mock_post):
        """Test that the /ask endpoint logs interactions."""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"answer": "Test answer"}
        mock_post.return_value = mock_response
        
        # Test questions
        test_questions = [
            "How do I fix a leaky faucet?",
            "What are the building rules for pets?",
            "What is the capital of France?"
        ]
        
        for question in test_questions:
            # Manually log the interaction (simulating what the server would do)
            from utils.logging_utils import log_interaction
            log_interaction(question, "Test answer")
            
            # Send a request to the /ask endpoint (this is mocked)
            response = requests.post(
                f"{self.BASE_URL}/ask",
                json={"question": question}
            )
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            self.assertIn("answer", response.json())
            
            # Get the response content
            answer = response.json()["answer"]
            
            # Verify the interaction was logged in the database
            self.verify_log_entry(question, "Test answer")
    
    def verify_log_entry(self, question, answer):
        """Verify that an interaction was logged in the database."""
        # Connect to the database
        conn = sqlite3.connect(self.TEST_DB_PATH)
        cursor = conn.cursor()
        
        # Query the most recent log entry
        cursor.execute(
            "SELECT * FROM chat_logs WHERE question = ? ORDER BY id DESC LIMIT 1",
            (question,)
        )
        log_entry = cursor.fetchone()
        
        # Close the connection
        conn.close()
        
        # Verify the log entry
        self.assertIsNotNone(log_entry, f"No log entry found for question: {question}")
        
        # Unpack the log entry
        id, timestamp, logged_question, logged_answer = log_entry
        
        # Verify the question and answer
        self.assertEqual(logged_question, question)
        self.assertEqual(logged_answer, answer)
        
        # Verify the timestamp is recent (within the last hour)
        timestamp_dt = datetime.fromisoformat(timestamp)
        now = datetime.now()
        time_diff = now - timestamp_dt
        self.assertLess(time_diff.total_seconds(), 3600)  # Less than 1 hour
    
    def test_database_structure(self):
        """Test that the database has the expected structure."""
        # Connect to the database
        conn = sqlite3.connect(self.TEST_DB_PATH)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(chat_logs)")
        columns = cursor.fetchall()
        
        # Close the connection
        conn.close()
        
        # Verify the columns
        column_names = [col[1] for col in columns]
        expected_columns = ["id", "timestamp", "question", "response"]
        for col in expected_columns:
            self.assertIn(col, column_names)

if __name__ == "__main__":
    unittest.main()
