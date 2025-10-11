# AI RAG Chatbot with Voice & Export Features

A production-ready Retrieval-Augmented Generation (RAG) chatbot with voice interaction, chat export, and advanced UI features - **completely FREE** using Groq API.

## Key Highlights

- **100% FREE** - Uses Groq's free API (70k tokens/day with Llama 3.1 8B Instant)
- **Voice Chat** - Speech-to-text input and text-to-speech output
- **Export Chats** - Export conversations in JSON, TXT, Markdown, or HTML
- **Chat History** - Sidebar with session management and history
- **Smart UI** - Context-based emojis, code highlighting, typing animation
- **Dark Theme** - Professional gray/black interface
- **Mobile Ready** - Fully responsive design

## Features

### Core AI Features
- **RAG Pipeline**: Retrieval-Augmented Generation for context-aware responses
- **FAISS Vector Store**: Fast semantic search with FAISS
- **Smart Context**: Automatically retrieves relevant documents
- **Session Management**: Multi-turn conversations with history
- **Document Ingestion**: Upload and index PDF, TXT, HTML, MD files

### UI/UX Features
- **Voice Input**: Click mic button to speak your query
- **Voice Output**: Toggle to hear AI responses read aloud
- **Chat Export**: Export conversations in 4 formats (JSON, TXT, MD, HTML)
- **Chat History Sidebar**: Browse and switch between past conversations
- **Context Emojis**: Auto-adds relevant emojis like ChatGPT
- **Code Highlighting**: Beautiful code blocks with copy button
- **Typing Animation**: Word-by-word typing effect
- **Feedback System**: Thumbs up/down for response quality
- **Suggested Questions**: Quick-start suggestions
- **Professional Icons**: Font Awesome 6.4.0 icons throughout

### Technical Features
- **FastAPI Backend**: High-performance async API
- **Free LLM**: Groq API (Llama 3.1 8B Instant) - no cost
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Document Management**: Web interface for managing documents
- **Analytics Page**: View usage statistics and insights

## Screenshots

### Main Chat Interface
- Dark theme with professional design
- Voice input/output controls
- Export button for conversations
- Sidebar toggle for chat history

### Chat History Sidebar
- Browse past conversations
- Delete old sessions
- Quick session switching
- Message counts and timestamps

### Export Modal
- JSON format for data analysis
- Text format for plain reading
- Markdown for documentation
- HTML for standalone viewing

## Architecture

```
User Query → Voice/Text Input → Embedding → Vector Search
                                               ↓
                                         Context Retrieval
                                               ↓
                                    Groq API (FREE Llama 3.1)
                                               ↓
                                         Response + Emojis
                                               ↓
                                    Typing Animation + Voice
                                               ↓
                                      Conversation History
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Quick Start

### Prerequisites

- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge)
- Microphone (for voice input)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd chatbot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and add your **FREE Groq API key**:
```env
GROQ_API_KEY=your_groq_api_key_here
```

**Get your FREE Groq API key**: Visit https://console.groq.com/keys

4. **Ingest sample data** (optional)
```bash
python scripts/ingest_data.py
```

5. **Start the backend server**
```bash
python run_server.py
```
The backend will start on `http://localhost:8002`

6. **Start the frontend**
```bash
cd frontend
python -m http.server 3000
```

7. **Open in browser**
Navigate to: `http://localhost:3000`

## Usage Guide

### Basic Chat
1. Type your message in the input box
2. Press Enter or click send button
3. Watch the AI respond with typing animation

### Voice Chat
1. Click the microphone button to speak
2. Your speech will be transcribed to text
3. Toggle the speaker icon to enable voice output
4. AI responses will be read aloud

### Chat History
1. Click the hamburger menu (top-left) to open sidebar
2. Browse past conversations
3. Click any session to load it
4. Click trash icon to delete
5. Click "New Chat" to start fresh

### Export Conversations
1. Click the download icon in header
2. Choose format: JSON, TXT, Markdown, or HTML
3. File downloads automatically
4. Use JSON for analysis, HTML for sharing

### Document Management
1. Click the book icon to open document manager
2. Upload PDF, TXT, HTML, or Markdown files
3. Documents are automatically indexed
4. AI uses them to answer questions

## Project Structure

