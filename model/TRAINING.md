# Model Training Guide

This document explains how to train the model for the Metropole.AI project.

## Overview

The Metropole.AI project uses a vector index built from PDF documents stored in Google Drive. The index is used to answer user questions about the apartment building. Training the model involves building this index from the PDF documents.

## Prerequisites

Before training the model, ensure you have:

1. A `service_account.json` file with Google Drive API credentials in the project root directory
2. The `FOLDER_ID` environment variable set in your `.env` file (pointing to the Google Drive folder containing your PDFs)
3. All required Python dependencies installed (see `requirements.txt`)

## Training Process

### Using the Training Script

The project includes a dedicated script for training the model:

```bash
python -m model.train
```

This script will:
1. List all PDFs in your Google Drive folder
2. Download and extract text from each PDF
3. Build a new index from the extracted texts
4. Save the index to the `model/index` directory

### When to Train

You should train the model when:
- New PDF documents are added to the Google Drive folder
- Existing PDF documents are updated or modified
- You want to change the model parameters or chunking strategy

### Verifying the Training

After training, you can verify that the new index is working correctly by:
1. Starting the FastAPI server: `uvicorn main:app --reload`
2. Sending test questions to the `/ask` endpoint
3. Checking that the responses include information from your updated documents

## Troubleshooting

If you encounter issues during training:

- Check that your `service_account.json` file is valid and has the correct permissions
- Ensure the `FOLDER_ID` environment variable is set correctly
- Look for error messages in the console output
- Check that your PDF files are readable and contain extractable text

## Future Improvements

In the future, we plan to implement an automatic synchronization feature that will:
- Periodically check for changes in the Google Drive folder
- Automatically train the model when changes are detected
- Log all sync activities for monitoring
