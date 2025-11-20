# Running with Docker Desktop

## Prerequisites
1. Install **Docker Desktop** from: https://www.docker.com/products/docker-desktop/
2. Make sure Docker Desktop is running

## Quick Start

### Step 1: Build and Run

Open terminal in the project folder and run:

```bash
docker-compose up --build
```

This will:
- Build the Docker image
- Start the backend on `http://localhost:8002`
- Enable hot-reload for development

### Step 2: Access the Application

**Backend API:**
- URL: http://localhost:8002
- Docs: http://localhost:8002/docs
- Health: http://localhost:8002/health

**Frontend:**
- GitHub Pages: https://naieem-55.github.io/chat-bot/
- Or open `frontend/index.html` in your browser

### Step 3: Upload Documents

1. Visit http://localhost:8002/docs
2. Go to `/documents/upload` endpoint
3. Upload your PDF files
4. Or use the frontend Documents page

## Commands

**Start the backend:**
```bash
docker-compose up
```

**Start in background (detached mode):**
```bash
docker-compose up -d
```

**Stop the backend:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Rebuild after code changes:**
```bash
docker-compose up --build
```

**Stop and remove everything (including volumes):**
```bash
docker-compose down -v
```

## Environment Variables

Edit `docker-compose.yml` to update your API keys:

```yaml
environment:
  - GROQ_API_KEY=your_groq_key_here
  - ANTHROPIC_API_KEY=your_anthropic_key_here
```

Or create a `.env` file:

```env
GROQ_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Data Persistence

Your data is stored in the `./data` folder:
- Vector store: `./data/vector_store/`
- Feedback: `./data/feedback/`

This data persists even when you stop Docker!

## Troubleshooting

**Port already in use:**
```bash
# Change the port in docker-compose.yml
ports:
  - "8003:8002"  # Use 8003 instead
```

**Out of memory:**
- Increase Docker Desktop memory limit in Settings → Resources

**Logs not showing:**
```bash
docker-compose logs -f backend
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up --build
```

## Production Deployment

For production, use:
```bash
docker build -t chatbot-backend .
docker run -p 8002:8002 -e GROQ_API_KEY=your_key chatbot-backend
```

---

🎉 Your chatbot backend is now running in Docker!
