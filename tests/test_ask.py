"""
Test the enhanced /ask endpoint with top-3 match rewriting.
"""

import json
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the parent directory to the Python path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

# Create a test client
client = TestClient(app)

def test_ask_endpoint():
    """
    Test the /ask endpoint using TestClient.
    """
    # Test question
    test_question = "What are the building's quiet hours?"
    
    # Send request to the endpoint
    response = client.post("/ask", json={"question": test_question})
    
    # Check response status code
    assert response.status_code == 200
    
    # Parse response data
    data = response.json()
    
    # Check that the response contains all expected fields
    assert "question" in data
    assert "score" in data
    assert "response_type" in data
    assert "raw_passages" in data
    assert "filtered_out" in data
    assert "final_response" in data
    
    # Check that the question matches what we sent
    assert data["question"] == test_question
    
    # Print the response for manual inspection
    print("\nResponse from /ask endpoint:")
    print(json.dumps(data, indent=2))
    
    # Additional checks based on the response
    if data["response_type"] == "rewrite":
        # If we got a rewrite, check that we have raw passages
        assert len(data["raw_passages"]) > 0
        # Check that the highest score passage is first
        if len(data["raw_passages"]) > 1:
            assert data["raw_passages"][0]["score"] >= data["raw_passages"][1]["score"]
    elif data["response_type"] == "fallback":
        # If we got a fallback, check that we have filtered_out passages
        assert len(data["filtered_out"]) > 0
    
    return data

if __name__ == "__main__":
    # Run the test
    print("Testing /ask endpoint...")
    result = test_ask_endpoint()
