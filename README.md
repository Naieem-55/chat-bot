# AI RAG Chatbot with Full Duplex Voice & Email Notifications

A production-ready Retrieval-Augmented Generation (RAG) chatbot with **full duplex voice conversations**, email notifications, long-term memory, and advanced UI features - **completely FREE** using Groq API.

## 🌟 Key Highlights

- **100% FREE** - Uses Groq's free API (70k tokens/day with Llama 3.1 8B Instant)
- **Full Duplex Voice Chat** - Speak while AI responds, interrupt anytime, natural conversations
- **Email Notifications** - Get notified via email for chat events (new messages, errors, feedback)
- **Long-Term Memory** - Remembers facts, preferences, and conversation context
- **Chat Export** - Export conversations in JSON, TXT, Markdown, or HTML
- **Chat Pinning** - Pin important conversations to the top of sidebar
- **Smart UI** - Context-based emojis, code highlighting, typing animation
- **Dark Theme** - Professional gray/black interface
- **Mobile Ready** - Fully responsive design

## ✨ New Features

### 🎙️ Full Duplex Voice Conversations
- **True 2-way communication**: Speak while AI is responding
- **Interrupt capability**: Stop AI mid-sentence to speak
- **Continuous listening**: Auto-resumes after AI finishes
- **Real-time transcription**: See your words as you speak
- **Visual feedback**: Animated sound waves and status indicators
- **Browser-based**: Works in Chrome, Edge, Safari (no plugins needed)

### 📧 Email Notifications & Webhooks
- **Email alerts**: Get notified when important events occur
- **Event types**: New messages, errors, user feedback, session management
- **Easy setup**: Simple 2-step configuration via web UI
- **Gmail support**: Works with Gmail App Passwords
- **Webhook management**: Create, enable, disable, and delete webhooks
- **HTML emails**: Beautiful formatted email notifications

### 🧠 Long-Term Memory System
- **Context fusion**: Combines recent conversation with long-term memory
- **Fact extraction**: Automatically learns facts about users
- **Preferences**: Remembers user preferences and settings
- **Conversation summaries**: Stores summaries of past conversations
- **Memory UI**: View and manage stored memories

### 📌 Chat Management
- **Pin conversations**: Keep important chats at the top
- **Session history**: Browse all past conversations
- **Auto-titles**: AI generates descriptive titles
- **Timestamps**: See when each conversation occurred
- **Message counts**: Track conversation length

## 🚀 Features

### Core AI Features
- **RAG Pipeline**: Retrieval-Augmented Generation for context-aware responses
- **FAISS Vector Store**: Fast semantic search with FAISS
- **BM25 Hybrid Search**: Combines semantic + keyword search
- **Query Reformulation**: Improves search accuracy
- **Smart Context**: Automatically retrieves relevant documents
- **Session Management**: Multi-turn conversations with history
- **Document Ingestion**: Upload and index PDF, TXT, HTML, MD files
- **Hallucination Detection**: Flags potentially inaccurate responses

### UI/UX Features
- **Full Duplex Voice**: Real-time 2-way voice conversations
- **Voice Input**: Click mic button to speak your query
- **Voice Output**: Toggle to hear AI responses read aloud
- **Chat Export**: Export conversations in 4 formats (JSON, TXT, MD, HTML)
- **Chat History Sidebar**: Browse and switch between past conversations
- **Pin Conversations**: Keep important chats at the top
- **Context Emojis**: Auto-adds relevant emojis like ChatGPT
- **Code Highlighting**: Beautiful code blocks with copy button
- **Typing Animation**: Word-by-word typing effect
- **Feedback System**: Thumbs up/down for response quality
- **Suggested Questions**: Quick-start suggestions
- **People Also Asked**: Related questions after responses
- **Memory Viewer**: Browse stored facts, preferences, and summaries
- **Professional Icons**: Font Awesome 6.4.0 icons throughout

### Technical Features
- **FastAPI Backend**: High-performance async API
- **Free LLM**: Groq API (Llama 3.1 8B Instant) - no cost
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Document Management**: Web interface for managing documents
- **Analytics Dashboard**: View usage statistics and insights
- **Email Notifications**: SMTP integration for event alerts
- **Webhook System**: Subscribe to events and receive notifications

## 📸 Screenshots

### Main Chat Interface
- Dark theme with professional design
- Full duplex voice button next to microphone
- Export button for conversations
- Sidebar toggle for chat history
- Memory viewer button

