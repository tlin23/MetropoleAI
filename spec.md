# Metropole.AI – MVP Specification

## ✅ Overview
Metropole.AI is a web-based AI chatbot designed to preserve and surface collective knowledge about an apartment building. Residents will be able to interact with a conversational agent that can answer practical questions related to building maintenance, rules, and history.

---

## 🧠 Core Functionality

### User Capabilities
- Ask natural language questions about the building (e.g., “What do I do if my toilet leaks?”).
- Upload a **photo or text file** during the session to provide context.
- Interact with the bot in a conversational style (with memory *within* the session).
- Click a **“Start Over”** button to reset the chat.
- See a welcome message when landing on the page.

---

## 💬 Chatbot Behavior

### Response Style
- Conversational tone.
- Friendly but utility-focused.
- If the agent **has building-specific information**, it provides a direct answer.
- If the info comes from general knowledge, the agent must say so clearly.
- DIY instructions are okay *only if safe* and must include a **disclaimer**:
  > “This is based on past residents’ experience and should not be considered professional advice. When in doubt, contact the board or a licensed professional.”

### Input Handling
- Accepts user text input via a fixed chat UI.
- Accepts image and text file uploads, which are **used for that session only** and discarded afterward.
- Each session is stateless beyond the browser session.

---

## 📄 Data Sources & Processing

### Documents
- All source content lives in **Google Drive**, managed by the admin (you).
- For MVP: **PDFs only**.
- Extraction: **Basic text extraction only** (no layout parsing).
- Automatically ingest and update knowledge when new files are added or existing ones are modified.
- Documents may contain sensitive info — **do not expose names/contact details** unless content is generically labeled (“contact the board”).

### Knowledge Categorization
Content may include:
- Maintenance tips
- HOA rules
- Building history
- Repair/replacement timelines
- Appliance info
- Emergency procedures

### Source Handling
- For MVP: Do **not** cite filenames or links in responses.
- Logged conversations should be anonymized.

---

## ⚙️ Tech Stack (Recommended)

### Backend
- **LlamaIndex** or **LangChain** for document ingestion + retrieval-augmented generation (RAG).
- **OpenAI GPT-4 or GPT-3.5** for the LLM (configurable).
- Basic server with FastAPI or Flask for managing uploads, chatbot API, and Drive sync.

### Frontend
- **Minimal web UI** (React or plain HTML/CSS/JS).
- Chat interface styled like a messenger:
  - Scrolling history
  - Fixed input field
  - "Start Over" button
  - Welcome message on load

### Hosting
- Use free/low-cost platform like **Vercel** or **Netlify** for frontend.
- Use **Render**, **Replit**, or **Fly.io** for backend if needed.

---

## 🔐 Security & Privacy

- Public access for MVP.
- Uploaded files are stored **temporarily** and cleared post-session.
- No personally identifiable information (PII) shown in answers.
- All chat logs stored anonymously (e.g., timestamp + question + response).

---

## 🚫 Error Handling

### PDF ingestion
- If a PDF can’t be read, log the filename and skip it.

### Chatbot responses
- If the agent doesn’t have a good answer:
  > “I don’t have building-specific information on that yet. You may want to contact the board or check back later.”

---

## 📊 Logging & Monitoring

- Log:
  - Anonymized chat transcripts (timestamp, question, response)
  - File upload errors
  - Drive sync updates

- No usage dashboard or admin panel in MVP.

---

## 🧪 Testing Plan

### Functional Testing
- ✅ Text-based questions return relevant answers
- ✅ General fallback responses include disclaimer
- ✅ Uploads work and are discarded after session
- ✅ Start Over button resets chat
- ✅ Session is stateless across refreshes
- ✅ Ingested content updates when PDFs are changed in Drive

### Edge Cases
- ❌ PDF with unusual formatting (should be skipped gracefully)
- ❌ Large file upload (should return error)
- ❌ Question with no relevant data (should fallback to general with disclaimer)

---

## 📆 Development Timeline Suggestion (4 weeks, ~3–4 hrs/day)

| Week | Focus |
|------|-------|
| 1 | Set up Google Drive integration + PDF ingestion + basic LLM-powered Q&A backend |
| 2 | Build frontend chat UI (with file upload + Start Over + welcome message) |
| 3 | Hook up backend to frontend, test chat flow, add logging |
| 4 | Final polish, error handling, testing, deployment on free host |
