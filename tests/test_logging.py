import unittest
import requests
import sqlite3
import json
from datetime import datetime

class TestLogging(unittest.TestCase):
    """Test cases for the chat logging functionality."""
    
    BASE_URL = "http://localhost:8000"
    
    def setUp(self):
        """Set up the test case."""
        # Verify the server is running
        try:
            response = requests.get(f"{self.BASE_URL}/ping")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "ok"})
        except requests.exceptions.ConnectionError:
            self.fail("Server is not running. Please start the server before running tests.")
    
    def test_ask_endpoint_logs_interaction(self):
        """Test that the /ask endpoint logs interactions."""
        # Test questions
        test_questions = [
            "How do I fix a leaky faucet?",
            "What are the building rules for pets?",
            "What is the capital of France?"
        ]
        
        for question in test_questions:
            # Send a request to the /ask endpoint
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
            self.verify_log_entry(question, answer)
    
    def verify_log_entry(self, question, answer):
        """Verify that an interaction was logged in the database."""
        # Connect to the database
        conn = sqlite3.connect('chat_logs.db')
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
        conn = sqlite3.connect('chat_logs.db')
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