### Voice Chat Modal
- Animated sound wave visualizer
- Real-time transcription display
- Status indicators (listening/speaking/processing)
- Interrupt button for mid-conversation stops
- Full duplex information panel

### Chat History Sidebar
- Browse past conversations
- Pin/unpin conversations
- Delete old sessions
- Quick session switching
- Message counts and timestamps

### Notification Settings
- Email configuration (SMTP settings)
- Webhook creation and management
- Event subscription checkboxes
- Live status display

## 🏗️ Architecture

```
User Query → Voice/Text Input → Embedding → Hybrid Search (Vector + BM25)
                                               ↓
                                    Context Retrieval + Memory
                                               ↓
                                    Groq API (FREE Llama 3.1)
                                               ↓
                                    Response + Emojis + Memory Update
                                               ↓
                              Hallucination Detection + Typing Animation
                                               ↓
                                    Voice Output + Email Notifications
                                               ↓
                                      Conversation History + Memory
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## 🎯 Quick Start

### Prerequisites

- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge)
- Microphone (for voice input)
- Gmail account (optional, for email notifications)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Naieem-55/chat-bot
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
HUGGINGFACE_API_KEY=your_groq_api_key_here
```

**Get your FREE Groq API key**: Visit https://console.groq.com/keys

4. **Ingest sample data** (optional)
```bash
python scripts/ingest_data.py
```

5. **Start the backend server**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8002 --reload
```
The backend will start on `http://localhost:8002`

6. **Open the frontend**
Simply open `frontend/index.html` in your browser, or serve it:
```bash
cd frontend
python -m http.server 3000
```

7. **Start chatting!**
Navigate to: `http://localhost:3000` or open `index.html` directly

## 📖 Usage Guide

### Basic Chat
1. Type your message in the input box
2. Press Enter or click send button
3. Watch the AI respond with typing animation
4. Click thumbs up/down to provide feedback

### Full Duplex Voice Chat
1. Click the **📞 phone icon** button (next to microphone)
2. Voice chat modal opens and starts listening
3. Start speaking - see real-time transcription
4. AI responds with voice automatically
5. **Interrupt anytime**: Just start speaking or click "Interrupt"
6. Conversation continues hands-free!

**Voice Chat Features:**
- Speak while AI is responding
- Natural conversation flow
- Visual sound wave indicators
- Auto-resumes listening after AI speaks
- No need to press buttons repeatedly

