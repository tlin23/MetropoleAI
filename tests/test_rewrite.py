"""
Tests for the rewrite functionality of the Metropole.AI chatbot.
"""

import os
import sys
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from fastapi.testclient import TestClient

# Add the parent directory to the Python path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from model.index import SIMILARITY_THRESHOLD
from model.rewrite_utils import rewrite_answer

# Create a test client
client = TestClient(app)

# Sample data for testing
SAMPLE_QUESTION = "What are the pool hours?"
SAMPLE_PASSAGE = "The pool is open from 6am to 10pm on weekdays, and 8am to 9pm on weekends. Residents must have their key fob to access the pool area."
SAMPLE_REWRITTEN = "The pool is open from 6am to 10pm Monday through Friday, and 8am to 9pm on weekends. Don't forget to bring your key fob to access the pool area!"


class MockIndex:
    """Mock index for testing."""
    
    def query(self, query_text, top_k=3):
        """Mock query method that returns predefined results based on the query."""
        # Return high score for specific test question
        if query_text == SAMPLE_QUESTION:
            return [
                {"text": SAMPLE_PASSAGE, "score": 0.85},
                {"text": "Additional information about the pool.", "score": 0.75},
                {"text": "Some other text about the building.", "score": 0.65}
            ]
        # Return low score for fallback testing
        elif query_text == "fallback test":
            return [
                {"text": "Some irrelevant text", "score": 0.2},
                {"text": "More irrelevant text", "score": 0.15},
                {"text": "Even more irrelevant text", "score": 0.1}
            ]
        # Return empty for error testing
        elif query_text == "error test":
            return []
        # Default response
        else:
            return [
                {"text": "Generic response", "score": 0.75},
                {"text": "Another generic response", "score": 0.65},
                {"text": "Yet another generic response", "score": 0.55}
            ]


@pytest.fixture
def mock_index():
    """Fixture to patch the index in the main module."""
    with patch("main.index", MockIndex()):
        yield


@pytest.fixture
def mock_rewrite_success():
    """Fixture to mock a successful rewrite."""
    async def mock_rewrite(question, passage):
        return SAMPLE_REWRITTEN
    
    with patch("main.rewrite_answer", mock_rewrite):
        yield


@pytest.fixture
def mock_rewrite_failure():
    """Fixture to mock a failed rewrite."""
    async def mock_rewrite(question, passage):
        return None
    
    with patch("main.rewrite_answer", mock_rewrite):
        yield


@pytest.fixture
def mock_env_threshold(monkeypatch):
    """Fixture to set the similarity threshold via environment variable."""
    original_threshold = SIMILARITY_THRESHOLD
    
    class ThresholdContext:
        def __init__(self, value):
            self.value = value
            
        def __enter__(self):
            monkeypatch.setenv("SIMILARITY_THRESHOLD", str(self.value))
            # We need to reload the module to pick up the new environment variable
            import importlib
            import model.index
            importlib.reload(model.index)
            # Update the imported value in main
            self.patcher = patch("main.SIMILARITY_THRESHOLD", float(self.value))
            self.patcher.start()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.patcher.stop()
            # Reset to original value
            monkeypatch.setenv("SIMILARITY_THRESHOLD", str(original_threshold))
            import importlib
            import model.index
            importlib.reload(model.index)
    
    def _set_threshold(value):
        return ThresholdContext(value)
    
    return _set_threshold


def test_rewrite_answer_success():
    """Test that rewrite_answer successfully rewrites passages."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.json.return_value = [{"generated_text": SAMPLE_REWRITTEN}]
    mock_response.raise_for_status.return_value = None
    
    # Create a mock client
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
    
    # Patch the AsyncClient class to return our mock
    with patch("httpx.AsyncClient", return_value=mock_client):
        # Set the API token for testing
        with patch.dict(os.environ, {"HF_TOKEN": "test_token"}):
            # Run the test
            import asyncio
            passages = [
                {"text": SAMPLE_PASSAGE, "score": 0.85},
                {"text": "Additional information about the pool.", "score": 0.75}
            ]
            result = asyncio.run(rewrite_answer(SAMPLE_QUESTION, passages))
            
            # Verify the result
            assert result == SAMPLE_REWRITTEN


def test_rewrite_answer_failure():
    """Test that rewrite_answer handles API failures gracefully."""
    # Create a proper async mock for the client that raises an exception
    async def mock_post(*args, **kwargs):
        raise httpx.RequestError("Connection error")
    
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.post = mock_post
    
    with patch("httpx.AsyncClient", return_value=mock_client_instance):
        # Set the API token for testing
        with patch.dict(os.environ, {"HF_TOKEN": "test_token"}):
            # Run the test
            import asyncio
            passages = [
                {"text": SAMPLE_PASSAGE, "score": 0.85},
                {"text": "Additional information about the pool.", "score": 0.75}
            ]
            result = asyncio.run(rewrite_answer(SAMPLE_QUESTION, passages))
            
            # Verify the result is None on failure
            assert result is None


def test_ask_endpoint_high_score(mock_index, mock_rewrite_success):
    """Test that /ask endpoint returns rewritten answer for high scores."""
    response = client.post("/ask", json={"question": SAMPLE_QUESTION})
    assert response.status_code == 200
    assert response.json()["final_response"] == SAMPLE_REWRITTEN


def test_ask_endpoint_rewrite_failure(mock_index, mock_rewrite_failure):
    """Test that /ask endpoint falls back to raw passage when rewrite fails."""
    response = client.post("/ask", json={"question": SAMPLE_QUESTION})
    assert response.status_code == 200
    assert response.json()["final_response"] == SAMPLE_PASSAGE


def test_ask_endpoint_low_score(mock_index):
    """Test that /ask endpoint returns fallback message for low scores."""
    response = client.post("/ask", json={"question": "fallback test"})
    assert response.status_code == 200
    assert "No strong match found in index" in response.json()["final_response"]


def test_ask_endpoint_error(mock_index):
    """Test that /ask endpoint handles errors gracefully."""
    response = client.post("/ask", json={"question": "error test"})
    assert response.status_code == 200
    assert "No information found" in response.json()["final_response"]


def test_debug_ask_endpoint(mock_index, mock_rewrite_success):
    """Test that /debug/ask endpoint returns detailed information."""
    # Note: The debug endpoint has been removed in the current implementation
    # This test is kept for reference but will be skipped
    pytest.skip("Debug endpoint has been removed in the current implementation")


def test_threshold_change(mock_index, mock_rewrite_success, mock_env_threshold):
    """Test that changing the threshold affects the rewrite behavior."""
    # Set threshold high so the score (0.85) is below it
    with mock_env_threshold(0.9):
        response = client.post("/ask", json={"question": SAMPLE_QUESTION})
        assert response.status_code == 200
        assert "No strong match found in index" in response.json()["final_response"]
    
    # Set threshold low so the score (0.85) is above it
    with mock_env_threshold(0.8):
        response = client.post("/ask", json={"question": SAMPLE_QUESTION})
        assert response.status_code == 200
        assert response.json()["final_response"] == SAMPLE_REWRITTEN