```
chatbot/
├── src/
│   ├── api/
│   │   └── main.py                  # FastAPI application with all endpoints
│   ├── data_ingestion/
│   │   ├── document_loader.py       # Load documents from files
│   │   └── text_processor.py        # Text chunking and preprocessing
│   ├── vector_store/
│   │   ├── embeddings.py            # Embedding generation (sentence-transformers)
│   │   ├── faiss_store.py           # FAISS vector store
│   │   └── vector_store_manager.py  # Vector store orchestration
│   ├── retrieval/
│   │   └── retriever.py             # Document retrieval and ranking
│   ├── llm/
│   │   └── groq_client.py           # Groq API integration (FREE)
│   ├── session/
│   │   └── session_manager.py       # Conversation session management
│   ├── config.py                    # Configuration management
│   └── rag_pipeline.py              # Main RAG orchestration
├── frontend/
│   ├── index.html                   # Main chat UI with voice controls
│   ├── documents.html               # Document management interface
│   ├── analytics.html               # Analytics dashboard
│   ├── style.css                    # Dark theme styling
│   ├── chat.js                      # Chat logic with voice & export
│   └── documents.js                 # Document upload logic
├── scripts/
│   ├── ingest_data.py               # Data ingestion script
│   └── test_chatbot.py              # Testing script
├── data/
│   ├── documents/                   # Place your documents here
│   └── vector_store/                # Vector store data (auto-generated)
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
Response: {"status": "healthy"}
```

### Create Session
```bash
POST /session/create
Response: {
  "session_id": "uuid",
  "created_at": "2025-10-11T..."
}
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
  "message_id": "uuid",
  "sources": [
    {
      "source": "faq_shipping.txt",
      "relevance_score": 0.89,
      "category": "Shipping"
    }
  ],
  "context_used": true
}
```

### Get Session History
```bash
GET /session/{session_id}/history
Response: {
  "session_id": "uuid",
  "history": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2025-10-11T..."
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?",
      "timestamp": "2025-10-11T..."
    }
  ]
}
```

### List All Sessions
```bash
GET /sessions/list
Response: {
  "sessions": [
    {
      "session_id": "uuid",
      "title": "Order tracking help",
      "message_count": 12,
      "last_active": "2025-10-11T..."
    }
  ]
}
```

### Delete Session
```bash
DELETE /session/{session_id}
Response: {"message": "Session deleted successfully"}
```

### Submit Feedback
```bash
POST /feedback
Body: {
  "message_id": "uuid",
  "session_id": "uuid",
  "user_query": "How do I return?",
  "bot_response": "You can return...",
  "feedback": "positive",
  "sources": [...],
  "context_used": true
}
```

### Upload Document
```bash
POST /documents/upload
Body: multipart/form-data
  file: <file>
  category: "Product Info"
```

## Configuration

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key (FREE from console.groq.com) | Required |
| `MODEL_NAME` | Groq model name | llama-3.1-8b-instant |
| `VECTOR_DB_TYPE` | Vector database type | faiss |
| `TOP_K_DOCUMENTS` | Documents to retrieve | 5 |
| `CHUNK_SIZE` | Text chunk size | 500 |
| `CHUNK_OVERLAP` | Overlap between chunks | 50 |
| `MAX_CONVERSATION_HISTORY` | Messages to remember | 10 |
| `EMBEDDING_MODEL` | Sentence transformer model | all-MiniLM-L6-v2 |
| `SESSION_TIMEOUT_MINUTES` | Session expiry time | 60 |

## Voice Chat Details

### Browser Support
- **Chrome/Edge**: Full support (recommended)
- **Firefox**: Speech recognition limited
- **Safari**: Partial support

### Voice Input
- Uses Web Speech API (webkitSpeechRecognition)
- Supports English language
- Click microphone button to start
- Auto-sends when voice mode enabled

### Voice Output
- Uses Speech Synthesis API
- Cleans markdown before speaking
- Adjustable rate (1.1x default)
- Prefers natural-sounding voices

## Export Formats

### JSON
```json
{
  "session_id": "uuid",
  "exported_at": "2025-10-11T...",
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?"
    }
  ]
}
```

### Text (TXT)
```
You:
Hello

---

AI Assistant:
Hi! How can I help?

---
```

### Markdown (MD)
```markdown
# Chat Conversation Export

**Exported:** 10/11/2025, 3:45:23 PM

---

### **You**

Hello

---

### **AI Assistant**

Hi! How can I help?
```

### HTML
Standalone HTML file with inline CSS, dark theme, properly formatted messages.

## Customization

### Add Your Own Documents
1. Place files in `data/documents/`
2. Supported: PDF, TXT, HTML, Markdown
3. Run `python scripts/ingest_data.py`
4. Documents indexed with FAISS

### Customize System Prompt
Edit `src/llm/groq_client.py`:
```python
system_message = "Your custom system prompt here..."
```