### Email Notifications Setup
1. Click the **🔔 bell icon** in the header
2. **Step 1**: Configure email settings
   - Enter your Gmail address
   - Generate App Password at [Google Account Settings](https://myaccount.google.com/apppasswords)
   - Click "Save & Test Email"
3. **Step 2**: Enable notifications
   - Check events you want to monitor (New Messages, Errors, Feedback)
   - Click "Enable Notifications"
4. Done! You'll receive emails when events occur

### Chat History & Pinning
1. Click the hamburger menu (top-left) to open sidebar
2. Browse past conversations
3. **Pin**: Click 📌 to pin important chats to top
4. **Switch**: Click any session to load it
5. **Delete**: Click 🗑️ trash icon to remove
6. **New**: Click "New Chat" button to start fresh

### Memory Viewer
1. Click the **🧠 brain icon** in header
2. View stored facts about you
3. Browse preferences and settings
4. See conversation summaries
5. Clear memory if needed

### Export Conversations
1. Click the **📥 download icon** in header
2. Choose format: JSON, TXT, Markdown, or HTML
3. File downloads automatically
4. Use JSON for analysis, HTML for sharing

### Document Management
1. Click the **📚 book icon** to open document manager
2. Upload PDF, TXT, HTML, or Markdown files
3. Documents are automatically indexed
4. AI uses them to answer questions

## 📁 Project Structure

```
chatbot/
├── src/
│   ├── api/
│   │   └── main.py                  # FastAPI application with all endpoints
│   ├── data_ingestion/
│   │   ├── document_loader.py       # Load documents from files
│   │   └── text_processor.py        # Text chunking and preprocessing
│   ├── vector_store/
│   │   ├── embeddings.py            # Embedding generation
│   │   ├── faiss_store.py           # FAISS vector store
│   │   └── vector_store_manager.py  # Vector store orchestration
│   ├── retrieval/
│   │   ├── bm25_retriever.py        # BM25 keyword search
│   │   └── retriever.py             # Hybrid retrieval
│   ├── llm/
│   │   ├── huggingface_client.py    # Groq API integration (FREE)
│   │   └── claude_client.py         # Claude API (optional)
│   ├── session/
│   │   └── session_manager.py       # Conversation session management
│   ├── memory/
│   │   └── memory_manager.py        # Long-term memory system
│   ├── feedback/
│   │   ├── feedback_manager.py      # Feedback collection
│   │   └── hallucination_detector.py # Hallucination detection
│   ├── suggestions/
│   │   └── question_generator.py    # Question suggestions
│   ├── notifications/
│   │   ├── email_notifier.py        # Email notification system
│   │   └── webhook_manager.py       # Webhook management
│   ├── config.py                    # Configuration management
│   └── rag_pipeline.py              # Main RAG orchestration
├── frontend/
│   ├── index.html                   # Main chat UI
│   ├── documents.html               # Document management interface
│   ├── analytics.html               # Analytics dashboard
│   ├── notifications.html           # Email notification settings
│   ├── style.css                    # Dark theme styling
│   ├── voice-chat.css               # Voice chat modal styling
│   ├── chat.js                      # Chat logic
│   ├── voice-chat.js                # Full duplex voice system
│   ├── documents.js                 # Document upload logic
│   └── icons/
│       └── logo.png                 # Chatbot logo
├── scripts/
│   ├── ingest_data.py               # Data ingestion script
│   └── test_chatbot.py              # Testing script
├── data/
│   ├── documents/                   # Place your documents here
│   ├── vector_store/                # Vector store data (auto-generated)
│   ├── feedback/                    # Feedback data
│   ├── memory/                      # Long-term memory storage
│   └── webhooks/                    # Webhook configurations
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables
├── ARCHITECTURE.md                  # Detailed architecture documentation
└── README.md                        # This file
```

## 🔌 API Endpoints

### Core Chat Endpoints

**Health Check**
```bash
GET /health
Response: {"status": "healthy", "vector_store_stats": {...}}
```

**Create Session**
```bash
POST /session/create
Response: {"session_id": "uuid"}
```

**Chat**
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
  "sources": [...],
  "context_used": true,
  "hallucination_risk": {...},
  "memory_stats": {...}
}
```

**Session Management**
```bash
GET /sessions/list                      # List all sessions
GET /session/{session_id}/history       # Get conversation history
DELETE /session/{session_id}            # Delete session
PUT /session/{session_id}/pin           # Toggle pin status
PUT /session/{session_id}/title         # Update session title
```

### Memory Endpoints

```bash
GET /memory/{session_id}/facts          # Get stored facts
GET /memory/{session_id}/preferences    # Get preferences
GET /memory/{session_id}/summaries      # Get conversation summaries
GET /memory/{session_id}/stats          # Get memory statistics
DELETE /memory/{session_id}             # Clear user memory
```

### Feedback & Analytics

```bash
POST /feedback                          # Submit feedback
GET /feedback/stats                     # Get feedback statistics
GET /feedback/problematic-queries       # Get problematic queries
GET /feedback/hallucinations            # Get detected hallucinations
```

### Document Management

```bash
POST /documents/upload                  # Upload document
GET /documents/list                     # List all documents
DELETE /documents/{doc_id}              # Delete document
POST /documents/clear                   # Clear all documents
POST /documents/upload-url              # Ingest from URL
```

### Email Notifications & Webhooks

```bash
POST /webhooks/email/configure          # Configure SMTP settings
POST /webhooks/email/test               # Send test email
POST /webhooks/create                   # Create webhook subscription
GET /webhooks/list                      # List all webhooks
GET /webhooks/{webhook_id}              # Get webhook details
DELETE /webhooks/{webhook_id}           # Delete webhook
PUT /webhooks/{webhook_id}/enable       # Enable webhook
PUT /webhooks/{webhook_id}/disable      # Disable webhook
GET /webhooks/events/available          # List available events
```

### Suggestions

```bash
GET /suggestions/common-questions       # Get suggested questions
POST /suggestions/people-also-asked     # Get related questions
```

## ⚙️ Configuration

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (huggingface/claude) | huggingface |
| `HUGGINGFACE_API_KEY` | Groq API key (FREE) | Required |
| `HUGGINGFACE_MODEL` | Model name | mistral |
| `VECTOR_DB_TYPE` | Vector database type | faiss |
| `TOP_K_DOCUMENTS` | Documents to retrieve | 5 |
| `CHUNK_SIZE` | Text chunk size | 500 |
| `CHUNK_OVERLAP` | Overlap between chunks | 50 |
| `MAX_CONVERSATION_HISTORY` | Messages to remember | 10 |
| `EMBEDDING_MODEL` | Sentence transformer model | BAAI/bge-base-en-v1.5 |
| `EMAIL_NOTIFICATIONS_ENABLED` | Enable email notifications | false |
| `SMTP_SERVER` | SMTP server address | smtp.gmail.com |
| `SMTP_PORT` | SMTP port | 587 |
| `SMTP_USERNAME` | SMTP username (email) | |
| `SMTP_PASSWORD` | SMTP password (app password) | |

## 🎙️ Voice Chat Details

### Browser Support
- **Chrome/Edge**: Full support ✅ (recommended)
- **Firefox**: Limited speech recognition
- **Safari**: Partial support (iOS works)
- **Mobile**: Works on modern mobile browsers

### Full Duplex Features
- **Continuous Recognition**: Never stops listening
- **Interrupt Handling**: Gracefully handles interruptions
- **Auto-Restart**: Resumes after errors or interruptions
- **Visual Feedback**: Real-time status indicators
- **Error Recovery**: Automatically recovers from failures

### Voice Input
- Uses Web Speech API (webkitSpeechRecognition)
- Supports English language (can be extended)
- Real-time interim results
- Automatic final transcription

### Voice Output
- Uses Speech Synthesis API
- Natural-sounding voices (Google voices preferred)
- Adjustable rate (1.1x default for faster response)
- Markdown cleaned before speaking

## 📧 Email Notification Events

Available webhook events:

| Event | Description | Trigger |
|-------|-------------|---------|
| `new_message` 💬 | New chat message received | When user sends a message |
| `error` ⚠️ | Error occurred | When chat processing fails |
| `feedback` 📊 | User feedback received | When user gives thumbs up/down |
| `session_created` 🆕 | New session created | When new chat session starts |
| `session_deleted` 🗑️ | Session deleted | When user deletes a session |

## 🎨 Export Formats

### JSON
```json
{
  "session_id": "uuid",
  "exported_at": "2025-10-13T...",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2025-10-13T..."
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?",
      "timestamp": "2025-10-13T..."
    }
  ]
}
```

### Text (TXT)
```
=== Chat Conversation Export ===
Exported: 10/13/2025, 3:45:23 PM

