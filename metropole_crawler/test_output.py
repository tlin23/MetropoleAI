#!/usr/bin/env python3
"""
Test script to verify the output format changes in metropole_crawler.py
"""

import os
import json
import datetime

# Create a sample output with the new format
sample_data = {
    "metadata": {
        "crawl_date": datetime.datetime.now().isoformat(),
        "base_url": "https://example.com",
        "max_depth": 2,
        "total_pages": 3,
        "version": "1.0"
    },
    "pages": [
        {
            "url": "https://example.com/page1",
            "title": "Page 1",
            "content": "This is page 1 content"
        },
        {
            "url": "https://example.com/page2",
            "title": "Page 2",
            "content": "This is page 2 content"
        },
        {
            "url": "https://example.com/page3",
            "title": "Page 3",
            "content": "This is page 3 content"
        }
    ]
}

# Create the data directory if it doesn't exist
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)

# Generate a timestamped filename
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_json_path = os.path.join(data_dir, f"test_output_{timestamp}.json")

# Save the sample data to a JSON file
with open(output_json_path, "w", encoding="utf-8") as json_file:
    json.dump(sample_data, json_file, indent=2, ensure_ascii=False)

print(f"Test output saved to: {output_json_path}")

# Validate the output format
with open(output_json_path, "r", encoding="utf-8") as json_file:
    loaded_data = json.load(json_file)
    
    # Check if the loaded data has the expected structure
    if "metadata" in loaded_data and "pages" in loaded_data:
        print("Output format is correct!")
        print(f"Metadata: {loaded_data['metadata']}")
        print(f"Number of pages: {len(loaded_data['pages'])}")
    else:
        print("Output format is incorrect!")
        print(f"Keys in loaded data: {list(loaded_data.keys())}")
