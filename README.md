# RAG Customer Support Chatbot

A production-ready Retrieval-Augmented Generation (RAG) chatbot powered by for customer support.

## Features

- 🤖 **AI Integration**: Uses  intelligent context-aware responses
- 📚 **Vector Search**: FAISS-based semantic search for accurate document retrieval
- 💬 **Multi-turn Conversations**: Session management for contextual dialogue
- 🎨 **Modern UI**: Clean, responsive web interface
- ⚡ **Fast API**: Built with FastAPI for high performance
- 🔧 **Configurable**: Easy configuration via environment variables

## Architecture

```
User Query → Embedding → Vector Search → Context Retrieval → API → Response
                                                ↓
                                        Conversation History
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Quick Start

### 🚀 Easy Start (Recommended)

Run the entire application with a single command:

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

The script will automatically:
1. Check for `.env` configuration
2. Run data ingestion (if needed)
3. Start the backend server (http://localhost:8000)
4. Start the frontend server (http://localhost:3000)
5. Open the chatbot in your browser

### 📋 Manual Setup

If you prefer to set up manually:

#### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

#### 2. Configuration

Create a `.env` file from the example:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and add your API key:

```env
API_KEY=your_api_key
```

#### 3. Ingest Data

Index your documents (or use the example FAQ data):

```bash
python scripts/ingest_data.py
```

To add your own documents:
1. Place files (PDF, TXT, HTML, MD) in `data/documents/`
2. Uncomment the directory loading section in `ingest_data.py`
3. Run the ingestion script

#### 4. Start the Server

```bash
# Using the provided script
python run_server.py

# Or directly with uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. Open the Chatbot

Open `frontend/index.html` in your browser or serve it with:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 3000
```

Then navigate to: `http://localhost:3000`

## Project Structure

```
chatbot/
├── src/
│   ├── api/
│   │   └── main.py                  # FastAPI application
│   ├── data_ingestion/
│   │   ├── document_loader.py       # Load documents from files
│   │   └── text_processor.py        # Text chunking and preprocessing
│   ├── vector_store/
│   │   ├── embeddings.py            # Embedding generation
│   │   ├── faiss_store.py           # FAISS vector store
│   │   └── vector_store_manager.py  # Vector store orchestration
│   ├── retrieval/
│   │   └── retriever.py             # Document retrieval and ranking
│   ├── llm/
│   │   └── claude_client.py         # Claude API integration
│   ├── session/
│   │   └── session_manager.py       # Conversation session management
│   ├── config.py                    # Configuration management
│   └── rag_pipeline.py              # Main RAG orchestration
├── frontend/
│   ├── index.html                   # Chatbot UI
│   ├── style.css                    # Styling
│   └── chat.js                      # Frontend logic
├── scripts/
│   ├── ingest_data.py               # Data ingestion script
│   └── test_chatbot.py              # Testing script
├── data/
│   ├── documents/                   # Place your documents here
│   └── vector_store/                # Vector store data (auto-generated)
├── start.bat                        # Windows startup script
├── start.sh                         # Linux/Mac startup script
├── run_server.py                    # Backend server runner
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── ARCHITECTURE.md                  # Detailed architecture documentation
└── README.md                        # This file
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Create Session
```bash
POST /session/create
Response: {"session_id": "uuid"}
```

### Chat
```bash
POST /chat
Body: {
  "message": "How do I track my order?",
  "session_id": "uuid",
  "stream": false
}
Response: {
  "response": "You can track your order...",
  "session_id": "uuid",
  "sources": [...],
  "context_used": true
}
```

### Get Session History
```bash
GET /session/{session_id}/history
```

### Delete Session
```bash
DELETE /session/{session_id}
```

## Testing

### Interactive CLI Test
```bash
python scripts/test_chatbot.py
```

### Example Test Queries

The chatbot comes with example FAQ data. Try these queries:

- "How do I track my order?"
- "What is your return policy?"
- "Do you ship internationally?"
- "What payment methods do you accept?"
- "How do I reset my password?"

## Configuration Options

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | API key | Required |
| `MODEL` | model name | ... |
| `VECTOR_DB_TYPE` | Vector database type | faiss |
| `TOP_K_DOCUMENTS` | Documents to retrieve | 5 |
| `CHUNK_SIZE` | Text chunk size | 500 |
| `MAX_CONVERSATION_HISTORY` | Messages to remember | 10 |

## Customization

### Adding Your Own Documents

1. Place documents in `data/documents/`
2. Supported formats: PDF, TXT, HTML, Markdown
3. Run `python scripts/ingest_data.py`

### Customizing Prompts

```python
class PromptTemplate:
    SYSTEM_PROMPT = """Your custom system prompt..."""
```

### Changing Embedding Model

Edit `.env`:

```env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

Available models: https://www.sbert.net/docs/pretrained_models.html

## Production Deployment

### Docker Deployment (Coming Soon)

```dockerfile
# Dockerfile example
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment Considerations

1. **Vector Store**: Use Pinecone for scalable cloud vector storage
2. **Session Storage**: Use Redis for distributed session management
3. **Load Balancing**: Deploy multiple API instances behind a load balancer
4. **Monitoring**: Add logging and monitoring (e.g., DataDog, New Relic)
5. **Security**:
   - Use HTTPS only
   - Add rate limiting
   - Implement API authentication

## Performance Optimization

- **Batch Processing**: Process multiple queries in parallel
- **Caching**: Cache frequent queries with Redis
- **GPU Acceleration**: Use `faiss-gpu` for faster similarity search
- **Async Processing**: All I/O operations are async-ready


## Contributing

Contributions welcome! Areas for improvement:
- Streaming responses implementation
- Additional vector store backends (Pinecone, Weaviate)
- Advanced reranking with cross-encoders
- Multi-language support
- Analytics and monitoring dashboard

## License

MIT License - feel free to use for commercial or personal projects

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---