---

You:
Hello

---

AI Assistant:
Hi! How can I help?
```

### Markdown (MD)
```markdown
# Chat Conversation Export

**Exported:** 10/13/2025, 3:45:23 PM

---

### **You**

Hello

---

### **AI Assistant**

Hi! How can I help?
```

### HTML
Standalone HTML file with:
- Inline CSS styling
- Dark theme matching the app
- Properly formatted messages
- Code syntax highlighting
- Responsive design

## 🔧 Customization

### Add Your Own Documents
1. Place files in `data/documents/`
2. Supported: PDF, TXT, HTML, Markdown
3. Run ingestion or use web UI
4. Documents indexed with FAISS + BM25

### Customize System Prompt
Edit `src/llm/huggingface_client.py`:
```python
system_message = "Your custom system prompt here..."
```

### Change Embedding Model
Edit `.env`:
```env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

Available models: https://www.sbert.net/docs/pretrained_models.html

### Adjust Voice Settings
Edit `frontend/voice-chat.js`:
```javascript
this.currentUtterance.rate = 1.2;  // Speech rate
this.currentUtterance.pitch = 1.0; // Voice pitch
this.currentUtterance.volume = 1.0; // Volume
```

### Customize Email Templates
Edit `src/notifications/email_notifier.py`:
```python
# Customize HTML email templates
html_body = f"""
<!DOCTYPE html>
<!-- Your custom email template -->
</html>
"""
```

### Customize Colors
Edit `frontend/style.css` and `frontend/voice-chat.css`:
```css
/* Main theme colors */
--bg-primary: #0f0f0f;
--bg-secondary: #1a1a1a;
--text-primary: #ffffff;
--accent-color: #3498db;
```

## ⚡ Performance

### Free Tier Limits
- **Groq Free API**: 70,000 tokens/day
- **Speed**: ~750 tokens/second
- **Model**: Llama 3.1 8B Instant
- **No credit card required**

### Optimization Tips
- Use smaller chunk sizes for faster retrieval
- Reduce `TOP_K_DOCUMENTS` for quicker responses
- Enable BM25 for better keyword matching
- Use memory to reduce context size
- Cache frequent queries

