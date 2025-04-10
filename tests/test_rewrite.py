"""
Tests for the rewrite functionality of the Metropole.AI chatbot.
"""

import os
import pytest
from unittest.mock import patch, AsyncMock
import httpx
from fastapi.testclient import TestClient

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
    
    def query(self, query_text):
        """Mock query method that returns predefined results based on the query."""
        # Return high score for specific test question
        if query_text == SAMPLE_QUESTION:
            return {"text": SAMPLE_PASSAGE, "score": 0.85}
        # Return low score for fallback testing
        elif query_text == "fallback test":
            return {"text": "Some irrelevant text", "score": 0.2}
        # Return empty for error testing
        elif query_text == "error test":
            return {"text": "", "score": 0.0}
        # Default response
        else:
            return {"text": "Generic response", "score": 0.75}


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
    """Test that rewrite_answer successfully rewrites a passage."""
    # Create a mock response object
    mock_response = AsyncMock()
    # Set up json() and raise_for_status() to be awaitable
    mock_response.json = AsyncMock(return_value={"generated_text": SAMPLE_REWRITTEN})
    mock_response.raise_for_status = AsyncMock()
    
    # Create a mock client
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.post.return_value = mock_response
    
    # Patch the AsyncClient class to return our mock
    with patch("httpx.AsyncClient", return_value=mock_client):
        # Set the API token for testing
        with patch.dict(os.environ, {"HF_TOKEN": "test_token"}):
            # Run the test
            import asyncio
            result = asyncio.run(rewrite_answer(SAMPLE_QUESTION, SAMPLE_PASSAGE))
            
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
            result = asyncio.run(rewrite_answer(SAMPLE_QUESTION, SAMPLE_PASSAGE))
            
            # Verify the result is None on failure
            assert result is None


def test_ask_endpoint_high_score(mock_index, mock_rewrite_success):
    """Test that /ask endpoint returns rewritten answer for high scores."""
    response = client.post("/ask", json={"question": SAMPLE_QUESTION})
    assert response.status_code == 200
    assert response.json()["answer"] == SAMPLE_REWRITTEN


def test_ask_endpoint_rewrite_failure(mock_index, mock_rewrite_failure):
    """Test that /ask endpoint falls back to raw passage when rewrite fails."""
    response = client.post("/ask", json={"question": SAMPLE_QUESTION})
    assert response.status_code == 200
    assert response.json()["answer"] == SAMPLE_PASSAGE


def test_ask_endpoint_low_score(mock_index):
    """Test that /ask endpoint returns fallback message for low scores."""
    response = client.post("/ask", json={"question": "fallback test"})
    assert response.status_code == 200
    assert "No strong match found in index" in response.json()["answer"]


def test_ask_endpoint_error(mock_index):
    """Test that /ask endpoint handles errors gracefully."""
    response = client.post("/ask", json={"question": "error test"})
    assert response.status_code == 200
    assert "No information found" in response.json()["answer"]


def test_debug_ask_endpoint(mock_index, mock_rewrite_success):
    """Test that /debug/ask endpoint returns detailed information."""
    response = client.post("/debug/ask", json={"question": SAMPLE_QUESTION})
    assert response.status_code == 200
    data = response.json()
    
    # Verify all expected fields are present
    assert data["question"] == SAMPLE_QUESTION
    assert data["score"] == 0.85
    assert data["response_type"] == "rewrite"
    assert data["raw_passage"] == SAMPLE_PASSAGE
    assert data["final_response"] == SAMPLE_REWRITTEN


def test_threshold_change(mock_index, mock_rewrite_success, mock_env_threshold):
    """Test that changing the threshold affects the rewrite behavior."""
    # Set threshold high so the score (0.85) is below it
    with mock_env_threshold(0.9):
        response = client.post("/ask", json={"question": SAMPLE_QUESTION})
        assert response.status_code == 200
        assert "No strong match found in index" in response.json()["answer"]
    
    # Set threshold low so the score (0.85) is above it
    with mock_env_threshold(0.8):
        response = client.post("/ask", json={"question": SAMPLE_QUESTION})
        assert response.status_code == 200
        assert response.json()["answer"] == SAMPLE_REWRITTEN
