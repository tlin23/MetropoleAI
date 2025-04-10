#!/usr/bin/env python3
"""
Unit tests for the smart chunking module.
"""

import os
import pytest
from model.smart_chunking import (
    load_metropole_pages,
    clean_text,
    extract_breadcrumb,
    split_sentences,
    is_contact_info,
    count_tokens,
    chunk_sentences,
    format_chunks,
    write_chunks_debug,
    smart_chunk_metropole_pages
)

# Sample test data
SAMPLE_PAGES = [
    {
        "title": "Board 2024",
        "url": "https://sites.google.com/view/metropoleballard/board-2024",
        "content": "# Board Members\n\nFrederic Wehman, iii\nUnit 22, Seat 5 (2024)\nfrederic@example.com\n555-123-4567\n\nJane Smith\nUnit 15, Seat 3 (2024)\njane@example.com\n555-987-6543"
    },
    {
        "title": "Newsletter",
        "url": "https://sites.google.com/view/metropoleballard/newsletter",
        "content": "# Latest Updates\n\nWelcome to the Metropole newsletter. Here you'll find the latest updates about our community.\n\n## March 2024\n\nThe annual meeting is scheduled for April 15th. Please mark your calendars and plan to attend. We'll be discussing the budget for the upcoming year and electing new board members.\n\n## February 2024\n\nThe renovation of the lobby is complete. Thank you for your patience during this process. We hope you enjoy the new look!"
    },
    {
        "title": "Missing Content",
        "url": "https://sites.google.com/view/metropoleballard/missing",
        "content": ""
    },
    {
        "url": "https://sites.google.com/view/metropoleballard/no-title",
        "content": "This page has no title."
    }
]

def test_load_metropole_pages():
    """Test loading and validating Metropole pages."""
    valid_pages = load_metropole_pages(SAMPLE_PAGES)
    
    # Should only include pages with title, url, and non-empty content
    assert len(valid_pages) == 2
    assert valid_pages[0]["title"] == "Board 2024"
    assert valid_pages[1]["title"] == "Newsletter"

def test_clean_text():
    """Test cleaning and normalizing text content."""
    raw_text = "# Heading\n\n\nMultiple newlines\n\n## Subheading\nNormal text"
    cleaned_text = clean_text(raw_text)
    
    # Should remove markdown headers and normalize newlines
    assert "# Heading" not in cleaned_text
    assert "## Subheading" not in cleaned_text
    assert "\n\n\n" not in cleaned_text
    
    # Check that content is preserved with normalized newlines
    assert "Heading" in cleaned_text
    assert "Multiple newlines" in cleaned_text
    assert "Subheading" in cleaned_text
    assert "Normal text" in cleaned_text

def test_extract_breadcrumb():
    """Test extracting breadcrumb from title or content."""
    # From title
    title1 = "Board 2024"
    content1 = "Some content"
    assert extract_breadcrumb(title1, content1) == "Board 2024"
    
    # From content
    title2 = "Page"
    content2 = "First line\nNewsletter\nThird line"
    assert extract_breadcrumb(title2, content2) == "Newsletter"
    
    # Fallback to title
    title3 = "Regular Page"
    content3 = "No special headings here"
    assert extract_breadcrumb(title3, content3) == "Regular Page"

def test_split_sentences():
    """Test splitting text into sentences using spaCy."""
    text = "This is sentence one. This is sentence two! What about sentence three?"
    sentences = split_sentences(text)
    
    assert len(sentences) == 3
    assert sentences[0] == "This is sentence one."
    assert sentences[1] == "This is sentence two!"
    assert sentences[2] == "What about sentence three?"

def test_is_contact_info():
    """Test detecting contact information."""
    # Contact info with multiple patterns
    contact_text = "Unit 22, Seat 5 (2024)\nfrederic@example.com\n555-123-4567"
    assert is_contact_info(contact_text) == True
    
    # Regular text
    regular_text = "This is just a regular paragraph with no contact information."
    assert is_contact_info(regular_text) == False
    
    # Text with only one contact pattern
    partial_text = "This text mentions Unit 22 but nothing else."
    assert is_contact_info(partial_text) == False

def test_count_tokens():
    """Test counting tokens in text."""
    text = "This is a sample text for token counting."
    token_count = count_tokens(text)
    
    # The exact count may vary depending on the tokenizer, but should be reasonable
    assert token_count > 0
    assert token_count < 20  # Reasonable upper bound for this short text

def test_chunk_sentences():
    """Test grouping sentences into chunks based on token limit."""
    sentences = [
        "This is sentence one.",
        "This is sentence two.",
        "This is sentence three.",
        "This is sentence four.",
        "This is sentence five."
    ]
    
    # With a high token limit, all sentences should be in one chunk
    chunks_high_limit = chunk_sentences(sentences, 1000)
    assert len(chunks_high_limit) == 1
    assert len(chunks_high_limit[0]) == 5
    
    # With a very low token limit, each sentence should be its own chunk
    chunks_low_limit = chunk_sentences(sentences, 5)
    assert len(chunks_low_limit) >= 4  # At least 4 chunks

def test_format_chunks():
    """Test formatting chunks with metadata."""
    sentence_chunks = [
        ["This is chunk one."],
        ["This is chunk two."]
    ]
    breadcrumb = "Test Page"
    url = "https://example.com/test"
    
    formatted_chunks = format_chunks(sentence_chunks, breadcrumb, url)
    
    assert len(formatted_chunks) == 2
    assert formatted_chunks[0]["text"].startswith("Test Page >")
    assert formatted_chunks[0]["metadata"]["breadcrumb"] == "Test Page"
    assert formatted_chunks[0]["metadata"]["source_url"] == url
    assert "tokens" in formatted_chunks[0]["metadata"]

def test_write_chunks_debug(tmp_path):
    """Test writing chunks to a debug file."""
    chunks = [
        {
            "text": "Test Page > This is chunk one.",
            "metadata": {
                "breadcrumb": "Test Page",
                "source_url": "https://example.com/test",
                "tokens": 10
            }
        }
    ]
    
    debug_path = os.path.join(tmp_path, "test_chunks.txt")
    write_chunks_debug(chunks, debug_path)
    
    # Check that the file exists and contains the expected content
    assert os.path.exists(debug_path)
    with open(debug_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "--- Chunk 1 ---" in content
        assert "Test Page > This is chunk one." in content
        assert "breadcrumb=Test Page" in content

def test_smart_chunk_metropole_pages(tmp_path):
    """Test the end-to-end smart chunking process."""
    debug_path = os.path.join(tmp_path, "test_chunks.txt")
    chunk_texts = smart_chunk_metropole_pages(SAMPLE_PAGES, max_tokens=100, debug_path=debug_path)
    
    # Check that we got some chunks
    assert len(chunk_texts) > 0
    
    # Check that the debug file was created
    assert os.path.exists(debug_path)
    
    # Check that the chunks have the expected format (breadcrumb > text)
    for chunk in chunk_texts:
        assert " > " in chunk