### Change Embedding Model
Edit `.env`:
```env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

Available models: https://www.sbert.net/docs/pretrained_models.html

### Adjust Emoji Patterns
Edit `frontend/chat.js` function `addContextEmojis()`:
```javascript
const emojiPatterns = [
    { pattern: /\b(custom|word)\b/gi, emoji: '✨', position: 'after' },
    // Add your patterns...
];
```

### Customize Colors
Edit `frontend/style.css`:
```css
:root {
    --bg-primary: #0f0f0f;
    --bg-secondary: #1a1a1a;
    --text-primary: #ffffff;
    --accent-color: #3498db;
}
```

## Performance

### Free Tier Limits
- **Groq Free API**: 70,000 tokens/day
- **Speed**: ~750 tokens/second
- **Model**: Llama 3.1 8B Instant

### Optimization Tips
- Use smaller chunk sizes for faster retrieval
- Reduce `TOP_K_DOCUMENTS` for quicker responses
- Cache frequent queries
- Use `faiss-gpu` for GPU acceleration

### Response Times
- Vector search: <50ms
- LLM generation: 1-3 seconds
- Total response: 1.5-3.5 seconds

## Testing

### Test Sample Queries
Try these with the default FAQ data:

- "How do I track my order?"
- "What is your return policy?"
- "Do you ship internationally?"
- "What payment methods do you accept?"
- "How do I reset my password?"
- "Tell me about your company"

### Voice Testing
1. Enable voice mode (speaker icon)
2. Click microphone and say: "What payment methods do you accept?"
3. Listen to the AI response
4. Test different accents and speeds

### Export Testing
1. Have a conversation (3-5 messages)
2. Click export button
3. Try each format
4. Verify downloaded files

## Troubleshooting

### Backend Won't Start
```bash
# Check if port 8002 is in use
netstat -ano | findstr :8002

# Kill process if needed (Windows)
taskkill /PID <pid> /F

# Restart backend
python run_server.py
```

### Voice Input Not Working
- Check browser support (use Chrome)
- Enable microphone permissions
- Check browser console for errors
- Try refreshing page (Ctrl+F5)

### Export Not Downloading
- Check browser download settings
- Allow pop-ups for localhost
- Check browser console for errors

### Chat History Not Loading
- Check backend is running on port 8002
- Clear browser cache (Ctrl+F5)
- Check console for API errors
- Verify session_id in localStorage

## Deployment

### Production Checklist
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS only
- [ ] Add rate limiting
- [ ] Implement authentication
- [ ] Set up monitoring/logging
- [ ] Use Redis for session storage
- [ ] Deploy with Docker
- [ ] Configure CORS properly
- [ ] Set up CDN for frontend
- [ ] Enable compression

### Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

Build and run:
```bash
docker build -t rag-chatbot .
docker run -p 8002:8002 --env-file .env rag-chatbot
```

## Security Considerations

- Store API keys in environment variables (never commit)
- Validate all user inputs
- Sanitize file uploads
- Implement rate limiting (10 requests/minute)
- Use HTTPS in production
- Add CSRF protection
- Sanitize HTML output
- Limit file upload sizes (10MB max)

## Future Enhancements

Planned features:
- [ ] Real-time streaming responses
- [ ] Multi-language support
- [ ] Image understanding
- [ ] File attachments in chat
- [ ] Advanced analytics dashboard
- [ ] User authentication
- [ ] Team collaboration features
- [ ] Custom branding options
- [ ] API rate limiting UI
- [ ] Webhook integrations

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- FAISS (vector database)
- Sentence Transformers (embeddings)
- Groq API (FREE LLM)

**Frontend:**
- Vanilla JavaScript (no frameworks)
- Font Awesome 6.4.0 (icons)
- Web Speech API (voice)
- CSS3 (dark theme)

**Storage:**
- In-memory sessions (can switch to Redis)
- Local file system (documents)
- FAISS index files

## Contributing

Contributions welcome! Areas for improvement:
- Additional export formats (PDF, CSV)
- Vector store backends (Pinecone, Weaviate)
- Advanced reranking algorithms
- Multi-language voice support
- Mobile app version
- Browser extension

## License

MIT License - free for commercial and personal use

## Support

- **Issues**: Open a GitHub issue
- **Questions**: Check existing issues first
- **Feature Requests**: Submit via GitHub issues

## Acknowledgments

- Groq for providing FREE LLM API
- Font Awesome for beautiful icons
- FAISS team for vector search
- Sentence Transformers community

---

**Built with ❤️ using FREE Groq API**

**No credit card required • 70k tokens/day free tier**
