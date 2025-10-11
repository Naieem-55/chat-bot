# 🤖 RAG Customer Support Chatbot - System Architecture

## 📋 Overview

This is a **RAG (Retrieval Augmented Generation)** chatbot system that combines:
- **Document retrieval** from a vector database
- **LLM generation** using free models (Groq API with Llama 3.1)
- **Conversation management** with session history
- **Smart features** like autocomplete, suggestions, and hallucination detection

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Port 3001)                      │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ index.html │  │  chat.js     │  │  suggestions.js        │  │
│  │            │  │  (v3.4)      │  │  (autocomplete, PAA)   │  │
│  │  - UI      │  │  - Messages  │  │  - Smart suggestions   │  │
│  │  - Input   │  │  - API calls │  │  - Follow-ups          │  │
│  └────────────┘  └──────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                         HTTP/JSON
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (Port 8000)                       │
│                         FastAPI Server                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  main.py - API Endpoints:                                │   │
│  │  • POST /session/create    - Create session              │   │
│  │  • POST /chat              - Send message                │   │
│  │  • POST /feedback          - Submit feedback             │   │
│  │  • GET  /suggestions/*     - Get suggestions             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG PIPELINE CORE                           │
│                      (rag_pipeline.py)                           │
└─────────────────────────────────────────────────────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐
  │   Session    │ │    Query     │ │   Document   │ │   LLM    │
  │   Manager    │ │Reformulator  │ │  Retriever   │ │  Client  │
  │              │ │              │ │              │ │          │
  │ - History    │ │ - Context    │ │ - Vector     │ │ - Groq   │
  │ - Context    │ │ - Improve    │ │ - BM25       │ │   API    │
  └──────────────┘ └──────────────┘ │ - Hybrid     │ └──────────┘
                                     └──────────────┘
                                            │
                                            ▼
                                  ┌──────────────────┐
                                  │  Vector Store    │
                                  │   (FAISS DB)     │
                                  │                  │
                                  │ - Embeddings     │
                                  │ - Documents      │
                                  │ - Metadata       │
                                  └──────────────────┘
```

---

## 🔄 Message Flow (Step-by-Step)

### **1️⃣ User Sends a Message**

```
User types: "What is your return policy?"
           ↓
    [Send Button Click]
           ↓
    chat.js: sendMessage()
           ↓
    POST /chat → Backend API
```

**File**: `frontend/chat.js:499-691`

---

### **2️⃣ Backend Receives Request**

```
FastAPI: /chat endpoint
           ↓
    Validate request
           ↓
    Get/Create session_id
           ↓
    Call RAG Pipeline
```

**File**: `src/api/main.py:179-243`

---

### **3️⃣ RAG Pipeline Processing**

```
rag_pipeline.process_query()
           │
           ├─► Step 1: Get conversation history
           │   SessionManager → Retrieve past messages
           │
           ├─► Step 2: Reformulate query (if needed)
           │   QueryReformulator → Improve question clarity
           │   "return policy" → "What is the return and refund policy?"
           │
           ├─► Step 3: Hybrid Document Retrieval
           │   ┌──────────────────────────────────┐
           │   │ Vector Search (semantic)   50%   │
           │   │ BM25 Search (keyword)      30%   │
           │   │ Reformulated Query         20%   │
           │   └──────────────────────────────────┘
           │   → Retrieve top 5 most relevant documents
           │
           ├─► Step 4: Format context
           │   Combine retrieved documents into text
           │
           ├─► Step 5: Build LLM prompt
           │   System Prompt + History + Context + User Query
           │
           ├─► Step 6: Generate response
           │   LLM Client → Groq API (Llama 3.1)
           │   → "Our return policy allows returns within 30 days..."
           │
           ├─► Step 7: Save to history
           │   SessionManager → Store user query + bot response
           │
           └─► Step 8: Return response with metadata
               {
                 "response": "Our return policy...",
                 "sources": [{...}],
                 "session_id": "abc123",
                 "context_used": true
               }
```

**File**: `src/rag_pipeline.py:67-151`

---

### **4️⃣ Response Enhancement**

```
API adds extra features:
           │
           ├─► Hallucination Detection
           │   Check if response is grounded in sources
           │   Risk level: Low/Medium/High
           │
           ├─► Generate message_id
           │   UUID for feedback tracking
           │
           └─► Return ChatResponse
```

**File**: `src/api/main.py:216-236`

---

### **5️⃣ Frontend Displays Response**

```
chat.js receives response
           │
           ├─► Remove loading spinner
           │
           ├─► Stream text with typing effect
           │   Character-by-character animation
           │
           ├─► Add sources (📚 section)
           │   Show relevant documents used
           │
           ├─► Add feedback buttons (👍 👎)
           │
           ├─► Show "People Also Asked"
           │   Generate related follow-up questions
           │
           └─► Re-enable input field
```

**File**: `frontend/chat.js:543-672`

---

## 🧩 Key Components Explained

### **📦 Vector Store (FAISS)**
**Location**: `src/vector_store/faiss_store.py`

- Stores document embeddings (768-dimensional vectors)
- Uses `sentence-transformers/all-MiniLM-L6-v2` model
- Fast similarity search (IndexFlatL2)
- Currently has **125 documents** loaded

**How it works**:
```python
User Query: "refund"
    ↓
Embedding Model → [0.24, -0.18, 0.91, ...] (768 numbers)
    ↓
FAISS Search → Find similar document vectors
    ↓
Return top 5 matching documents
```

---

### **🔍 Hybrid Retrieval**
**Location**: `src/retrieval/retriever.py`, `src/retrieval/bm25_retriever.py`

Combines 3 search methods:

| Method | Type | Weight | Purpose |
|--------|------|--------|---------|
| **Vector Search** | Semantic | 50% | Understands meaning |
| **BM25 Search** | Keyword | 30% | Exact word matching |
| **Reformulated Query** | Enhanced | 20% | Improved question |

**Example**:
```
User: "can I return"
Vector Search → Finds "return policy", "refund guidelines"
BM25 Search   → Finds exact word "return" in docs
Reformulated  → "What is the return policy?" (clearer)
```

---

### **🧠 LLM Client (Groq API)**
**Location**: `src/llm/huggingface_client.py`

- **Model**: `llama-3.1-8b-instant` (FREE tier)
- **API**: Groq (70k tokens/day free)
- **Speed**: Ultra-fast inference
- **Cost**: $0 (completely free)

**Prompt Template**:
```
System: You are a helpful customer support assistant...

Context from Documents:
---
[Retrieved document 1]
[Retrieved document 2]
...
---

User: What is your return policy?