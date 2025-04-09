
# 🧱 Metropole.AI – MVP Build Blueprint

This is a detailed step-by-step implementation plan for Metropole.AI, broken down into small, testable chunks, each with code-generation prompts for implementation.

---

## 🗺️ Phase 1: Foundation – Backend & Website Content Ingestion

### Goal: Set up backend system to ingest content from the Metropole website and expose a basic Q&A API.

---

### **Step 1.1: Set Up Backend Project**
**Tasks:**
- Initialize a Python project.
- Install core dependencies (FastAPI, Uvicorn, LlamaIndex, BeautifulSoup4, Requests).
- Create basic FastAPI app scaffold with health check route.

**Prompt:**
```
Create a FastAPI backend with a health check endpoint at `/ping` that returns `{"status": "ok"}`. Use `uvicorn` as the development server. Set up the project structure with a `main.py` file.
```

---

### **Step 1.2: Website Content Extraction**
**Tasks:**
- Implement a webcrawler to scrape text content from the Metropole website.
- Process and clean the extracted content.

**Prompt:**
```
Implement a webcrawler to scrape text content from the Metropole website (https://sites.google.com/view/metropoleballard). Create functions to process and clean the extracted content, ensuring it's ready for indexing.
```

---

### **Step 1.3: Index Documents with LlamaIndex**
**Tasks:**
- Create a LlamaIndex from the extracted website content.
- Save/load the index to disk.

**Prompt:**
```
Using LlamaIndex, create a simple function that builds an index from the extracted website content. Allow saving the index to disk and loading it later.
```

---

### **Step 1.4: Add Query Endpoint**
**Tasks:**
- Add `/ask` POST endpoint to FastAPI.
- Pass user queries to LlamaIndex and return answers.

**Prompt:**
```
Create a `/ask` POST endpoint in FastAPI that accepts a JSON payload with a `question` field. Use the LlamaIndex index to generate a response and return it as JSON.
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
Set up a React app. Create a full-screen layout with a central chat window, fixed input box, and scrolling message area.
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

### **Step 3.3: Implement Website Content Refresh**
**Tasks:**
- Schedule periodic website crawling to check for new content.
- Re-index when new content is detected.

**Prompt:**
```
Implement a scheduled task that crawls the Metropole website every 24 hours to check for new or updated content. Rebuild the LlamaIndex if changes are detected.
```

---

### **Step 3.4: Final Testing + Edge Cases**
**Tasks:**
- Write test cases for:
  - Website crawling failure
  - Content processing issues
  - No match in knowledge base
  - Error handling

**Prompt:**
```
Write unit and integration tests to verify error handling for website crawling failures, content processing issues, and behavior when no answer is found in the knowledge base.
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
