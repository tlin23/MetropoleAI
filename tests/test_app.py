import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, fallback_response

class TestApp(unittest.TestCase):
    """Test cases for the main application."""
    
    def setUp(self):
        """Set up the test case."""
        self.client = TestClient(app)
    
    def test_no_match_in_knowledge_base(self):
        """Test fallback behavior when there's no match in the knowledge base."""
        # Mock the query_engine.query method to return an empty result
        with patch('main.index.as_query_engine') as mock_query_engine:
            mock_engine = MagicMock()
            mock_query_engine.return_value = mock_engine
            mock_engine.query.return_value = ""
            
            # Mock the fallback_response function
            with patch('main.fallback_response') as mock_fallback:
                mock_fallback.return_value = "This is based on general knowledge and not specific to the building.\nTest fallback response."
                
                # Send a request to the /ask endpoint
                response = self.client.post(
                    "/ask",
                    json={"question": "What is quantum physics?"}
                )
                
                # Verify the response
                self.assertEqual(response.status_code, 200)
                self.assertIn("answer", response.json())
                
                # Verify that the fallback response was used
                self.assertEqual(
                    response.json()["answer"],
                    "This is based on general knowledge and not specific to the building.\nTest fallback response."
                )
                
                # Verify that the fallback_response function was called
                mock_fallback.assert_called_once()
    
    def test_fallback_disclaimer(self):
        """Test that the fallback response includes the disclaimer."""
        # Mock the openai.ChatCompletion.create method
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.return_value = {
                'choices': [
                    {
                        'message': {
                            'content': 'This is a test response from OpenAI.'
                        }
                    }
                ]
            }
            
            # Call the fallback_response function
            response = fallback_response("Test question")
            
            # Verify that the response includes the disclaimer
            self.assertTrue(
                response.startswith("This is based on general knowledge and not specific to the building."),
                "Fallback response should start with the disclaimer"
            )
            
            # Verify that the response includes the content from OpenAI
            self.assertIn("This is a test response from OpenAI.", response)
    

if __name__ == "__main__":
    unittest.main()