### Response Times
- Vector search: <50ms
- BM25 search: <20ms
- Hybrid retrieval: <70ms
- LLM generation: 1-3 seconds
- Total response: 1.5-3.5 seconds

## 🧪 Testing

### Test Sample Queries
Try these with the default FAQ data:

- "How do I track my order?"
- "What is your return policy?"
- "Do you ship internationally?"
- "What payment methods do you accept?"
- "How do I reset my password?"
- "Tell me about your company"

### Voice Testing
1. Click the 📞 phone button
2. Say: "What payment methods do you accept?"
3. Listen to the AI response
4. Try interrupting mid-response
5. Continue conversation naturally

### Email Notification Testing
1. Configure email settings
2. Create a webhook for "new_message" event
3. Send a chat message
4. Check your email inbox
5. Verify HTML formatting

### Memory Testing
1. Tell the chatbot facts about yourself
2. Open memory viewer (brain icon)
3. Verify facts are stored
4. Start a new session
5. Ask related questions - it should remember

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check if port 8002 is in use
netstat -ano | findstr :8002

# Kill process if needed (Windows)
taskkill /PID <pid> /F

# Restart backend
uvicorn src.api.main:app --reload
```

### Voice Chat Not Working
- Check browser support (use Chrome/Edge)
- Enable microphone permissions
- Check browser console for errors
- Try refreshing page (Ctrl+F5)
- Verify HTTPS or localhost (required for mic access)

### Email Notifications Not Sending
- Verify SMTP credentials
- Use Gmail App Password (not regular password)
- Check "Less secure app access" disabled (use App Password)
- Test email configuration using test button
- Check backend logs for SMTP errors

### Chat History Not Loading
- Check backend is running on port 8002
- Clear browser cache (Ctrl+F5)
- Check console for API errors
- Verify CORS is configured correctly

### Memory Not Persisting
- Check `data/memory/` directory exists
- Verify file permissions
- Check backend logs for errors
- Ensure session_id is consistent

## 🚀 Deployment

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
- [ ] Configure email server properly
- [ ] Set up database backups

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

## 🔒 Security Considerations

- Store API keys in environment variables (never commit)
- Validate all user inputs
- Sanitize file uploads (limit size, check types)
- Implement rate limiting (10 requests/minute)
- Use HTTPS in production
- Add CSRF protection
- Sanitize HTML output
- Secure email credentials (use app passwords)
- Validate webhook URLs
- Implement authentication for production

## 🎯 Future Enhancements

Planned features:
- [ ] Real-time streaming responses
- [ ] Multi-language voice support
- [ ] Image understanding (vision)
- [ ] File attachments in chat
- [ ] Advanced analytics dashboard
- [ ] User authentication system
- [ ] Team collaboration features
- [ ] Custom branding options
- [ ] Slack/Discord integrations
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [ ] Voice cloning options
- [ ] Multi-model support

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- FAISS (vector database)
- BM25 (keyword search)
- Sentence Transformers (embeddings)
- Groq API (FREE LLM via Hugging Face)
- SMTP (email notifications)

**Frontend:**
- Vanilla JavaScript (no frameworks)
- Web Speech API (full duplex voice)
- Font Awesome 6.4.0 (icons)
- CSS3 (dark theme + animations)

**Storage:**
- In-memory sessions (can switch to Redis)
- Local file system (documents, memory, webhooks)
- FAISS index files

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional export formats (PDF, CSV)
- Vector store backends (Pinecone, Weaviate)
- Advanced reranking algorithms
- Multi-language voice support
- Mobile app version
- Browser extension
- Additional notification channels (Slack, Discord)
- Voice recognition accuracy improvements

## 📄 License

MIT License - free for commercial and personal use

## 💬 Support

- **Issues**: Open a GitHub issue
- **Questions**: Check existing issues first
- **Feature Requests**: Submit via GitHub issues
- **Documentation**: Check ARCHITECTURE.md

## Acknowledgments

- Groq for providing FREE LLM API
- Font Awesome for beautiful icons
- FAISS team for vector search
- Sentence Transformers community
- Web Speech API contributors

---

**Built with ❤️ using FREE Groq API**

**Features:**
✅ Full duplex voice conversations
✅ Email notifications
✅ Long-term memory
✅ Chat pinning
✅ Export in 4 formats
✅ Hallucination detection
✅ Analytics dashboard
