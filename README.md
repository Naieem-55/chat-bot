# AI RAG Chatbot with Full Duplex Voice & Email Notifications

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready Retrieval-Augmented Generation (RAG) chatbot with **full duplex voice conversations**, email notifications, long-term memory, and advanced UI features - **completely FREE** using Groq API.

## Key Highlights

- **100% FREE** - Uses Groq's free API (70k tokens/day with Llama 3.1 8B Instant)
- **Full Duplex Voice Chat** - Speak while AI responds, interrupt anytime, natural conversations
- **Email Notifications** - Get notified via email for chat events
- **Long-Term Memory** - Remembers facts, preferences, and conversation context
- **Chat Export** - Export conversations in JSON, TXT, Markdown, or HTML
- **Smart UI** - Context-based emojis, code highlighting, typing animation

## Quick Start

```bash
# Clone and install
git clone https://github.com/Naieem-55/chat-bot
cd chatbot
pip install -r requirements.txt

# Configure (get FREE key from https://console.groq.com/keys)
cp .env.example .env
# Edit .env and add: HUGGINGFACE_API_KEY=your_groq_api_key

# Run
uvicorn src.api.main:app --host 0.0.0.0 --port 8002 --reload
```

Open `frontend/index.html` in your browser and start chatting!

## Features

### Core AI Features
- **RAG Pipeline**: Retrieval-Augmented Generation for context-aware responses
- **FAISS Vector Store**: Fast semantic search with FAISS
- **BM25 Hybrid Search**: Combines semantic + keyword search
- **Query Reformulation**: Improves search accuracy
- **Session Management**: Multi-turn conversations with history
- **Document Ingestion**: Upload and index PDF, TXT, HTML, MD files
- **Hallucination Detection**: Flags potentially inaccurate responses

### Voice & UI Features
- **Full Duplex Voice**: Real-time 2-way voice conversations
- **Voice Input/Output**: Speak queries and hear responses
- **Chat Export**: Export in 4 formats (JSON, TXT, MD, HTML)
- **Pin Conversations**: Keep important chats at the top
- **Context Emojis**: Auto-adds relevant emojis
- **Code Highlighting**: Beautiful code blocks with copy button

## Architecture

```
User Query → Voice/Text Input → Embedding → Hybrid Search (Vector + BM25)
                                               ↓
                                    Context Retrieval + Memory
                                               ↓
                                    Groq API (FREE Llama 3.1)
                                               ↓
                                    Response + Voice Output + Notifications
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Project Structure

```
chatbot/
├── src/
│   ├── api/main.py                 # FastAPI application
│   ├── data_ingestion/             # Document loading & processing
│   ├── vector_store/               # FAISS vector store
│   ├── retrieval/                  # Hybrid retrieval (BM25 + semantic)
│   ├── llm/                        # Groq/Claude API clients
│   ├── session/                    # Session management
│   ├── memory/                     # Long-term memory system
│   ├── feedback/                   # Feedback & hallucination detection
│   └── notifications/              # Email & webhook system
├── frontend/
│   ├── index.html                  # Main chat UI
│   ├── style.css                   # Dark theme styling
│   └── chat.js                     # Chat logic
├── data/
│   ├── documents/                  # Your documents
│   ├── vector_store/               # FAISS index
│   └── memory/                     # Memory storage
└── requirements.txt
```

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/session/create` | POST | Create new session |
| `/chat` | POST | Send message |
| `/sessions/list` | GET | List all sessions |
| `/session/{id}/history` | GET | Get conversation history |

### Memory & Feedback

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/memory/{id}/facts` | GET | Get stored facts |
| `/feedback` | POST | Submit feedback |
| `/feedback/stats` | GET | Get feedback statistics |

### Documents & Notifications

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/documents/upload` | POST | Upload document |
| `/documents/list` | GET | List documents |
| `/webhooks/email/configure` | POST | Configure email |
| `/webhooks/create` | POST | Create webhook |

## Configuration

Key options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `HUGGINGFACE_API_KEY` | Groq API key (FREE) | Required |
| `TOP_K_DOCUMENTS` | Documents to retrieve | 5 |
| `CHUNK_SIZE` | Text chunk size | 500 |
| `EMBEDDING_MODEL` | Sentence transformer | BAAI/bge-base-en-v1.5 |
| `SMTP_SERVER` | Email server | smtp.gmail.com |

## Security Considerations

### Authentication & Data Protection
- Store API keys in environment variables (never commit `.env`)
- Validate all user inputs server-side
- Sanitize file uploads (limit size, check MIME types)
- Use HTTPS in production

### Rate Limiting
- Groq API: 70k tokens/day (free tier)
- Implement request rate limiting (recommended: 10 req/min per user)

### Session Security
- Session IDs are UUID v4 (cryptographically secure)
- Sessions stored server-side only
- Consider adding user authentication for production

### Production Checklist
- [ ] Enable HTTPS only
- [ ] Add user authentication
- [ ] Implement rate limiting middleware
- [ ] Configure CORS properly
- [ ] Set up request logging
- [ ] Enable CSRF protection
- [ ] Use Redis for session storage

## Testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8002/health

# Test chat
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test-session"}'
```

### Sample Queries
- "How do I track my order?"
- "What is your return policy?"
- "What payment methods do you accept?"

### Voice Testing
1. Click the phone button
2. Say: "What payment methods do you accept?"
3. Try interrupting mid-response
4. Continue conversation naturally

## Performance

| Metric | Value |
|--------|-------|
| Vector search | <50ms |
| BM25 search | <20ms |
| LLM generation | 1-3 seconds |
| Total response | 1.5-3.5 seconds |

### Optimization Tips
- Reduce `TOP_K_DOCUMENTS` for faster responses
- Use smaller chunk sizes for quicker retrieval
- Enable BM25 for better keyword matching

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check if port 8002 is in use: `netstat -ano \| findstr :8002` |
| Voice not working | Use Chrome/Edge; enable microphone permissions |
| Email not sending | Use Gmail App Password, not regular password |
| Memory not persisting | Check `data/memory/` directory permissions |

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Write tests for new functionality
4. Commit your changes (`git commit -m 'Add new feature'`)
5. Push to the branch (`git push origin feature/new-feature`)
6. Open a Pull Request

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to functions
- Type hints are encouraged

## Known Limitations

- Voice chat requires Chrome/Edge (Firefox has limited support)
- Groq free tier: 70k tokens/day limit
- Memory storage is file-based (consider Redis for production)
- No built-in user authentication

## License

MIT License - free for commercial and personal use.

## Acknowledgments

- Groq for providing FREE LLM API
- FAISS team for vector search
- Sentence Transformers community
