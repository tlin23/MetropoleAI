
# 🧱 Metropole.AI – MVP Build Blueprint

This is a detailed step-by-step implementation plan for Metropole.AI, broken down into small, testable chunks, each with code-generation prompts for implementation.

---

## 🗺️ Phase 1: Foundation – Backend & Document Ingestion

### Goal: Set up backend system to ingest PDFs from Google Drive and expose a basic Q&A API.

---

### **Step 1.1: Set Up Backend Project**
**Tasks:**
- Initialize a Python project.
- Install core dependencies (FastAPI, Uvicorn, LlamaIndex, PyPDF2).
- Create basic FastAPI app scaffold with health check route.

**Prompt:**
```
Create a FastAPI backend with a health check endpoint at `/ping` that returns `{"status": "ok"}`. Use `uvicorn` as the development server. Set up the project structure with a `main.py` file.
```

---

### **Step 1.2: Connect to Google Drive**
**Tasks:**
- Authenticate with Google Drive API using a service account.
- List files in a specified folder.

**Prompt:**
```
Implement Google Drive API integration using a service account. Create a function to list all PDF files in a specific folder, returning their names and IDs.
```

---

### **Step 1.3: Download and Extract PDF Text**
**Tasks:**
- Download a PDF file by ID.
- Extract text from the PDF using PyPDF2 or pdfminer.

**Prompt:**
```
Write a function that downloads a PDF file from Google Drive using its file ID and extracts its text content using PyPDF2. Return the extracted text.
```

---

### **Step 1.4: Index Documents with LlamaIndex**
**Tasks:**
- Create a LlamaIndex from the extracted PDF content.
- Save/load the index to disk.

**Prompt:**
```
Using LlamaIndex, create a simple function that builds an index from a list of document texts. Allow saving the index to disk and loading it later.
```

---

### **Step 1.5: Add Query Endpoint**
**Tasks:**
- Add `/ask` POST endpoint to FastAPI.
- Pass user queries to LlamaIndex and return answers.

**Prompt:**
```
Create a `/ask` POST endpoint in FastAPI that accepts a JSON payload with a `question` field. Use the LlamaIndex index to generate a response and return it as JSON.
```

---

### **Step 1.6: Add General Knowledge Fallback**
**Tasks:**
- Use OpenAI GPT API when LlamaIndex returns low confidence or no answer.
- Clearly indicate fallback in the response.

**Prompt:**
```
Enhance the `/ask` endpoint to include a fallback using OpenAI GPT-3.5 if LlamaIndex returns no result. Prefix fallback responses with: "This is based on general knowledge and not specific to the building."
```

---

## 🖼️ Phase 2: UI – Web Chat Interface

### Goal: Create a minimal, styled chat UI that interacts with the backend.

---

### **Step 2.1: Set Up Web Project**
**Tasks:**
- Initialize a React project (Vite or Create React App).
- Install dependencies (Axios, Tailwind).
- Create basic layout.

**Prompt:**
```
Set up a React app with Tailwind CSS. Create a full-screen layout with a central chat window, fixed input box, and scrolling message area.
```

---

### **Step 2.2: Implement Chat Functionality**
**Tasks:**
- Create message state array.
- Submit question via input box.
- Display response in chat window.

**Prompt:**
```
Create a React component for a chat UI. It should maintain a history of messages and send user input to a backend `/ask` endpoint. Display messages in a scrollable window.
```

---

### **Step 2.3: Add Welcome Message + Start Over Button**
**Tasks:**
- Auto-display a welcome message.
- Add a "Start Over" button that resets the chat.

**Prompt:**
```
Update the React chat UI to display a welcome message when the app loads. Add a "Start Over" button that clears all chat history.
```

---

### **Step 2.4: Add File Upload (Images/Text Only)**
**Tasks:**
- Enable drag-and-drop/file select upload.
- Send uploaded file to backend for temporary parsing (MVP scope).

**Prompt:**
```
Enhance the React chat UI to allow uploading `.jpg`, `.png`, or `.txt` files. Send the file to the backend along with the chat message.
```

---

### **Step 2.5: Backend File Upload Handler**
**Tasks:**
- Add `/upload` endpoint to FastAPI.
- Parse text file or image content (OCR stub for now).
- Return parsed result to frontend for context.

**Prompt:**
```
Add a `/upload` POST endpoint to FastAPI that accepts image or text files. Return basic placeholder text for OCR for now. Limit file size to 10MB.
```

---

## 🔗 Phase 3: Integration, Logging, Testing

### Goal: Wire everything together, add logging, polish responses.

---

### **Step 3.1: Add Anonymized Logging**
**Tasks:**
- Log timestamp, question, and response.
- Save to local file or SQLite.

**Prompt:**
```
Log each user interaction in the backend: timestamp, question, and response. Save to a local file or SQLite DB, omitting user identifiers.
```

---

### **Step 3.2: Add Disclaimer Logic for DIY Responses**
**Tasks:**
- If response includes repair suggestions, prepend safety disclaimer.

**Prompt:**
```
Add a disclaimer to any chatbot response that includes keywords like "fix", "repair", or "DIY": "This is based on past residents’ experience and should not be considered professional advice..."
```

---

### **Step 3.3: Implement PDF Watcher for Auto-Sync**
**Tasks:**
- Poll Google Drive folder every N minutes.
- Re-ingest changed files.

**Prompt:**
```
Implement a scheduled task that checks the Google Drive folder every 10 minutes for new or updated PDFs. Rebuild the LlamaIndex if changes are detected.
```

---

### **Step 3.4: Final Testing + Edge Cases**
**Tasks:**
- Write test cases for:
  - PDF ingestion failure
  - File too large
  - No match in knowledge base
  - Fallback disclaimer

**Prompt:**
```
Write unit and integration tests to verify error handling for large uploads, unrecognized PDFs, and fallback behavior when no answer is found.
```

---

## ✅ Phase 4: Deployment

### **Step 4.1: Deploy Backend + Frontend**
**Tasks:**
- Deploy FastAPI backend to Render/Fly.io.
- Deploy React frontend to Vercel or Netlify.

**Prompt:**
```
Provide deployment config for deploying a FastAPI backend on Render and a React frontend on Vercel. Ensure CORS is configured correctly.
```

---

This blueprint provides a clean, testable progression to MVP with no dangling code. Ready to proceed with code-gen prompts for each phase? Let’s build this step by step. 🚀
