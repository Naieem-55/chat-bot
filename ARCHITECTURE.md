# RAG Customer Support Chatbot Architecture

## Overview
This chatbot uses Retrieval-Augmented Generation (RAG) to provide accurate customer support by combining vector search with Claude AI's reasoning capabilities.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Website)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Chat Interface (React/HTML+JS)                          │   │
│  │  - Message display                                       │   │
│  │  - User input                                            │   │
│  │  - Session handling                                      │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└────────────────────────┼──────────────────────────────────────────┘
                         │ WebSocket/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Python/FastAPI)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Layer                                               │   │
│  │  - /chat endpoint                                        │   │
│  │  - Session management                                    │   │
│  │  - Conversation memory                                   │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                          │
│  ┌────────────────────┴─────────────────────────────────────┐   │
│  │  RAG Pipeline                                            │   │
│  │  ┌─────────────────────────────────────────────────────┐│   │
│  │  │ 1. Query Processing                                 ││   │
│  │  │    - Query embedding generation                     ││   │
│  │  └─────────────────────┬───────────────────────────────┘│   │
│  │                        │                                 │   │
│  │  ┌─────────────────────▼───────────────────────────────┐│   │
│  │  │ 2. Vector Search (FAISS/Pinecone)                   ││   │
│  │  │    - Similarity search                              ││   │
│  │  │    - Top-k document retrieval                       ││   │
│  │  └─────────────────────┬───────────────────────────────┘│   │
│  │                        │                                 │   │
│  │  ┌─────────────────────▼───────────────────────────────┐│   │
│  │  │ 3. Context Assembly                                 ││   │
│  │  │    - Rank retrieved documents                       ││   │
│  │  │    - Build context window                           ││   │
│  │  └─────────────────────┬───────────────────────────────┘│   │
│  │                        │                                 │   │
│  │  ┌─────────────────────▼───────────────────────────────┐│   │
│  │  │ 4. LLM Generation (Claude API)                      ││   │
│  │  │    - Prompt construction                            ││   │
│  │  │    - Response generation                            ││   │
│  │  │    - Answer validation                              ││   │
│  │  └─────────────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA INGESTION (Offline)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Document Processing                                     │   │
│  │  1. Load documents (FAQs, docs, help articles)          │   │
│  │  2. Chunk text (overlap strategy)                       │   │
│  │  3. Generate embeddings                                 │   │
│  │  4. Store in vector database                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. **Document Ingestion Pipeline (Offline/Batch)**
- **Location**: Backend (Python scripts)
- **Purpose**: Process company documentation into searchable vectors
- **Components**:
  - Document loaders (PDF, HTML, Markdown, TXT)
  - Text chunkers with overlap
  - Embedding model (sentence-transformers)
  - Vector database (FAISS for local, Pinecone for cloud)

### 2. **Vector Store**
- **Options**:
  - **FAISS** (Local): Fast, free, no API calls, good for <1M docs
  - **Pinecone** (Cloud): Scalable, managed, better for >1M docs
- **Storage**: Persistent on disk/cloud
- **Index Type**: HNSW for fast approximate nearest neighbor search

### 3. **Backend API (Runtime)**
- **Framework**: FastAPI (async support, automatic docs)
- **Responsibilities**:
  - Receive user queries
  - Manage conversation sessions
  - Orchestrate RAG pipeline
  - Stream responses to frontend
- **Session Management**: Redis or in-memory dict for multi-turn context

### 4. **RAG Orchestration**
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (fast, good quality)
- **Retrieval**: Top-k similar documents (k=3-5)
- **Reranking**: Optional cross-encoder for better relevance
- **LLM**: Claude API (Sonnet for balance of speed/quality)

### 5. **Frontend Interface**
- **Technology**: React or vanilla HTML/JS
- **Features**:
  - Real-time messaging
  - Typing indicators
  - Session persistence
  - Responsive design

## Data Flow

### Query Processing Flow
```
User Query
    ↓
[1] Embed query using same model as documents
    ↓
[2] Search vector store for top-k similar chunks (k=5)
    ↓
[3] Retrieve document metadata and text
    ↓
[4] Construct prompt:
    - System instructions
    - Retrieved context documents
    - Conversation history (last 5 turns)
    - Current user query
    ↓
[5] Send to Claude API
    ↓
[6] Stream response back to user
    ↓
[7] Store exchange in session memory
```

## Deployment Strategy

### Development
- FAISS local vector store
- In-memory session storage
- Single-server FastAPI

### Production
- Pinecone vector database (or managed FAISS)
- Redis for session management
- Load-balanced FastAPI instances
- CDN for frontend
- Environment-based configuration

## Security Considerations
- API key management (environment variables)
- Rate limiting on endpoints
- Input validation and sanitization
- CORS configuration
- HTTPS only in production

## Scalability
- Horizontal scaling of API servers
- Vector database sharding for large datasets
- Caching frequent queries
- Async processing for non-blocking I/O
